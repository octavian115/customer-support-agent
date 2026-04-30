"""
Billing node — handles billing-related requests with human-in-the-loop.

This node analyzes the billing request, drafts a proposed action,
then uses interrupt() to pause the graph for human approval.

The human reviewer sees the proposed action on the agent dashboard
and can approve, reject, or edit it before the response is sent.

Reliability:
    - LLM call retries up to 2 times with backoff
    - If LLM fails entirely, escalates with an error message
    - Response parsing handles missing/malformed section separators
"""

import logging
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import interrupt
from backend.state import SupportState
from backend.config import llm
from backend.prompts import BILLING_PROMPT
from backend.reliability import safe_llm_call

logger = logging.getLogger(__name__)


def _extract_customer_response(analysis_content: str) -> str:
    """
    Extract the customer-facing section from the billing analysis.

    Expected format:
        SECTION 1 - ANALYSIS (internal)
        ---
        SECTION 2 - CUSTOMER RESPONSE (to send)

    Handles edge cases:
        - Missing --- separator
        - Missing SECTION 2 header
        - Completely unexpected format
    """
    parts = analysis_content.split("---")

    if len(parts) >= 2:
        customer_section = parts[-1].strip()
        lines = customer_section.split("\n")
        # Remove the section header if present
        filtered = [
            line for line in lines
            if not line.strip().upper().startswith("SECTION 2")
        ]
        result = "\n".join(filtered).strip()
        if result:
            return result

    # Fallback: if parsing fails, return the full content
    # The reviewer already approved it, so this is safe
    logger.warning("Could not parse billing response sections, using full content")
    return analysis_content


def billing_node(state: SupportState) -> dict:
    """Analyze billing request, draft action, and wait for human approval."""

    docs_text = "\n\n---\n\n".join(state["retrieved_docs"])
    system_prompt = BILLING_PROMPT.format(retrieved_docs=docs_text)
    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    # LLM call with retry
    try:
        analysis = safe_llm_call(llm, messages)
    except Exception as e:
        logger.error(f"Billing LLM call failed after retries: {e}")
        # Can't draft a billing action without LLM — escalate gracefully
        return {
            "messages": [
                AIMessage(
                    content="I'm having trouble processing your billing request right now. "
                    "I've flagged this for our billing team and they'll follow up with you "
                    "within 1 business day. Sorry about the delay."
                )
            ],
            "escalation_reason": f"Billing node LLM failure: {e}",
        }

    # Interrupt for human review
    decision = interrupt({
        "type": "billing_approval",
        "customer_message": state["messages"][-1].content,
        "proposed_action": analysis.content,
        "intent": state["intent"],
    })

    # Resume after human decision
    if isinstance(decision, dict) and decision.get("approved") == "yes":
        if decision.get("edited_response"):
            final_response = decision["edited_response"]
        else:
            final_response = _extract_customer_response(analysis.content)

        return {"messages": [AIMessage(content=final_response)]}

    else:
        return {
            "messages": [
                AIMessage(
                    content="I've forwarded your billing request to our billing team. "
                    "They'll review it and get back to you within 1 business day. "
                    "Is there anything else I can help you with?"
                )
            ]
        }
