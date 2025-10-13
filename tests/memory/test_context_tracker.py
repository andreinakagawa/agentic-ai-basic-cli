"""Tests for context_tracker module."""

import pytest

from src.common.types import Message
from src.memory.context_tracker import (
    CLEANUP_THRESHOLD,
    MIN_MESSAGES_TO_KEEP,
    TARGET_USAGE_AFTER_CLEANUP,
    ContextTracker,
    cleanup_messages,
)


class TestCleanupMessages:
    """Tests for cleanup_messages function."""

    def test_empty_messages_list(self):
        """Test cleanup with empty messages list."""
        cleaned, removed = cleanup_messages([], target_tokens=1000)
        assert cleaned == []
        assert removed == 0

    def test_already_under_target(self):
        """Test cleanup when already under target tokens."""
        messages = [
            Message(role="user", content="Hello", tokens=10),
            Message(role="assistant", content="Hi", tokens=10),
        ]
        cleaned, removed = cleanup_messages(messages, target_tokens=100)
        assert cleaned == messages
        assert removed == 0

    def test_preserves_system_messages(self):
        """Test that system messages are never removed."""
        messages = [
            Message(role="system", content="You are helpful", tokens=50),
            Message(role="user", content="Old message", tokens=100),
            Message(role="assistant", content="Old response", tokens=100),
            Message(role="user", content="Recent message", tokens=10),
            Message(role="assistant", content="Recent response", tokens=10),
        ]
        cleaned, removed = cleanup_messages(messages, target_tokens=100)

        # System message should still be there
        system_msgs = [msg for msg in cleaned if msg.role == "system"]
        assert len(system_msgs) == 1
        assert system_msgs[0].content == "You are helpful"

    def test_keeps_minimum_messages(self):
        """Test that at least MIN_MESSAGES_TO_KEEP non-system messages are kept."""
        messages = [
            Message(role="user", content=f"Message {i}", tokens=100)
            for i in range(10)
        ]
        cleaned, removed = cleanup_messages(messages, target_tokens=50)

        # Should keep at least MIN_MESSAGES_TO_KEEP messages
        assert len(cleaned) >= MIN_MESSAGES_TO_KEEP

    def test_too_few_messages_no_cleanup(self):
        """Test that cleanup doesn't happen if too few messages."""
        messages = [
            Message(role="user", content=f"Message {i}", tokens=100)
            for i in range(MIN_MESSAGES_TO_KEEP)
        ]
        cleaned, removed = cleanup_messages(messages, target_tokens=10)

        # All messages should be kept
        assert cleaned == messages
        assert removed == 0

    def test_fifo_removal_order(self):
        """Test that oldest messages are removed first (FIFO)."""
        messages = [
            Message(role="user", content="Old 1", tokens=100),
            Message(role="assistant", content="Response 1", tokens=100),
            Message(role="user", content="Old 2", tokens=100),
            Message(role="assistant", content="Response 2", tokens=100),
            Message(role="user", content="Recent 1", tokens=10),
            Message(role="assistant", content="Recent Response 1", tokens=10),
            Message(role="user", content="Recent 2", tokens=10),
            Message(role="assistant", content="Recent Response 2", tokens=10),
        ]
        cleaned, removed = cleanup_messages(messages, target_tokens=100)

        # Recent messages should be preserved
        recent_contents = [msg.content for msg in cleaned]
        assert "Recent 1" in recent_contents
        assert "Recent Response 1" in recent_contents
        assert "Recent 2" in recent_contents
        assert "Recent Response 2" in recent_contents

        # Old messages should be removed
        assert "Old 1" not in recent_contents or "Old 2" not in recent_contents

    def test_removes_correct_token_count(self):
        """Test that cleanup removes correct number of tokens."""
        messages = [
            Message(role="user", content="Msg 1", tokens=100),
            Message(role="assistant", content="Resp 1", tokens=100),
            Message(role="user", content="Msg 2", tokens=100),
            Message(role="assistant", content="Resp 2", tokens=100),
            Message(role="user", content="Msg 3", tokens=10),
            Message(role="assistant", content="Resp 3", tokens=10),
        ]
        # Total: 420 tokens, target: 100
        cleaned, removed = cleanup_messages(messages, target_tokens=100)

        # Check that we removed enough tokens
        remaining_tokens = sum(msg.tokens for msg in cleaned)
        assert remaining_tokens <= 100 or len(cleaned) <= MIN_MESSAGES_TO_KEEP

        # Verify removed count is accurate
        assert removed == sum(msg.tokens for msg in messages) - remaining_tokens

    def test_mixed_system_and_user_messages(self):
        """Test cleanup with mixed system and user/assistant messages."""
        messages = [
            Message(role="system", content="System 1", tokens=50),
            Message(role="user", content="Old 1", tokens=100),
            Message(role="assistant", content="Old Response 1", tokens=100),
            Message(role="system", content="System 2", tokens=50),
            Message(role="user", content="Recent 1", tokens=10),
            Message(role="assistant", content="Recent Response 1", tokens=10),
            Message(role="user", content="Recent 2", tokens=10),
        ]
        cleaned, removed = cleanup_messages(messages, target_tokens=150)

        # All system messages should be preserved
        system_msgs = [msg for msg in cleaned if msg.role == "system"]
        assert len(system_msgs) == 2

        # Recent messages should be preserved
        recent_contents = [msg.content for msg in cleaned]
        assert "Recent 1" in recent_contents
        assert "Recent Response 1" in recent_contents

    def test_cleanup_reaches_target(self):
        """Test that cleanup gets close to target token count."""
        messages = [
            Message(role="user", content=f"Msg {i}", tokens=50) for i in range(20)
        ]
        # Total: 1000 tokens
        target = 300
        cleaned, removed = cleanup_messages(messages, target_tokens=target)

        remaining_tokens = sum(msg.tokens for msg in cleaned)

        # Should be at or below target (within reason, given MIN_MESSAGES_TO_KEEP)
        # If we have more than MIN_MESSAGES_TO_KEEP, we should be close to target
        if len(cleaned) > MIN_MESSAGES_TO_KEEP:
            assert remaining_tokens <= target * 1.2  # Allow 20% overage


class TestContextTracker:
    """Tests for ContextTracker class."""

    def test_initialization_default(self):
        """Test default initialization."""
        tracker = ContextTracker()
        assert tracker.get_total_tokens() == 0
        assert tracker.get_usage_percentage() == 0.0

    def test_initialization_custom_window(self):
        """Test initialization with custom context window."""
        tracker = ContextTracker(context_window=50000)
        assert tracker.get_total_tokens() == 0
        # Add tokens to test percentage calculation
        tracker.add_tokens(25000)
        assert tracker.get_usage_percentage() == 50.0

    def test_add_tokens(self):
        """Test adding tokens."""
        tracker = ContextTracker()
        tracker.add_tokens(100)
        assert tracker.get_total_tokens() == 100

        tracker.add_tokens(50)
        assert tracker.get_total_tokens() == 150

    def test_add_tokens_zero(self):
        """Test adding zero tokens."""
        tracker = ContextTracker()
        tracker.add_tokens(0)
        assert tracker.get_total_tokens() == 0

    def test_add_tokens_negative_raises_error(self):
        """Test that adding negative tokens raises ValueError."""
        tracker = ContextTracker()
        with pytest.raises(ValueError, match="Token count cannot be negative"):
            tracker.add_tokens(-10)

    def test_remove_tokens(self):
        """Test removing tokens."""
        tracker = ContextTracker()
        tracker.add_tokens(100)
        tracker.remove_tokens(30)
        assert tracker.get_total_tokens() == 70

    def test_remove_tokens_more_than_total(self):
        """Test that removing more tokens than total doesn't go negative."""
        tracker = ContextTracker()
        tracker.add_tokens(50)
        tracker.remove_tokens(100)
        assert tracker.get_total_tokens() == 0

    def test_remove_tokens_from_zero(self):
        """Test removing tokens when count is already zero."""
        tracker = ContextTracker()
        tracker.remove_tokens(10)
        assert tracker.get_total_tokens() == 0

    def test_get_usage_percentage(self):
        """Test usage percentage calculation."""
        tracker = ContextTracker(context_window=1000)

        tracker.add_tokens(0)
        assert tracker.get_usage_percentage() == 0.0

        tracker.add_tokens(250)
        assert tracker.get_usage_percentage() == 25.0

        tracker.add_tokens(250)
        assert tracker.get_usage_percentage() == 50.0

        tracker.add_tokens(450)
        assert tracker.get_usage_percentage() == 95.0

    def test_get_usage_percentage_precision(self):
        """Test usage percentage with decimal precision."""
        tracker = ContextTracker(context_window=1000)
        tracker.add_tokens(333)
        assert pytest.approx(tracker.get_usage_percentage(), 0.1) == 33.3

    def test_needs_cleanup_below_threshold(self):
        """Test needs_cleanup returns False below 90% threshold."""
        tracker = ContextTracker(context_window=1000)
        tracker.add_tokens(800)  # 80%
        assert not tracker.needs_cleanup()

        tracker.add_tokens(89)  # 89%
        assert not tracker.needs_cleanup()

    def test_needs_cleanup_at_threshold(self):
        """Test needs_cleanup returns True at exactly 90%."""
        tracker = ContextTracker(context_window=1000)
        tracker.add_tokens(900)  # 90%
        assert tracker.needs_cleanup()

    def test_needs_cleanup_above_threshold(self):
        """Test needs_cleanup returns True above 90%."""
        tracker = ContextTracker(context_window=1000)
        tracker.add_tokens(950)  # 95%
        assert tracker.needs_cleanup()

        tracker.add_tokens(50)  # 100%
        assert tracker.needs_cleanup()

    def test_reset(self):
        """Test reset functionality."""
        tracker = ContextTracker()
        tracker.add_tokens(500)
        assert tracker.get_total_tokens() == 500

        tracker.reset()
        assert tracker.get_total_tokens() == 0
        assert tracker.get_usage_percentage() == 0.0
        assert not tracker.needs_cleanup()

    def test_full_workflow(self):
        """Test a complete workflow with adds, removes, and cleanup check."""
        tracker = ContextTracker(context_window=1000)

        # Add tokens gradually
        tracker.add_tokens(300)  # 30%
        assert not tracker.needs_cleanup()

        tracker.add_tokens(400)  # 70% (300+400=700)
        assert not tracker.needs_cleanup()

        tracker.add_tokens(200)  # 90% (700+200=900)
        assert tracker.needs_cleanup()

        # Simulate cleanup by removing tokens
        tracker.remove_tokens(300)  # Back to 60% (900-300=600)
        assert not tracker.needs_cleanup()
        assert tracker.get_usage_percentage() == 60.0

    def test_edge_case_exact_context_window(self):
        """Test behavior when tokens exactly match context window."""
        tracker = ContextTracker(context_window=1000)
        tracker.add_tokens(1000)  # 100%
        assert tracker.get_usage_percentage() == 100.0
        assert tracker.needs_cleanup()

    def test_edge_case_exceeds_context_window(self):
        """Test behavior when tokens exceed context window."""
        tracker = ContextTracker(context_window=1000)
        tracker.add_tokens(1200)  # 120%
        assert tracker.get_usage_percentage() == 120.0
        assert tracker.needs_cleanup()
