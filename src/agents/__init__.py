"""Agent interface and implementations for the Agentic AI CLI Framework.

This module provides the core agent interface that defines the contract all
agent implementations must follow, along with a mock agent for testing.

To create a custom agent:
1. Inherit from AgentInterface
2. Implement the async process() method
3. Accept AgentConfig in the constructor
4. Ensure the agent is stateless (no conversation state in instance variables)

Example:
    ```python
    from src.agents import AgentInterface, MockAgent
    from src.common import AgentConfig, AgentContext, AgentResponse

    # Use the mock agent for testing
    mock_agent = MockAgent()
    response = await mock_agent.process(context)

    # Create a custom agent
    class MyAgent(AgentInterface):
        def __init__(self, config: AgentConfig):
            self.config = config

        async def process(self, context: AgentContext) -> AgentResponse:
            # Your implementation here
            return AgentResponse(output="...", metadata={})
    ```
"""

from src.agents.base import AgentInterface
from src.agents.mock_agent import MockAgent

__all__ = [
    "AgentInterface",
    "MockAgent",
]
