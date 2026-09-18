"""Main menu for Pac-Man using bitmap fonts and Button components.

Layout del blocco [titolo + bottoni]: delegato a `MenuLayout`.
La matematica di posizionamento vive là; qui solo il collegamento
tra il layout calcolato e le entità della scena.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

from ..components.button import Button
from ..scene import Scene
from ..layout.menu_layout import MenuLayout

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class MainMenu(Scene):
    """Main menu scene.

    Il titolo PAC-MAN e il brand 42+SCHOOL sono parte del layout del
    menu, mentre i bottoni formano un blocco centrato nello schermo.
    La scena resta una semplice schermata navigabile senza alcuna
    animazione di intro o parata.
    """

    # =========================================================
    #   Init
    # =========================================================
    def __init__(self, app: GameApp) -> None:
        """Fa TODO: Docstring."""
        super().__init__(app)

        fonts = app.font_manager
        self.font_title = fonts.font_title_extraLarge
        self.font_option = fonts.font_value_med
        self.font_option_selected = fonts.font_value_med_y

        self._menu_layout = MenuLayout()
        self.title_surface = self.font_title.render("PAC-MAN")

        self.selected_index = 0
        self.buttons: list[Button] = []
        self._create_buttons()

    # =========================================================
    #   Lifecycle
    # =========================================================
    def handle_events(self) -> None:
        """Fa TODO: Docstring."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)

    def _handle_key(self, event: pygame.event.Event) -> None:
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
        elif event.key == pygame.K_g:
            from .game_over import GameOverPage
            self.app.switch_scene(GameOverPage(self.app, score=123))
        elif event.key == pygame.K_v:
            from .victory_screen import VictoryPage
            self.app.switch_scene(VictoryPage(self.app, score=456))

    def draw(self, screen: Surface) -> None:
        """Draw the Menu in screen."""
        screen.fill((20, 20, 30))

        self._layout_menu_block(screen)

        title_rect = self.title_surface.get_rect(
            center=(
                screen.get_width() // 2, self._title_center_y
            )
        )
        screen.blit(self.title_surface, title_rect)

        for button in self.buttons:
            button.draw(screen)

    def _layout_menu_block(self, screen: Surface) -> None:
        """Calcola il layout del titolo e dei pulsanti del menu."""
        block = self._menu_layout.compute_block(
            screen.get_width(),
            screen.get_height(),
            title_h=self.title_surface.get_height(),
            brand_y=int(screen.get_height() * 0.12),
            nbr_btn=len(self.buttons),
        )
        self._title_center_y = block.center_titolo_y

        for i, (button, rect) in enumerate(
            zip(self.buttons, block.button_rect)
        ):
            button.rect = rect
            button.set_selected(i == self.selected_index)

    # =========================================================
    #   Buttons
    # =========================================================
    def _create_buttons(self) -> None:
        """Create the Menu buttons.

        The size (rect) is a placeholder.
        It is redefined every frame by _layout_menu_block.
        """
        options = [
            ("Start Game",       self._start_game),
            ("View Highscores",  self._show_highscores),
            ("Instructions",     self._show_instructions),
            ("Settings",         self._show_impostazioni),
            ("Exit",             self._exit_game),
        ]
        for label, callback in options:
            rect = pygame.Rect(0, 0, 10, 10)   # segnaposto!
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
        """Manage the start of the game."""
        from .game_page import GamePage
        self.app.switch_scene(GamePage(self.app))

    def _show_highscores(self) -> None:
        logger.info(
            "Highscores requested (not yet implemented)"
        )

    def _show_instructions(self) -> None:
        """Show the game instructions page."""
        # from .instruction_page import InstructionPage
        # self.app.switch_scene(InstructionPage(self.app))
        logger.info(
            "InstructionPage requested (not yet implemented)"
        )

    def _show_impostazioni(self) -> None:
        """Show the page with the game's cheating settings."""
        from .cheat import CheatPage
        self.app.switch_scene(CheatPage(self.app))

    def _exit_game(self) -> None:
        """Must Exits the game."""
        self.app.running = False
