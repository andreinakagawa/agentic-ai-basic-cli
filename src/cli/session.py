"""Session state management for CLI interactions."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.common.types import Message


class Session(BaseModel):
    """Manages session state and conversation history.

    The Session class provides in-memory storage for conversation messages
    during an interactive CLI session. It is designed to be simple and
    focused on the core responsibility of managing message history.

    All state is in-memory and cleared when session ends. For persistent
    storage, export the conversation using the exporter module.

    Attributes:
        session_id: Unique identifier for the session (auto-generated timestamp)
        messages: List of conversation messages in chronological order
    """

    session_id: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"),
        description="Unique session identifier",
    )
    messages: list[Message] = Field(
        default_factory=list, description="Conversation message history"
    )

    def add_message(self, role: str, content: str, tokens: int = 0) -> None:
        """Add a message to the conversation history.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
            tokens: Token count for this message (default 0)
        """
        message = Message(role=role, content=content, tokens=tokens)
        self.messages.append(message)

    def get_messages(self) -> list[Message]:
        """Get all messages in the conversation history.

        Returns:
            List of messages in chronological order
        """
        return self.messages.copy()

    def clear_history(self) -> None:
        """Clear all conversation history.

        Used for context cleanup or session reset.
        """
        self.messages.clear()

    def message_count(self) -> int:
        """Get the number of messages in history.

        Returns:
            Count of messages
        """
        return len(self.messages)
