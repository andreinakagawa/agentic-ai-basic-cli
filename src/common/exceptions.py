"""Custom exceptions for the Agentic AI CLI Framework."""


class AgentError(RuntimeError):
    """Base exception for agent-related errors.

    This exception is used to wrap errors that occur during agent processing,
    providing user-friendly messages while hiding internal implementation details.
    """

    pass


class AgentConfigError(ValueError):
    """Raised when agent configuration is invalid.

    This exception is used when AgentConfig validation fails or when
    required configuration parameters are missing or invalid.
    """

    pass


class AgentProcessingError(RuntimeError):
    """Raised when agent processing encounters a runtime error.

    This exception is used for errors during agent.process() execution,
    such as API errors, timeouts, or processing failures.
    """

    pass


class CommandParseError(ValueError):
    """Raised when command parsing fails.

    This exception is used when user input cannot be parsed correctly,
    such as invalid command syntax or missing required arguments.
    """

    pass
