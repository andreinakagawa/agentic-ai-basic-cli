"""Tests for Session class."""


from src.cli.session import Session
from src.common.types import Message


class TestSession:
    """Test suite for the Session class."""

    def test_session_creation_default(self):
        """Test creating a session with default values."""
        session = Session()

        # Should have auto-generated session_id
        assert session.session_id is not None
        assert len(session.session_id) > 0

        # Should have empty messages list
        assert session.messages == []
        assert isinstance(session.messages, list)

    def test_session_creation_with_session_id(self):
        """Test creating a session with custom session_id."""
        custom_id = "custom_session_123"
        session = Session(session_id=custom_id)

        assert session.session_id == custom_id
        assert session.messages == []

    def test_session_id_format(self):
        """Test that auto-generated session_id has expected format."""
        session = Session()

        # Should be in format YYYYMMDD_HHMMSS
        assert "_" in session.session_id
        parts = session.session_id.split("_")
        assert len(parts) == 2

        # Date part should be 8 digits
        assert len(parts[0]) == 8
        assert parts[0].isdigit()

        # Time part should be 6 digits
        assert len(parts[1]) == 6
        assert parts[1].isdigit()

    def test_add_message(self):
        """Test adding a message to the session."""
        session = Session()

        session.add_message(role="user", content="Hello world")

        assert len(session.messages) == 1
        assert session.messages[0].role == "user"
        assert session.messages[0].content == "Hello world"
        assert session.messages[0].tokens == 0  # Default

    def test_add_message_with_tokens(self):
        """Test adding a message with token count."""
        session = Session()

        session.add_message(role="assistant", content="Hi there!", tokens=5)

        assert len(session.messages) == 1
        assert session.messages[0].role == "assistant"
        assert session.messages[0].content == "Hi there!"
        assert session.messages[0].tokens == 5

    def test_add_multiple_messages(self):
        """Test adding multiple messages."""
        session = Session()

        session.add_message("user", "First message")
        session.add_message("assistant", "First response")
        session.add_message("user", "Second message")

        assert len(session.messages) == 3
        assert session.messages[0].content == "First message"
        assert session.messages[1].content == "First response"
        assert session.messages[2].content == "Second message"

    def test_get_messages(self):
        """Test getting messages from session."""
        session = Session()

        session.add_message("user", "Message 1")
        session.add_message("assistant", "Message 2")

        messages = session.get_messages()

        assert len(messages) == 2
        assert messages[0].content == "Message 1"
        assert messages[1].content == "Message 2"

    def test_get_messages_returns_copy(self):
        """Test that get_messages returns a copy, not the original list."""
        session = Session()

        session.add_message("user", "Original")

        messages = session.get_messages()

        # Modify the returned list
        messages.append(Message(role="system", content="New"))

        # Original session should be unchanged
        assert len(session.messages) == 1
        assert session.messages[0].content == "Original"

    def test_clear_history(self):
        """Test clearing conversation history."""
        session = Session()

        session.add_message("user", "Message 1")
        session.add_message("assistant", "Message 2")
        session.add_message("user", "Message 3")

        assert len(session.messages) == 3

        session.clear_history()

        assert len(session.messages) == 0
        assert session.messages == []

    def test_message_count(self):
        """Test getting message count."""
        session = Session()

        assert session.message_count() == 0

        session.add_message("user", "Message 1")
        assert session.message_count() == 1

        session.add_message("assistant", "Message 2")
        assert session.message_count() == 2

        session.add_message("user", "Message 3")
        assert session.message_count() == 3

    def test_message_count_after_clear(self):
        """Test message count after clearing history."""
        session = Session()

        session.add_message("user", "Message")
        session.add_message("assistant", "Response")

        assert session.message_count() == 2

        session.clear_history()

        assert session.message_count() == 0

    def test_add_message_with_different_roles(self):
        """Test adding messages with various roles."""
        session = Session()

        roles = ["user", "assistant", "system", "function", "tool"]

        for role in roles:
            session.add_message(role, f"Content for {role}")

        assert session.message_count() == len(roles)

        for i, role in enumerate(roles):
            assert session.messages[i].role == role
            assert session.messages[i].content == f"Content for {role}"

    def test_add_message_with_empty_content(self):
        """Test adding a message with empty content."""
        session = Session()

        session.add_message("user", "")

        assert session.message_count() == 1
        assert session.messages[0].content == ""

    def test_add_message_with_long_content(self):
        """Test adding a message with very long content."""
        session = Session()

        long_content = "This is a very long message. " * 1000

        session.add_message("user", long_content)

        assert session.message_count() == 1
        assert len(session.messages[0].content) > 10000

    def test_session_chronological_order(self):
        """Test that messages maintain chronological order."""
        session = Session()

        for i in range(10):
            session.add_message("user" if i % 2 == 0 else "assistant", f"Message {i}")

        messages = session.get_messages()

        for i in range(10):
            assert messages[i].content == f"Message {i}"

    def test_session_serialization(self):
        """Test that session can be serialized to dict."""
        session = Session(session_id="test_123")
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi")

        data = session.model_dump()

        assert data["session_id"] == "test_123"
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "Hello"
        assert data["messages"][1]["content"] == "Hi"

    def test_session_deserialization(self):
        """Test creating a session from dict."""
        data = {
            "session_id": "restored_session",
            "messages": [
                {"role": "user", "content": "Test", "tokens": 5},
                {"role": "assistant", "content": "Response", "tokens": 3}
            ]
        }

        session = Session(**data)

        assert session.session_id == "restored_session"
        assert session.message_count() == 2
        assert session.messages[0].content == "Test"
        assert session.messages[0].tokens == 5
        assert session.messages[1].content == "Response"
        assert session.messages[1].tokens == 3

    def test_multiple_sessions_independent(self):
        """Test that multiple sessions are independent."""
        session1 = Session(session_id="session_1")
        session2 = Session(session_id="session_2")

        session1.add_message("user", "Message in session 1")
        session2.add_message("user", "Message in session 2")

        assert session1.message_count() == 1
        assert session2.message_count() == 1
        assert session1.messages[0].content == "Message in session 1"
        assert session2.messages[0].content == "Message in session 2"

        session1.clear_history()

        assert session1.message_count() == 0
        assert session2.message_count() == 1

    def test_get_messages_from_empty_session(self):
        """Test getting messages from empty session."""
        session = Session()

        messages = session.get_messages()

        assert messages == []
        assert isinstance(messages, list)

    def test_clear_already_empty_history(self):
        """Test clearing an already empty history."""
        session = Session()

        assert session.message_count() == 0

        session.clear_history()

        assert session.message_count() == 0
        assert session.messages == []

    def test_session_token_tracking(self):
        """Test tracking tokens across messages."""
        session = Session()

        session.add_message("user", "Hello", tokens=5)
        session.add_message("assistant", "Hi there!", tokens=8)
        session.add_message("user", "How are you?", tokens=6)

        total_tokens = sum(msg.tokens for msg in session.messages)

        assert total_tokens == 19

    def test_session_with_conversation_flow(self):
        """Test a realistic conversation flow."""
        session = Session()

        # User starts conversation
        session.add_message("user", "Hello, I need help")

        # Assistant responds
        session.add_message("assistant", "Hello! How can I assist you today?")

        # User asks question
        session.add_message("user", "What is the weather like?")

        # Assistant responds
        session.add_message("assistant", "I'm a mock assistant and don't have weather data.")

        # User thanks
        session.add_message("user", "Thank you")

        # Assistant acknowledges
        session.add_message("assistant", "You're welcome!")

        # Check conversation
        assert session.message_count() == 6

        messages = session.get_messages()

        # Verify alternating pattern
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
        assert messages[2].role == "user"
        assert messages[3].role == "assistant"
        assert messages[4].role == "user"
        assert messages[5].role == "assistant"
