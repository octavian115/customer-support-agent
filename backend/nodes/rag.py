"""
RAG node — retrieves relevant documents from the TaskFlow knowledge base.

This node embeds the customer's query, searches Pinecone for similar chunks,
and stores the results + confidence score in state.

The confidence score (highest similarity from results) is used downstream
to decide whether the response node should answer or escalate.

Reliability:
    - Embedding and Pinecone calls retry up to 2 times with backoff
    - If retrieval fails entirely, returns empty docs with confidence 0.0
      which triggers confidence-based escalation downstream
"""

import logging
from backend.state import SupportState
from backend.config import embeddings, pinecone_index, PINECONE_NAMESPACE
from backend.reliability import safe_embed, safe_pinecone_query

logger = logging.getLogger(__name__)


def rag_node(state: SupportState) -> dict:
    """Retrieve relevant docs from the knowledge base."""

    query = state["messages"][-1].content

    # Embed the query — retries on transient failures
    try:
        query_embedding = safe_embed(embeddings, query)
    except Exception as e:
        logger.error(f"Embedding failed after retries: {e}")
        # Return empty results — confidence 0.0 will trigger escalation
        return {
            "retrieved_docs": [],
            "confidence": 0.0,
        }

    # Search Pinecone — retries on transient failures
    try:
        results = safe_pinecone_query(
            pinecone_index,
            vector=query_embedding,
            top_k=3,
            namespace=PINECONE_NAMESPACE,
        )
    except Exception as e:
        logger.error(f"Pinecone query failed after retries: {e}")
        return {
            "retrieved_docs": [],
            "confidence": 0.0,
        }

    # Extract text and confidence
    retrieved_docs = []
    scores = []

    for match in results.get("matches", []):
        doc_title = match["metadata"].get("doc_title", "")
        section = match["metadata"].get("section_heading", "")
        text = match["metadata"].get("text", "")

        formatted = f"[Source: {doc_title} > {section}]\n{text}"
        retrieved_docs.append(formatted)
        scores.append(match["score"])

    confidence = max(scores) if scores else 0.0

    return {
        "retrieved_docs": retrieved_docs,
        "confidence": confidence,
    }

