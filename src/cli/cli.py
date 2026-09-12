"""CLI orchestrator for Pac-Man.

This module ties together argument parsing, input validation,
configuration loading, and the central error handler.
"""

from __future__ import annotations

import logging
import sys

from .cli_args_parser import ArgumentParser
from .cli_validator_input import CLIValidator
from ..core.parsing.parsey import ConfigLoader, GameConfig

logger = logging.getLogger(__name__)


class CLIApplication:
    """Encapsulate the command-line interface flow."""

    def __init__(self) -> None:
        """Initialize the CLI components."""
        self.argument_parser = ArgumentParser()
        self.validator = CLIValidator()

    def run(self) -> GameConfig:
        """Execute the CLI flow and return the loaded configuration.

        Returns:
            GameConfig: The loaded and validated game configuration.

        Raises:
            CliParsingError: If the command-line arguments are invalid.
            CliValidationError: If the configuration file path is invalid.
            ConfigError: If the configuration file cannot be parsed.
        """
        # ----------------------------------------------------------------
        # 1. Parse arguments from sys.argv[1:].
        # ----------------------------------------------------------------
        args = self.argument_parser.parse(sys.argv[1:])

        # ----------------------------------------------------------------
        # 2. Validate the parsed arguments.
        # ----------------------------------------------------------------
        self.validator.validate(args)

        # ----------------------------------------------------------------
        # 3. Load the configuration.
        # ----------------------------------------------------------------
        config_loader = ConfigLoader(args.config_path)
        config = config_loader.load()

        # ----------------------------------------------------------------
        # 4. Print a summary (info, not a replacement for returning)
        # ----------------------------------------------------------------
        sys.stdout.write(
            f"[INFO] Configuration loaded from '{args.config_path}':\n"
        )
        sys.stdout.write(
            f"  Lives: {config.lives}\n"
        )
        sys.stdout.write(
            f"  Seed: {config.seed}\n"
        )
        sys.stdout.write(
            f"  Levels: {len(config.levels)}\n"
        )
        for i, level in enumerate(config.levels, start=1):
            sys.stdout.write(
                f"    Level {i}: {level.width}x{level.height}\n"
            )
        sys.stdout.write("[START] Starting game...\n")

        # ----------------------------------------------------------------
        # 5. Return the config so the main can use it
        # ----------------------------------------------------------------
        return config
