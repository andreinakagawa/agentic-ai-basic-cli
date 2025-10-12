"""Tests for CLI output formatters."""

from rich.text import Text

from src.cli.formatters import (
    format_assistant_message,
    format_error,
    format_goodbye,
    format_help,
    format_session_info,
    format_system_message,
    format_user_message,
    format_welcome,
    get_context_color,
)


class TestFormatUserMessage:
    """Test suite for format_user_message."""

    def test_format_user_message_simple(self):
        """Test formatting a simple user message."""
        result = format_user_message("Hello world")
        assert "You: Hello world" == result

    def test_format_user_message_empty(self):
        """Test formatting empty user message."""
        result = format_user_message("")
        assert "You: " == result

    def test_format_user_message_multiline(self):
        """Test formatting multiline user message."""
        result = format_user_message("Line 1\nLine 2")
        assert "You: Line 1\nLine 2" == result

    def test_format_user_message_returns_string(self):
        """Test that function returns a string."""
        result = format_user_message("Test")
        assert isinstance(result, str)


class TestFormatAssistantMessage:
    """Test suite for format_assistant_message."""

    def test_format_assistant_message_simple(self):
        """Test formatting a simple assistant message."""
        result = format_assistant_message("Hello there")
        assert isinstance(result, Text)

    def test_format_assistant_message_returns_text(self):
        """Test that function returns Rich Text object."""
        result = format_assistant_message("Test")
        assert isinstance(result, Text)

    def test_format_assistant_message_contains_content(self):
        """Test that formatted message contains the content."""
        result = format_assistant_message("Test content")
        text_str = result.plain
        assert "Assistant:" in text_str
        assert "Test content" in text_str

    def test_format_assistant_message_empty(self):
        """Test formatting empty assistant message."""
        result = format_assistant_message("")
        text_str = result.plain
        assert "Assistant:" in text_str


class TestFormatSystemMessage:
    """Test suite for format_system_message."""

    def test_format_system_message_simple(self):
        """Test formatting a simple system message."""
        result = format_system_message("System notification")
        assert isinstance(result, Text)

    def test_format_system_message_returns_text(self):
        """Test that function returns Rich Text object."""
        result = format_system_message("Test")
        assert isinstance(result, Text)

    def test_format_system_message_contains_content(self):
        """Test that formatted message contains the content."""
        result = format_system_message("Test message")
        text_str = result.plain
        assert "System:" in text_str
        assert "Test message" in text_str

    def test_format_system_message_empty(self):
        """Test formatting empty system message."""
        result = format_system_message("")
        text_str = result.plain
        assert "System:" in text_str


class TestFormatError:
    """Test suite for format_error."""

    def test_format_error_simple(self):
        """Test formatting a simple error message."""
        result = format_error("Something went wrong")
        assert isinstance(result, Text)

    def test_format_error_returns_text(self):
        """Test that function returns Rich Text object."""
        result = format_error("Test error")
        assert isinstance(result, Text)

    def test_format_error_contains_content(self):
        """Test that formatted error contains the content."""
        result = format_error("Test error message")
        text_str = result.plain
        assert "Error:" in text_str
        assert "Test error message" in text_str

    def test_format_error_empty(self):
        """Test formatting empty error message."""
        result = format_error("")
        text_str = result.plain
        assert "Error:" in text_str


class TestFormatWelcome:
    """Test suite for format_welcome."""

    def test_format_welcome_without_session_id(self):
        """Test welcome message without session ID."""
        result = format_welcome()
        assert "Welcome to Agentic AI CLI!" in result
        assert "/exit" in result
        assert "/help" in result

    def test_format_welcome_with_session_id(self):
        """Test welcome message with session ID."""
        result = format_welcome("session_123")
        assert "Welcome to Agentic AI CLI!" in result
        assert "Session ID: session_123" in result

    def test_format_welcome_returns_string(self):
        """Test that function returns a string."""
        result = format_welcome()
        assert isinstance(result, str)

    def test_format_welcome_contains_usage_info(self):
        """Test that welcome contains usage information."""
        result = format_welcome()
        assert "Type your messages below" in result or "messages" in result.lower()


class TestFormatGoodbye:
    """Test suite for format_goodbye."""

    def test_format_goodbye_message(self):
        """Test goodbye message content."""
        result = format_goodbye()
        assert "Goodbye" in result or "goodbye" in result.lower()

    def test_format_goodbye_returns_string(self):
        """Test that function returns a string."""
        result = format_goodbye()
        assert isinstance(result, str)


class TestFormatHelp:
    """Test suite for format_help."""

    def test_format_help_returns_text(self):
        """Test that help returns Rich Text object."""
        result = format_help()
        assert isinstance(result, Text)

    def test_format_help_contains_commands(self):
        """Test that help contains available commands."""
        result = format_help()
        text_str = result.plain

        # Should contain main commands
        assert "/help" in text_str
        assert "/exit" in text_str
        assert "/session" in text_str
        assert "/export" in text_str

    def test_format_help_contains_descriptions(self):
        """Test that help contains command descriptions."""
        result = format_help()
        text_str = result.plain

        # Should have some explanatory text
        assert len(text_str) > 50  # Should be substantial


class TestGetContextColor:
    """Test suite for get_context_color."""

    def test_context_color_green_low(self):
        """Test color for low usage (green)."""
        assert get_context_color(0) == "green"
        assert get_context_color(50) == "green"
        assert get_context_color(69) == "green"

    def test_context_color_yellow_moderate(self):
        """Test color for moderate usage (yellow)."""
        assert get_context_color(70) == "yellow"
        assert get_context_color(80) == "yellow"
        assert get_context_color(89) == "yellow"

    def test_context_color_red_high(self):
        """Test color for high usage (red)."""
        assert get_context_color(90) == "red"
        assert get_context_color(95) == "red"
        assert get_context_color(100) == "red"

    def test_context_color_boundary_values(self):
        """Test color at boundary values."""
        assert get_context_color(69.9) == "green"
        assert get_context_color(70.0) == "yellow"
        assert get_context_color(89.9) == "yellow"
        assert get_context_color(90.0) == "red"


class TestFormatSessionInfo:
    """Test suite for format_session_info."""

    def test_format_session_info_basic(self):
        """Test formatting session info without context."""
        result = format_session_info(
            session_id="test_session",
            message_count=5
        )
        assert isinstance(result, Text)

        text_str = result.plain
        assert "test_session" in text_str
        assert "5" in text_str

    def test_format_session_info_with_context(self):
        """Test formatting session info with context tokens."""
        result = format_session_info(
            session_id="test_session",
            message_count=10,
            context_tokens=5000,
            context_window=10000
        )
        text_str = result.plain

        assert "test_session" in text_str
        assert "10" in text_str
        assert "5" in text_str or "5,000" in text_str  # Token count
        assert "10" in text_str or "10,000" in text_str  # Window size

    def test_format_session_info_no_context(self):
        """Test session info without context parameters."""
        result = format_session_info(
            session_id="session_123",
            message_count=3
        )
        text_str = result.plain

        assert "session_123" in text_str
        assert "3" in text_str
        # Should not contain context info
        assert "Context:" not in text_str or "Context" in text_str  # May vary

    def test_format_session_info_returns_text(self):
        """Test that function returns Rich Text object."""
        result = format_session_info("test", 0)
        assert isinstance(result, Text)

    def test_format_session_info_zero_messages(self):
        """Test session info with zero messages."""
        result = format_session_info("session_0", 0)
        text_str = result.plain

        assert "session_0" in text_str
        assert "0" in text_str

    def test_format_session_info_many_messages(self):
        """Test session info with many messages."""
        result = format_session_info("session_big", 1000)
        text_str = result.plain

        assert "session_big" in text_str
        assert "1000" in text_str or "1,000" in text_str


class TestFormatterIntegration:
    """Integration tests for formatters."""

    def test_all_formatters_callable(self):
        """Test that all main formatters are callable."""
        formatters = [
            format_user_message,
            format_assistant_message,
            format_system_message,
            format_error,
            format_welcome,
            format_goodbye,
            format_help,
            get_context_color,
            format_session_info,
        ]

        for formatter in formatters:
            assert callable(formatter)

    def test_conversation_formatting_flow(self):
        """Test formatting a complete conversation."""
        # Welcome
        welcome = format_welcome("session_test")
        assert isinstance(welcome, str)

        # User message
        user_msg = format_user_message("Hello")
        assert isinstance(user_msg, str)

        # Assistant message
        asst_msg = format_assistant_message("Hi there!")
        assert isinstance(asst_msg, Text)

        # System message
        sys_msg = format_system_message("Processing...")
        assert isinstance(sys_msg, Text)

        # Error message
        err_msg = format_error("Something failed")
        assert isinstance(err_msg, Text)

        # Session info
        info = format_session_info("session_test", 2)
        assert isinstance(info, Text)

        # Goodbye
        goodbye = format_goodbye()
        assert isinstance(goodbye, str)

    def test_rich_text_objects_have_plain_text(self):
        """Test that Rich Text objects can be converted to plain text."""
        text_formatters = [
            format_assistant_message("test"),
            format_system_message("test"),
            format_error("test"),
            format_help(),
            format_session_info("id", 1),
        ]

        for text_obj in text_formatters:
            assert isinstance(text_obj, Text)
            assert hasattr(text_obj, "plain")
            assert isinstance(text_obj.plain, str)
            assert len(text_obj.plain) > 0
