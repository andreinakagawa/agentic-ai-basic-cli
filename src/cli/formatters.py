"""Output formatting utilities for the CLI."""

from contextlib import contextmanager

from rich.console import Console
from rich.spinner import Spinner
from rich.text import Text

# Initialize Rich console for colored output
console = Console()


def format_user_message(content: str) -> str:
    """Format a user message.

    Args:
        content: The message content

    Returns:
        Formatted message string
    """
    return f"You: {content}"


def format_assistant_message(content: str) -> str:
    """Format an assistant message.

    Args:
        content: The message content

    Returns:
        Formatted message string with styling
    """
    text = Text()
    text.append("Assistant: ", style="bold cyan")
    text.append(content)
    return text


def format_system_message(content: str) -> str:
    """Format a system message.

    Args:
        content: The message content

    Returns:
        Formatted message string with styling
    """
    text = Text()
    text.append("System: ", style="bold yellow")
    text.append(content, style="yellow")
    return text


def format_error(error: str) -> str:
    """Format an error message.

    Args:
        error: The error message

    Returns:
        Formatted error string with styling
    """
    text = Text()
    text.append("Error: ", style="bold red")
    text.append(error, style="red")
    return text


def format_welcome(session_id: str | None = None) -> str:
    """Format the welcome message.

    Args:
        session_id: Optional session ID to display

    Returns:
        Welcome message string
    """
    welcome = "Welcome to Agentic AI CLI!"
    if session_id:
        welcome += f"\nSession ID: {session_id}"
    welcome += "\nType your messages below. Use /exit to quit, /help for commands.\n"
    return welcome


def format_goodbye() -> str:
    """Format the goodbye message.

    Returns:
        Goodbye message string
    """
    return "\nGoodbye! Thanks for using Agentic AI CLI."


def format_help() -> str:
    """Format the help message showing available commands.

    Returns:
        Help message string with styling
    """
    text = Text()
    text.append("Available Commands\n\n", style="bold cyan")

    # Session Commands
    text.append("Session Commands:\n", style="bold yellow")
    text.append("  /help         ", style="bold green")
    text.append("- Show this help message\n")
    text.append("  /session      ", style="bold green")
    text.append("- Show current session information\n")
    text.append("  /exit         ", style="bold green")
    text.append("- Exit the application\n\n")

    # Export Commands
    text.append("Export Commands:\n", style="bold yellow")
    text.append("  /export       ", style="bold green")
    text.append("- Export chat to chat_<session_id>.txt\n")
    text.append("  /export ", style="bold green")
    text.append("<filename>", style="italic")
    text.append(" - Export chat to custom file\n")
    text.append("                  Example: ", style="dim")
    text.append("/export my_conversation.txt\n", style="italic dim")

    text.append("\n")
    text.append(
        "Just type your message to chat with the agent!",
        style="dim",
    )
    return text


def get_context_color(percentage: float) -> str:
    """Get color for context usage based on percentage.

    Args:
        percentage: Usage percentage (0-100)

    Returns:
        Color name for Rich styling (green, yellow, or red)
    """
    if percentage < 70:
        return "green"
    elif percentage < 90:
        return "yellow"
    else:
        return "red"


def format_context_usage(percentage: float) -> str:
    """Format context usage percentage for display.

    Args:
        percentage: Usage percentage (0-100)

    Returns:
        Formatted context usage string with color coding
    """
    color = get_context_color(percentage)
    text = Text()
    text.append(f"[Context: {int(percentage)}%] ", style=f"bold {color}")
    return text


def format_session_info(
    session_id: str,
    message_count: int,
    context_tokens: int | None = None,
    context_window: int | None = None,
) -> str:
    """Format session information display.

    Args:
        session_id: Current session ID
        message_count: Number of messages in session
        context_tokens: Optional current token usage
        context_window: Optional maximum context window

    Returns:
        Formatted session info string with styling
    """
    text = Text()
    text.append("Session Information\n", style="bold cyan")
    text.append("  Session ID: ", style="bold")
    text.append(f"{session_id}\n")
    text.append("  Messages: ", style="bold")
    text.append(f"{message_count}\n")

    # Add context info if provided
    if context_tokens is not None and context_window is not None:
        percentage = (context_tokens / context_window) * 100
        color = get_context_color(percentage)
        text.append("  Context: ", style="bold")
        text.append(f"{context_tokens:,} / {context_window:,} tokens ", style=color)
        text.append(f"({int(percentage)}%)\n", style=color)

        # Status indicator
        text.append("  Status: ", style="bold")
        if percentage < 70:
            text.append("Healthy\n", style="green")
        elif percentage < 90:
            text.append("Moderate\n", style="yellow")
        else:
            text.append("Cleanup needed\n", style="red")

    return text


def print_formatted(text: str | Text) -> None:
    """Print formatted text to console.

    Args:
        text: String or Rich Text object to print
    """
    if isinstance(text, Text):
        console.print(text)
    else:
        print(text)


@contextmanager
def loading_animation(message: str = "Thinking"):
    """Display a loading spinner while performing an async operation.

    Args:
        message: Text to display next to the spinner

    Yields:
        None - context manager for use with 'with' statement

    Example:
        with loading_animation("Processing your query"):
            result = asyncio.run(some_async_function())
    """
    # Create spinner with custom text
    spinner = Spinner("dots", text=Text(message, style="cyan"), style="cyan")

    # Start the spinner
    with console.status(spinner):
        yield
