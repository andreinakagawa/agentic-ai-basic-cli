"""Base agent interface for the Agentic AI CLI Framework.

This module defines the core AgentInterface that all agent implementations must follow.
The interface is designed to be:
- Generic and domain-agnostic (works for any agent type)
- Stateless (agents don't maintain conversation state)
- Portable (can be used in any context: CLI, web service, notebooks, etc.)
- Framework-agnostic (no assumptions about underlying LLM framework)
"""

from abc import ABC, abstractmethod

from src.common.types import AgentContext, AgentResponse


class AgentInterface(ABC):
    """Abstract base class for all agent implementations.

    This interface defines the contract that all agents must follow. It is intentionally
    minimal and generic to support a wide variety of agent types beyond just data analysis.

    Design Principles:
    - **Stateless**: Agents do not maintain conversation history or session state.
      All context is passed in via AgentContext on each call.
    - **Generic**: Uses generic terms (input/output) rather than domain-specific
      terminology to support any agent type (data analyst, code reviewer, etc.).
    - **Portable**: Can be used in any environment (CLI, web service, Jupyter, etc.)
      without dependencies on specific infrastructure.
    - **Framework-Agnostic**: No assumptions about underlying LLM framework
      (Agno, LangGraph, or custom implementations).

    Configuration:
    - Agents receive all configuration via constructor (dependency injection)
    - AgentConfig includes system_prompt, model settings, API keys, etc.
    - No environment variable reading in agent code (handled by caller)

    Usage Example:
        ```python
        from src.agents.data_analyst import DataAnalystAgent
        from src.common.config import AgentConfig
        from src.common.types import AgentContext, Message

        # Configure agent
        config = AgentConfig(
            system_prompt="You are an AI data analyst...",
            model="gpt-4",
            api_key="...",
            temperature=0.7
        )

        # Create agent instance
        agent = DataAnalystAgent(config)

        # Use agent
        context = AgentContext(
            input="What are the sales trends?",
            conversation_history=[
                Message(role="user", content="Hi"),
                Message(role="assistant", content="Hello! How can I help?")
            ],
            session_id="session_123",
            additional_context={"data_summary": {...}}
        )

        response = await agent.process(context)
        print(response.output)
        print(response.metadata)  # tokens used, model info, etc.
        ```

    Implementing a New Agent:
        1. Inherit from AgentInterface
        2. Implement the process() method
        3. Accept AgentConfig in constructor
        4. Ensure stateless design (no instance variables for conversation state)
        5. Use dependency injection for all external dependencies

        Example:
        ```python
        class CustomAgent(AgentInterface):
            def __init__(self, config: AgentConfig):
                self.config = config
                # Initialize your LLM client, framework, etc.

            async def process(self, context: AgentContext) -> AgentResponse:
                # Process the input using context
                # Return structured response
                return AgentResponse(
                    output="...",
                    metadata={"tokens": 100, "model": "gpt-4"}
                )
        ```
    """

    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResponse:
        """Process an input with full context and return a response.

        This is the core method all agents must implement. It receives complete context
        including the current input, conversation history, and any additional data,
        then returns a structured response.

        The agent should:
        - Process the input based on its configuration (system prompt, model settings)
        - Consider conversation history for coherent responses
        - Use additional_context for domain-specific data (e.g., CSV metadata)
        - Return output along with useful metadata

        The agent should NOT:
        - Store conversation state in instance variables
        - Modify the input context
        - Make assumptions about the caller's infrastructure
        - Import from CLI or session management modules

        Args:
            context: Complete context for processing including:
                - input: The user's current input/query/request
                - conversation_history: Previous messages in the conversation
                - session_id: Identifier for the current session
                - additional_context: Optional domain-specific data (dict)

        Returns:
            AgentResponse containing:
                - output: The agent's response/result
                - metadata: Additional information (tokens used, model info, etc.)

        Raises:
            Exception: Implementation-specific exceptions (API errors, timeouts, etc.)
                      Callers should handle exceptions appropriately.

        Example:
            ```python
            context = AgentContext(
                input="Analyze the sales data",
                conversation_history=[...],
                session_id="session_123",
                additional_context={"data_summary": {...}}
            )

            response = await agent.process(context)
            # response.output: "Based on the data, I see..."
            # response.metadata: {"tokens": 150, "model": "gpt-4", ...}
            ```
        """
        pass
