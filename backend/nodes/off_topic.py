from langchain_core.messages import AIMessage
from backend.state import SupportState


def off_topic_node(state: SupportState) -> dict:
    return {
        "messages": [
            AIMessage(
                content="I'm a TaskFlow support assistant, so I can only help with "
                "questions about our product — features, troubleshooting, billing, and account management. "
                "Is there anything TaskFlow-related I can help you with?"
            )
        ]
    }