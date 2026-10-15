#!/usr/bin/env python3
"""Entry point for Pac-Man.

Flow:
    1. Parse and validate CLI arguments
    2. Load configuration from file
    3. Initialize and launch the game
"""

from __future__ import annotations

import logging
import sys
import atexit
import pygame
import json
from pathlib import Path

from src.cli.cli import CLIApplication
from src.cli.cli_error_handler import CLIErrorHandler
from src.ui.app import GameApp

# registra pygame quit per essere eseguito all'uscita --------------
atexit.register(pygame.quit)
# Configure logging -----------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class GameEntry:
    """Encapsulates the boot sequence and game loop."""

    def __init__(self) -> None:
        """Initialize the command-line application wrapper."""
        self.cli_app = CLIApplication()

    def _load_highscores(self, game: GameApp) -> None:
        """Load and validate high scores from the configured file.

        Args:
            game: Application whose high-score list receives valid records.
        """
        highscore_path = Path(game.config.highscore_filename)
        legacy_path = Path("highscore.txt")
        if not highscore_path.exists() and legacy_path.exists():
            logger.info(
                "Configured highscore file %s is missing; loading legacy %s.",
                highscore_path,
                legacy_path,
            )
            highscore_path = legacy_path
        try:
            with highscore_path.open("r", encoding="utf-8") as savefile:
                records = json.load(savefile)
        except FileNotFoundError:
            logger.info(
                "No highscore file found at %s; starting empty.",
                highscore_path,
            )
            return
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            logger.warning(
                "Could not read highscore file %s; starting empty: %s",
                highscore_path,
                error,
            )
            return

        if not isinstance(records, list):
            logger.warning(
                "Ignoring highscore file %s: expected a list of records.",
                highscore_path,
            )
            return

        for index, record in enumerate(records, start=1):
            if not isinstance(record, list) or len(record) != 2:
                logger.warning(
                    "Ignoring malformed highscore record %d in %s.",
                    index,
                    highscore_path,
                )
                continue

            name, score = record
            valid_name = (
                isinstance(name, str)
                and 0 < len(name) <= 10
                and all(
                    character == " "
                    or (character.isascii() and character.isalnum())
                    for character in name
                )
            )
            valid_score = (
                isinstance(score, int)
                and not isinstance(score, bool)
                and score >= 0
            )
            if not valid_name or not valid_score:
                logger.warning(
                    "Ignoring invalid highscore record %d in %s.",
                    index,
                    highscore_path,
                )
                continue

            game.HIGHSCORE.append((name, score))

        game.HIGHSCORE[:] = sorted(
            game.HIGHSCORE,
            key=lambda record: record[1],
            reverse=True,
        )[:10]

    def run(self) -> None:
        """Parse configuration, initialize the game, and start its loop.

        Raises:
            SystemExit : If command-line or configuration validation fails.
        """
        # ---------------------------------------------------------------
        #    [START] Pacman Game
        # ---------------------------------------------------------------
        config = self.cli_app.run()

        if config is None:
            logger.error(
                "Configuration invalid or missing. Exiting."
            )
            sys.exit(1)

        game = GameApp(config)

        self._load_highscores(game)
        try:
            game.run()
        except ModuleNotFoundError as error:
            logger.error(
                "Required Python module '%s' not found. "
                "Check the virtual environment and dependencies.",
                error.name,
            )
            sys.exit(1)


def main() -> None:
    """Entry point for Pac-Man.

    Raises:
        SystemExit: If configuration is invalid or the game crashes.
    """
    # 1. Crea l'error handler con exit_on_error=True
    handler = CLIErrorHandler(exit_on_error=True)
    # 2. Crea il launcher (Eseguiamo tutto)
    launcher = GameEntry()
    # 3. eseguiamo tutto dentro handler
    logger.info(
        "[STARTING] Pac-Man running..."
    )
    handler.run(launcher.run)
    logger.info(
        "[END] Game execution finished."
    )


if __name__ == "__main__":
    main()
