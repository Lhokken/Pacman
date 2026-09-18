"""Pause menu for Pac-Man.

Displays the paused game beneath a semi-transparent overlay, featuring a
vertical menu (Resume / Settings / Main menu).

NOTE: the `GamePage` received by the constructor is
**reused** upon resuming, not recreated. The HUD timer survives
the pause because the `GamePage` instance remains alive in the
`self.game_page` field of this menu.

Layout: delegated to `PauseLayout`. Positioning ratios are defined there.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import logging
import pygame
from pygame.surface import Surface

from ..scene import Scene
from ..components.button import Button
from ..layout.pause_layout import PauseLayout

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class PauseMenu(Scene):
    """Pause menu scene."""

    # Overlay nero sopra il gioco (alpha 0-255).
    OVERLAY_ALPHA = 180

    # =========================================================
    #   Init
    # =========================================================
    def __init__(self, app: GameApp, game_page: Scene) -> None:
        """Inizializza il menu pausa.

        Args:
            app: istanza GameApp.
            game_page: la GamePage da riprendere al resume. Va
                conservata per istanza: ricrearla perderebbe lo
                stato (incluso il timer dell'HUD).
        """
        super().__init__(app)

        # Riferimento alla scena di gioco da riprendere. NON ricrearla.
        self.game_page = game_page

        # Manager condivisi (da Scene). Alias di comodo.
        self.font_title = self.fonts.font_title_extraLarge
        self.font_option = self.fonts.font_white
        self.font_option_selected = self.fonts.font_title_small

        # Layout: titolo ancorato in alto, bottoni centrati.
        self._pause_layout = PauseLayout()

        # Overlay pre-renderizzato una volta (evita di ricrearlo ogni frame).
        self._overlay: Surface | None = None

        self.buttons: list[Button] = []
        self._create_buttons()
        self.selected_index = 0

    # =========================================================
    #   Lifecycle
    # =========================================================
    def handle_events(self) -> None:
        """FA TODO: Docstring."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)

    def _handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_UP:
            self.selected_index = (
                (self.selected_index - 1) % len(self.buttons)
            )
        elif event.key == pygame.K_DOWN:
            self.selected_index = (
                (self.selected_index + 1) % len(self.buttons)
            )
        elif event.key == pygame.K_ESCAPE:
            # ESC in pausa = resume (scorciatoia naturale).
            self._resume_game()
        elif event.key == pygame.K_RETURN:
            self.buttons[self.selected_index].handle_event(event)
        elif event.key == pygame.K_c:
            # Scorciatoia dev. Da gateare su app.debug quando esisterà.
            from .cheat import CheatPage
            self.app.switch_scene(CheatPage(self.app))

    # Nessun `update()`: il gioco sotto è in pausa, l'HUD non deve
    # avanzare, e questa schermata non ha animazioni proprie.

    def draw(self, screen: Surface) -> None:
        """FA TODO: Docstring."""
        self._draw_overlay(screen)
        self._layout_pause_menu(screen)
        for button in self.buttons:
            button.draw(screen)

    # =========================================================
    #   Layout
    # =========================================================
    def _layout_pause_menu(self, screen: Surface) -> None:
        """Calculate the title and button layout, then draws the title.

        The math is in PauseLayout. Here:
            1. calculate positions
            2. draw title (depends on the calculated Y)
            3. apply rect + selection to the buttons
        """
        block = self._pause_layout.compute(
            screen.get_width(),
            screen.get_height(),
            n_buttons=len(self.buttons),
        )

        # Titolo.
        title_surface = self.font_title.render("PAUSE")
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, block.title_center_y)
        )
        screen.blit(title_surface, title_rect)

        # Bottoni.
        for i, (button, rect) in enumerate(
            zip(self.buttons, block.button_rects)
        ):
            button.rect = rect
            button.set_selected(i == self.selected_index)

    # =========================================================
    #   Overlay
    # =========================================================
    def _draw_overlay(self, screen: Surface) -> None:
        """Disegna il gioco sotto, poi scurisce con un overlay nero."""
        # 1) Frame congelato della scena di gioco.
        self.game_page.draw(screen)

        # 2) Overlay semitrasparente pre-renderizzato.
        w, h = screen.get_size()
        if self._overlay is None or self._overlay.get_size() != (w, h):
            self._overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            self._overlay.fill((20, 20, 30, self.OVERLAY_ALPHA))
        screen.blit(self._overlay, (0, 0))

    # =========================================================
    #   Buttons
    # =========================================================
    def _create_buttons(self) -> None:
        options = [
            ("Resume",    self._resume_game),
            ("Settings",  self._show_impostazioni),
            ("Main menu", self._go_main_menu),
        ]
        for label, callback in options:
            # Rect placeholder: posizionato in _layout_pause_menu.
            rect = pygame.Rect(0, 0, 10, 10)
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
        """Resumes the existing GamePage (same instance).

        The Page's `on_resume()` method (which resynchronizes the HUD)
        is automatically invoked by `GameApp.switch_scene()`.
        """
        self.app.switch_scene(self.game_page)

    def _go_main_menu(self) -> None:
        from .main_menu import MainMenu
        self.app.switch_scene(MainMenu(self.app))

    def _show_impostazioni(self) -> None:
        """Show the page with the game's cheating settings."""
        from .cheat import CheatPage
        self.app.switch_scene(CheatPage(self.app))
