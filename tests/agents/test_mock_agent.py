"""Tests for MockAgent implementation."""

import pytest

from src.agents.mock_agent import MockAgent, estimate_tokens
from src.common.config import AgentConfig
from src.common.types import AgentContext, AgentResponse, Message


class TestEstimateTokens:
    """Test suite for the estimate_tokens utility function."""

    def test_estimate_tokens_empty_string(self):
        """Test token estimation for empty string."""
        assert estimate_tokens("") == 0

    def test_estimate_tokens_short_string(self):
        """Test token estimation for short strings."""
        # "Hi" (2 chars) should be ~1 token (2/4 = 0.5, ceil = 1)
        assert estimate_tokens("Hi") == 1

        # "Test" (4 chars) should be 1 token
        assert estimate_tokens("Test") == 1

    def test_estimate_tokens_medium_string(self):
        """Test token estimation for medium strings."""
        # "Hello world" (11 chars) should be ~3 tokens (11/4 = 2.75, ceil = 3)
        assert estimate_tokens("Hello world") == 3

        # "This is a test" (14 chars) should be ~4 tokens
        assert estimate_tokens("This is a test") == 4

    def test_estimate_tokens_long_string(self):
        """Test token estimation for long strings."""
        long_text = "This is a longer sentence with multiple words. " * 10
        # Should estimate based on ~4 chars per token
        estimated = estimate_tokens(long_text)
        expected = len(long_text) / 4
        assert estimated == pytest.approx(expected, rel=0.1)  # Within 10%

    def test_estimate_tokens_special_characters(self):
        """Test token estimation with special characters."""
        text = "Hello! How are you? I'm fine, thanks."
        estimated = estimate_tokens(text)
        assert estimated > 0
        assert estimated == (len(text) + 3) // 4  # Ceiling division


class TestMockAgent:
    """Test suite for the MockAgent class."""

    def test_mock_agent_creation_no_config(self):
        """Test creating MockAgent without config."""
        agent = MockAgent()
        assert agent.config is None
        assert agent.debug is False

    def test_mock_agent_creation_with_config(self):
        """Test creating MockAgent with config."""
        config = AgentConfig(
            system_prompt="Test prompt",
            model="test-model"
        )
        agent = MockAgent(config=config)
        assert agent.config == config

    def test_mock_agent_creation_with_debug(self):
        """Test creating MockAgent with debug enabled."""
        agent = MockAgent(debug=True)
        assert agent.debug is True

    @pytest.mark.asyncio
    async def test_process_simple_input(self):
        """Test processing simple input."""
        agent = MockAgent()
        context = AgentContext(
            input="Hello",
            session_id="test_session"
        )

        response = await agent.process(context)

        assert isinstance(response, AgentResponse)
        assert len(response.output) > 0
        assert isinstance(response.metadata, dict)

    @pytest.mark.asyncio
    async def test_process_greeting(self):
        """Test processing greeting input."""
        agent = MockAgent()
        context = AgentContext(
            input="Hello there!",
            session_id="test_session"
        )

        response = await agent.process(context)

        # Should recognize greeting and respond appropriately
        assert "hello" in response.output.lower() or "mock agent" in response.output.lower()

    @pytest.mark.asyncio
    async def test_process_help_request(self):
        """Test processing help request."""
        agent = MockAgent()
        context = AgentContext(
            input="How can you help me?",
            session_id="test_session"
        )

        response = await agent.process(context)

        # Should provide helpful response
        assert "mock agent" in response.output.lower() or "help" in response.output.lower()

    @pytest.mark.asyncio
    async def test_process_thanks(self):
        """Test processing thank you message."""
        agent = MockAgent()
        context = AgentContext(
            input="Thank you!",
            session_id="test_session"
        )

        response = await agent.process(context)

        # Should acknowledge thanks
        assert "welcome" in response.output.lower()

    @pytest.mark.asyncio
    async def test_process_farewell(self):
        """Test processing farewell message."""
        agent = MockAgent()
        context = AgentContext(
            input="Goodbye!",
            session_id="test_session"
        )

        response = await agent.process(context)

        # Should say goodbye
        assert "goodbye" in response.output.lower()

    @pytest.mark.asyncio
    async def test_process_with_conversation_history(self):
        """Test processing with conversation history."""
        agent = MockAgent()

        history = [
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello!"),
            Message(role="user", content="How are you?"),
        ]

        context = AgentContext(
            input="Tell me more",
            conversation_history=history,
            session_id="test_session"
        )

        response = await agent.process(context)

        # Should acknowledge conversation history
        assert "3 messages" in response.output or "exchanged" in response.output.lower()
        assert response.metadata["message_count"] == 3

    @pytest.mark.asyncio
    async def test_process_with_additional_context(self):
        """Test processing with additional context."""
        agent = MockAgent()

        context = AgentContext(
            input="Analyze this",
            session_id="test_session",
            additional_context={
                "data": {"rows": 100, "columns": 5},
                "file": "test.csv"
            }
        )

        response = await agent.process(context)

        assert response.metadata["has_additional_context"] is True
        assert "additional_context_keys" in response.metadata
        assert "data" in response.metadata["additional_context_keys"]
        assert "file" in response.metadata["additional_context_keys"]

    @pytest.mark.asyncio
    async def test_process_metadata_structure(self):
        """Test that response metadata has expected structure."""
        agent = MockAgent()

        context = AgentContext(
            input="Test input",
            conversation_history=[
                Message(role="user", content="Previous message")
            ],
            session_id="test_session_123"
        )

        response = await agent.process(context)

        # Check metadata contains expected keys
        assert "message_count" in response.metadata
        assert "session_id" in response.metadata
        assert "mock_version" in response.metadata
        assert "has_additional_context" in response.metadata
        assert "input_keywords" in response.metadata
        assert "input_tokens" in response.metadata
        assert "output_tokens" in response.metadata
        assert "total_tokens" in response.metadata

        # Check values
        assert response.metadata["message_count"] == 1
        assert response.metadata["session_id"] == "test_session_123"
        assert response.metadata["has_additional_context"] is False
        assert response.metadata["mock_version"] == "1.0"

    @pytest.mark.asyncio
    async def test_process_token_estimation(self):
        """Test that token counts are estimated correctly."""
        agent = MockAgent()

        context = AgentContext(
            input="This is a test input message",
            session_id="test_session"
        )

        response = await agent.process(context)

        # Check token counts are present and reasonable
        assert response.metadata["input_tokens"] > 0
        assert response.metadata["output_tokens"] > 0
        assert response.metadata["total_tokens"] == (
            response.metadata["input_tokens"] + response.metadata["output_tokens"]
        )

    @pytest.mark.asyncio
    async def test_process_keyword_detection(self):
        """Test keyword detection in inputs."""
        agent = MockAgent()

        test_cases = [
            ("Hello!", ["greeting"]),
            ("Hi there, how can you help?", ["greeting", "help"]),
            ("Thanks for your help!", ["thanks", "help"]),
            ("Goodbye and thank you", ["farewell", "thanks"]),
        ]

        for input_text, expected_keywords in test_cases:
            context = AgentContext(input=input_text, session_id="test")
            response = await agent.process(context)

            detected = response.metadata["input_keywords"]
            for keyword in expected_keywords:
                assert keyword in detected, f"Expected '{keyword}' in {detected} for input '{input_text}'"

    @pytest.mark.asyncio
    async def test_process_empty_history(self):
        """Test processing with empty conversation history."""
        agent = MockAgent()

        context = AgentContext(
            input="First message",
            conversation_history=[],
            session_id="test_session"
        )

        response = await agent.process(context)

        assert response.metadata["message_count"] == 0
        # Response should not mention previous messages
        assert "0 messages" in response.output or "exchanged" not in response.output.lower()

    @pytest.mark.asyncio
    async def test_process_long_input(self):
        """Test processing with very long input."""
        agent = MockAgent()

        long_input = "This is a very long message. " * 100

        context = AgentContext(
            input=long_input,
            session_id="test_session"
        )

        response = await agent.process(context)

        # Should handle long input without errors
        assert len(response.output) > 0
        assert response.metadata["input_tokens"] > 0

    @pytest.mark.asyncio
    async def test_process_multiple_calls_stateless(self):
        """Test that agent is stateless across multiple calls."""
        agent = MockAgent()

        # First call
        context1 = AgentContext(
            input="First call",
            conversation_history=[],
            session_id="session_1"
        )
        response1 = await agent.process(context1)

        # Second call with different context
        context2 = AgentContext(
            input="Second call",
            conversation_history=[
                Message(role="user", content="Previous"),
                Message(role="assistant", content="Response")
            ],
            session_id="session_2"
        )
        response2 = await agent.process(context2)

        # Responses should be based only on their respective contexts
        assert response1.metadata["message_count"] == 0
        assert response2.metadata["message_count"] == 2
        assert response1.metadata["session_id"] == "session_1"
        assert response2.metadata["session_id"] == "session_2"

    @pytest.mark.asyncio
    async def test_process_with_config(self):
        """Test that agent accepts config even though it doesn't use it."""
        config = AgentConfig(
            system_prompt="You are a mock agent",
            model="mock-model",
            temperature=0.5
        )

        agent = MockAgent(config=config)

        context = AgentContext(
            input="Test with config",
            session_id="test_session"
        )

        response = await agent.process(context)

        # Should work normally even with config
        assert isinstance(response, AgentResponse)
        assert len(response.output) > 0

    @pytest.mark.asyncio
    async def test_process_case_insensitive_keywords(self):
        """Test that keyword detection is case-insensitive."""
        agent = MockAgent()

        test_inputs = [
            "HELLO",
            "Hello",
            "hello",
            "HeLLo"
        ]

        for input_text in test_inputs:
            context = AgentContext(input=input_text, session_id="test")
            response = await agent.process(context)

            # All should detect greeting keyword
            assert "greeting" in response.metadata["input_keywords"]

    @pytest.mark.asyncio
    async def test_process_combined_keywords(self):
        """Test inputs with multiple keyword types."""
        agent = MockAgent()

        context = AgentContext(
            input="Hello! How can you help? Thanks!",
            session_id="test"
        )

        response = await agent.process(context)

        keywords = response.metadata["input_keywords"]
        # Should detect all three types
        assert "greeting" in keywords
        assert "help" in keywords
        assert "thanks" in keywords

    @pytest.mark.asyncio
    async def test_process_no_keywords(self):
        """Test input with no special keywords."""
        agent = MockAgent()

        context = AgentContext(
            input="What is the capital of France?",
            session_id="test"
        )

        response = await agent.process(context)

        # May detect "what" as help, or have empty keywords
        assert "input_keywords" in response.metadata
        # Should still generate a response
        assert len(response.output) > 0

    @pytest.mark.asyncio
    async def test_response_references_input(self):
        """Test that default responses reference the input."""
        agent = MockAgent()

        context = AgentContext(
            input="This is a unique test message xyz123",
            session_id="test"
        )

        response = await agent.process(context)

        # For non-keyword inputs, should reference the input
        # (may be truncated to 50 chars in the response)
        assert "received" in response.output.lower() or "mock agent" in response.output.lower()


class TestMockAgentDebugMode:
    """Tests for MockAgent debug mode (should not break functionality)."""

    @pytest.mark.asyncio
    async def test_debug_mode_enabled(self, capsys):
        """Test that debug mode prints information (output captured)."""
        agent = MockAgent(debug=True)

        context = AgentContext(
            input="Test debug",
            session_id="debug_session"
        )

        response = await agent.process(context)

        # Should still return valid response
        assert isinstance(response, AgentResponse)

        # Note: In actual test runs with pytest, capsys can capture print output
        # For this test, we just verify it doesn't break functionality

    @pytest.mark.asyncio
    async def test_debug_mode_disabled(self):
        """Test normal operation with debug disabled."""
        agent = MockAgent(debug=False)

        context = AgentContext(
            input="Test no debug",
            session_id="normal_session"
        )

        response = await agent.process(context)

        assert isinstance(response, AgentResponse)
        assert len(response.output) > 0
