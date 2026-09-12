"""Pause menu for Pac-Man.

Allows the player to resume the game or return to the main menu,
as specified in VI.8 User Interface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import logging
import pygame
from pygame.surface import Surface

from pathlib import Path
from ..scene import Scene
from ..components.button import Button
from ..managers.font_manager import FontManager

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class PauseMenu(Scene):
    """Pause menu scene."""

    def __init__(self, app: GameApp, game_page: Scene) -> None:
        """Initialize the pause menu and keep a reference to the game scene.

        Args:
            app: The parent application instance.
            game_page: The scene to resume when the user selects Resume.
        """
        super().__init__(app)

        # Use absolute path derived from this file's location
        assets_base = Path(__file__).resolve().parents[3] / "assets" / "img"

        # TODO: Replace with self.fonts = self.app.font_manager
        # (use cached instance)
        self.fonts = FontManager(assets_base)
        self.font_title = self.fonts.font_title_big              # y, scale 3.0
        self.font_option = self.fonts.font_white                 # w, scale 2.0
        self.font_option_selected = self.fonts.font_title_small  # y, scale 2.

        # Create buttons with placeholder rects (updated in _layout_buttons)
        self.buttons: list[Button] = []
        self._create_buttons()
        self.selected_index = 0

    # Pubblic Method ------------------------------------------------------
    # =====================================================================
    #   MENU
    # =====================================================================
    def handle_events(self) -> None:
        """Process pause menu input and switch scenes accordingly.

        Handles quit requests, keyboard navigation, and confirmation of the
        selected action, such as resuming the current game or returning to the
        main menu.
        """
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
                elif event.key == pygame.K_c:
                    # TEMPORARY access for testing cheat page
                    from .cheat import CheatPage
                    self.app.switch_scene(CheatPage(self.app))

    def draw(self, screen: Surface) -> None:
        """Render the pause overlay and its menu options.

        Args:
            screen: The pygame surface on which the pause menu is drawn.
        """
        """Render the menu title and options on the target surface.

        Args:
            screen: The pygame surface used for drawing the main menu.
        """
        screen.fill((0, 0, 0))
        # -------------------------------------------------------------
        #   Title
        # -------------------------------------------------------------
        title_surface = self.font_title.render("PAUSE")
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
            ("Resume", self._resume_game),
            ("Impostazioni", self._show_impostazioni),
            ("Main menu", self._go_main_menu),
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
            button.rect.width = 400  # arbitrary; text centering uses center
            button.rect.height = 50
            button.rect.center = (screen_width // 2, y)
        # Update selected state
        for i, button in enumerate(self.buttons):
            button.set_selected(i == self.selected_index)

    def _resume_game(self) -> None:
        """Switch to the game scene."""
        from .game_page import GamePage
        self.app.switch_scene(GamePage(self.app))

    def _go_main_menu(self) -> None:
        """Display (placeholder for now)."""
        logger.info("(not yet implemented)")

    def _show_impostazioni(self) -> None:
        """Display (placeholder for now)."""
        logger.info("(not yet implemented)")
