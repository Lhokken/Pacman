"""Command-line argument parsing for Pac-Man.

The game requires exactly one positional argument: the path to the JSON
configuration file. No flags or optional arguments are allowed.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import NoReturn, Optional, Sequence

from .cli_exceptions import CliParsingError


@dataclass(frozen=True)
class CliArgs:
    """Validated command-line arguments for the game.

    Attributes:
        config_path: Path to the JSON configuration file.
    """

    config_path: str


class _NoExitArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that never prints usage or calls sys.exit.

    Instead of exiting, it raises CliParsingError which is caught
    by the CLIErrorHandler.
    """

    def error(self, message: str) -> NoReturn:
        """Override to raise CliParsingError instead of exiting.

        Args:
            message: The error message from argparse.

        Raises:
            CliParsingError: Always raised with a user-friendly
                message.
        """
        raise CliParsingError(
            f"Invalid arguments: {message}"
        )

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        """Override to raise CliParsingError instead of exiting.

        Args:
            status: The exit status code.
            message: Optional message to include.

        Raises:
            CliParsingError: Always raised with a user-friendly
                message.
        """
        if message:
            raise CliParsingError(
                f"Argument parsing failed: {message.strip()}"
            )
        raise CliParsingError(
            "Usage: python3 pac-man.py <config_file.json>"
        )


class ArgumentParser:
    """Parse the single required configuration-file argument."""

    def __init__(self) -> None:
        """Initialize the argument parser."""
        self.parser = _NoExitArgumentParser(
            description="Pac-Man game",
            add_help=False,
        )
        self.parser.add_argument(
            "config_file",
        )

    def parse(self, args: Optional[Sequence[str]] = None) -> CliArgs:
        """Parse command-line arguments.

        Expects exactly one positional argument: the path to a JSON
        configuration file. No flags or optional arguments are supported.

        Args:
            args: Optional list of command-line arguments. If ``None``,
                ``sys.argv[1:]`` is used.

        Returns:
            A :class:`CliArgs` instance containing the configuration file
            path.

        Raises:
            CliParsingError: If no arguments are provided, if too many
                arguments are provided, or if argparse fails to parse them.
        """
        # ----------------------------------------------------------------
        # 1. Parse arguments from sys.argv[1:].
        # ----------------------------------------------------------------

        # Use sys.argv[1:] if args is None
        if args is None:
            args = sys.argv[1:]
        # ----------------------------------------------------------------
        # 2. Pre-check for argument count to provide clearer error messages.
        # ----------------------------------------------------------------

        if len(args) == 0:
            raise CliParsingError(
                "Missing configuration file. "
                "Usage: python3 pac-man.py <config_file.json>"
            )

        if len(args) > 1:
            raise CliParsingError(
                f"Too many arguments ({len(args)}). "
                "Usage: python3 pac-man.py <config_file.json>"
            )

        # ----------------------------------------------------------------
        # 3. Parse the arguments using argparse.
        # ----------------------------------------------------------------
        try:
            namespace = self.parser.parse_args(args)
        except CliParsingError:
            raise
        except argparse.ArgumentError as exc:
            raise CliParsingError(str(exc)) from exc

        # ----------------------------------------------------------------
        # 4. Validate that the config_file attribute is present.
        # ----------------------------------------------------------------
        if (
            not hasattr(namespace, "config_file")
            or not namespace.config_file
        ):
            # Defensive check: config_file should always be present
            raise CliParsingError(
                "Configuration file path is required"
            )

        return CliArgs(config_path=namespace.config_file)
