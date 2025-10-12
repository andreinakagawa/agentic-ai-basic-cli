"""Common type definitions used across the application."""

from typing import Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a message in a conversation.

    Attributes:
        role: The role of the message sender (e.g., "user", "assistant", "system")
        content: The message content
        tokens: Number of tokens used by this message
    """

    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    tokens: int = Field(default=0, ge=0, description="Number of tokens used")


class AgentContext(BaseModel):
    """Context passed to an agent for processing.

    This model provides all the information an agent needs to process a request,
    including the current input, conversation history, and any domain-specific data.

    The design is intentionally generic to support any agent type, not just data analysis.

    Attributes:
        input: The user's current input/query/request (generic, domain-agnostic)
        conversation_history: List of previous messages in the conversation
        session_id: Identifier for the current session
        additional_context: Optional domain-specific data (e.g., CSV metadata, code context)

    Example:
        ```python
        context = AgentContext(
            input="What are the sales trends?",
            conversation_history=[
                Message(role="user", content="Hi"),
                Message(role="assistant", content="Hello!")
            ],
            session_id="session_123",
            additional_context={"data_summary": {...}}
        )
        ```
    """

    input: str = Field(..., min_length=1, description="User's current input/query")
    conversation_history: list[Message] = Field(
        default_factory=list, description="Previous conversation messages"
    )
    session_id: str = Field(..., min_length=1, description="Current session ID")
    additional_context: dict[str, Any] | None = Field(
        default=None, description="Optional domain-specific context data"
    )


class AgentResponse(BaseModel):
    """Response from an agent after processing.

    This model provides structured output from an agent, including the main result
    and any additional metadata about the processing.

    Attributes:
        output: The agent's response/result/answer (generic, domain-agnostic)
        metadata: Additional information about the response (tokens, model info, artifacts, etc.)

    Example:
        ```python
        response = AgentResponse(
            output="Based on the data, sales increased 15% in Q3.",
            metadata={
                "tokens": 150,
                "model": "gpt-4",
                "confidence": 0.95
            }
        )
        ```
    """

    output: str = Field(..., description="Agent's response/result")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional response metadata"
    )
