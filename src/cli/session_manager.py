"""Session manager for orchestrating CLI interactions."""

import asyncio
from pathlib import Path

from src.agents.base import AgentInterface
from src.agents.mock_agent import MockAgent
from src.cli.exporter import format_export_content, get_default_export_filename
from src.cli.formatters import (
    format_assistant_message,
    format_context_usage,
    format_error,
    format_goodbye,
    format_help,
    format_session_info,
    format_system_message,
    format_welcome,
    loading_animation,
    print_formatted,
)
from src.cli.parser import parse_input
from src.cli.session import Session
from src.common.types import AgentContext
from src.memory import TARGET_USAGE_AFTER_CLEANUP, ContextTracker, cleanup_messages


class SessionManager:
    """Manages CLI session state and orchestrates interactions.

    The SessionManager is the main orchestrator for the CLI, handling:
    - Interactive session loop
    - Command parsing and routing
    - Agent interaction with proper context
    - Session state management
    - Message history and export

    It provides a clean separation between the CLI interface and agent logic.
    """

    def __init__(
        self, agent: AgentInterface | None = None, context_window: int = 100000
    ) -> None:
        """Initialize the session manager.

        Args:
            agent: Agent for generating responses to queries.
                  Defaults to MockAgent if not provided.
            context_window: Maximum context window in tokens for tracking.
                  Defaults to 100,000. Set to 0 to disable context tracking.
        """
        self._running = False
        self._agent = agent or MockAgent()
        self._session = Session()
        self._context_tracker = ContextTracker(context_window=context_window)

    def run(self) -> None:
        """Run the interactive session loop."""
        self._running = True
        self._display_welcome()

        try:
            while self._running:
                try:
                    user_input = input("> ")
                    self._handle_input(user_input)
                except EOFError:
                    # Handle Ctrl+D
                    break
        except KeyboardInterrupt:
            # Handle Ctrl+C
            print()  # New line after ^C
        finally:
            self._display_goodbye()

    def _display_welcome(self) -> None:
        """Display welcome message."""
        print_formatted(format_welcome(self._session.session_id))

    def _display_goodbye(self) -> None:
        """Display goodbye message."""
        print_formatted(format_goodbye())

    def _handle_input(self, user_input: str) -> None:
        """Handle user input.

        Args:
            user_input: The input string from the user
        """
        # Parse the input
        command_type, argument = parse_input(user_input)

        # Route based on command type
        if command_type == "exit":
            self._running = False
            return

        if command_type == "help":
            print_formatted(format_help())
            return

        if command_type == "session":
            self._handle_session_info()
            return

        if command_type == "export":
            self._handle_export(argument)
            return

        if command_type == "unknown_command":
            self._handle_unknown_command(argument)
            return

        # Handle text input - send to agent
        if command_type == "text":
            # Store user message
            self._session.add_message("user", argument)

            # Build agent context
            context = AgentContext(
                input=argument,
                conversation_history=self._session.get_messages()[
                    :-1
                ],  # Exclude the just-added user message
                session_id=self._session.session_id,
                additional_context=None,  # Can be populated by custom agents
            )

            # Get response from agent with loading animation
            with loading_animation("Thinking"):
                agent_response = asyncio.run(self._agent.process(context))

            # Extract token counts from metadata (if provided by agent)
            input_tokens = agent_response.metadata.get("input_tokens", 0)
            output_tokens = agent_response.metadata.get("output_tokens", 0)
            total_tokens = agent_response.metadata.get("total_tokens", 0)

            # Update the user message with tokens if available
            if input_tokens > 0 and self._session.messages:
                self._session.messages[-1].tokens = input_tokens

            # Store assistant message with tokens
            self._session.add_message("assistant", agent_response.output, output_tokens)

            # Update context tracker if tokens are available
            if total_tokens > 0:
                self._context_tracker.add_tokens(total_tokens)

                # Check if cleanup is needed
                if self._context_tracker.needs_cleanup():
                    self._perform_cleanup()

            # Display formatted response
            print_formatted(format_assistant_message(agent_response.output))

            # Display context usage indicator if tokens are being tracked
            if total_tokens > 0:
                self._display_context_usage()

    def _handle_export(self, custom_filename: str | None) -> None:
        """Handle export command - write chat history to file.

        Args:
            custom_filename: Optional custom filename, or None for default
        """
        try:
            # Determine filename
            if custom_filename:
                filename = custom_filename
            else:
                filename = get_default_export_filename(self._session)

            # Get formatted content
            content = format_export_content(self._session)

            # Write to file
            filepath = Path(filename)
            filepath.write_text(content, encoding="utf-8")

            # Display success message
            success_msg = f"Chat history exported to {filename}"
            print_formatted(format_system_message(success_msg))

        except OSError as e:
            # Handle file write errors
            error_msg = f"Failed to export chat: {e}"
            print_formatted(format_error(error_msg))

    def _handle_session_info(self) -> None:
        """Handle session info command - display current session details."""
        # Get context info if tracking is enabled
        context_tokens = self._context_tracker.get_total_tokens()
        context_window = self._context_tracker._context_window

        # Only include context info if tokens are being tracked
        if context_tokens > 0:
            session_info = format_session_info(
                session_id=self._session.session_id,
                message_count=self._session.message_count(),
                context_tokens=context_tokens,
                context_window=context_window,
            )
        else:
            session_info = format_session_info(
                session_id=self._session.session_id,
                message_count=self._session.message_count(),
            )
        print_formatted(session_info)

    def _handle_unknown_command(self, error_info: dict) -> None:
        """Handle unknown command with helpful suggestion.

        Args:
            error_info: Dictionary with error type, command, and optional suggestion
        """
        cmd = error_info.get("command", "")
        suggestion = error_info.get("suggestion")

        if suggestion:
            error_msg = (
                f"Unknown command: /{cmd}\n"
                f"💡 Did you mean: /{suggestion}?\n"
                f"💡 Type /help to see all available commands"
            )
        else:
            error_msg = (
                f"Unknown command: /{cmd}\n💡 Type /help to see all available commands"
            )

        print_formatted(format_error(error_msg))

    def _perform_cleanup(self) -> None:
        """Perform context cleanup when threshold is reached.

        This removes old messages to bring token usage down to target level,
        while preserving system messages and recent conversation.
        """
        # Calculate target tokens (60% of context window)
        target_tokens = int(
            self._context_tracker._context_window * TARGET_USAGE_AFTER_CLEANUP
        )

        # Get current usage percentage for notification
        usage_percentage = int(self._context_tracker.get_usage_percentage())

        # Perform cleanup
        cleaned_messages, tokens_removed = cleanup_messages(
            self._session.messages, target_tokens
        )

        # Update session with cleaned messages
        self._session.messages = cleaned_messages

        # Update context tracker
        self._context_tracker.remove_tokens(tokens_removed)

        # Notify user
        notification = (
            f"⚠ Context at {usage_percentage}% - clearing old messages to free space"
        )
        print_formatted(format_system_message(notification))

    def _display_context_usage(self) -> None:
        """Display context usage indicator after each response."""
        context_tokens = self._context_tracker.get_total_tokens()
        context_window = self._context_tracker._context_window

        if context_window > 0 and context_tokens > 0:
            percentage = (context_tokens / context_window) * 100
            print_formatted(format_context_usage(percentage))
