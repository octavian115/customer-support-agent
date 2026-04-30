"""
Escalation node — hands the conversation off to a human agent.

This is triggered when:
- The classifier detects an angry/frustrated customer
- The customer explicitly asks for a human
- RAG confidence is too low to respond reliably
- The request doesn't fit other categories
- An upstream node failed (LLM error, Pinecone down, etc.)

Reliability:
    - LLM call for summary retries up to 2 times
    - If summary generation fails, uses a basic fallback summary
      built from state data (no LLM needed)
    - This is the last line of defense — it must never crash
"""

import logging
from langchain_core.messages import SystemMessage, AIMessage
from backend.state import SupportState
from backend.config import llm
from backend.prompts import ESCALATION_PROMPT
from backend.reliability import safe_llm_call

logger = logging.getLogger(__name__)


def _build_fallback_summary(state: SupportState) -> str:
    """
    Build a basic escalation summary without LLM when summary generation fails.
    Uses raw state data so the human agent still has context.
    """
    parts = ["Escalation summary (auto-generated — LLM summary unavailable):"]

    # Include the customer's last message
    if state.get("messages"):
        last_msg = state["messages"][-1].content
        parts.append(f"Customer's last message: {last_msg}")

    # Include intent if available
    if state.get("intent"):
        parts.append(f"Classified intent: {state['intent']}")

    # Include confidence if available
    if state.get("confidence") is not None:
        parts.append(f"Retrieval confidence: {state['confidence']:.2f}")

    # Include existing escalation reason if set by an upstream failure
    if state.get("escalation_reason"):
        parts.append(f"Escalation trigger: {state['escalation_reason']}")

    return "\n".join(parts)


def escalation_node(state: SupportState) -> dict:
    """Generate a summary for the human agent and notify the customer."""

    # Build context including retrieved docs if available
    context = ""
    if state.get("retrieved_docs"):
        context = "\n\nRelevant documentation found:\n" + "\n---\n".join(state["retrieved_docs"])

    prompt = ESCALATION_PROMPT + context
    messages = [SystemMessage(content=prompt)] + state["messages"]

    # Generate summary — with fallback if LLM fails
    try:
        summary_response = safe_llm_call(llm, messages)
        summary = summary_response.content
    except Exception as e:
        logger.error(f"Escalation summary generation failed: {e}")
        summary = _build_fallback_summary(state)

    # Determine escalation reason
    # Check if an upstream node already set a reason (e.g. LLM failure)
    if state.get("escalation_reason"):
        reason = state["escalation_reason"]
    elif state.get("confidence", 1.0) < 0.65:
        reason = f"Low retrieval confidence ({state['confidence']:.2f})"
    elif state.get("intent") == "escalation":
        reason = "Classified as needing human intervention"
    else:
        reason = "Routed to escalation"

    customer_message = AIMessage(
        content="I'm going to connect you with a human agent who can better assist you. "
        "I've shared a summary of our conversation so you won't need to repeat yourself. "
        "A team member will be with you shortly."
    )

    return {
        "messages": [customer_message],
        "escalation_reason": reason,
        "escalation_summary": summary,
    }
