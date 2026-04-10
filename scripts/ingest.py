"""
Ingestion script for TaskFlow knowledge base.

Reads markdown docs from knowledge_base/docs/,
splits them by markdown headings into sections,
embeds each section using OpenAI text-embedding-3-small,
and upserts to a Pinecone index.

Usage:
    python scripts/ingest.py

Prerequisites:
    - OPENAI_API_KEY in .env
    - PINECONE_API_KEY in .env
    - A Pinecone index named "taskflow-support" with dimension=1536 and metric="cosine"
"""

import os
import re
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

# -------------------
# Config
# -------------------
DOCS_DIR = Path(__file__).parent.parent / "knowledge_base" / "docs"
INDEX_NAME = "taskflow-support"
EMBEDDING_MODEL = "text-embedding-3-small"
NAMESPACE = "taskflow-kb"
BATCH_SIZE = 50  # Pinecone upsert batch size


# -------------------
# 1. Read markdown files
# -------------------
def load_markdown_files(docs_dir: Path) -> list[dict]:
    """Load all .md files from the docs directory."""
    files = []
    for filepath in sorted(docs_dir.glob("*.md")):
        text = filepath.read_text(encoding="utf-8")
        files.append({
            "filename": filepath.name,
            "content": text,
        })
    print(f"Loaded {len(files)} markdown files from {docs_dir}")
    return files


# -------------------
# 2. Chunk by markdown headings
# -------------------
def chunk_by_headings(filename: str, content: str) -> list[dict]:
    """
    Split a markdown document into chunks based on headings (## and ###).
    
    Each chunk contains:
    - The heading text (if any)
    - All content under that heading until the next heading of equal or higher level
    - The document title (first # heading) is prepended as context to every chunk
    
    This preserves semantic boundaries — each chunk is a coherent section
    rather than an arbitrary character cutoff.
    """
    lines = content.split("\n")
    chunks = []
    
    # Extract the document title (first H1)
    doc_title = ""
    for line in lines:
        if line.startswith("# ") and not line.startswith("## "):
            doc_title = line.strip("# ").strip()
            break
    
    # Split on ## and ### headings
    current_heading = doc_title
    current_lines = []
    
    for line in lines:
        # Check if this line is an H2 or H3 heading
        if re.match(r"^#{2,3}\s+", line):
            # Save the previous chunk if it has content
            if current_lines:
                chunk_text = "\n".join(current_lines).strip()
                if chunk_text and len(chunk_text) > 50:  # skip tiny fragments
                    chunks.append({
                        "filename": filename,
                        "doc_title": doc_title,
                        "section_heading": current_heading,
                        "text": chunk_text,
                    })
            
            # Start a new chunk
            current_heading = line.strip("# ").strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    
    # Don't forget the last chunk
    if current_lines:
        chunk_text = "\n".join(current_lines).strip()
        if chunk_text and len(chunk_text) > 50:
            chunks.append({
                "filename": filename,
                "doc_title": doc_title,
                "section_heading": current_heading,
                "text": chunk_text,
            })
    
    return chunks


def chunk_all_docs(files: list[dict]) -> list[dict]:
    """Chunk all loaded markdown files."""
    all_chunks = []
    for f in files:
        file_chunks = chunk_by_headings(f["filename"], f["content"])
        all_chunks.extend(file_chunks)
    
    print(f"Created {len(all_chunks)} chunks from {len(files)} files")
    return all_chunks


# -------------------
# 3. Generate embeddings
# -------------------
def generate_embeddings(chunks: list[dict], client: OpenAI) -> list[dict]:
    """
    Generate embeddings for each chunk.
    
    The text we embed includes the doc title + section heading + content.
    This gives the embedding model full context about what this section is about.
    """
    texts_to_embed = []
    for chunk in chunks:
        # Prepend doc title and section heading for richer embedding context
        embed_text = f"{chunk['doc_title']} - {chunk['section_heading']}\n\n{chunk['text']}"
        texts_to_embed.append(embed_text)
    
    print(f"Generating embeddings for {len(texts_to_embed)} chunks...")
    
    # OpenAI allows batching — send all at once (for 13 docs this is fine)
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts_to_embed,
    )
    
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = response.data[i].embedding
    
    print(f"Generated {len(chunks)} embeddings (dim={len(chunks[0]['embedding'])})")
    return chunks


# -------------------
# 4. Upsert to Pinecone
# -------------------
def generate_chunk_id(chunk: dict) -> str:
    """Generate a deterministic ID for a chunk based on its content."""
    content_hash = hashlib.md5(
        f"{chunk['filename']}:{chunk['section_heading']}".encode()
    ).hexdigest()[:12]
    return f"{chunk['filename'].replace('.md', '')}_{content_hash}"


def upsert_to_pinecone(chunks: list[dict], index) -> None:
    """Upsert all chunks with embeddings to Pinecone."""
    vectors = []
    for chunk in chunks:
        vectors.append({
            "id": generate_chunk_id(chunk),
            "values": chunk["embedding"],
            "metadata": {
                "filename": chunk["filename"],
                "doc_title": chunk["doc_title"],
                "section_heading": chunk["section_heading"],
                "text": chunk["text"],  # store the raw text for retrieval
            },
        })
    
    # Upsert in batches
    for i in range(0, len(vectors), BATCH_SIZE):
        batch = vectors[i : i + BATCH_SIZE]
        index.upsert(vectors=batch, namespace=NAMESPACE)
        print(f"  Upserted batch {i // BATCH_SIZE + 1} ({len(batch)} vectors)")
    
    print(f"Total vectors upserted: {len(vectors)} to namespace '{NAMESPACE}'")


# -------------------
# 5. Main
# -------------------
def main():
    # Validate env vars
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment")
    if not os.getenv("PINECONE_API_KEY"):
        raise ValueError("PINECONE_API_KEY not found in environment")
    
    # Initialize clients
    openai_client = OpenAI()
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    
    # Connect to index (must already exist)
    index = pc.Index(INDEX_NAME)
    print(f"Connected to Pinecone index: {INDEX_NAME}")
    print(f"Index stats: {index.describe_index_stats()}")

    try:
        # Clear existing vectors before re-ingesting
        index.delete(delete_all=True, namespace=NAMESPACE)
        print(f"Cleared PINECONE namespace '{NAMESPACE}'")
    except Exception:
        print(f"Namespace 'PINECONE {NAMESPACE} is empty, skipping clear")

    # Pipeline
    files = load_markdown_files(DOCS_DIR)
    chunks = chunk_all_docs(files)
    chunks = generate_embeddings(chunks, openai_client)
    upsert_to_pinecone(chunks, index)
    
    # Verify
    stats = index.describe_index_stats()
    print(f"\nDone! Index stats after ingestion: {stats}")


if __name__ == "__main__":
    main()
