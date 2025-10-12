"""CLI interface for the Agentic AI CLI Framework.

This module provides the command-line interface components including:
- Session management and orchestration
- Command parsing
- Output formatting
- Chat history export
- Main CLI entry point

The CLI layer is designed to be simple and focused on user interaction,
delegating all agent logic to the agent implementations.
"""

from src.cli.main import cli

__all__ = ["cli"]
