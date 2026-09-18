"""Instruction page for Pac-Man.

Shows the ghost characters with their nicknames, an animated attract
sequence where the ghosts parade and Pac-Man eats them, and information
about pacgums and super-pacgums. Uses only sprite assets and bitmap
fonts (no pygame.draw or pygame.font.Font).

classe: AnimationScene;
istanza: una specifica animazione creata e aggiornata;
pagina: contenitore che usa quell istanza.
"""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING
# from pygame.surface import Surface

from ..scene import Scene

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class InstructionPage(Scene):
    """Instruction / attract mode scene."""
    # TODO: Mettere del testo per le istruzioni
    # --------------------------------------------------------------------
    # Timings (in frames at 60 FPS)
    # --------------------------------------------------------------------

    def __init__(self, app: GameApp) -> None:
        """Initialize the instruction scene.

        Args:
            app: The parent application instance.
        """
        super().__init__(app)
        # instanzia ----------------------------------------------------

    # Pubblic methods --------------------------------------------------
    # ==================================================================
    #   Scene interface
    # ==================================================================

    # ==================================================================
    #   Animation setup
    # ==================================================================
