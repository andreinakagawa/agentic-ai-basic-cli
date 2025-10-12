"""Context tracker for monitoring token usage and managing context limits."""

from src.common.types import Message

# Cleanup configuration constants
CLEANUP_THRESHOLD = 0.90  # 90% - trigger cleanup at this usage level
MIN_MESSAGES_TO_KEEP = 5  # Always keep at least last 5 messages for coherence
TARGET_USAGE_AFTER_CLEANUP = 0.60  # 60% - target usage level after cleanup


def cleanup_messages(
    messages: list[Message], target_tokens: int
) -> tuple[list[Message], int]:
    """Clean up messages using FIFO strategy to reach target token count.

    This function removes the oldest user/assistant messages while preserving:
    - All system messages (never removed)
    - Last N messages for conversation coherence (MIN_MESSAGES_TO_KEEP)

    Args:
        messages: List of messages to clean up
        target_tokens: Target token count to achieve after cleanup

    Returns:
        Tuple of (cleaned_messages, tokens_removed)
            - cleaned_messages: New list with old messages removed
            - tokens_removed: Total tokens removed during cleanup
    """
    if not messages:
        return ([], 0)

    # Separate system messages from user/assistant messages
    system_messages = [msg for msg in messages if msg.role == "system"]
    non_system_messages = [msg for msg in messages if msg.role != "system"]

    # Calculate current total tokens
    current_tokens = sum(msg.tokens for msg in messages)

    # If already under target, nothing to do
    if current_tokens <= target_tokens:
        return (messages, 0)

    # Separate messages: keep last N non-system messages, consider older ones for removal
    if len(non_system_messages) <= MIN_MESSAGES_TO_KEEP:
        # Too few messages to remove any - keep all
        return (messages, 0)

    messages_to_consider = non_system_messages[:-MIN_MESSAGES_TO_KEEP]

    # Remove oldest messages (FIFO) until we hit target
    tokens_removed = 0
    removed_count = 0

    for msg in messages_to_consider:
        # Check if removing this message would get us close enough to target
        if current_tokens - tokens_removed <= target_tokens:
            break

        tokens_removed += msg.tokens
        removed_count += 1

    # Build final message list: system + remaining non-system
    remaining_non_system = non_system_messages[removed_count:]
    cleaned_messages = system_messages + remaining_non_system

    return (cleaned_messages, tokens_removed)


class ContextTracker:
    """Tracks token usage and determines when cleanup is needed.

    The ContextTracker monitors total token consumption across a conversation
    and provides methods to detect when the context window is approaching
    capacity (≥90%), triggering cleanup if necessary.
    """

    def __init__(self, context_window: int = 100000) -> None:
        """Initialize the context tracker.

        Args:
            context_window: Maximum number of tokens allowed in the context.
                Defaults to 100,000 tokens.
        """
        self._context_window = context_window
        self._total_tokens = 0

    def add_tokens(self, count: int) -> None:
        """Add tokens to the total count.

        Args:
            count: Number of tokens to add. Must be non-negative.

        Raises:
            ValueError: If count is negative.
        """
        if count < 0:
            raise ValueError("Token count cannot be negative")
        self._total_tokens += count

    def remove_tokens(self, count: int) -> None:
        """Remove tokens from the total count.

        The total will not go below zero.

        Args:
            count: Number of tokens to remove.
        """
        self._total_tokens = max(0, self._total_tokens - count)

    def get_total_tokens(self) -> int:
        """Get the current total token count.

        Returns:
            Current total number of tokens.
        """
        return self._total_tokens

    def get_usage_percentage(self) -> float:
        """Calculate the percentage of context window used.

        Returns:
            Usage percentage as a float (e.g., 45.5 for 45.5%).
        """
        return (self._total_tokens / self._context_window) * 100

    def needs_cleanup(self) -> bool:
        """Check if cleanup is needed based on usage threshold.

        Returns:
            True if usage is at or above 90%, False otherwise.
        """
        return self.get_usage_percentage() >= 90.0

    def reset(self) -> None:
        """Reset the token counter to zero."""
        self._total_tokens = 0
