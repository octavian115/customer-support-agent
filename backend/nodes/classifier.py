"""
Classifier node — determines the intent of the customer's message.

This is the entry point of the graph. It classifies the customer's
latest message into one of: faq, technical, billing, escalation.

The conditional edge after this node reads state["intent"] to route
to the appropriate next node.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from backend.state import SupportState
from backend.config import llm
from backend.prompts import CLASSIFIER_PROMPT

from pydantic import BaseModel, Field
from typing import Literal

class IntentClassification(BaseModel):
    intent: Literal["greeting","faq", "technical", "billing", "escalation","off_topic","closing"] = Field(
        description="The classified intent of the customer message"
    )

classifier_llm = llm.with_structured_output(IntentClassification)


def classifier_node(state: SupportState) -> dict:
    """Classify the customer's intent based on conversation history."""

    # Get the latest customer message
    latest_message = state["messages"][-1].content

    response = classifier_llm.invoke([
        SystemMessage(content=CLASSIFIER_PROMPT),
        HumanMessage(content=latest_message),
    ])
    
    return {"intent": response.intent}
