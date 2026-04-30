"""
Response node — generates the final customer-facing response.

Takes the conversation history and retrieved docs from state,
and produces a grounded response using the RAG context.

Reliability:
    - LLM call retries up to 2 times with backoff
    - If LLM fails entirely, returns an apology message and flags for escalation
"""

import logging
from langchain_core.messages import SystemMessage, AIMessage
from backend.state import SupportState
from backend.config import llm
from backend.prompts import RAG_RESPONSE_PROMPT
from backend.reliability import safe_llm_call

logger = logging.getLogger(__name__)


def response_node(state: SupportState) -> dict:
    """Generate a response grounded in retrieved documentation."""

    docs_text = "\n\n---\n\n".join(state["retrieved_docs"])
    system_prompt = RAG_RESPONSE_PROMPT.format(retrieved_docs=docs_text)
    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    try:
        response = safe_llm_call(llm, messages)
        return {"messages": [response]}
    except Exception as e:
        logger.error(f"Response generation failed after retries: {e}")
        return {
            "messages": [
                AIMessage(
                    content="I found some relevant information but I'm having trouble "
                    "putting together a response right now. Let me connect you with "
                    "a team member who can help. One moment."
                )
            ],
            "escalation_reason": f"Response node LLM failure: {e}",
        }

