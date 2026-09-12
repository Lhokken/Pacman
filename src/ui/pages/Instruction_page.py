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
from pygame.surface import Surface

from ..scene import Scene
from ..animation.instructions_game import (
    IstructionPage as InstructionAnimation
)

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class InstructionPage(Scene):
    """Instruction / attract mode scene."""
    # TODO: centra in manier appropriata tutte e tre le scene
    # TODO: usare AnimationScene senza duplicare stato, asset, font e costanti
    # TODO: separare il layout della pagina dal rendering dell'animazione
    # TODO: decidere se il MainMenu deve ospitare una versione ridotta
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
        self.animation_scene = InstructionAnimation(app)

    # Pubblic methods --------------------------------------------------
    # ==================================================================
    #   Scene interface
    # ==================================================================

    def handle_events(self) -> None:
        """Handle input: ESC returns to main menu."""
        self.animation_scene.handle_events()

    # ==================================================================
    #   Animation setup
    # ==================================================================
    def update(self) -> None:
        """Advance the animation based on the current state."""
        self.animation_scene.update()

    def draw(self, screen: Surface) -> None:
        """Render the current animation state."""
        self.animation_scene.draw(screen)
