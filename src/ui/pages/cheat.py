
"""Cheat page for enabling/disabling debug features."""

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


class CheatPage(Scene):
    """Scene for toggling cheat options (for peer review)."""

    def __init__(self, app: GameApp) -> None:
        super().__init__(app)

        file_path = Path(__file__).resolve()
        assets_base = file_path.parent.parent.parent.parent / "assets" / "img"
        # ====================================================================
        #   TODO: Replace with self.fonts = self.app.font_manager
        #         (use cached instance)
        # ====================================================================
        self.fonts = FontManager(assets_base)
        self.font_title = self.fonts.font_title_big
        self.font_option = self.fonts.font_white
        self.font_option_selected = self.fonts.font_title_small
        # ====================================================================
        #   PLACEHOLDER - Cheat state (persona B collega la logica reale)
        # ====================================================================
        self.invincible = False
        self.level_skip = False
        self.ghost_freeze = False
        self.extra_lives = False
        self.increased_speed = False

        self.buttons: list[Button] = []
        self._create_buttons()
        self.selected_index = 0

    def _create_buttons(self) -> None:
        """Create toggle buttons and back button."""
        # ---------------------------------------------------------------------
        #   PLACEHOLDER -  Toggle options with dynamic text (updated later)
        # ---------------------------------------------------------------------
        self.toggles = [
            (
                "Invincibility",
                "invincible"
            ),
            (
                "Level Skip", "level_skip"
            ),
            (
                "Ghost Freeze",
                "ghost_freeze"
            ),
            (
                "Extra Lives",
                "extra_lives"
            ),
            (
                "Increased Speed",
                "increased_speed"
            ),
        ]
        for i, (label, attr_name) in enumerate(self.toggles):
            rect = pygame.Rect(0, 0, 400, 50)

            # Use a closure to capture attr_name and avoid type
            # inference issues
            def make_toggle_callback(attr: str):
                def callback() -> None:
                    self._toggle(attr)
                return callback
            button = Button(
                rect,
                f"{label}: OFF",
                self.font_option,
                self.font_option_selected,
                on_select=make_toggle_callback(attr_name),
            )
            self.buttons.append(button)
        # ---------------------------------------------------------------------
        #   Back button
        # ---------------------------------------------------------------------
        back_rect = pygame.Rect(0, 0, 200, 50)
        back_button = Button(
            back_rect,
            "Back",
            self.font_option,
            self.font_option_selected,
            on_select=self._go_back,
        )
        self.buttons.append(back_button)

    # ========================================================================
    # Private methods for button callbacks
    # ========================================================================

    def _toggle(self, attr_name: str) -> None:
        """Toggle the given cheat attribute and update button text."""
        current = getattr(self, attr_name)
        setattr(self, attr_name, not current)
        self._update_toggle_texts()

    def _update_toggle_texts(self) -> None:
        """Refresh button texts to reflect current state."""
        for i, (label, attr_name) in enumerate(self.toggles):
            state = getattr(self, attr_name)
            on_off = "ON" if state else "OFF"
            self.buttons[i].set_text(f"{label}: {on_off}")

    def _go_back(self) -> None:
        from .main_menu import MainMenu
        self.app.switch_scene(MainMenu(self.app))

    def _layout_buttons(self, screen_width: int, screen_height: int) -> None:
        """Position buttons vertically centered."""
        # -----------------------------------------------------
        # Layout buttons vertically centered with spacing
        # -----------------------------------------------------
        start_y = 150
        spacing = 60
        # total_buttons = len(self.buttons)
        for i, button in enumerate(self.buttons):
            button.rect.width = 500
            button.rect.height = 50
            button.rect.center = (screen_width // 2, start_y + i * spacing)
            button.set_selected(i == self.selected_index)

    # =======================================================================
    #   Public methods for scene interface
    # =======================================================================
    def handle_events(self) -> None:
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

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((0, 0, 0))
        # ---------------------------------------------------------------------
        # Title
        # ---------------------------------------------------------------------
        title_surface = self.font_title.render("Cheats")
        title_rect = (
            title_surface.get_rect(center=(screen.get_width() // 2, 80))
        )
        screen.blit(title_surface, title_rect)
        # ---------------------------------------------------------------------
        # Layout and draw buttons
        # ---------------------------------------------------------------------
        self._layout_buttons(screen.get_width(), screen.get_height())
        for button in self.buttons:
            button.draw(screen)
