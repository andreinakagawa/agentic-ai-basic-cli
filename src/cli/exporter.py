"""Chat export formatting for conversation history."""

from src.cli.session import Session


def format_export_content(session: Session) -> str:
    """Format conversation history for export to text file.

    This is a pure formatter function - it does not perform file I/O.
    The SessionManager is responsible for writing the content to a file.

    Args:
        session: Session object containing conversation history

    Returns:
        Formatted string content ready for file export
    """
    lines = []
    lines.append(f"Session: {session.session_id}")
    lines.append("")

    # Check if there are any messages
    if session.message_count() == 0:
        lines.append("(No messages in this conversation)")
    else:
        # Add each message
        for message in session.get_messages():
            role_label = message.role.upper()
            lines.append(f"[{role_label}]:")
            lines.append(message.content)
            lines.append("")

    return "\n".join(lines)


def get_default_export_filename(session: Session) -> str:
    """Get the default export filename for a session.

    Args:
        session: Session object

    Returns:
        Default filename string (e.g., "chat_20250104_143022.txt")
    """
    return f"chat_{session.session_id}.txt"
