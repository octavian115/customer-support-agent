"""
Response node — generates the final customer-facing response.

Takes the conversation history and retrieved docs from state,
and produces a grounded response using the RAG context.
"""

from langchain_core.messages import SystemMessage, AIMessage
from backend.state import SupportState
from backend.config import llm
from backend.prompts import RAG_RESPONSE_PROMPT


def response_node(state: SupportState) -> dict:
    """Generate a response grounded in retrieved documentation."""

    # Format retrieved docs into the prompt
    docs_text = "\n\n---\n\n".join(state["retrieved_docs"])
    system_prompt = RAG_RESPONSE_PROMPT.format(retrieved_docs=docs_text)

    # Build message list: system prompt + full conversation history
    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = llm.invoke(messages)

    return {"messages": [response]}
