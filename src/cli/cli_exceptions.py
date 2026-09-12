"""CLI-specific exceptions for Pac-Man.

This module defines a small exception hierarchy used by the command-line
interface to report errors cleanly. Every exception carries a
user-friendly message and an exit code so the error handler can terminate
the program without showing a Python traceback.
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes used by the CLI error handler."""

    OK = 0                  # Successful execution
    CLI_PARSING = 2         # Failed to parse command-line arguments
    CLI_VALIDATION = 2      # Parsed args failed post-parsing validation
    CLI_OTHER = 1           # Other CLI-related errors
    CONFIG = 1              # Configuration file parsing or loading failed
    ASSET = 1               # Assets related Errors
    ENTITIES = 1            # Entities related Error
    UNEXPECTED = 1          # Unexpected runtime error
    INTERRUPT = 130         # Convenzione interruzione ctrl + C


# ==========================================================================
#   CLI - ERROR_BASE
# ==========================================================================
class CliError(Exception):
    """Base class for all CLI-related errors.

    Attributes:
        message: User-friendly error message.
        exit_code: Process exit code to return to the OS.
    """

    def __init__(self, message: str, exit_code: int = 1) -> None:
        """Initialize the CLI error.

        Args:
            message: User-friendly error message.
            exit_code: Process exit code to use when terminating.
        """
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code

    def __str__(self) -> str:
        """Return the user-friendly message."""
        return self.message


# ==========================================================================
#   CLI - PARSING_ERROR
# ==========================================================================
class CliParsingError(CliError):
    """Raised when command-line arguments cannot be parsed.

    This occurs when the user provides zero arguments, more than one
    argument, or when ``argparse`` fails for any other reason.
    """

    def __init__(self, message: str) -> None:
        """Initialize the parsing error.

        Args:
            message: User-friendly explanation of the parsing problem.
        """
        super().__init__(message, exit_code=2)


# ==========================================================================
#   CLI - VALIDATION_ERROR
# ==========================================================================
class CliValidationError(CliError):
    """Raised when parsed CLI arguments fail post-parsing validation.

    This includes missing files, wrong file extensions, or unreadable
    configuration paths.
    """

    def __init__(self, message: str) -> None:
        """Initialize the validation error.

        Args:
            message: User-friendly explanation of the validation problem.
        """
        super().__init__(message, exit_code=2)
