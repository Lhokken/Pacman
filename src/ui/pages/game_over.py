"""User Interface Game Over Screen.

    Game specifications - VI.8 Game Over Screen:
    Displays the final score and Prompts the player to
    enter their name to save the score in the highscores list.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from ..scene import Scene
from ..components.button import Button
from ..managers.font_manager import FontManager

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class GameOverPage(Scene):
    """Scene shown when the game is over."""

    def __init__(self, app: GameApp, score: int = 0) -> None:
        """Initialize game over scene.

        Args:
            app: The parent application instance.
            score: Final score to display (PLACEHOLDER — real value will
                come from game state when game-over condition is wired).
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
        # ------------------------------------------------------------------
        # PLACEHOLDER — real score will be passed from game state
        # ------------------------------------------------------------------
        self.score = score

        # ------------------------------------------------------------------
        #   Back button (only one, so it's always selected)
        # ------------------------------------------------------------------
        self.back_button = Button(
            pygame.Rect(0, 0, 300, 50),
            "Back to Menu",
            self.font_button,
            self.font_button_selected,
            on_select=self._go_back,
        )
        self.buttons = [self.back_button]

    # ======================================================================
    #   Private methods
    # ======================================================================
    def _go_back(self) -> None:
        """Return to the main menu.

        This method is called when the back button is pressed or when the
        user presses the ESC key.
        """
        from .main_menu import MainMenu
        self.app.switch_scene(MainMenu(self.app))

    def _layout_buttons(self, screen_width: int, screen_height: int) -> None:
        """Position the back button near the bottom.
        This method is called during the draw phase to ensure the button is
        always centered horizontally and positioned near the bottom of the
        screen, regardless of the screen size.
        """
        self.back_button.rect.center = (
            screen_width // 2,
            screen_height - 100,
        )
        self.back_button.set_selected(True)

    # ======================================================================
    #   Public methods
    # ======================================================================
    def handle_events(self) -> None:
        """Process input events.

        This method handles user input events, such as quitting the game or
        pressing keys. It checks for the QUIT event to stop the application,
        and it also checks for key presses. If the RETURN key is pressed, it
        triggers the back button's event handler. If the ESCAPE key is pressed,
        it calls the _go_back method to return to the main menu.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.back_button.handle_event(event)
                elif event.key == pygame.K_ESCAPE:
                    self._go_back()

    def draw(self, screen: pygame.Surface) -> None:
        """Render the game over screen.

        Renders the game over screen, including the title, final score, and
        back button. The title is displayed at the top center of the screen,
        followed by the final score below it. The back button is positioned
        near the bottom of the screen and is always centered horizontally.
        The screen is filled with a black background before rendering the
        text and button.
        """
        screen.fill((0, 0, 0))
        # ------------------------------------------------------------------
        #   Title
        # -----------------------------------------------------------------
        title_surface = self.font_title.render("Game Over")
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, 100)
        )
        screen.blit(title_surface, title_rect)
        # -----------------------------------------------------------------
        #   Score
        # -----------------------------------------------------------------
        score_surface = self.font_text.render(f"Final Score: {self.score}")
        score_rect = score_surface.get_rect(
            center=(screen.get_width() // 2, 200)
        )
        screen.blit(score_surface, score_rect)
        # -----------------------------------------------------------------
        # Back button
        # -----------------------------------------------------------------
        self._layout_buttons(screen.get_width(), screen.get_height())
        self.back_button.draw(screen)
