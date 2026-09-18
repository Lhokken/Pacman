"""VI.8 User Interface Game Vicotory Screen.

# Vicotory Screen:
#    ◦ Displays the final score and a congratulatory message.
#    ◦ Prompts the player to enter their name to save the score
#      in the highscores list.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

from ..scene import Scene
from ..components.button import Button
from ..managers.font_manager import FontManager

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class VictoryPage(Scene):
    """Scene shown when the player completes all levels."""

    def __init__(self, app: GameApp, score: int = 0) -> None:
        """Initialize victory scene.

        Args:
            app: The parent application instance.
            score: Final score to display (PLACEHOLDER — real value will
                come from game state when victory condition is wired).
        """
        super().__init__(app)

        # ------------------------------------------------------------------
        #   Assets and fonts
        # ------------------------------------------------------------------
        assets_base = Path(__file__).resolve().parents[3] / "assets" / "img"
        self.fonts = FontManager(assets_base)
        self.font_title = self.fonts.font_title_big
        self.font_text = self.fonts.font_white
        self.font_button = self.fonts.font_white
        self.font_button_selected = self.fonts.font_title_small

        # PLACEHOLDER — real score will be passed from game state
        self.score = score

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
        """Render the victory screen."""
        screen.fill((0, 0, 0))

        # Title
        title_surface = self.font_title.render("You Win!")
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, 100)
        )
        screen.blit(title_surface, title_rect)

        # Congratulatory message
        msg_surface = self.font_text.render(
            "Congratulations! You completed all levels."
        )
        msg_rect = msg_surface.get_rect(
            center=(screen.get_width() // 2, 180)
        )
        screen.blit(msg_surface, msg_rect)

        # Score
        score_surface = self.font_text.render(f"Final Score: {self.score}")
        score_rect = score_surface.get_rect(
            center=(screen.get_width() // 2, 240)
        )
        screen.blit(score_surface, score_rect)

        # Back button
        self._layout_buttons(screen.get_width(), screen.get_height())
        self.back_button.draw(screen)
