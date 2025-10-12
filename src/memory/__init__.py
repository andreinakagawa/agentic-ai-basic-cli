"""Memory management utilities for the Agentic AI CLI Framework.

This module provides utilities for managing conversation context and token tracking:
- ContextTracker: Monitors token usage and triggers cleanup when approaching limits
- cleanup_messages: FIFO-based message cleanup to reduce context size

These utilities help manage long conversations by automatically removing old messages
while preserving system messages and recent context.
"""

from src.memory.context_tracker import (
    CLEANUP_THRESHOLD,
    MIN_MESSAGES_TO_KEEP,
    TARGET_USAGE_AFTER_CLEANUP,
    ContextTracker,
    cleanup_messages,
)

__all__ = [
    "ContextTracker",
    "cleanup_messages",
    "CLEANUP_THRESHOLD",
    "MIN_MESSAGES_TO_KEEP",
    "TARGET_USAGE_AFTER_CLEANUP",
]
