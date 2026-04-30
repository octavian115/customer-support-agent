"""
Classifier node — determines the intent of the customer's message.

This is the entry point of the graph. It classifies the customer's
latest message into one of the 7 intent categories.

The conditional edge after this node reads state["intent"] to route
to the appropriate next node.

Reliability:
    - LLM call retries up to 2 times with backoff
    - If structured output parsing fails, defaults to escalation
      (safest fallback — human gets involved)
    - If LLM is completely unreachable, defaults to escalation
"""

import logging
from langchain_core.messages import SystemMessage, HumanMessage
from backend.state import SupportState
from backend.config import llm
from backend.prompts import CLASSIFIER_PROMPT
from backend.reliability import retry_with_backoff

from pydantic import BaseModel, Field
from typing import Literal

logger = logging.getLogger(__name__)


class IntentClassification(BaseModel):
    intent: Literal["greeting", "faq", "technical", "billing", "escalation", "off_topic", "closing"] = Field(
        description="The classified intent of the customer message"
    )


classifier_llm = llm.with_structured_output(IntentClassification)

# The default when classification fails — escalation is the safest route
# because a human will review the conversation
FALLBACK_INTENT = "escalation"


@retry_with_backoff(max_retries=2, base_delay=1.0)
def _classify(latest_message: str) -> str:
    """Classify intent with retry. Raises on failure for the retry decorator to catch."""
    response = classifier_llm.invoke([
        SystemMessage(content=CLASSIFIER_PROMPT),
        HumanMessage(content=latest_message),
    ])
    return response.intent


def classifier_node(state: SupportState) -> dict:
    """Classify the customer's intent based on conversation history."""

    latest_message = state["messages"][-1].content

    try:
        intent = _classify(latest_message)
        return {"intent": intent}
    except Exception as e:
        logger.error(f"Classification failed after retries: {e}. Falling back to '{FALLBACK_INTENT}'")
        return {
            "intent": FALLBACK_INTENT,
            "escalation_reason": f"Classification failure — defaulted to escalation: {e}",
        }
