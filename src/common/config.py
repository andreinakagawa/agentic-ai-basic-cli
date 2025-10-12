"""Configuration models for agents."""

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for agent instances.

    This model encapsulates all configuration needed by an agent, including
    system prompts, model settings, API credentials, and behavior parameters.

    All configuration is passed to agents via constructor injection, ensuring
    agents remain portable and testable without relying on environment variables.

    Attributes:
        system_prompt: The agent's system prompt/instructions
        model: Model name (e.g., "gpt-4", "claude-3-5-sonnet-20241022")
        temperature: Model temperature for response randomness (0.0-1.0)
        max_tokens: Maximum tokens for responses
        api_key: API key for LLM provider (optional, can be loaded from env by caller)
        timeout: Timeout in seconds for API calls
        retry_attempts: Number of retry attempts on failure

    Example:
        ```python
        config = AgentConfig(
            system_prompt="You are an AI data analyst...",
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        agent = DataAnalystAgent(config)
        ```
    """

    system_prompt: str | None = Field(
        default=None, description="System prompt for the agent (optional)"
    )
    model: str | None = Field(default=None, description="Model name to use (optional)")
    temperature: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Model temperature"
    )
    max_tokens: int | None = Field(default=None, description="Maximum response tokens (optional)")
    api_key: str | None = Field(default=None, description="API key for LLM provider")
    timeout: int = Field(default=30, gt=0, description="API call timeout in seconds")
    retry_attempts: int = Field(
        default=3, ge=0, description="Number of retry attempts on failure"
    )
