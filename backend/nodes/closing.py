from langchain_core.messages import AIMessage
from backend.state import SupportState


def closing_node(state: SupportState) -> dict:
    return {
        "messages": [
            AIMessage(
                content="You're welcome! If you need anything else in the future, "
                "don't hesitate to reach out. Have a great day!"
            )
        ]
    }