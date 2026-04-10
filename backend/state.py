"""
State schema for the TaskFlow support agent graph.

This defines the shape of data that flows through every node in the graph.
Each node reads from and writes to this shared state.
"""

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class SupportState(TypedDict):
    """
    State schema for the customer support agent.

    Fields:
        messages: Conversation history (auto-appended via add_messages reducer).
        intent: Classified intent of the latest customer message.
                One of: "faq", "technical", "billing", "escalation".
        retrieved_docs: Documents retrieved from the knowledge base by the RAG node.
        confidence: Confidence score from RAG retrieval (0.0 to 1.0).
                    Used to decide whether to respond or escalate.
        escalation_reason: Why the conversation was escalated to a human agent.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    intent: str
    retrieved_docs: list[str]
    confidence: float
    escalation_reason: str
