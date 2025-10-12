"""Mock agent implementation for testing and demonstration.

This module provides a MockAgent that implements the AgentInterface without
using real LLMs. It demonstrates the agent pattern and provides context-aware
responses based on simple keyword matching and conversation history.
"""

import math

from src.agents.base import AgentInterface
from src.common.config import AgentConfig
from src.common.types import AgentContext, AgentResponse


def estimate_tokens(text: str) -> int:
    """Estimate token count for text using character-based approximation.

    This is a simple estimation using ~4 characters per token, which is
    reasonable for English text. Real implementations should use provider-
    specific tokenizers (tiktoken for OpenAI, anthropic tokenizer for Claude).

    Args:
        text: Input text to estimate tokens for

    Returns:
        Estimated token count (minimum 1 for non-empty strings, 0 for empty)
    """
    if not text:
        return 0
    # Approximation: ~4 characters per token, round up
    return math.ceil(len(text) / 4)


class MockAgent(AgentInterface):
    """Mock agent for testing and demonstration.

    This agent implements the AgentInterface without using real LLM APIs.
    It provides context-aware responses based on:
    - Input keyword matching
    - Conversation history length
    - Session ID
    - Additional context presence

    The MockAgent is useful for:
    - Testing the agent integration without API calls
    - Demonstrating the agent pattern
    - Development and debugging
    - Integration testing

    The agent is stateless - all context is passed in on each call.

    Example:
        ```python
        from src.agents.mock_agent import MockAgent
        from src.common.config import AgentConfig
        from src.common.types import AgentContext

        config = AgentConfig(system_prompt="You are a helpful assistant")
        agent = MockAgent(config, debug=True)  # Enable debug output

        context = AgentContext(
            input="Hello!",
            conversation_history=[],
            session_id="test_session"
        )

        response = await agent.process(context)
        # Prints detailed debug info about input, history, and context
        print(response.output)  # Greeting response
        print(response.metadata)  # {"message_count": 0, ...}
        ```
    """

    def __init__(self, config: AgentConfig | None = None, debug: bool = False):
        """Initialize the MockAgent.

        Args:
            config: Optional AgentConfig. Accepted for consistency with other
                   agents, but not used by MockAgent since it doesn't call real APIs.
            debug: If True, prints detailed debugging information about inputs,
                  metadata, and conversation history during processing.
        """
        self.config = config
        self.debug = debug

    async def process(self, context: AgentContext) -> AgentResponse:
        """Process input and return a context-aware mock response.

        This method analyzes the input and context to provide relevant responses:
        - Greetings get greeting responses
        - Help requests get helpful responses
        - Thank you messages get acknowledgments
        - Farewell messages get goodbye responses
        - Acknowledges conversation history
        - Mentions additional context if present

        Args:
            context: Complete context including input, history, session_id, and
                    optional additional_context.

        Returns:
            AgentResponse with contextually appropriate output and metadata including:
                - message_count: Number of messages in conversation history
                - session_id: The current session ID
                - mock_version: Version identifier for the mock
                - has_additional_context: Whether additional context was provided
                - input_keywords: Keywords detected in the input
                - input_tokens: Estimated token count for input
                - output_tokens: Estimated token count for output
                - total_tokens: Sum of input and output tokens

        Example:
            ```python
            context = AgentContext(
                input="How can you help me?",
                conversation_history=[
                    Message(role="user", content="Hi"),
                    Message(role="assistant", content="Hello!")
                ],
                session_id="session_123",
                additional_context={"custom_data": {...}}
            )

            response = await agent.process(context)
            # response.output: "I see we've exchanged 2 messages. I'm a mock agent..."
            # response.metadata: {"message_count": 2, "has_additional_context": True, ...}
            ```
        """
        # Debug output if enabled
        if self.debug:
            self._print_debug_info(context)

        input_lower = context.input.lower()
        message_count = len(context.conversation_history)

        # Detect input type via keyword matching
        keywords = self._detect_keywords(input_lower)

        # Generate appropriate response
        output = self._generate_response(
            input_lower, message_count, context.additional_context, keywords
        )

        # Estimate token counts
        input_tokens = estimate_tokens(context.input)
        output_tokens = estimate_tokens(output)
        total_tokens = input_tokens + output_tokens

        # Build metadata
        metadata = {
            "message_count": message_count,
            "session_id": context.session_id,
            "mock_version": "1.0",
            "has_additional_context": context.additional_context is not None,
            "input_keywords": keywords,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }

        # Add additional context info if present
        if context.additional_context:
            metadata["additional_context_keys"] = list(
                context.additional_context.keys()
            )

        return AgentResponse(output=output, metadata=metadata)

    def _detect_keywords(self, input_lower: str) -> list[str]:
        """Detect keywords in the input to determine response type.

        Args:
            input_lower: Lowercased input string

        Returns:
            List of detected keyword categories
        """
        keywords = []

        if any(word in input_lower for word in ["hello", "hi", "hey", "greetings"]):
            keywords.append("greeting")

        if any(word in input_lower for word in ["help", "how", "what", "can you"]):
            keywords.append("help")

        if any(word in input_lower for word in ["thank", "thanks"]):
            keywords.append("thanks")

        if any(word in input_lower for word in ["bye", "goodbye", "exit"]):
            keywords.append("farewell")

        return keywords

    def _generate_response(
        self,
        input_lower: str,
        message_count: int,
        additional_context: dict | None,
        keywords: list[str],
    ) -> str:
        """Generate a contextually appropriate response.

        Args:
            input_lower: Lowercased input string
            message_count: Number of previous messages
            additional_context: Optional additional context data
            keywords: Detected keywords from input

        Returns:
            Generated response string
        """
        # Build conversation context acknowledgment
        context_ack = ""
        if message_count > 0:
            context_ack = f"I see we've exchanged {message_count} messages so far. "

        # Generate response based on keywords (prioritize specific over general)
        # Check for thanks/farewell first (most specific)
        if "thanks" in keywords:
            return f"{context_ack}You're welcome! Happy to help."

        if "farewell" in keywords:
            return f"{context_ack}Goodbye! It was nice chatting with you."

        # Then greetings
        if "greeting" in keywords:
            return (
                f"{context_ack}Hello! I'm a mock agent here to help you. "
                f"I can respond to your queries and demonstrate the agent interface."
            )

        # General help last (most generic)
        if "help" in keywords:
            return (
                f"{context_ack}I'm a mock agent designed to demonstrate the agent pattern. "
                f"You can ask me questions, greet me, or chat about anything. "
                f"I'll respond based on keyword matching to show how agents work."
            )

        # Default response
        additional_note = ""
        if additional_context:
            additional_note = (
                " I notice you've included additional context in your request."
            )

        return (
            f"{context_ack}I received your message: '{input_lower[:50]}...'. "
            f"As a mock agent, I'm responding based on pattern matching.{additional_note} "
            f"A real agent would use LLMs to provide more intelligent responses."
        )

    def _print_debug_info(self, context: AgentContext) -> None:
        """Print detailed debugging information about the agent context.

        Args:
            context: The AgentContext being processed
        """
        print("\n" + "=" * 80)
        print("MockAgent DEBUG INFO")
        print("=" * 80)

        # Session info
        print(f"\n📌 SESSION ID: {context.session_id}")

        # Input
        print("\n💬 INPUT:")
        print(f"  {context.input}")
        print(f"  Length: {len(context.input)} chars, ~{estimate_tokens(context.input)} tokens")

        # Conversation history
        print(f"\n📚 CONVERSATION HISTORY: ({len(context.conversation_history)} messages)")
        if context.conversation_history:
            for i, msg in enumerate(context.conversation_history, 1):
                role_icon = "👤" if msg.role == "user" else "🤖"
                print(f"  {i}. {role_icon} [{msg.role}]:")
                # Truncate long messages for readability
                content_preview = (
                    msg.content[:100] + "..."
                    if len(msg.content) > 100
                    else msg.content
                )
                print(f"     {content_preview}")
                print(f"     (~{estimate_tokens(msg.content)} tokens)")
        else:
            print("  (No previous messages)")

        # Additional context
        print("\n🔍 ADDITIONAL CONTEXT:")
        if context.additional_context:
            print(f"  Keys: {list(context.additional_context.keys())}")
            for key, value in context.additional_context.items():
                print(f"\n  [{key}]:")
                # Handle different value types
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        sub_str = str(sub_value)
                        preview = (
                            sub_str[:80] + "..." if len(sub_str) > 80 else sub_str
                        )
                        print(f"    - {sub_key}: {preview}")
                elif isinstance(value, (list, tuple)):
                    print(f"    - Type: {type(value).__name__}")
                    print(f"    - Length: {len(value)}")
                    if len(value) > 0:
                        preview = str(value[0])[:80]
                        print(f"    - First item: {preview}...")
                else:
                    value_str = str(value)
                    preview = value_str[:100] + "..." if len(value_str) > 100 else value_str
                    print(f"    {preview}")
        else:
            print("  (No additional context provided)")

        # Config info
        print("\n⚙️  AGENT CONFIG:")
        if self.config:
            print(f"  System Prompt: {self.config.system_prompt[:80] if self.config.system_prompt else 'None'}...")
            print(f"  Model: {self.config.model if hasattr(self.config, 'model') else 'N/A'}")
        else:
            print("  (No config provided)")

        print("\n" + "=" * 80 + "\n")
