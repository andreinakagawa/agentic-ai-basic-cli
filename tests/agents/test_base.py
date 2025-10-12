"""Tests for AgentInterface base class."""

import pytest

from src.agents.base import AgentInterface
from src.common.config import AgentConfig
from src.common.types import AgentContext, AgentResponse


class TestAgentInterface:
    """Test suite for the AgentInterface abstract class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that AgentInterface cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            AgentInterface()  # type: ignore

        # The error message should indicate it's an abstract class
        error_msg = str(exc_info.value)
        assert "abstract" in error_msg.lower() or "instantiat" in error_msg.lower()

    def test_must_implement_process_method(self):
        """Test that subclasses must implement the process method."""

        class IncompleteAgent(AgentInterface):
            """An agent that doesn't implement process."""
            pass

        with pytest.raises(TypeError) as exc_info:
            IncompleteAgent()  # type: ignore

        error_msg = str(exc_info.value)
        assert "abstract" in error_msg.lower() or "process" in error_msg.lower()

    def test_can_implement_concrete_agent(self):
        """Test that we can create a concrete agent by implementing process."""

        class ConcreteAgent(AgentInterface):
            """A minimal concrete agent implementation."""

            def __init__(self, config: AgentConfig | None = None):
                self.config = config

            async def process(self, context: AgentContext) -> AgentResponse:
                """Simple implementation that echoes input."""
                return AgentResponse(
                    output=f"Echo: {context.input}",
                    metadata={"test": True}
                )

        # Should not raise any errors
        agent = ConcreteAgent()
        assert isinstance(agent, AgentInterface)

    def test_concrete_agent_process_method(self):
        """Test that a concrete agent's process method works correctly."""

        class SimpleAgent(AgentInterface):
            """A simple test agent."""

            async def process(self, context: AgentContext) -> AgentResponse:
                return AgentResponse(
                    output="Simple response",
                    metadata={"session": context.session_id}
                )

        agent = SimpleAgent()
        context = AgentContext(
            input="Test input",
            session_id="test_session"
        )

        # Test is async
        import asyncio
        response = asyncio.run(agent.process(context))

        assert isinstance(response, AgentResponse)
        assert response.output == "Simple response"
        assert response.metadata["session"] == "test_session"

    def test_agent_with_config(self):
        """Test creating an agent with configuration."""

        class ConfigurableAgent(AgentInterface):
            """An agent that uses configuration."""

            def __init__(self, config: AgentConfig):
                self.config = config

            async def process(self, context: AgentContext) -> AgentResponse:
                prompt = self.config.system_prompt or "default"
                return AgentResponse(
                    output=f"Using prompt: {prompt}",
                    metadata={"model": self.config.model}
                )

        config = AgentConfig(
            system_prompt="Custom prompt",
            model="test-model"
        )
        agent = ConfigurableAgent(config)

        context = AgentContext(input="test", session_id="session_1")

        import asyncio
        response = asyncio.run(agent.process(context))

        assert "Custom prompt" in response.output
        assert response.metadata["model"] == "test-model"

    def test_agent_stateless_design(self):
        """Test that agents should be stateless (context passed each time)."""

        class StatelessAgent(AgentInterface):
            """An agent that demonstrates stateless design."""

            async def process(self, context: AgentContext) -> AgentResponse:
                # Agent should not store conversation state
                # It receives everything it needs via context
                message_count = len(context.conversation_history)
                return AgentResponse(
                    output=f"Received {message_count} previous messages",
                    metadata={"input": context.input}
                )

        agent = StatelessAgent()

        # First call
        context1 = AgentContext(
            input="First",
            conversation_history=[],
            session_id="session_1"
        )

        import asyncio
        response1 = asyncio.run(agent.process(context1))
        assert "0 previous messages" in response1.output

        # Second call with history - agent doesn't maintain state
        from src.common.types import Message
        context2 = AgentContext(
            input="Second",
            conversation_history=[
                Message(role="user", content="First"),
                Message(role="assistant", content="Response")
            ],
            session_id="session_1"
        )

        response2 = asyncio.run(agent.process(context2))
        assert "2 previous messages" in response2.output

    def test_agent_with_additional_context(self):
        """Test agent processing with additional context."""

        class ContextAwareAgent(AgentInterface):
            """An agent that uses additional context."""

            async def process(self, context: AgentContext) -> AgentResponse:
                additional = context.additional_context or {}

                return AgentResponse(
                    output="Processed with context",
                    metadata={"received_keys": list(additional.keys())}
                )

        agent = ContextAwareAgent()

        context = AgentContext(
            input="test",
            session_id="session_1",
            additional_context={
                "metadata": {"version": "1.0"},
                "data": [1, 2, 3]
            }
        )

        import asyncio
        response = asyncio.run(agent.process(context))

        assert "metadata" in response.metadata["received_keys"]
        assert "data" in response.metadata["received_keys"]

    def test_multiple_agent_implementations(self):
        """Test that multiple agents can implement the interface."""

        class AgentA(AgentInterface):
            async def process(self, context: AgentContext) -> AgentResponse:
                return AgentResponse(output="Agent A response", metadata={})

        class AgentB(AgentInterface):
            async def process(self, context: AgentContext) -> AgentResponse:
                return AgentResponse(output="Agent B response", metadata={})

        agent_a = AgentA()
        agent_b = AgentB()

        assert isinstance(agent_a, AgentInterface)
        assert isinstance(agent_b, AgentInterface)

        context = AgentContext(input="test", session_id="session_1")

        import asyncio
        response_a = asyncio.run(agent_a.process(context))
        response_b = asyncio.run(agent_b.process(context))

        assert response_a.output == "Agent A response"
        assert response_b.output == "Agent B response"

    def test_agent_type_checking(self):
        """Test that we can use isinstance to check for AgentInterface."""

        class MyAgent(AgentInterface):
            async def process(self, context: AgentContext) -> AgentResponse:
                return AgentResponse(output="test", metadata={})

        agent = MyAgent()

        # Should be instance of AgentInterface
        assert isinstance(agent, AgentInterface)

        # Should not be instance of a concrete string or other type
        assert not isinstance("not an agent", AgentInterface)
        assert not isinstance(123, AgentInterface)


class TestAgentInterfaceContract:
    """Tests for the AgentInterface contract and expectations."""

    def test_process_method_signature(self):
        """Test that process method has correct signature."""

        class TestAgent(AgentInterface):
            async def process(self, context: AgentContext) -> AgentResponse:
                return AgentResponse(output="test", metadata={})

        agent = TestAgent()

        # Check that the method exists and is callable
        assert hasattr(agent, "process")
        assert callable(agent.process)

        # Check that it's a coroutine (async method)
        import inspect
        assert inspect.iscoroutinefunction(agent.process)

    def test_agent_should_accept_agent_context(self):
        """Test that agent process method accepts AgentContext."""

        class TestAgent(AgentInterface):
            async def process(self, context: AgentContext) -> AgentResponse:
                # Should be able to access all AgentContext fields
                assert hasattr(context, "input")
                assert hasattr(context, "conversation_history")
                assert hasattr(context, "session_id")
                assert hasattr(context, "additional_context")

                return AgentResponse(output="validated", metadata={})

        agent = TestAgent()
        context = AgentContext(input="test", session_id="session_1")

        import asyncio
        response = asyncio.run(agent.process(context))

        assert response.output == "validated"

    def test_agent_should_return_agent_response(self):
        """Test that agent process method returns AgentResponse."""

        class TestAgent(AgentInterface):
            async def process(self, context: AgentContext) -> AgentResponse:
                return AgentResponse(
                    output="response text",
                    metadata={"key": "value"}
                )

        agent = TestAgent()
        context = AgentContext(input="test", session_id="session_1")

        import asyncio
        response = asyncio.run(agent.process(context))

        # Should be an AgentResponse instance
        assert isinstance(response, AgentResponse)
        assert hasattr(response, "output")
        assert hasattr(response, "metadata")
        assert response.output == "response text"
        assert response.metadata["key"] == "value"
