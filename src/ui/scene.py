"""Base class for all game scenes."""

from __future__ import annotations

import pygame
from pygame.surface import Surface
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import GameApp


class Scene:
    """Base class for all game scenes.

    A scene represents a single screen or state in the game
    (e.g., main menu, game play, pause menu, game over).

    Subclasses must override:
        handle_events: Process pygame events.
        update: Update scene logic (optional).
        draw: Draw the scene to the screen.
    """

    def __init__(self, app: GameApp) -> None:
        """Initialize the scene.

        Args:
            app: The parent GameApp instance.
        """
        self.app = app

    def handle_events(self) -> None:
        """Process pygame events.

        Override in subclasses to handle input.
        """

    def update(self) -> None:
        """Update scene logic.

        Override in subclasses to update state each frame.
        """

    def draw(self, screen: Surface) -> None:
        """Draw the scene.

        Args:
            screen: The pygame surface to draw on.

        Override in subclasses to render the scene.
        """
