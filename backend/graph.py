"""
LangGraph definition for the TaskFlow support agent.

Graph topology:
    START → classifier → (conditional routing by intent)
        ├── "faq"        → rag → (confidence check)
        │                         ├── high → response → END
        │                         └── low  → escalation → END
        ├── "technical"  → rag → (confidence check)
        │                         ├── high → response → END
        │                         └── low  → escalation → END
        ├── "billing"    → rag → billing (HITL interrupt) → END
        └── "escalation" → escalation → END
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.state import SupportState
from backend.config import CONFIDENCE_THRESHOLD

# Import nodes
from backend.nodes.classifier import classifier_node
from backend.nodes.rag import rag_node
from backend.nodes.response import response_node
from backend.nodes.billing import billing_node
from backend.nodes.escalation import escalation_node


# -------------------
# Conditional edge functions
# -------------------
def route_by_intent(state: SupportState) -> str:
    """Route to the appropriate node based on classified intent."""
    intent = state["intent"]

    if intent in ("faq", "technical"):
        return "rag_node"
    elif intent == "billing":
        return "rag_node"  # billing also needs RAG to fetch policies first
    elif intent == "escalation":
        return "escalation_node"
    else:
        return "escalation_node"  # fallback


def route_after_rag(state: SupportState) -> str:
    """After RAG retrieval, decide next step based on intent and confidence."""
    intent = state["intent"]
    confidence = state.get("confidence", 0.0)

    # Billing always goes to billing node (needs HITL regardless of confidence)
    if intent == "billing":
        return "billing_node"

    # For FAQ/technical: check confidence threshold
    if confidence >= CONFIDENCE_THRESHOLD:
        return "response_node"
    else:
        return "escalation_node"


# -------------------
# Build the graph
# -------------------
def build_graph():
    """Construct and compile the support agent graph."""

    graph = StateGraph(SupportState)

    # Add nodes
    graph.add_node("classifier_node", classifier_node)
    graph.add_node("rag_node", rag_node)
    graph.add_node("response_node", response_node)
    graph.add_node("billing_node", billing_node)
    graph.add_node("escalation_node", escalation_node)

    # Entry point
    graph.add_edge(START, "classifier_node")

    # Conditional routing after classification
    graph.add_conditional_edges(
        "classifier_node",
        route_by_intent,
        {
            "rag_node": "rag_node",
            "escalation_node": "escalation_node",
        },
    )

    # Conditional routing after RAG retrieval
    graph.add_conditional_edges(
        "rag_node",
        route_after_rag,
        {
            "response_node": "response_node",
            "billing_node": "billing_node",
            "escalation_node": "escalation_node",
        },
    )

    # Terminal edges
    graph.add_edge("response_node", END)
    graph.add_edge("billing_node", END)
    graph.add_edge("escalation_node", END)

    # Compile with checkpointer (MemorySaver for dev, Postgres for prod)
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


# Create the compiled graph instance
support_agent = build_graph()
