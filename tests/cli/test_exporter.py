"""Tests for chat export functionality."""


from src.cli.exporter import format_export_content, get_default_export_filename
from src.cli.session import Session


class TestFormatExportContent:
    """Test suite for format_export_content function."""

    def test_export_empty_session(self):
        """Test exporting a session with no messages."""
        session = Session(session_id="test_session_123")

        content = format_export_content(session)

        assert "Session: test_session_123" in content
        assert "(No messages in this conversation)" in content

    def test_export_single_message(self):
        """Test exporting a session with one message."""
        session = Session(session_id="session_001")
        session.add_message("user", "Hello, world!")

        content = format_export_content(session)

        assert "Session: session_001" in content
        assert "[USER]:" in content
        assert "Hello, world!" in content

    def test_export_multiple_messages(self):
        """Test exporting a session with multiple messages."""
        session = Session(session_id="session_002")
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")
        session.add_message("user", "How are you?")
        session.add_message("assistant", "I'm doing well, thank you!")

        content = format_export_content(session)

        # Check session ID
        assert "Session: session_002" in content

        # Check all messages are present
        assert "[USER]:" in content
        assert "[ASSISTANT]:" in content
        assert "Hello" in content
        assert "Hi there!" in content
        assert "How are you?" in content
        assert "I'm doing well, thank you!" in content

    def test_export_role_labels_uppercase(self):
        """Test that role labels are uppercase in export."""
        session = Session()
        session.add_message("user", "Test user message")
        session.add_message("assistant", "Test assistant message")
        session.add_message("system", "Test system message")

        content = format_export_content(session)

        assert "[USER]:" in content
        assert "[ASSISTANT]:" in content
        assert "[SYSTEM]:" in content
        # Should not have lowercase
        assert "[user]:" not in content
        assert "[assistant]:" not in content

    def test_export_message_order(self):
        """Test that messages maintain chronological order in export."""
        session = Session()
        session.add_message("user", "First message")
        session.add_message("assistant", "Second message")
        session.add_message("user", "Third message")

        content = format_export_content(session)

        # Find positions of messages in content
        pos_first = content.find("First message")
        pos_second = content.find("Second message")
        pos_third = content.find("Third message")

        # Verify order
        assert pos_first < pos_second < pos_third

    def test_export_with_multiline_message(self):
        """Test exporting messages with newlines."""
        session = Session()
        multiline = "Line 1\nLine 2\nLine 3"
        session.add_message("user", multiline)

        content = format_export_content(session)

        assert "Line 1" in content
        assert "Line 2" in content
        assert "Line 3" in content

    def test_export_with_special_characters(self):
        """Test exporting messages with special characters."""
        session = Session()
        special_msg = "Special chars: !@#$%^&*()_+-={}[]|:;<>?,./~`"
        session.add_message("user", special_msg)

        content = format_export_content(session)

        assert special_msg in content

    def test_export_with_unicode(self):
        """Test exporting messages with Unicode characters."""
        session = Session()
        session.add_message("user", "Hello 世界! Héllo wörld! 👋")

        content = format_export_content(session)

        assert "Hello 世界!" in content
        assert "Héllo wörld!" in content
        assert "👋" in content

    def test_export_with_long_message(self):
        """Test exporting very long messages."""
        session = Session()
        long_msg = "This is a very long message. " * 100
        session.add_message("user", long_msg)

        content = format_export_content(session)

        assert long_msg in content

    def test_export_with_empty_message_content(self):
        """Test exporting message with empty content."""
        session = Session()
        session.add_message("user", "")

        content = format_export_content(session)

        assert "[USER]:" in content
        # Empty content should still be exported

    def test_export_conversation_flow(self):
        """Test exporting a realistic conversation."""
        session = Session(session_id="conversation_123")

        session.add_message("user", "Hello, I need help with something.")
        session.add_message("assistant", "Hello! I'd be happy to help. What do you need?")
        session.add_message("user", "Can you explain how sessions work?")
        session.add_message("assistant", "Sessions store your conversation history in memory.")
        session.add_message("user", "Thank you!")
        session.add_message("assistant", "You're welcome!")

        content = format_export_content(session)

        # Verify structure
        assert content.startswith("Session: conversation_123")
        assert content.count("[USER]:") == 3
        assert content.count("[ASSISTANT]:") == 3

    def test_export_format_structure(self):
        """Test the basic structure of exported content."""
        session = Session(session_id="test_123")
        session.add_message("user", "Test message")

        content = format_export_content(session)
        lines = content.split("\n")

        # First line should be session ID
        assert lines[0] == "Session: test_123"
        # Second line should be empty
        assert lines[1] == ""
        # Should have role label
        assert "[USER]:" in content

    def test_export_returns_string(self):
        """Test that export returns a string."""
        session = Session()
        session.add_message("user", "Test")

        content = format_export_content(session)

        assert isinstance(content, str)


class TestGetDefaultExportFilename:
    """Test suite for get_default_export_filename function."""

    def test_default_filename_format(self):
        """Test that default filename has correct format."""
        session = Session(session_id="20250112_143022")

        filename = get_default_export_filename(session)

        assert filename == "chat_20250112_143022.txt"

    def test_default_filename_with_custom_session_id(self):
        """Test filename with custom session ID."""
        session = Session(session_id="custom_session_123")

        filename = get_default_export_filename(session)

        assert filename == "chat_custom_session_123.txt"

    def test_default_filename_extension(self):
        """Test that filename has .txt extension."""
        session = Session(session_id="test")

        filename = get_default_export_filename(session)

        assert filename.endswith(".txt")

    def test_default_filename_prefix(self):
        """Test that filename starts with 'chat_'."""
        session = Session(session_id="test")

        filename = get_default_export_filename(session)

        assert filename.startswith("chat_")

    def test_default_filename_includes_session_id(self):
        """Test that filename includes the session ID."""
        session_id = "my_unique_session_456"
        session = Session(session_id=session_id)

        filename = get_default_export_filename(session)

        assert session_id in filename

    def test_default_filename_returns_string(self):
        """Test that function returns a string."""
        session = Session()

        filename = get_default_export_filename(session)

        assert isinstance(filename, str)

    def test_default_filename_different_sessions(self):
        """Test that different sessions get different filenames."""
        session1 = Session(session_id="session_001")
        session2 = Session(session_id="session_002")

        filename1 = get_default_export_filename(session1)
        filename2 = get_default_export_filename(session2)

        assert filename1 != filename2
        assert "session_001" in filename1
        assert "session_002" in filename2


class TestExporterIntegration:
    """Integration tests for exporter functionality."""

    def test_export_and_filename_together(self):
        """Test using both export functions together."""
        session = Session(session_id="integration_test_123")
        session.add_message("user", "Test message 1")
        session.add_message("assistant", "Test response 1")

        # Get content and filename
        content = format_export_content(session)
        filename = get_default_export_filename(session)

        # Verify they use the same session ID
        assert "integration_test_123" in content
        assert "integration_test_123" in filename

    def test_export_preserves_conversation_context(self):
        """Test that export preserves complete conversation context."""
        session = Session()

        # Build conversation
        messages = [
            ("user", "What is Python?"),
            ("assistant", "Python is a programming language."),
            ("user", "What can I do with it?"),
            ("assistant", "You can build web apps, data analysis, AI, and more."),
        ]

        for role, content in messages:
            session.add_message(role, content)

        export_content = format_export_content(session)

        # Verify all messages are in export
        for role, content in messages:
            assert content in export_content
