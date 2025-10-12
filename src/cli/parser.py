"""Command parser for CLI input."""


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Number of single-character edits (insertions, deletions, substitutions)
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def _suggest_similar_command(unknown_cmd: str) -> str | None:
    """Suggest a similar command based on Levenshtein distance.

    Args:
        unknown_cmd: The unknown command (without /)

    Returns:
        Suggested command name, or None if no close match
    """
    known_commands = ["exit", "help", "session", "export"]

    # Find the closest match
    min_distance = float("inf")
    suggestion = None

    for cmd in known_commands:
        distance = _levenshtein_distance(unknown_cmd.lower(), cmd.lower())
        # Only suggest if within 2 edits (typo territory)
        if distance < min_distance and distance <= 2:
            min_distance = distance
            suggestion = cmd

    return suggestion


def parse_input(user_input: str) -> tuple[str, str | None | dict]:
    """Parse user input to identify commands vs regular text.

    Commands start with '/' and are case-sensitive.
    Currently recognized commands: /exit, /help, /session, /export
    All other input is treated as regular text (queries).

    Args:
        user_input: Raw input string from the user

    Returns:
        Tuple of (command_type, argument) where:
        - command_type: "exit" | "help" | "session" | "export" | "text" | "unknown_command"
        - argument: None for exit/help/session, filename (str) for export,
                   text content (str) for "text", error dict for "unknown_command"
    """
    # Strip whitespace
    stripped = user_input.strip()

    # Handle empty input as text
    if not stripped:
        return ("text", "")

    # Check for /exit command
    if stripped == "/exit":
        return ("exit", None)

    # Check for /help command
    if stripped == "/help":
        return ("help", None)

    # Check for /session command
    if stripped == "/session":
        return ("session", None)

    # Check for /export command (with optional filename)
    if stripped.startswith("/export"):
        # Extract filename if provided
        parts = stripped.split(maxsplit=1)
        if len(parts) > 1:
            # Custom filename provided
            return ("export", parts[1].strip())
        else:
            # No filename, use default
            return ("export", None)

    # Check if it looks like an unknown command (starts with /)
    if stripped.startswith("/"):
        # Extract command name
        cmd_parts = stripped[1:].split(maxsplit=1)
        unknown_cmd = cmd_parts[0] if cmd_parts else ""

        # Try to suggest a similar command
        suggestion = _suggest_similar_command(unknown_cmd)

        if suggestion:
            error_dict = {
                "error": "unknown_command",
                "command": unknown_cmd,
                "suggestion": suggestion,
            }
        else:
            error_dict = {
                "error": "unknown_command",
                "command": unknown_cmd,
            }

        return ("unknown_command", error_dict)

    # Everything else is treated as text
    return ("text", user_input)
