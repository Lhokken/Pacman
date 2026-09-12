"""Main menu for Pac-Man using bitmap fonts and Button components."""

from __future__ import annotations

import logging
import pygame

from pathlib import Path
from typing import TYPE_CHECKING

from ..scene import Scene
from ..components.button import Button
from ..managers.font_manager import FontManager

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class MainMenu(Scene):
    """Main menu scene."""

    # =========================================================
    #   Private Methods
    # =========================================================
    def __init__(self, app: GameApp) -> None:
        """Initialize the main menu scene.

        Args:
            app: The parent application instance that owns the scene.
        """
        super().__init__(app)

        # Use absolute path derived from this file's location
        assets_base = Path(__file__).resolve().parents[3] / "assets" / "img"

        # TODO: Replace with self.fonts = self.app.font_manager
        # (use cached instance)
        self.fonts = FontManager(assets_base)
        self.font_title = self.fonts.font_title_big              # y, scale 3.0
        self.font_option = self.fonts.font_white                 # w, scale 2.0
        self.font_option_selected = self.fonts.font_title_small  # y, scale 2.0

        # Create buttons with placeholder rects (updated in _layout_buttons)
        self.buttons: list[Button] = []
        self._create_buttons()
        self.selected_index = 0

    # Pubblic Method ------------------------------------------------------
    # =====================================================================
    #   MENU
    # =====================================================================
    def handle_events(self) -> None:
        """Process input events for menu navigation and option selection."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (
                        (self.selected_index - 1) % len(self.buttons)
                    )
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (
                        (self.selected_index + 1) % len(self.buttons)
                    )
                elif event.key == pygame.K_RETURN:
                    self.buttons[self.selected_index].handle_event(event)
                elif event.key == pygame.K_g:
                    # TEMPORARY access for testing game over screen
                    from .game_over import GameOverPage
                    self.app.switch_scene(GameOverPage(self.app, score=123))
                elif event.key == pygame.K_v:
                    # TEMPORARY access for testing victory screen
                    from .victory_screen import VictoryPage
                    self.app.switch_scene(VictoryPage(self.app, score=456))

    def draw(self, screen: pygame.Surface) -> None:
        """Render the menu title and options on the target surface.

        Args:
            screen: The pygame surface used for drawing the main menu.
        """
        screen.fill((0, 0, 0))
        # -------------------------------------------------------------
        #   Title
        # -------------------------------------------------------------
        title_surface = self.font_title.render("Pac-Man")
        title_rect = (
            title_surface.get_rect(
                center=(screen.get_width() // 2, 80)
            )
        )
        screen.blit(title_surface, title_rect)
        # -------------------------------------------------------------
        # Layout buttons and draw them
        # -------------------------------------------------------------
        self._layout_buttons(screen.get_width())
        for button in self.buttons:
            button.draw(screen)

    # Private Method ------------------------------------------------------
    # =====================================================================
    #   BUTTON
    # =====================================================================
    def _create_buttons(self) -> None:
        """Create the menu buttons and assign callbacks."""
        options = [
            ("Start Game", self._start_game),
            ("View Highscores", self._show_highscores),
            ("Instructions", self._show_instructions),
            ("Settings", self._show_impostazioni),
            ("Exit", self._exit_game),
        ]
        for label, callback in options:
            rect = pygame.Rect(0, 0, 10, 10)  # will be positioned later
            button = Button(
                rect,
                label,
                self.font_option,
                self.font_option_selected,
                on_select=callback,
            )
            self.buttons.append(button)

    def _layout_buttons(self, screen_width: int) -> None:
        """Center the buttons vertically starting at y=150, spacing 60.

        Args:
            screen_width: Current width of the game window.
        """
        y_positions = [150 + i * 60 for i in range(len(self.buttons))]
        for button, y in zip(self.buttons, y_positions):
            button.rect.width = 400
            button.rect.height = 50
            button.rect.center = (screen_width // 2, y)
        # Update selected state
        for i, button in enumerate(self.buttons):
            button.set_selected(i == self.selected_index)

    # =====================================================================
    #   METHODS MENU
    # =====================================================================
    def _start_game(self) -> None:
        """Switch to the game scene."""
        from .game_page import GamePage
        self.app.switch_scene(GamePage(self.app))

    def _show_highscores(self) -> None:
        """Display the highscore list (placeholder for now)."""
        logger.info("Highscores requested (not yet implemented)")

    def _show_instructions(self) -> None:
        """Switch to the instructions / attract mode scene."""
        from src.ui.pages.Instruction_page import InstructionPage
        self.app.switch_scene(InstructionPage(self.app))

    def _show_impostazioni(self) -> None:
        """Display (placeholder for now)."""
        logger.info("(not yet implemented)")

    def _exit_game(self) -> None:
        """Exit the application."""
        self.app.running = False
