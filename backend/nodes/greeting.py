from langchain_core.messages import AIMessage
from backend.state import SupportState


def greeting_node(state: SupportState) -> dict:
    return {
        "messages": [
            AIMessage(
                content="Hello! Welcome to TaskFlow support. "
                "How can I help you today? I can answer questions about our features, "
                "help with technical issues, or assist with billing requests."
            )
        ]
    }