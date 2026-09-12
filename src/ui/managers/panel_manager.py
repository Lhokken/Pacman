"""Manages creation of side panels for the game UI."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .font_manager import FontManager

from ..components.panels import (
    ScorePanel,
    LivesPanel,
    HighscorePanel,
    FruitPanel,
)
from ..layout.game_layout import GameLayout


class PanelManager:
    """Creates and holds references to side panels.

    The manager uses the game layout and fonts to instantiate panels.
    It also provides placeholder data updates.
    """

    def __init__(
        self,
        layout: GameLayout,
        fonts: FontManager,
        assets_base: Path,
        tile_size: int,
    ) -> None:
        """Initialize the panel manager and create the UI panels.

        Args:
            layout: Game layout containing the panel rectangles to draw into.
            fonts: Font manager providing the predefined bitmap fonts.
            assets_base: Base path used to locate icon assets.
            tile_size: Tile size used for icon scaling.
        """
        self.layout = layout
        self.fonts = fonts
        self.assets_base = assets_base
        self.tile_size = tile_size
        self._create_panels()

    # =======================================================================
    #   Metodi pubblici
    # =======================================================================
    def update_score(self, score: int) -> None:
        """Update the displayed score value.

        Args:
            score: The current score to show in the score panel.
        """
        self.score_panel.update_score(score)

    def update_lives(self, lives: int) -> None:
        """Update the number of remaining lives to display.

        Args:
            lives: The remaining number of lives.
        """
        self.lives_panel.update_lives(lives)

    def update_highscore(self, highscore: int) -> None:
        """Update the displayed high score value.

        Args:
            highscore: The current high score to show.
        """
        self.highscore_panel.update_highscore(highscore)

    def update_fruit_count(self, count: int) -> None:
        """Update the number of fruit icons shown in the fruit panel.

        Args:
            count: The number of fruits currently available to display.
        """
        self.fruit_panel.update_count(count)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all registered panels on the given screen surface.

        Args:
            screen: The pygame surface on which the UI panels are rendered.
        """
        self.score_panel.draw(screen)
        self.lives_panel.draw(screen)
        self.highscore_panel.draw(screen)
        self.fruit_panel.draw(screen)

    # =======================================================================
    #   Metodi privati
    # =======================================================================
    def _create_panels(self) -> None:
        """Create all panel instances from the configured layout rectangles.

        The left and right panel areas are split into their top and bottom
        sections, and each individual panel is instantiated with the
        corresponding font and icon configuration.
        """
        # --------------------------------------------------------------
        # Split panels
        # --------------------------------------------------------------
        left_rect = self.layout.left_panel.to_pygame_rect()
        right_rect = self.layout.right_panel.to_pygame_rect()

        # Split left panel into top (score) and bottom (lives)

        left_top_rect = pygame.Rect(
            left_rect.x,
            left_rect.y,
            left_rect.width,
            left_rect.height // 2
        )
        left_bottom_rect = pygame.Rect(
            left_rect.x,
            left_rect.y + left_rect.height // 2,
            left_rect.width,
            left_rect.height // 2,
        )

        # Split right panel into top (highscore) and bottom (fruit)

        right_top_rect = pygame.Rect(
            right_rect.x,
            right_rect.y,
            right_rect.width,
            right_rect.height // 2
        )
        right_bottom_rect = pygame.Rect(
            right_rect.x,
            right_rect.y + right_rect.height // 2,
            right_rect.width,
            right_rect.height // 2,
        )

        # --------------------------------------------------------------
        # Score panel
        # --------------------------------------------------------------
        self.score_panel = ScorePanel(
            left_top_rect,
            font_value=self.fonts.font_value_med,
            font_title=self.fonts.font_title_big,
        )

        # --------------------------------------------------------------
        # Lives panel
        # --------------------------------------------------------------
        self.lives_panel = LivesPanel(
            left_bottom_rect,
            self.fonts.font_white,
            self.fonts.font_title_small,
            pacman_icon_path=(
                self.assets_base
                / "player"
                / "animation"
                / "Player_start.png"
            ),
            icon_size=self.tile_size,
        )

        # --------------------------------------------------------------
        # Highscore panel
        # --------------------------------------------------------------
        self.highscore_panel = HighscorePanel(
            right_top_rect,
            font_value=self.fonts.font_value_med,
            font_title=self.fonts.font_title_big,
        )

        # --------------------------------------------------------------
        # Fruit panel
        # --------------------------------------------------------------
        self.fruit_panel = FruitPanel(
            right_bottom_rect,
            self.fonts.font_white,
            self.fonts.font_title_small,
            fruit_icon_path=self.assets_base / "fruit" / "cherry.png",
            icon_size=self.tile_size,
            initial_count=3,
        )

        # --------------------------------------------------------------
        # Placeholder data
        # --------------------------------------------------------------
        self.update_score(0)
        self.update_lives(3)
        self.update_highscore(0)
        self.update_fruit_count(3)
