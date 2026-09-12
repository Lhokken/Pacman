"""Centralized error handling for the Pac-Man CLI.

This module provides a handler that catches CLI-specific errors and
unexpected exceptions, prints a clean message to stderr, and exits with
an appropriate status code. It never lets a Python traceback reach the
user.
"""

from __future__ import annotations

import logging
import sys
import pygame

from typing import Any, Callable, TypeVar

from .cli_exceptions import (
    CliError,
    ExitCode,
)
from ..core.parsing.parser_exceptions import ConfigError
from ..core.entities.entity_exceptions import EntityError
from ..ui.managers.asset_exceptions import AssetError


T = TypeVar("T")

logger = logging.getLogger(__name__)


class CLIErrorHandler:
    """Execute CLI commands and handle errors gracefully.

    Attributes:
        exit_on_error: If ``True`` (default), the handler calls ``sys.exit``
            after reporting an error. Set to ``False`` if you want to handle
            the error in a different way (e.g., during tests).
    """

    def __init__(
        self, exit_on_error: bool = True
    ) -> None:
        """Initialize the error handler.

        Args:
            exit_on_error: Whether to terminate the program after handling
                an error.
        """
        self.exit_on_error = exit_on_error

    # ==================================================================
    #   Public methods
    # ==================================================================
    def run(
        self, func: Callable[..., T], *args: Any, **kwargs: Any
    ) -> T | None:
        """Run a function and handle any resulting exception.

        The function is expected to be the main entry point of a CLI command
        (e.g., the game launch). If it raises a known :class:`CliError`, the
        handler prints the user-friendly message and exits. If an unexpected
        exception occurs, it is reported as a generic error and the program
        exits with code 1.

        Args:
            func: The function to execute.
            *args: Positional arguments passed to ``func``.
            **kwargs: Keyword arguments passed to ``func``.

        Returns:
            The return value of ``func`` if no error occurs, otherwise
            ``None`` (though the program usually exits before returning).
        """
        # ----------------------------------------------------------------
        # 1. Execute the function and catch any exceptions.
        # ----------------------------------------------------------------
        try:
            return func(*args, **kwargs)
        except CliError as error:
            self._report_error(
                error.message,
                int(error.exit_code)
            )
        except ConfigError as error:
            self._report_error(
                str(error),
                int(ExitCode.CONFIG)
            )
        except AssetError as error:
            self._report_error(
                str(error),
                int(ExitCode.ASSET)
            )
        except EntityError as error:
            self._report_error(
                str(error),
                int(ExitCode.ENTITIES)
            )
        except pygame.error as error:
            self._report_error(
                f"Graphics initialization error: {error}",
                int(ExitCode.UNEXPECTED)
            )
        except KeyboardInterrupt:
            self._report_error(
                "User Manual Interruption",
                int(ExitCode.INTERRUPT)
            )
        except Exception as error:
            logger.exception(
                "Unexpected error while running CLI command"
            )
            self._report_error(
                f"Unexpected error: {error}",
                int(ExitCode.UNEXPECTED)
            )

        return None

    # ==================================================================
    #   Private methods
    # ==================================================================
    def _report_error(self, message: str, exit_code: int) -> None:
        """Print the error message to stderr and optionally exit.

        Args:
            message: The user-friendly error message.
            exit_code: The process exit code to use.
        """
        # ----------------------------------------------------------------
        # Step 1: Write error message to stderr for clean console output
        # ----------------------------------------------------------------
        sys.stderr.write(
            f"[ERROR]: {message}\n"
        )
        sys.stderr.flush()
        # ----------------------------------------------------------------
        # Step 2: Exit with appropriate code if exit_on_error is enabled
        # ----------------------------------------------------------------
        if self.exit_on_error:
            sys.exit(exit_code)
