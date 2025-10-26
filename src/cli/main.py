"""Main CLI entry point for Agentic AI CLI Framework."""

import click
from dotenv import load_dotenv

from src.cli.session_manager import SessionManager

# Load environment variables from .env file
load_dotenv()


@click.group()
def cli() -> None:
    """Agentic AI CLI - Interactive chat powered by pluggable agents."""
    pass


@cli.command()
def start() -> None:
    """Start an interactive chat session.

    By default, uses MockAgent for demonstration.
    To use a custom agent, instantiate SessionManager with your agent implementation.
    """
    # Use MockAgent by default (SessionManager default behavior)
    manager = SessionManager()
    manager.run()


@cli.command()
def version() -> None:
    """Display version information."""
    click.echo("Agentic AI CLI v1.0.0")


if __name__ == "__main__":
    cli()
