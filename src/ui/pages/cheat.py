"""Cheat page for enabling/disabling debug features.

Flow:
      GamePage  --ESC   --> PauseMenu --Settings--> CheatPage
      CheatPage --Back  --> PauseMenu (SAME GamePage)
      PauseMenu --Resume--> GamePage (timer resumed)

The `GamePage` received by the constructor is **reused**,
never recreated:
the HUD timer survives the pause -> settings -> pause cycle.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

import pygame
from pygame.surface import Surface

from ..scene import Scene
from ..components.button import Button
from ..configUI.ui_config import FontRole
from ..layout.cheat_layout import CheatLayout

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class CheatPage(Scene):
    """Scena per attivare/disattivare le opzioni cheat.

    Pensata per la peer review: mostra una lista di toggle navigabili
    da tastiera e una voce "Back" per tornare alla schermata
    precedente senza ricreare la partita.
    """

    # ================================================================
    #   Stato dei cheat
    #
    #   TODO: ATTACCA AL CORE
    #   Questi flag devono vivere nello stato di partita (es.
    #   core/game/state.py) e essere letti da PacmanPlayer / GhostBase
    #   / orchestratore. Qui sono attributi di CLASSE solo per non
    #   perderli tra un'apertura e l'altra della pagina: una nuova
    #   istanza di CheatPage viene creata ad ogni switch_scene.
    # ================================================================

    invincible: bool = False
    data_debug: bool = False
    ghost_freeze: bool = False
    extra_lives: bool = False
    increased_speed: bool = False
    # ----------------------------------------------------------------
    #   Etichette
    # ----------------------------------------------------------------
    _TOGGLES: tuple[tuple[str, str], ...] = (
        (
            "Invincibility", "invincible"
        ),
        (
            "Data Debug", "data_debug"
        ),
        (
            "Ghost Freeze", "ghost_freeze"
        ),
        (
            "Extra Lives", "extra_lives"
        ),
        (
            "Increased Speed", "increased_speed"
        ),
    )

    # ================================================================
    #   Init
    # ================================================================
    def __init__(
        self,
        app: GameApp,
        game_page: Scene | None = None,
    ) -> None:
        """Initialize the cheat page.

        Args:
            app: Instance of `GameApp`.
            game_page: The active `GamePage` from which the user arrived
            (via `PauseMenu`). If `None`, the page was opened from the
            `MainMenu`: the Back action will return there.
        """
        super().__init__(app)
        # --------------------------------------------------------------
        #   Reference the active match. Do NOT recreate it.
        # --------------------------------------------------------------
        self.game_page = game_page
        # --------------------------------------------------------------
        #   FONT
        # --------------------------------------------------------------
        # shared by Scenes. No local FontManager.
        self.font_title = self.theme.font_config(FontRole.HEADING)
        self.font_option = self.theme.font_config(FontRole.OPTION)
        self.font_option_selected = (
            self.theme.font_config(FontRole.OPTION_SELECTED)
        )

        self.buttons: list[Button] = []
        self._create_buttons()

        self.selected_index = 0
        self._cheat_layout = CheatLayout()

    # ================================================================
    #   CREATE BUTTONS
    # ================================================================
    def _create_buttons(self) -> None:
        """Create the toggle buttons and the "Back" button."""
        for label, attr_name in self._TOGGLES:
            rect = pygame.Rect(0, 0, 500, 50)

            # --------------------------------------------------------------
            #   Closure per catturare attr_name
            # --------------------------------------------------------------
            def make_toggle_callback(attr: str) -> Callable[[], None]:
                def callback() -> None:
                    self._toggle(attr)
                return callback

            state = getattr(self, attr_name)
            text = f"{label}: {'ON' if state else 'OFF'}"
            self.buttons.append(Button(
                rect,
                text,
                self.font_option,
                self.font_option_selected,
                on_select=make_toggle_callback(attr_name),
            ))

        self.buttons.append(Button(
            pygame.Rect(0, 0, 200, 50),
            "Back",
            self.font_option,
            self.font_option_selected,
            on_select=self._go_back,
        ))

    # ================================================================
    #   Logica toggle
    # ================================================================
    def _toggle(self, attr_name: str) -> None:
        """Toggles the specified flag and updates the UI and core.

        Args:
            attr_name: Name of the boolean attribute to toggle.
        """
        setattr(self, attr_name, not getattr(self, attr_name))
        self._update_toggle_texts()
        self._apply_cheats()

    def _update_toggle_texts(self) -> None:
        """Rewrites the label of each toggle based on its state."""
        for i, (label, attr_name) in enumerate(self._TOGGLES):
            state = getattr(self, attr_name)
            self.buttons[i].set_text(
                f"{label}: {'ON' if state else 'OFF'}"
            )

    def _apply_cheats(self) -> None:
        """Propagates the cheat state to the current match.

        This page only owns the toggle controls. When opened from a live
        match, it must forward the complete state through the existing
        GamePage instance; GamePage will then delegate to the core.

        The flow is:
            GamePage -> PauseMenu -> CheatPage -> same GamePage -> core

        No match exists when this page is opened from the main menu, so
        there is nothing to update in that case.

        TODO(core-integration): Replace the commented call below with the
        GamePage adapter once `GamePage.apply_cheats()` exists. Pass boolean
        values, not "ON"/"OFF" strings, and keep this page unaware of how
        each cheat changes gameplay.
        """
        if self.game_page is None:
            return
        # Activate this adapter when GamePage exposes the core method.
        # self.game_page.apply_cheats({
        #     name: getattr(self, name) for _, name in self._TOGGLES
        # })

    # ================================================================
    #   Navigazione
    # ================================================================
    def _go_back(self) -> None:
        """Return to where we came from, without recreating the game.

        - `game_page` present -> `PauseMenu`, with the SAME `GamePage`.
        - `game_page` absent  -> `MainMenu`.
        """
        if self.game_page is not None:
            from .pause_menu import PauseMenu
            self.app.switch_scene(
                PauseMenu(self.app, self.game_page)
            )
        else:
            from .main_menu import MainMenu
            self.app.switch_scene(MainMenu(self.app))

    # ================================================================
    #   Layout
    # ================================================================
    def _layout_buttons(self, screen_w: int, screen_h: int) -> int:
        """Positions the title and buttons using `CheatLayout`.

        Args:
            screen_w: Screen width in pixels.
            screen_h: Screen height in pixels.

            Returns:
            The Y-coordinate of the title's center.
        """
        block = self._cheat_layout.compute(
            screen_w, screen_h,
            n_buttons=len(self.buttons),
        )
        for i, (button, rect) in enumerate(
            zip(
                  self.buttons,
                  block.button_rects
            )
        ):
            button.rect = rect
            button.set_selected(i == self.selected_index)
        return block.title_center_y

    # ================================================================
    #   Lifecycle
    # ================================================================
    def handle_events(self) -> None:
        """Handle input events for the cheat page.

        Supports navigation using the up/down arrow keys, confirmation with
        Enter, and exiting with Esc (equivalent to the "Back" button).
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
                elif event.key == pygame.K_ESCAPE:
                    self._go_back()

    def draw(self, screen: Surface) -> None:
        """Draws the title and buttons on the surface.

        Args:
            screen: Target surface.
        """
        screen.fill(self.theme.palette.DARK)

        # TITLE ------------------------------------------
        title_y = self._layout_buttons(
            screen.get_width(), screen.get_height()
        )
        title = (
              self.font_title.render("Cheats")
        )
        # SCREEN ------------------------------------------
        screen.blit(
            title,
            title.get_rect(
                center=(screen.get_width() // 2, title_y)
            ),
        )
        # BUTTON ------------------------------------------
        for button in self.buttons:
            button.draw(screen)
