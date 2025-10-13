# Agentic AI CLI Framework

A generic, pluggable framework for building and testing conversational AI agents. This framework provides a complete CLI interface with session management, message history, and conversation export - all while remaining completely agent-agnostic.

## What is This?

This framework handles the boring infrastructure (CLI commands, session state, token tracking, message history) so you can focus on building great agents. Your agents can use any LLM provider (OpenAI, Anthropic, etc.) and any agentic framework (LangGraph, CrewAI, Agno) or none at all - it's completely up to you.

## Key Features

- **Pluggable Agent Interface**: Implement one method, get a full CLI
- **Session Management**: Automatic conversation history and context tracking
- **Smart Memory Management**: Automatic context cleanup at 90% token threshold
- **Portable Agents**: Your agents work in CLI, web apps, notebooks, batch scripts - anywhere
- **Export Functionality**: Save conversations to text files
- **Testing Ready**: Includes mock agent and comprehensive test suite

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd agentic-ai-basic-cli

# Install dependencies using uv
uv sync

# Copy environment template
cp .env.example .env

# Add your API keys to .env
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

### Run the CLI

```bash
uv run python -m src.cli.main
```

### Available Commands

- Type your message and press Enter to chat
- `/help` - Show available commands
- `/export` - Export conversation to a text file
- `/clear` - Clear conversation history
- `/session` - Show session information
- `/exit` or `/quit` - Exit the session

## Building Your First Agent

Create a new agent by implementing the `AgentInterface`:

```python
from src.agents.base import AgentInterface
from src.common.types import AgentContext, AgentResponse

class MyAgent(AgentInterface):
    def __init__(self, api_key: str = None, model: str = None):
        # Agent handles its own configuration
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("DEFAULT_MODEL", "gpt-4")
        # Initialize your LLM client

    async def process(self, context: AgentContext) -> AgentResponse:
        # Your agent logic here
        # Access context.input, context.conversation_history, etc.
        return AgentResponse(
            output="Your agent's response",
            metadata={"tokens": 123}
        )
```

Then use it in the CLI:

```python
# In src/cli/main.py
from src.agents.my_agent import MyAgent

agent = MyAgent()  # Agent loads its own config
session_manager = SessionManager(agent=agent)
```

## Project Structure

```
agentic-ai-cli/
├── src/
│   ├── agents/          # Agent interface and implementations
│   ├── cli/             # CLI interface (framework provided)
│   ├── memory/          # Context tracking and cleanup
│   └── common/          # Shared types and utilities
├── tests/               # Comprehensive test suite
├── examples/            # Example agent implementations
└── docs/                # Documentation
```

## Documentation

- **[Getting Started](docs/getting-started.md)** - Quick start guide and overview
- **[Architecture](docs/architecture.md)** - Core design and key decisions

## Architecture Highlights

### Agent Portability

Agents are completely portable - they work anywhere, not just in the CLI.

### Smart Context Management

The framework automatically manages context windows:
- Tracks token usage as percentage of context window
- Triggers cleanup at 90% threshold
- Reduces to 60% usage after cleanup
- Preserves system messages and recent conversation
- Visual feedback with color-coded indicators

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/memory/test_context_tracker.py -v
```

## Design Philosophy

1. **Generic over Specific**: No domain-specific code
2. **Composition over Configuration**: Inject agents, don't configure them
3. **Interface over Implementation**: Define contracts, let users implement
4. **Portability over Features**: Agents work anywhere, not just in CLI
5. **Simplicity over Completeness**: Provide essentials, let users extend

## License

MIT License

## Support

- Check [getting-started.md](docs/getting-started.md) for quick help
- Review [architecture.md](docs/architecture.md) for design questions
