"""Pause menu for Pac-Man.

Displays the paused game beneath a semi-transparent overlay, featuring a
vertical menu (Resume / Settings / Main menu).

NOTE: The `GamePage` received by the constructor is **reused** upon resuming,
not recreated. The HUD timer survives the pause because the `GamePage
instance remains active in this menu's `self.game_page` field.

Layout is delegated to `PauseLayout`.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

from ..scene import Scene
from ..components.button import Button
from ..layout.pause_layout import PauseLayout
from ..configUI.ui_config import FontRole

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class PauseMenu(Scene):
    """Scena del menu di pausa.

    Disegna la partita sottostante tramite `game_page.draw()`, applica
    un overlay semi-trasparente e mostra un menu verticale navigabile
    da tastiera.
    """

    # =========================================================
    #   Init
    # =========================================================
    def __init__(self, app: GameApp, game_page: Scene) -> None:
        """Initialize pause menu.

        Args:
            app       : The `GameApp` instance used for screen access
                        and scene switching.
            game_page : The active `GamePage` to be paused. It is not
                        recreated upon resuming.
        """
        super().__init__(app)
        self.game_page = game_page
        # ------------------------------------------------------------
        #   FONT
        # ------------------------------------------------------------
        self.font_title = (
            self.theme.font_config(
                FontRole.SCREEN_TITLE
            )
        )
        self.font_option = (
            self.theme.font_config(
                FontRole.OPTION
            )
        )
        self.font_option_selected = (
            self.theme.font_config(
                FontRole.OPTION_SELECTED
            )
        )
        # ------------------------------------------------------------
        #   MENU PAGE
        # ------------------------------------------------------------
        self._pause_layout = PauseLayout()
        self._overlay: Surface | None = None
        # ------------------------------------------------------------
        #   BUTTONS
        # ------------------------------------------------------------
        self.buttons: list[Button] = []
        self._create_buttons()
        self.selected_index = 0

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
                (self.selected_index - 1) % len(self.buttons)
            )
        elif event.key == pygame.K_DOWN:
            self.selected_index = (
                (self.selected_index + 1) % len(self.buttons)
            )
        elif event.key == pygame.K_ESCAPE:
            self._resume_game()
        elif event.key == pygame.K_RETURN:
            self.buttons[self.selected_index].handle_event(event)

    def draw(self, screen: Surface) -> None:
        """Disegna la partita sotto OVERLAY , l'overlay e il menu.

        Args:
            screen: Target surface.
        """
        # OVERLAY ------------------------------------------
        self._draw_overlay(screen)
        # PAUSE --------------------------------------------
        self._layout_pause_menu(screen)
        # BUTTON -------------------------------------------
        for button in self.buttons:
            button.draw(screen)

    # =========================================================
    #   Layout
    # =========================================================
    def _layout_pause_menu(self, screen: Surface) -> None:
        """Calculate the layout of the title and menu buttons.

        Args:
            screen : Surface from which to read the current
                     dimensions.
        """
        block = self._pause_layout.compute(
            screen.get_width(),
            screen.get_height(),
            n_buttons=len(self.buttons),
        )
        # TITLE -------------------------------------------
        title_surface = (
            self.font_title.render("PAUSE")
        )
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, block.title_center_y)
        )
        # SCREEN -------------------------------------------
        screen.blit(
            title_surface, title_rect
        )
        # BUTTON -------------------------------------------
        for i, (button, rect) in enumerate(
            zip(self.buttons, block.button_rects)
        ):
            button.rect = rect
            button.set_selected(i == self.selected_index)

    # =========================================================
    #   layout - Overlay
    # =========================================================
    def _draw_overlay(self, screen: Surface) -> None:
        """Disegna la partita sottostante e applica l'overlay.

        L'overlay viene ricreato solo se la dimensione dello schermo
        cambia, per evitare di riallocare una surface ogni frame.

        Args:
            screen: Surface di destinazione.
        """
        self.game_page.draw(screen)

        w, h = screen.get_size()
        if self._overlay is None or self._overlay.get_size() != (w, h):
            self._overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            self._overlay.fill(self.theme.palette.OVERLAY_RGBA)
        screen.blit(self._overlay, (0, 0))

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
                "Resume",
                self._resume_game
            ),
            (
                "Settings",
                self._show_impostazioni
            ),
            (
                "Main menu",
                self._go_main_menu
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
    def _resume_game(self) -> None:
        """Riprende la partita tornando alla `GamePage` viva."""
        self.app.switch_scene(self.game_page)

    def _go_main_menu(self) -> None:
        """Torna al menu principale, abbandonando la partita."""
        from .main_menu import MainMenu
        self.app.switch_scene(MainMenu(self.app))

    def _show_impostazioni(self) -> None:
        """Show the cheat settings page."""
        from .cheat import CheatPage
        self.app.switch_scene(
            CheatPage(self.app, self.game_page)
        )
