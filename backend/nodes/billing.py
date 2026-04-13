"""
Billing node — handles billing-related requests with human-in-the-loop.

This node analyzes the billing request, drafts a proposed action,
then uses interrupt() to pause the graph for human approval.

The human reviewer sees the proposed action on the agent dashboard
and can approve, reject, or edit it before the response is sent.
"""

from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import interrupt
from backend.state import SupportState
from backend.config import llm
from backend.prompts import BILLING_PROMPT


def billing_node(state: SupportState) -> dict:
    """Analyze billing request, draft action, and wait for human approval."""

    # Format retrieved docs (billing policies) into the prompt
    docs_text = "\n\n---\n\n".join(state["retrieved_docs"])
    system_prompt = BILLING_PROMPT.format(retrieved_docs=docs_text)

    # Ask the LLM to analyze the billing request
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    analysis = llm.invoke(messages)

    # Interrupt for human review
    # The interrupt payload contains everything the reviewer needs to decide
    decision = interrupt({
        "type": "billing_approval",
        "customer_message": state["messages"][-1].content,
        "proposed_action": analysis.content,
        "intent": state["intent"],
    })

    # Resume: human has made a decision
    if isinstance(decision, dict) and decision.get("approved") == "yes":
    # Use edited response if provided, otherwise extract Section 2
        if decision.get("edited_response"):
            final_response = decision["edited_response"]
        else:
            # Split on --- and take Section 2 (customer response)
            parts = analysis.content.split("---")
            if len(parts) >= 2:
                # Extract just the customer-facing part
                customer_section = parts[-1].strip()
                # Remove the "SECTION 2 - CUSTOMER RESPONSE..." header if present
                lines = customer_section.split("\n")
                final_response = "\n".join(
                    line for line in lines 
                    if not line.strip().startswith("SECTION 2")
                ).strip()
            else:
                final_response = analysis.content

        return {"messages": [AIMessage(content=final_response)]}

    else:
        # Human rejected — send a polite message to the customer
        return {
            "messages": [
                AIMessage(
                    content="I've forwarded your billing request to our billing team. "
                    "They'll review it and get back to you within 1 business day. "
                    "Is there anything else I can help you with?"
                )
            ]
        }
