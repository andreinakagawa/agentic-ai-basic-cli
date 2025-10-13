# Developer Guide

This guide provides practical instructions for building agents, extending the framework, and using agents in different contexts.

**Prerequisites**: Read [architecture.md](./architecture.md) first to understand the core design.

## Table of Contents

- [Building Your First Agent](#building-your-first-agent)
- [Using Agents Outside the CLI](#using-agents-outside-the-cli)
- [Configuration Patterns](#configuration-patterns)
- [Testing Your Agent](#testing-your-agent)
- [Extending the CLI](#extending-the-cli)
- [Best Practices](#best-practices)

---

## Building Your First Agent

### Step 1: Create Your Agent Class

Create a new file in `src/agents/` or in your own package:

```python
from src.agents.base import AgentInterface
from src.common.types import AgentContext, AgentResponse, AgentConfig
import os

class MyCustomAgent(AgentInterface):
    def __init__(self, api_key: str = None, model: str = None, temperature: float = 0.7):
        # Agent handles its own configuration
        # Use AgentConfig convenience class (optional)
        self.config = AgentConfig(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            model=model or os.getenv("DEFAULT_MODEL", "gpt-4"),
            temperature=temperature
        )

        # Initialize your LLM client
        # Example: self.client = OpenAI(api_key=self.config.api_key)

    async def process(self, context: AgentContext) -> AgentResponse:
        # Access the current user input
        user_input = context.input

        # Access conversation history if needed
        history = context.conversation_history

        # Your agent logic here
        # Call your LLM, run your framework, process data, etc.

        # Example:
        # response = await self.client.chat.completions.create(...)

        # Return a response with metadata
        return AgentResponse(
            output="Your agent's response here",
            metadata={
                "model": self.config.model,
                "tokens": 123,  # Optional: for context tracking
                "prompt_tokens": 100,
                "completion_tokens": 23
            }
        )
```

### Step 2: Integrate with CLI

Update `src/cli/main.py` to use your agent:

```python
from src.agents.my_custom_agent import MyCustomAgent

# In the main() function
agent = MyCustomAgent()  # Agent handles its own config loading
session_manager = SessionManager(agent=agent)
```

That's it! The agent loads its own configuration from environment variables.

### Step 3: Run and Test

```bash
uv run python -m src.cli.main
```

---

## Using Agents Outside the CLI

One of the key features of this framework is that agents are **completely portable**. They work in any context, not just the CLI.

### Example: FastAPI Web Service

```python
from fastapi import FastAPI
from src.agents.my_custom_agent import MyCustomAgent
from src.common.types import AgentContext, Message

app = FastAPI()

# Initialize agent once at startup
# Pass explicit config or let it use defaults/env vars
agent = MyCustomAgent(api_key="your-api-key", model="gpt-4")

# In-memory session storage (replace with Redis in production)
sessions = {}

@app.post("/chat")
async def chat(message: str, session_id: str):
    # Load conversation history
    if session_id not in sessions:
        sessions[session_id] = []

    history = sessions[session_id]

    # Create context
    context = AgentContext(
        input=message,
        conversation_history=history,
        session_id=session_id
    )

    # Process with agent
    response = await agent.process(context)

    # Update history
    history.append(Message(role="user", content=message, tokens=0))
    history.append(Message(role="assistant", content=response.output,
                          tokens=response.metadata.get("tokens", 0)))

    return {"response": response.output, "metadata": response.metadata}
```

### Example: Jupyter Notebook

```python
from src.agents.my_custom_agent import MyCustomAgent
from src.common.types import AgentContext

# Initialize agent with explicit config
agent = MyCustomAgent(
    api_key="your-key-here",
    model="gpt-4",
    temperature=0.7
)

# Single interaction
context = AgentContext(
    input="Analyze this dataset",
    conversation_history=[],
    session_id="notebook_session"
)

response = await agent.process(context)
print(response.output)
```

### Example: Batch Processing Script

```python
import asyncio
from src.agents.my_custom_agent import MyCustomAgent
from src.common.types import AgentContext

async def process_batch(queries: list[str]):
    # Agent loads config from environment or uses defaults
    agent = MyCustomAgent()

    results = []
    for i, query in enumerate(queries):
        context = AgentContext(
            input=query,
            conversation_history=[],
            session_id=f"batch_{i}"
        )
        response = await agent.process(context)
        results.append(response.output)

    return results

# Run
queries = ["Query 1", "Query 2", "Query 3"]
results = asyncio.run(process_batch(queries))
```

---

## Configuration Patterns

### Pattern 1: Environment Variables with Defaults

```python
class MyAgent(AgentInterface):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("DEFAULT_MODEL", "gpt-4")

        if not self.api_key:
            raise ValueError("API key must be provided or set in OPENAI_API_KEY")
```

**Usage:**
```python
# Uses env vars
agent = MyAgent()

# Explicit config
agent = MyAgent(api_key="sk-...", model="gpt-4-turbo")
```

### Pattern 2: Using AgentConfig Convenience Class

```python
from src.common.types import AgentConfig

class MyAgent(AgentInterface):
    def __init__(self, **kwargs):
        # Use AgentConfig for validation and defaults
        self.config = AgentConfig(
            api_key=kwargs.get("api_key") or os.getenv("OPENAI_API_KEY"),
            model=kwargs.get("model", "gpt-4"),
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096)
        )
```

### Pattern 3: Config File Loading

```python
import json

class MyAgent(AgentInterface):
    def __init__(self, config_path: str = None):
        if config_path:
            with open(config_path) as f:
                config_data = json.load(f)
        else:
            # Fallback to env vars
            config_data = {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("DEFAULT_MODEL", "gpt-4")
            }

        self.config = AgentConfig(**config_data)
```

### Pattern 4: Custom Config Class

```python
from pydantic import BaseModel

class MyAgentConfig(BaseModel):
    api_key: str
    model: str
    custom_setting: bool = True
    another_setting: int = 42

class MyAgent(AgentInterface):
    def __init__(self, **kwargs):
        # Use your own config class
        self.config = MyAgentConfig(**kwargs)
```

---

## Testing Your Agent

### Unit Testing

Test your agent logic in isolation:

```python
import pytest
from src.agents.my_custom_agent import MyCustomAgent
from src.common.types import AgentContext, Message

@pytest.mark.asyncio
async def test_agent_responds_to_input():
    # Initialize agent with test config
    agent = MyCustomAgent(
        api_key="test-key",
        model="gpt-4"
    )

    context = AgentContext(
        input="Hello",
        conversation_history=[],
        session_id="test"
    )

    response = await agent.process(context)

    assert response.output is not None
    assert len(response.output) > 0
    assert "tokens" in response.metadata
```

### Integration Testing with CLI

Use the provided `MockAgent` to test CLI integration:

```python
from src.agents.mock_agent import MockAgent
from src.cli.session_manager import SessionManager

def test_cli_integration():
    agent = MockAgent()
    session_manager = SessionManager(agent=agent)

    # Test session flow
    session_manager.start_session()
    # ... test commands, history, export, etc.
```

### Mocking LLM Calls

When testing, mock external API calls:

```python
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_agent_with_mock_llm():
    agent = MyCustomAgent(api_key="test-key")

    # Mock the LLM client
    mock_client = Mock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=Mock(
            choices=[Mock(message=Mock(content="Mocked response"))],
            usage=Mock(total_tokens=100)
        )
    )

    # Inject mock into agent
    agent.client = mock_client

    # Test
    context = AgentContext(input="test", conversation_history=[], session_id="test")
    response = await agent.process(context)

    assert response.output == "Mocked response"
    mock_client.chat.completions.create.assert_called_once()
```

---

## Extending the CLI

The CLI is designed to be stable, but you can extend it if needed.

### Adding New Commands

1. **Update the parser** in `src/cli/parser.py`:

```python
class CommandType(Enum):
    CHAT = "chat"
    EXIT = "exit"
    EXPORT = "export"
    CLEAR = "clear"
    HELP = "help"
    STATS = "stats"  # New command example
```

2. **Handle the command** in `src/cli/session_manager.py`:

```python
async def handle_input(self, user_input: str) -> str:
    command = parse_input(user_input)

    if command.type == CommandType.STATS:
        return self._handle_stats()
    # ... existing handlers

def _handle_stats(self) -> str:
    total_messages = len(self.session.messages)
    total_tokens = self.context_tracker.current_tokens
    return f"Messages: {total_messages}, Tokens: {total_tokens}"
```

### Customizing Output Formatting

Edit `src/cli/formatters.py` to change how responses are displayed:

```python
def format_response(response: str, metadata: dict) -> str:
    # Add custom formatting
    model = metadata.get("model", "unknown")
    tokens = metadata.get("tokens", 0)
    return f"\n{response}\n\n[{model} | {tokens} tokens]"
```

### Adding Export Formats

Edit `src/cli/exporter.py` to add new export formats:

```python
def export_to_json(messages: list[Message], filepath: str):
    data = [msg.dict() for msg in messages]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def export_to_markdown(messages: list[Message], filepath: str):
    with open(filepath, 'w') as f:
        for msg in messages:
            f.write(f"## {msg.role.title()}\n\n")
            f.write(f"{msg.content}\n\n")
```

---

## Best Practices

### ✅ DO:

- **Accept optional parameters** in agent constructor with sensible defaults
- **Load environment variables** inside your agent constructor
- **Use AgentConfig** as a convenience if it fits your needs (optional)
- **Return token counts** in metadata for automatic context management
- **Keep agents stateless** - don't store conversation history in instance variables
- **Handle errors gracefully** - return error messages as responses, don't crash
- **Document your agent's** configuration options and metadata fields
- **Make agents async-compatible** for better performance

### ❌ DON'T:

- **Don't import from `src.cli`** in agent code (breaks portability)
- **Don't use global state** or singletons
- **Don't store conversation state** in agent instance variables
- **Don't assume CLI context** - agents should work anywhere
- **Don't hardcode API keys** - always use env vars or injected config

### Configuration Guidelines

```python
# ✅ Good: Agent loads its own config
class MyAgent(AgentInterface):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("DEFAULT_MODEL", "gpt-4")

# ✅ Good: CLI doesn't know about config
agent = MyAgent()  # Uses env vars
agent = MyAgent(api_key="...", model="gpt-4")  # Explicit config

# ❌ Bad: CLI builds config (coupling)
config = AgentConfig(api_key=os.getenv("..."), ...)
agent = MyAgent(config)  # Agent depends on CLI's config structure
```

### Error Handling

```python
async def process(self, context: AgentContext) -> AgentResponse:
    try:
        # Your agent logic
        result = await self.llm_call(context.input)
        return AgentResponse(output=result, metadata={"tokens": 100})
    except Exception as e:
        # Return error as response, don't crash
        return AgentResponse(
            output=f"Error: {str(e)}",
            metadata={"error": True, "error_type": type(e).__name__}
        )
```

### Token Tracking for Auto-Cleanup

Include token counts for automatic context window management:

```python
return AgentResponse(
    output=response_text,
    metadata={
        "tokens": total_tokens,  # Framework uses this for tracking
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "model": "gpt-4"
    }
)
```

### Portability Checklist

Your agent is portable if it can answer "yes" to all:

- [ ] Can be instantiated without CLI (just constructor params)
- [ ] Works in FastAPI, Jupyter notebooks, and batch scripts
- [ ] Has no imports from `src.cli`
- [ ] Loads its own configuration (not passed by CLI)
- [ ] Doesn't maintain conversation state internally
- [ ] Returns standard `AgentResponse` objects
- [ ] Can be tested in isolation with mocked dependencies

---

## Next Steps

- **Explore Examples**: Check `examples/` folder for reference implementations
- **Read Operations Guide**: See [operations.md](./operations.md) for deployment and performance tips
- **Check Roadmap**: See [roadmap.md](./roadmap.md) for upcoming features
- **Contribute**: Submit PRs with new agent examples or framework improvements

## Getting Help

- Check [architecture.md](./architecture.md) for design questions
- Review test files in `tests/` for implementation examples
- Look at `src/agents/mock_agent.py` for a minimal reference implementation
