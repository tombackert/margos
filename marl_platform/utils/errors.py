"""Error types and display utilities for the platform."""

import sys
import traceback

import typer


class PlatformError(Exception):
    """Base exception for platform errors."""

    def __init__(self, message: str, context: dict | None = None, fix: str | None = None):
        self.message = message
        self.context = context or {}
        self.fix = fix
        super().__init__(message)


class ConfigNotFoundError(PlatformError):
    """Raised when a config file is not found."""

    def __init__(self, path: str):
        super().__init__(
            message="Config file not found",
            context={"Path": path},
            fix="Create the config file or check the experiment name",
        )


class ExperimentNotFoundError(PlatformError):
    """Raised when an experiment directory is not found."""

    def __init__(self, path: str):
        super().__init__(
            message="Experiment not found",
            context={"Path": f"{path}/"},
            fix="Check the experiment ID or run `ls results/` to see available experiments",
        )


class BundleNotFoundError(PlatformError):
    """Raised when a bundle file is not found."""

    def __init__(self, path: str):
        super().__init__(
            message="Bundle not found",
            context={"Path": path},
            fix="Check the filename or run `ls bundles/` to see available bundles",
        )


class ValidationError(PlatformError):
    """Raised when validation fails."""

    def __init__(self, message: str, context: dict | None = None, fix: str | None = None):
        super().__init__(
            message=message,
            context=context,
            fix=fix or "Check the input and try again",
        )


def display_error(error: PlatformError, verbose: bool = False) -> None:
    """Format and display error to user."""
    typer.echo(f"Error: {error.message}")

    for key, value in error.context.items():
        typer.echo(f"  {key}: {value}")

    if error.fix:
        typer.echo(f"  Fix: {error.fix}")

    if verbose:
        typer.echo("")
        traceback.print_exc(file=sys.stderr)
