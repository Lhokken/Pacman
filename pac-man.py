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
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        self.cli_app = CLIApplication()

    def run(self) -> None:
        """Esegue il flusso dell'applicazione.

        Flow:
        1. Parse and validate CLI arguments
        2. Load configuration from file
        3. Initialize and launch the game

        """
        # ---------------------------------------------------------------
        #    [START] Pacman Game
        # ---------------------------------------------------------------
        # 1. Carica config (parsing CLI + File di config)
        config = self.cli_app.run()

        # 2. Se config è None (errore gestito), esce.
        if config is None:
            logger.error(
                "Configuration invalid or missing. Exiting."
            )
            sys.exit(1)

        # 5. Avvia la grafica
        game = GameApp(config)
        game.run()


def main() -> None:
    """Entry point for Pac-Man.

    Raises:
        SystemExit: If configuration is invalid or the game crashes.
    """
    # 1. Crea l'error handler con exit_on_error=True
    handler = CLIErrorHandler(exit_on_error=True)
    # 2. Crea il launcher (Eseguiamo tutto)
    launcher = GameEntry()
    # 3. eseguiamo tutto dentro handeler
    logger.info(
        "[STARTING] Pac-Man running..."
    )
    handler.run(launcher.run)
    logger.info(
        "[END] Configuration loaded successfully, launching game"
    )


if __name__ == "__main__":
    main()
