"""Pac-Man main menu featuring a bitmap font and Button components.

The layout of the [title + buttons] block is delegated to `MenuLayout`:
the positioning logic resides there, while this part handles only the
connection between the calculated layout and the scene entities.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

from ..components.button import Button
from ..scene import Scene
from ..layout.menu_layout import MenuLayout
from ..configUI.ui_config import FontRole

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class MainMenu(Scene):
    """Scena del menu principale."""

    # ================================================================
    #   Init
    # ================================================================
    def __init__(self, app: GameApp) -> None:
        """Initialize the main menu.

        Args:
            app: Instance of `GameApp` from which to access the screen
            and handle scene switching.
        """
        super().__init__(app)
        # ------------------------------------------------------------
        #   FONT
        # ------------------------------------------------------------
        self.font_title = (
            self.theme.font_config(FontRole.SCREEN_TITLE)
        )
        self.font_option = (
            self.theme.font_config(FontRole.OPTION)
        )
        self.font_option_selected = (
            self.theme.font_config(FontRole.OPTION_SELECTED)
        )
        # ------------------------------------------------------------
        #   MENU PAGE
        # ------------------------------------------------------------
        self._menu_layout = MenuLayout()
        self.title_surface = (
            self.font_title.render("PAC-MAN")
        )
        # ------------------------------------------------------------
        #   BUTTONS
        # ------------------------------------------------------------
        self.selected_index = 0
        self.buttons: list[Button] = []
        self._title_center_y: int = 0
        self._create_buttons()

    # =========================================================
    #   Lifecycle
    # =========================================================
    def handle_events(self) -> None:
        """Handle menu input events.

        It forwards keyboard events to `_handle_key` and closes
        the application if a QUIT event is received.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)

    def _handle_key(self, event: pygame.event.Event) -> None:
        """Handle a key press.

        Args:
            event : Keyboard event with a `key` attribute.
        """
        if event.key == pygame.K_UP:
            self.selected_index = (
                self.selected_index - 1
            ) % len(self.buttons)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (
                self.selected_index + 1
            ) % len(self.buttons)
        elif event.key == pygame.K_RETURN:
            self.buttons[self.selected_index].handle_event(event)
        # ----------------------------------------------------------
        # TODO: rimuovere a fine progetto — scorciatoie dev
        # ----------------------------------------------------------
        elif event.key == pygame.K_g:
            from .end_screen import GameOverPage
            self.app.switch_scene(GameOverPage(self.app, score=123))
            logger.debug(
                "Ancora in costruzione"
            )
        elif event.key == pygame.K_v:
            from .end_screen import VictoryPage
            self.app.switch_scene(VictoryPage(self.app, score=456))
            logger.debug(
                "Ancora in costruzione"
            )

    def draw(self, screen: Surface) -> None:
        """Draw the menu on the surface.

        Args:
            screen: Target surface.
        """
        # PALETTE -----------------------------------------
        screen.fill(self.theme.palette.DARK)

        self._layout_menu_block(screen)
        # TITLE -------------------------------------------
        title_rect = (
            self.title_surface.get_rect(
                center=(
                    screen.get_width() // 2,
                    self._title_center_y
                )
            )
        )
        # SCREEN -------------------------------------------
        screen.blit(
            self.title_surface,
            title_rect
        )
        # BUTTON -------------------------------------------
        for button in self.buttons:
            button.draw(screen)

    # =============================================================
    #   LAYOUT MENU - Calcolo
    # =============================================================
    def _layout_menu_block(self, screen: Surface) -> None:
        """Calculate the layout of the title and menu buttons.

        Updates `_title_center_y` and the button rectangles
        based on the layout calculated by `MenuLayout`.

        Args:
            screen : Surface from which to read the current
                     dimensions.
        """
        block = self._menu_layout.compute_block(
            screen.get_width(),
            screen.get_height(),
            title_h=self.title_surface.get_height(),
            brand_y=int(screen.get_height() * 0.12),
            nbr_btn=len(self.buttons),
        )
        self._title_center_y = block.center_titolo_y

        for i, (button, rect) in enumerate(
            zip(
                self.buttons,
                block.button_rect
            )
        ):
            button.rect = rect
            button.set_selected(i == self.selected_index)

    # =========================================================
    #   Buttons
    # =========================================================
    def _create_buttons(self) -> None:
        """Create the menu buttons.

        The size (rect) is a placeholder: it is redefined every
        frame by `_layout_menu_block`.
        """
        options = [
            (
                "Start Game",
                self._start_game
            ),
            (
                "View Highscores",
                self._show_highscores
            ),
            (
                "Instructions",
                self._show_instructions
            ),
            (
                "Settings",
                self._show_impostazioni),
            (
                "Exit",
                self._exit_game
            ),
        ]
        # LABEL BUTTONS -----------------------------------
        for label, callback in options:
            rect = pygame.Rect(0, 0, 10, 10)  # segnaposto!
            self.buttons.append(Button(
                rect,
                label,
                self.font_option,
                self.font_option_selected,
                on_select=callback,
            ))

    # =========================================================
    #   Actions
    # =========================================================
    def _start_game(self) -> None:
        """Start a new game by navigating to `GamePage`."""
        from .game_page import GamePage
        self.app.switch_scene(GamePage(self.app))

    def _show_highscores(self) -> None:
        """Show the high scores page."""
        # from .hight_score import HighScorePage
        # self.app.switch_scene(HighScorePage(self.app))

    def _show_instructions(self) -> None:
        """Show the game instructions page."""
        from .Instruction_page import InstructionPage
        self.app.switch_scene(InstructionPage(self.app))

    def _show_impostazioni(self) -> None:
        """Show the cheat settings page."""
        from .cheat import CheatPage
        self.app.switch_scene(CheatPage(self.app))

    def _exit_game(self) -> None:
        """Close the application."""
        self.app.running = False
