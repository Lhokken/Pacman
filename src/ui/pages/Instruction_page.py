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

import pygame
from pygame.surface import Surface

from pathlib import Path

from ..scene import Scene
from ..components.button import Button
from ..managers.font_manager import FontManager
# from ..layout.instructions_layout import InstructionsLayout

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
        # ------------------------------------------------------------------
        #   Assets and fonts
        # ------------------------------------------------------------------
        assets_base = Path(__file__).resolve().parents[3] / "assets" / "img"
        self.fonts = FontManager(assets_base)
        self.font_title = self.fonts.font_title_big
        self.font_text = self.fonts.font_white
        self.font_button = self.fonts.font_white
        self.font_button_selected = self.fonts.font_title_small

        # ------------------------------------------------------------------
        #   Back button (only one, always selected)
        # ------------------------------------------------------------------
        self.back_button = Button(
            pygame.Rect(0, 0, 300, 50),
            "Back to Menu",
            self.font_button,
            self.font_button_selected,
            on_select=self._go_back,
        )
        self.buttons = [self.back_button]

    def _go_back(self) -> None:
        """Return to the main menu."""
        from .main_menu import MainMenu
        self.app.switch_scene(MainMenu(self.app))

    def _layout_buttons(self, screen_width: int, screen_height: int) -> None:
        """Position the back button near the bottom."""
        self.back_button.rect.center = (
            screen_width // 2,
            screen_height - 100,
        )
        self.back_button.set_selected(True)

    def handle_events(self) -> None:
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.back_button.handle_event(event)
                elif event.key == pygame.K_ESCAPE:
                    self._go_back()

    def draw(self, screen: Surface) -> None:
        """Render the hght score."""
        screen.fill((20, 20, 30))
        # ---------------------------------------------------------------------
        # Title
        title_surface = self.font_title.render("Instruction")
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, 100)
        )
        screen.blit(title_surface, title_rect)
        # ----------------------------------------------------------------------
        # Istruzioni message
        msg_surface = self.font_text.render(
            "Scappa dai ghost!."
        )
        msg_rect = msg_surface.get_rect(
            center=(screen.get_width() // 2, 180)
        )
        screen.blit(msg_surface, msg_rect)
        # TODO: presentazione dei ghost utilizzando le immagini asset
        # Score
        text_surface = self.font_text.render(
            "Mangia i pacgum per raccogliere punti e super pacgum per "
            "rendere vulnerabili i ghost"
        )
        score_rect = text_surface.get_rect(
            center=(screen.get_width() // 2, 240)
        )
        # TODO: presentazione di pucgum e super pugum
        screen.blit(text_surface, score_rect)

        # Back button
        self._layout_buttons(screen.get_width(), screen.get_height())
        self.back_button.draw(screen)
