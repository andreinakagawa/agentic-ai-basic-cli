"""Tests for SessionManager class."""

from unittest.mock import patch, MagicMock

from src.cli.session_manager import SessionManager
from src.agents.mock_agent import MockAgent
from src.agents.base import AgentInterface
from src.common.types import AgentContext, AgentResponse


class TestSessionManagerInitialization:
    """Test suite for SessionManager initialization."""

    def test_session_manager_creation_default(self):
        """Test creating SessionManager with default agent."""
        manager = SessionManager()

        assert manager._agent is not None
        assert isinstance(manager._agent, MockAgent)
        assert manager._session is not None
        assert manager._running is False

    def test_session_manager_creation_with_custom_agent(self):
        """Test creating SessionManager with custom agent."""
        custom_agent = MockAgent()
        manager = SessionManager(agent=custom_agent)

        assert manager._agent is custom_agent

    def test_session_manager_creation_with_context_window(self):
        """Test creating SessionManager with custom context window."""
        manager = SessionManager(context_window=50000)

        assert manager._context_tracker._context_window == 50000

    def test_session_manager_has_session(self):
        """Test that SessionManager creates a session."""
        manager = SessionManager()

        assert manager._session is not None
        assert manager._session.session_id is not None

    def test_session_manager_initial_state(self):
        """Test SessionManager initial state."""
        manager = SessionManager()

        assert manager._running is False
        assert manager._session.message_count() == 0


class TestSessionManagerHandleExport:
    """Test suite for _handle_export method."""

    def test_handle_export_default_filename(self, tmp_path):
        """Test export with default filename."""
        manager = SessionManager()
        manager._session.add_message("user", "Test message")

        # Change to temp directory
        with patch('src.cli.session_manager.Path') as mock_path:
            mock_file = MagicMock()
            mock_path.return_value = mock_file

            manager._handle_export(None)

            # Verify file was written
            assert mock_file.write_text.called

    def test_handle_export_custom_filename(self, tmp_path):
        """Test export with custom filename."""
        manager = SessionManager()
        manager._session.add_message("user", "Test message")

        custom_file = "my_custom_chat.txt"

        with patch('src.cli.session_manager.Path') as mock_path:
            mock_file = MagicMock()
            mock_path.return_value = mock_file

            manager._handle_export(custom_file)

            # Verify custom filename was used
            mock_path.assert_called_with(custom_file)

    def test_handle_export_with_messages(self, tmp_path):
        """Test export with conversation messages."""
        manager = SessionManager()
        manager._session.add_message("user", "Hello")
        manager._session.add_message("assistant", "Hi there!")

        with patch('src.cli.session_manager.Path') as mock_path:
            mock_file = MagicMock()
            mock_path.return_value = mock_file

            manager._handle_export(None)

            # Verify content contains messages
            written_content = mock_file.write_text.call_args[0][0]
            assert "Hello" in written_content
            assert "Hi there!" in written_content

    def test_handle_export_file_error(self):
        """Test export handling file write errors."""
        manager = SessionManager()

        with patch('src.cli.session_manager.Path') as mock_path:
            mock_file = MagicMock()
            mock_file.write_text.side_effect = OSError("Permission denied")
            mock_path.return_value = mock_file

            # Should not raise, should handle error gracefully
            manager._handle_export("test.txt")


class TestSessionManagerHandleSessionInfo:
    """Test suite for _handle_session_info method."""

    def test_handle_session_info_basic(self):
        """Test displaying session info."""
        manager = SessionManager()

        # Should not raise
        with patch('src.cli.session_manager.print_formatted'):
            manager._handle_session_info()

    def test_handle_session_info_with_messages(self):
        """Test session info with messages."""
        manager = SessionManager()
        manager._session.add_message("user", "Test 1")
        manager._session.add_message("assistant", "Test 2")

        with patch('src.cli.session_manager.print_formatted') as mock_print:
            manager._handle_session_info()

            # Verify print was called
            assert mock_print.called


class TestSessionManagerHandleUnknownCommand:
    """Test suite for _handle_unknown_command method."""

    def test_handle_unknown_command_with_suggestion(self):
        """Test unknown command with suggestion."""
        manager = SessionManager()

        error_info = {
            "error": "unknown_command",
            "command": "exot",
            "suggestion": "exit"
        }

        with patch('src.cli.session_manager.print_formatted') as mock_print:
            manager._handle_unknown_command(error_info)

            # Verify error was printed
            assert mock_print.called

    def test_handle_unknown_command_without_suggestion(self):
        """Test unknown command without suggestion."""
        manager = SessionManager()

        error_info = {
            "error": "unknown_command",
            "command": "xyz"
        }

        with patch('src.cli.session_manager.print_formatted') as mock_print:
            manager._handle_unknown_command(error_info)

            # Verify error was printed
            assert mock_print.called


class TestSessionManagerHandleInput:
    """Test suite for _handle_input method."""

    def test_handle_input_exit_command(self):
        """Test handling exit command."""
        manager = SessionManager()
        manager._running = True

        manager._handle_input("/exit")

        assert manager._running is False

    def test_handle_input_help_command(self):
        """Test handling help command."""
        manager = SessionManager()

        with patch('src.cli.session_manager.print_formatted') as mock_print:
            manager._handle_input("/help")

            assert mock_print.called

    def test_handle_input_session_command(self):
        """Test handling session command."""
        manager = SessionManager()

        with patch('src.cli.session_manager.print_formatted') as mock_print:
            manager._handle_input("/session")

            assert mock_print.called

    def test_handle_input_export_command(self):
        """Test handling export command."""
        manager = SessionManager()

        with patch('src.cli.session_manager.Path') as mock_path:
            mock_file = MagicMock()
            mock_path.return_value = mock_file

            manager._handle_input("/export")

            # Should trigger export
            assert mock_file.write_text.called

    def test_handle_input_text_creates_message(self):
        """Test that text input creates user message."""
        manager = SessionManager()

        with patch('src.cli.session_manager.loading_animation'), \
             patch('src.cli.session_manager.print_formatted'), \
             patch('asyncio.run') as mock_run:

            # Mock agent response
            mock_run.return_value = AgentResponse(
                output="Response",
                metadata={}
            )

            manager._handle_input("Hello world")

            # Verify user message was added
            assert manager._session.message_count() >= 1
            messages = manager._session.get_messages()
            assert any(msg.content == "Hello world" for msg in messages)

    def test_handle_input_text_calls_agent(self):
        """Test that text input calls agent."""
        manager = SessionManager()

        with patch('src.cli.session_manager.loading_animation'), \
             patch('src.cli.session_manager.print_formatted'), \
             patch('asyncio.run') as mock_run:

            mock_run.return_value = AgentResponse(
                output="Response",
                metadata={}
            )

            manager._handle_input("Test input")

            # Verify asyncio.run was called (agent was invoked)
            assert mock_run.called

    def test_handle_input_unknown_command(self):
        """Test handling unknown command."""
        manager = SessionManager()

        with patch('src.cli.session_manager.print_formatted') as mock_print:
            manager._handle_input("/unknown")

            # Should print error
            assert mock_print.called


class TestSessionManagerIntegration:
    """Integration tests for SessionManager."""

    def test_session_manager_message_flow(self):
        """Test complete message flow through session manager."""
        manager = SessionManager()

        # Initially no messages
        assert manager._session.message_count() == 0

        with patch('src.cli.session_manager.loading_animation'), \
             patch('src.cli.session_manager.print_formatted'), \
             patch('asyncio.run') as mock_run:

            mock_run.return_value = AgentResponse(
                output="Hello!",
                metadata={"input_tokens": 5, "output_tokens": 3, "total_tokens": 8}
            )

            manager._handle_input("Hi")

            # Should have both user and assistant messages
            assert manager._session.message_count() == 2

    def test_session_manager_multiple_interactions(self):
        """Test multiple user interactions."""
        manager = SessionManager()

        with patch('src.cli.session_manager.loading_animation'), \
             patch('src.cli.session_manager.print_formatted'), \
             patch('asyncio.run') as mock_run:

            mock_run.return_value = AgentResponse(
                output="Response",
                metadata={}
            )

            # Multiple inputs
            manager._handle_input("First message")
            manager._handle_input("Second message")
            manager._handle_input("Third message")

            # Should have 6 messages (3 user + 3 assistant)
            assert manager._session.message_count() == 6

    def test_session_manager_with_custom_agent(self):
        """Test session manager with custom agent."""
        # Use MockAgent instead of creating a CustomAgent to avoid unawaited coroutine
        custom_agent = MockAgent()
        manager = SessionManager(agent=custom_agent)

        with patch('src.cli.session_manager.loading_animation'), \
             patch('src.cli.session_manager.print_formatted'), \
             patch('asyncio.run') as mock_run:

            mock_run.return_value = AgentResponse(
                output="Echo: test",
                metadata={}
            )

            manager._handle_input("test")

            # Verify message was handled
            assert manager._session.message_count() >= 1

    def test_session_manager_preserves_session_id(self):
        """Test that session ID is preserved throughout."""
        manager = SessionManager()

        session_id = manager._session.session_id

        with patch('src.cli.session_manager.loading_animation'), \
             patch('src.cli.session_manager.print_formatted'), \
             patch('asyncio.run') as mock_run:

            mock_run.return_value = AgentResponse(
                output="Response",
                metadata={}
            )

            manager._handle_input("Test")

            # Session ID should not change
            assert manager._session.session_id == session_id
