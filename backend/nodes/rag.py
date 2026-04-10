"""
RAG node — retrieves relevant documents from the TaskFlow knowledge base.

This node embeds the customer's query, searches Pinecone for similar chunks,
and stores the results + confidence score in state.

The confidence score (highest similarity from results) is used downstream
to decide whether the response node should answer or escalate.
"""

from backend.state import SupportState
from backend.config import embeddings, pinecone_index, PINECONE_NAMESPACE


def rag_node(state: SupportState) -> dict:
    """Retrieve relevant docs from the knowledge base."""

    # Get the latest customer message
    query = state["messages"][-1].content

    # Embed the query
    query_embedding = embeddings.embed_query(query)

    # Search Pinecone
    results = pinecone_index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
        namespace=PINECONE_NAMESPACE,
    )

    # Extract text and confidence
    retrieved_docs = []
    scores = []

    for match in results["matches"]:
        doc_title = match["metadata"].get("doc_title", "")
        section = match["metadata"].get("section_heading", "")
        text = match["metadata"].get("text", "")

        # Format: include source info for the response node
        formatted = f"[Source: {doc_title} > {section}]\n{text}"
        retrieved_docs.append(formatted)
        scores.append(match["score"])

    # Confidence = highest similarity score (0 to 1 for cosine)
    confidence = max(scores) if scores else 0.0

    return {
        "retrieved_docs": retrieved_docs,
        "confidence": confidence,
    }
