"""Base Class for reusable animation.

una descrizione bellina
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
import logging


from pathlib import Path
from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

from ..managers.asset_manager import AssetManager
from ..managers.font_manager import FontManager

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class AnimationScene(ABC):
    """Shered scaffolding: assets, font, timer, helpers.

    Subclasses only defie *how* the state machine advances and *what*
    get draw.
    """

    def __init__(self, app: GameApp) -> None:
        """Initialize the instruction scene.

        Args:
            app: The parent application instance.
        """
        self.app = app
        # ==============================================================
        #   Paths and managers
        # ==============================================================
        # Assets shared by all animations. -----------------------------
        file_path = Path(__file__).resolve()
        assets_base = (
            file_path.parent.parent.parent.parent / "assets" / "img"
        )
        self.assets = AssetManager(assets_base, tile_size=40)

        # Fonts --------------------------------------------------------
        self.fonts = FontManager(assets_base)
        self.font_title = self.fonts.font_title_small  # y: scale 2.0
        self.font_white = self.fonts.font_white        # w: scale 2.0
        self.font_big = self.fonts.font_title_big      # y: scale 3.0

        self.screen_width, self.screen_height = app.screen.get_size()

        # Shared state --------------------------------------------------
        self.timer = 0
        self.state = 0
        self._reset_animation()

        # Shared state -------------------------------------------------
        self.screen_width, self.screen_height = app.screen.get_size()

        # Internal animation state -------------------------------------
        self._reset_animation()

    # Pubblic methods --------------------------------------------------
    # ==================================================================
    #   Pubblic API (chiama Page)
    # ==================================================================
    def handle_events(self) -> None:
        """Handle input.

        ESC returns to main menu.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                self._on_escape()

    # ==================================================================
    #   Animation setup
    # ==================================================================
    def update(self) -> None:
        """Update method.

        descrizione
        """
        self.timer += 1
        self._update_state()

    def draw(self, screen: Surface) -> None:
        """Render the current animation state.

        TODO: Inserisci descrizione.
        """
        # Dark background: similar to Terminal color ---------------------
        screen.fill((30, 33, 36))
        self._draw_state(screen)

    # ====================================================================
    #   Draw Scenes
    # ====================================================================
    def _render_text(self, text: str, font, color=None) -> Surface:
        """Render text using a BitmapFont.

        BitmapFont.render returns a Surface with transparent background,
        Color ignored, font has its own
        """
        return font.render(text)  # TODO: Sostituisci funzione

    def _move_entity(self, entity: dict, speed: float) -> bool:
        """Move an entity towards its target_x.

        Return: True when entity arrived.
        """
        dx = entity["target_x"] - entity["x"]
        if abs(dx) < speed:
            entity["x"] = entity["target_x"]
            return True
        entity["x"] += speed if dx > 0 else -speed
        return False

    # ------------------------------------------------------------------
    #   Hooks per le sottoclassi
    # ------------------------------------------------------------------
    @abstractmethod
    def _reset_animation(self) -> None:
        """Gestisce Loop animazione.

        TODO: Inserisci descrizione.
        Reinitialize entity and state.
        """
        pass

    @abstractmethod
    def _update_state(self) -> None:
        """Advance the state machine by one frame.

        TODO: Inserisci descrizione.
    """
        pass

    @abstractmethod
    def _draw_state(self, screen: Surface) -> None:
        """Draw the current frame.

        TODO: Inserisci descrizione.
        Disegna il frame corrente.
        """

    def _on_escape(self) -> None:
        """Return to the main menu.

        TODO: Inserisci descrizione.
        """
        from ..pages.main_menu import MainMenu
        self.app.switch_scene(MainMenu(self.app))
