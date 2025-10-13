# Getting Started with Agentic AI CLI Framework

## What is this?

The Agentic AI CLI Framework is a generic, pluggable foundation for building and testing conversational AI agents. It provides a complete CLI interface with session management, message history, and conversation export capabilities - while remaining completely **agent-agnostic**.

This framework handles the boring infrastructure (CLI commands, session state, token tracking, message history) so you can focus on building great agents. Your agents can use any LLM provider (OpenAI, Anthropic, etc.) and any agentic framework (LangGraph, CrewAI, Agno) or none at all - it's completely up to you.

## Key Features

- **Pluggable Agent Interface**: Implement one method, get a full CLI
- **Session Management**: Automatic conversation history and context tracking
- **Smart Memory Management**: Automatic context cleanup at 90% token threshold
- **Portable Agents**: Your agents work in CLI, web apps, notebooks, batch scripts - anywhere
- **Export Functionality**: Save conversations to text files
- **Testing Ready**: Includes mock agent for testing

## Quick Example

Here's a minimal agent implementation:

```python
from src.agents.base import AgentInterface
from src.common.types import AgentContext, AgentResponse
from src.common.config import AgentConfig

class MyAgent(AgentInterface):
    def __init__(self, config: AgentConfig):
        self.config = config
        # Initialize your LLM client here

    async def process(self, context: AgentContext) -> AgentResponse:
        # Access context.input, context.conversation_history, etc.
        # Call your LLM, run your logic
        return AgentResponse(
            output="Your agent's response",
            metadata={"tokens": 123, "model": "gpt-4"}
        )
```

That's it! The framework handles everything else.

## Documentation Guide

Depending on what you're trying to do, read the appropriate docs:

### Just starting out?
→ **You're here!** Continue reading below for installation and first steps.

### Want to understand the architecture?
→ **[architecture.md](./architecture.md)** - Core design, components, data flow, key decisions

### Building or extending agents?
→ **[developer-guide.md](./developer-guide.md)** - How to implement agents, use them outside CLI, testing patterns

### Deploying or running in production?
→ **[operations.md](./operations.md)** - Security, performance, memory management

### Planning features or contributions?
→ **[roadmap.md](./roadmap.md)** - Future enhancements and evolution plans

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd agentic-ai-basic-cli

# Install dependencies (using uv)
uv sync

# Copy environment template
cp .env.example .env

# Add your API keys to .env
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

## Running the CLI

```bash
# Start a chat session with the mock agent (for testing)
uv run python -m src.cli.main

# Available commands in the CLI:
# - Type your message and press Enter to chat
# - /help - Show available commands
# - /export - Export conversation to a text file
# - /clear - Clear conversation history
# - /exit or /quit - Exit the session
```

## Next Steps

1. **Understand the Architecture**: Read [architecture.md](./architecture.md) to understand how components fit together
2. **Build Your First Agent**: Follow [developer-guide.md](./developer-guide.md) to implement a custom agent
3. **Explore Examples**: Check the `examples/` folder for reference implementations
4. **Run Tests**: Use `uv run pytest` to ensure everything works

## Project Philosophy

- **Generic over Specific**: No domain-specific code in the framework
- **Composition over Configuration**: Inject agents, don't configure them
- **Interface over Implementation**: Define contracts, let users implement
- **Portability over Features**: Agents work anywhere, not just in CLI
- **Simplicity over Completeness**: Provide essentials, let users extend

This framework is a **foundation**, not a complete solution. It handles the infrastructure so you can focus on building intelligent agents.
