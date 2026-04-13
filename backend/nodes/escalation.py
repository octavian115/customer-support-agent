"""
Escalation node — hands the conversation off to a human agent.

This is triggered when:
- The classifier detects an angry/frustrated customer
- The customer explicitly asks for a human
- RAG confidence is too low to respond reliably
- The request doesn't fit other categories
"""

from langchain_core.messages import SystemMessage, AIMessage
from backend.state import SupportState
from backend.config import llm
from backend.prompts import ESCALATION_PROMPT


def escalation_node(state: SupportState) -> dict:
    """Generate a summary for the human agent and notify the customer."""

    # Generate a summary for the human agent
    messages = [SystemMessage(content=ESCALATION_PROMPT)] + state["messages"]
    summary = llm.invoke(messages)

    # Determine the reason for escalation
    if state.get("confidence", 1.0) < 0.65:
        reason = f"Low retrieval confidence ({state['confidence']:.2f})"
    elif state.get("intent") == "escalation":
        reason = "Classified as needing human intervention"
    else:
        reason = "Routed to escalation"

    # Customer-facing message
    customer_message = AIMessage(
        content="I'm going to connect you with a human agent who can better assist you. "
        "I've shared a summary of our conversation so you won't need to repeat yourself. "
        "A team member will be with you shortly."
    )

    return {
        "messages": [customer_message],
        "escalation_reason": reason,
        "escalation_summary": summary.content,
    }
