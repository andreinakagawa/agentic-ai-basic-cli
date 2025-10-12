"""Tests for common type definitions (Message, AgentContext, AgentResponse)."""

import pytest
from pydantic import ValidationError

from src.common.types import AgentContext, AgentResponse, Message


class TestMessage:
    """Test suite for the Message model."""

    def test_message_creation_with_all_fields(self):
        """Test creating a message with all fields."""
        msg = Message(role="user", content="Hello world", tokens=10)
        assert msg.role == "user"
        assert msg.content == "Hello world"
        assert msg.tokens == 10

    def test_message_creation_with_defaults(self):
        """Test creating a message with default token value."""
        msg = Message(role="assistant", content="Hi there")
        assert msg.role == "assistant"
        assert msg.content == "Hi there"
        assert msg.tokens == 0  # Default value

    def test_message_creation_minimal(self):
        """Test creating a message with minimal required fields."""
        msg = Message(role="system", content="You are a helpful assistant")
        assert msg.role == "system"
        assert msg.content == "You are a helpful assistant"
        assert msg.tokens == 0

    def test_message_tokens_must_be_non_negative(self):
        """Test that tokens field must be non-negative."""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user", content="Test", tokens=-1)

        assert "tokens" in str(exc_info.value).lower()

    def test_message_role_required(self):
        """Test that role field is required."""
        with pytest.raises(ValidationError) as exc_info:
            Message(content="Test")  # type: ignore

        assert "role" in str(exc_info.value).lower()

    def test_message_content_required(self):
        """Test that content field is required."""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user")  # type: ignore

        assert "content" in str(exc_info.value).lower()

    def test_message_with_different_roles(self):
        """Test creating messages with various role types."""
        roles = ["user", "assistant", "system", "function", "tool"]
        for role in roles:
            msg = Message(role=role, content="Test content")
            assert msg.role == role

    def test_message_with_empty_content(self):
        """Test creating a message with empty content (should be allowed)."""
        msg = Message(role="user", content="")
        assert msg.content == ""

    def test_message_with_large_token_count(self):
        """Test message with large token count."""
        msg = Message(role="user", content="Long text...", tokens=100000)
        assert msg.tokens == 100000

    def test_message_immutability(self):
        """Test that Message is a Pydantic model (can be modified but validates)."""
        msg = Message(role="user", content="Original")
        # Pydantic v2 models are not frozen by default, but we can test reassignment
        msg = msg.model_copy(update={"content": "Updated"})
        assert msg.content == "Updated"


class TestAgentContext:
    """Test suite for the AgentContext model."""

    def test_context_creation_minimal(self):
        """Test creating context with minimal required fields."""
        ctx = AgentContext(
            input="What is the weather?",
            session_id="session_123"
        )
        assert ctx.input == "What is the weather?"
        assert ctx.session_id == "session_123"
        assert ctx.conversation_history == []
        assert ctx.additional_context is None

    def test_context_creation_with_history(self):
        """Test creating context with conversation history."""
        history = [
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello!")
        ]
        ctx = AgentContext(
            input="How are you?",
            conversation_history=history,
            session_id="session_456"
        )
        assert ctx.input == "How are you?"
        assert len(ctx.conversation_history) == 2
        assert ctx.conversation_history[0].content == "Hi"
        assert ctx.conversation_history[1].content == "Hello!"

    def test_context_creation_with_additional_context(self):
        """Test creating context with additional context data."""
        additional = {
            "data_summary": {"rows": 100, "columns": 5},
            "file_path": "/path/to/data.csv"
        }
        ctx = AgentContext(
            input="Analyze this data",
            session_id="session_789",
            additional_context=additional
        )
        assert ctx.additional_context is not None
        assert ctx.additional_context["data_summary"]["rows"] == 100
        assert ctx.additional_context["file_path"] == "/path/to/data.csv"

    def test_context_input_required(self):
        """Test that input field is required."""
        with pytest.raises(ValidationError) as exc_info:
            AgentContext(session_id="session_123")  # type: ignore

        assert "input" in str(exc_info.value).lower()

    def test_context_session_id_required(self):
        """Test that session_id field is required."""
        with pytest.raises(ValidationError) as exc_info:
            AgentContext(input="Test")  # type: ignore

        assert "session_id" in str(exc_info.value).lower()

    def test_context_input_min_length(self):
        """Test that input must have minimum length of 1."""
        with pytest.raises(ValidationError) as exc_info:
            AgentContext(input="", session_id="session_123")

        assert "input" in str(exc_info.value).lower()

    def test_context_session_id_min_length(self):
        """Test that session_id must have minimum length of 1."""
        with pytest.raises(ValidationError) as exc_info:
            AgentContext(input="Test", session_id="")

        assert "session_id" in str(exc_info.value).lower()

    def test_context_history_defaults_to_empty_list(self):
        """Test that conversation_history defaults to empty list."""
        ctx = AgentContext(input="Test", session_id="session_123")
        assert ctx.conversation_history == []
        assert isinstance(ctx.conversation_history, list)

    def test_context_additional_context_defaults_to_none(self):
        """Test that additional_context defaults to None."""
        ctx = AgentContext(input="Test", session_id="session_123")
        assert ctx.additional_context is None

    def test_context_with_complex_additional_context(self):
        """Test context with complex nested additional context."""
        additional = {
            "metadata": {
                "version": "1.0",
                "nested": {
                    "deep": "value"
                }
            },
            "list_data": [1, 2, 3],
            "string_value": "test"
        }
        ctx = AgentContext(
            input="Process this",
            session_id="session_123",
            additional_context=additional
        )
        assert ctx.additional_context["metadata"]["nested"]["deep"] == "value"
        assert ctx.additional_context["list_data"] == [1, 2, 3]

    def test_context_with_long_input(self):
        """Test context with very long input string."""
        long_input = "A" * 10000
        ctx = AgentContext(input=long_input, session_id="session_123")
        assert len(ctx.input) == 10000

    def test_context_with_many_history_messages(self):
        """Test context with many messages in history."""
        history = [
            Message(role="user" if i % 2 == 0 else "assistant", content=f"Message {i}")
            for i in range(100)
        ]
        ctx = AgentContext(
            input="Latest question",
            conversation_history=history,
            session_id="session_123"
        )
        assert len(ctx.conversation_history) == 100


class TestAgentResponse:
    """Test suite for the AgentResponse model."""

    def test_response_creation_minimal(self):
        """Test creating response with minimal required fields."""
        response = AgentResponse(output="This is the answer")
        assert response.output == "This is the answer"
        assert response.metadata == {}

    def test_response_creation_with_metadata(self):
        """Test creating response with metadata."""
        metadata = {
            "tokens": 150,
            "model": "gpt-4",
            "confidence": 0.95
        }
        response = AgentResponse(
            output="Based on the data, sales increased by 15%",
            metadata=metadata
        )
        assert response.output == "Based on the data, sales increased by 15%"
        assert response.metadata["tokens"] == 150
        assert response.metadata["model"] == "gpt-4"
        assert response.metadata["confidence"] == 0.95

    def test_response_output_required(self):
        """Test that output field is required."""
        with pytest.raises(ValidationError) as exc_info:
            AgentResponse()  # type: ignore

        assert "output" in str(exc_info.value).lower()

    def test_response_metadata_defaults_to_empty_dict(self):
        """Test that metadata defaults to empty dict."""
        response = AgentResponse(output="Test output")
        assert response.metadata == {}
        assert isinstance(response.metadata, dict)

    def test_response_with_empty_output(self):
        """Test creating response with empty output string."""
        response = AgentResponse(output="")
        assert response.output == ""

    def test_response_with_complex_metadata(self):
        """Test response with complex nested metadata."""
        metadata = {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            },
            "model_info": {
                "name": "gpt-4",
                "version": "0613"
            },
            "artifacts": ["chart.png", "data.csv"]
        }
        response = AgentResponse(
            output="Analysis complete",
            metadata=metadata
        )
        assert response.metadata["usage"]["total_tokens"] == 150
        assert response.metadata["artifacts"] == ["chart.png", "data.csv"]

    def test_response_with_long_output(self):
        """Test response with very long output string."""
        long_output = "Response text " * 1000
        response = AgentResponse(output=long_output)
        assert len(response.output) > 10000

    def test_response_metadata_various_types(self):
        """Test that metadata can contain various data types."""
        metadata = {
            "string": "value",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "data"},
            "none": None
        }
        response = AgentResponse(output="Test", metadata=metadata)
        assert response.metadata["string"] == "value"
        assert response.metadata["integer"] == 42
        assert response.metadata["float"] == 3.14
        assert response.metadata["boolean"] is True
        assert response.metadata["list"] == [1, 2, 3]
        assert response.metadata["dict"]["nested"] == "data"
        assert response.metadata["none"] is None

    def test_response_model_serialization(self):
        """Test that response can be serialized to dict."""
        response = AgentResponse(
            output="Test output",
            metadata={"key": "value"}
        )
        data = response.model_dump()
        assert data["output"] == "Test output"
        assert data["metadata"]["key"] == "value"

    def test_response_model_json_serialization(self):
        """Test that response can be serialized to JSON."""
        response = AgentResponse(
            output="Test output",
            metadata={"tokens": 100}
        )
        json_str = response.model_dump_json()
        assert "Test output" in json_str
        assert "tokens" in json_str
        assert "100" in json_str


class TestTypeIntegration:
    """Integration tests for types working together."""

    def test_message_in_context_history(self):
        """Test using Message objects in AgentContext history."""
        messages = [
            Message(role="user", content="First message", tokens=5),
            Message(role="assistant", content="Response", tokens=3),
            Message(role="user", content="Follow-up", tokens=4)
        ]
        ctx = AgentContext(
            input="Latest query",
            conversation_history=messages,
            session_id="session_123"
        )

        assert len(ctx.conversation_history) == 3
        assert ctx.conversation_history[0].role == "user"
        assert ctx.conversation_history[1].role == "assistant"
        assert sum(msg.tokens for msg in ctx.conversation_history) == 12

    def test_full_conversation_flow(self):
        """Test a complete conversation flow with all types."""
        # Start with empty history
        ctx1 = AgentContext(
            input="Hello, how are you?",
            conversation_history=[],
            session_id="session_abc"
        )

        # First response
        response1 = AgentResponse(
            output="I'm doing well, thank you!",
            metadata={"tokens": 8, "model": "mock"}
        )

        # Build history for next turn
        history = [
            Message(role="user", content=ctx1.input, tokens=5),
            Message(role="assistant", content=response1.output, tokens=8)
        ]

        # Second turn
        ctx2 = AgentContext(
            input="What can you help me with?",
            conversation_history=history,
            session_id="session_abc"
        )

        assert len(ctx2.conversation_history) == 2
        assert ctx2.session_id == ctx1.session_id
        assert ctx2.conversation_history[0].content == "Hello, how are you?"
        assert ctx2.conversation_history[1].content == "I'm doing well, thank you!"
