# Operations Guide

This guide covers security, performance, and operational considerations for running the Agentic AI CLI Framework.

**Audience**: DevOps engineers, security teams, and developers deploying to production.

## Table of Contents

- [Security Considerations](#security-considerations)
- [Performance Considerations](#performance-considerations)
- [Memory Management](#memory-management)
- [Monitoring and Observability](#monitoring-and-observability)

---

## Security Considerations

### API Key Management

**Environment Variables** (Recommended for Development):

```bash
# .env file (never commit this!)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=gpt-4
```

**Best Practices**:
- ✅ Use `.env` files for local development
- ✅ Add `.env` to `.gitignore`
- ✅ Never hardcode API keys in source code
- ✅ Rotate keys regularly
- ✅ Use different keys for development/staging/production

**Production Deployment**:

For production environments, use secure secret management:

```python
# Example: AWS Secrets Manager
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# In your agent
class MyAgent(AgentInterface):
    def __init__(self):
        secrets = get_secret('my-agent-secrets')
        self.api_key = secrets['api_key']
```

Other options:
- **HashiCorp Vault**: Enterprise secret management
- **Azure Key Vault**: For Azure deployments
- **GCP Secret Manager**: For Google Cloud deployments
- **Kubernetes Secrets**: For K8s deployments

### Input Validation

**Framework Level**:
The framework uses Pydantic for type validation on all core types (`Message`, `AgentContext`, `AgentResponse`).

**Agent Level** (Your Responsibility):

```python
class MyAgent(AgentInterface):
    async def process(self, context: AgentContext) -> AgentResponse:
        # Validate input length
        if len(context.input) > 10000:
            return AgentResponse(
                output="Input too long (max 10,000 characters)",
                metadata={"error": True}
            )

        # Sanitize input for your specific provider
        sanitized_input = self._sanitize(context.input)

        # Process with your LLM
        # ...
```

**Recommendations**:
- Set maximum input length limits
- Sanitize inputs before sending to LLM providers
- Validate file uploads if your agent handles them
- Rate limit user requests if exposing via API

### Prompt Injection Protection

If your agent uses user input in system prompts, be aware of prompt injection attacks:

```python
# ❌ Vulnerable
system_prompt = f"You are a helpful assistant. User preference: {user_input}"

# ✅ Better: Separate user input from system instructions
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": user_input}
]
```

**Best Practices**:
- Keep system prompts separate from user input
- Use provider-specific safety features (OpenAI moderation API, etc.)
- Validate and sanitize user inputs
- Monitor for suspicious patterns

---

## Performance Considerations

### Response Time

**Async Operations**:
The framework is built on async/await throughout:

```python
# Agents should be async
async def process(self, context: AgentContext) -> AgentResponse:
    # Use async LLM calls
    response = await self.client.chat.completions.create(...)
    return AgentResponse(...)
```

**Benefits**:
- Non-blocking I/O operations
- Better resource utilization
- Handles concurrent requests efficiently

**Connection Pooling** (Agent Responsibility):

```python
from openai import AsyncOpenAI

class MyAgent(AgentInterface):
    def __init__(self, api_key: str = None):
        # Client maintains connection pool automatically
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            max_retries=3,
            timeout=30.0
        )
```

### Streaming Responses

The framework supports streaming (though CLI implementation is basic):

```python
class StreamingAgent(AgentInterface):
    async def process(self, context: AgentContext) -> AgentResponse:
        # Stream from LLM
        stream = await self.client.chat.completions.create(
            model="gpt-4",
            messages=self._build_messages(context),
            stream=True
        )

        # Collect stream
        chunks = []
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                chunks.append(chunk.choices[0].delta.content)

        output = "".join(chunks)
        return AgentResponse(output=output, metadata={})
```

For web deployments, you can stream directly to the client:

```python
# FastAPI streaming example
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        context = AgentContext(...)
        async for chunk in agent.process_stream(context):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## Memory Management

### Session Storage

**CLI Mode** (Default):
- Sessions stored in memory during runtime
- Cleared on exit
- Export to file for archival

**Web Deployment**:
For production web services, use persistent storage:

**Option 1: Redis** (Recommended for most use cases)

```python
import redis.asyncio as redis
import json

class RedisSessionStore:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def save_history(self, session_id: str, messages: list[Message]):
        data = json.dumps([msg.dict() for msg in messages])
        await self.redis.setex(f"session:{session_id}", 3600, data)

    async def load_history(self, session_id: str) -> list[Message]:
        data = await self.redis.get(f"session:{session_id}")
        if data:
            return [Message(**m) for m in json.loads(data)]
        return []
```

**Option 2: Database** (PostgreSQL, MongoDB, etc.)

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def save_message(session: AsyncSession, session_id: str, message: Message):
    db_message = MessageModel(
        session_id=session_id,
        role=message.role,
        content=message.content,
        tokens=message.tokens
    )
    session.add(db_message)
    await session.commit()
```

### Context Window Management

The framework includes automatic context cleanup:

**How it Works**:
- Tracks token usage as percentage of context window
- **Cleanup threshold**: 90% usage triggers automatic cleanup
- **Target after cleanup**: 60% usage
- **Strategy**: FIFO removal of old messages, preserves system messages and last 5 messages

**Configuration**:

```python
# In SessionManager initialization
session_manager = SessionManager(
    agent=agent,
    context_window_size=100000,  # Default: 100k tokens
    cleanup_threshold=0.90,      # Trigger at 90%
    cleanup_target=0.60,         # Reduce to 60%
    min_messages_to_keep=5       # Always keep last 5 messages
)
```

**Token Tracking**:
Agents should return token counts in metadata:

```python
return AgentResponse(
    output=response_text,
    metadata={
        "tokens": total_tokens,  # Required for tracking
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens
    }
)
```

**Visual Feedback** (CLI):
- Green: < 70% usage
- Yellow: 70-89% usage
- Red: ≥ 90% usage (cleanup triggered)

### Memory Usage

**Framework Overhead**:
- Session state: O(n) where n = number of messages
- ContextTracker: O(1) - single integer counter
- Minimal overhead for typical conversations (< 1MB per session)

**Large Conversations**:
For very long conversations:
- Automatic cleanup prevents unbounded growth
- Export and clear history periodically
- Use persistent storage for archival

**Production Recommendations**:
- Set reasonable context window limits based on your LLM
- Monitor memory usage per session
- Implement session expiration (e.g., 1 hour of inactivity)
- Use Redis for session storage in distributed deployments

---

## Monitoring and Observability

### Logging

Add structured logging to your agents:

```python
import logging

logger = logging.getLogger(__name__)

class MyAgent(AgentInterface):
    async def process(self, context: AgentContext) -> AgentResponse:
        logger.info(
            "Processing request",
            extra={
                "session_id": context.session_id,
                "input_length": len(context.input),
                "history_length": len(context.conversation_history)
            }
        )

        try:
            response = await self._call_llm(context)
            logger.info(
                "Request completed",
                extra={
                    "session_id": context.session_id,
                    "tokens": response.metadata.get("tokens", 0)
                }
            )
            return response
        except Exception as e:
            logger.error(
                "Request failed",
                extra={"session_id": context.session_id, "error": str(e)}
            )
            raise
```

### Metrics

Track key metrics for production deployments:

```python
from prometheus_client import Counter, Histogram

# Define metrics
requests_total = Counter('agent_requests_total', 'Total requests')
request_duration = Histogram('agent_request_duration_seconds', 'Request duration')
tokens_used = Counter('agent_tokens_used_total', 'Total tokens used')

class MyAgent(AgentInterface):
    async def process(self, context: AgentContext) -> AgentResponse:
        requests_total.inc()

        with request_duration.time():
            response = await self._call_llm(context)

        tokens_used.inc(response.metadata.get("tokens", 0))
        return response
```

**Key Metrics to Track**:
- Request count and rate
- Request duration (p50, p95, p99)
- Token usage (cost tracking)
- Error rate
- Context cleanup frequency
- Active sessions

### Error Tracking

Integrate with error tracking services:

```python
import sentry_sdk

sentry_sdk.init(dsn="your-sentry-dsn")

class MyAgent(AgentInterface):
    async def process(self, context: AgentContext) -> AgentResponse:
        try:
            return await self._call_llm(context)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return AgentResponse(
                output="An error occurred. Please try again.",
                metadata={"error": True}
            )
```

### Health Checks

For web deployments, implement health checks:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    try:
        # Check agent can be initialized
        agent = MyAgent()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503

@app.get("/readiness")
async def readiness_check():
    # Check dependencies (API keys, databases, etc.)
    checks = {
        "api_key": bool(os.getenv("OPENAI_API_KEY")),
        "redis": await check_redis_connection()
    }
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    return {"status": "not_ready", "checks": checks}, 503
```

---

## Deployment Patterns

### Docker

Example `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application
COPY src/ ./src/

# Don't copy .env (use secrets management instead)

CMD ["uv", "run", "python", "-m", "src.cli.main"]
```

### Kubernetes

Example deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: agent
        image: my-agent:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Scaling Considerations

The framework is designed for horizontal scaling:

- **Stateless agents**: Each instance is independent
- **Session storage**: Use Redis or database for shared state
- **Load balancing**: Standard HTTP load balancing works
- **Rate limiting**: Implement at API gateway level

---

## Cost Management

### Token Usage Tracking

Track costs in agent metadata:

```python
PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
}

def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pricing = PRICING.get(model, {"input": 0, "output": 0})
    return (prompt_tokens * pricing["input"] + completion_tokens * pricing["output"]) / 1000

# In agent
return AgentResponse(
    output=response_text,
    metadata={
        "tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost": calculate_cost(model, prompt_tokens, completion_tokens)
    }
)
```

### Cost Optimization

- Use appropriate models (don't use GPT-4 when GPT-3.5 suffices)
- Implement caching for repeated queries
- Set maximum token limits
- Monitor and alert on cost spikes
- Use context cleanup to reduce prompt sizes

---

## Next Steps

- **Review Architecture**: See [architecture.md](./architecture.md) for design details
- **Build Agents**: See [developer-guide.md](./developer-guide.md) for implementation
- **Plan Features**: See [roadmap.md](./roadmap.md) for future enhancements
