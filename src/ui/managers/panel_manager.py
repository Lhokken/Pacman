"""Manages creation of side panels for the game UI.

The manager acts as the sole point of contact between the HUD and the
panels: it exposes update/draw methods for each, so the game does not
need that different classes exist.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pygame.surface import Surface

if TYPE_CHECKING:
    from .font_manager import FontManager

from ..components.panels import (
    ScorePanel,
    LivesPanel,
    HighscorePanel,
    LogoPanel,
)
from ..layout.game_layout import GameLayout


class PanelManager:
    """Creates and maintains the HUD side panels."""

    # Fraction of the side panel height reserved for the bottom
    # docked panel. Score/Highscore takes the remainder at the top.
    LIVES_BOTTOM_RATIO: float = 0.22
    LOGO_BOTTOM_RATIO: float = 0.35

    # ------------------------------------------------------------------
    #   Init
    # ------------------------------------------------------------------
    def __init__(
        self,
        layout: GameLayout,
        fonts: FontManager,
        assets_base: Path,
        tile_size: int,
    ) -> None:
        """Mette TODO: Docstring."""
        self.layout = layout
        self.fonts = fonts
        self.assets_base = assets_base
        self.tile_size = tile_size
        self._create_panels()

    # ==================================================================
    #   UPDATE STATUS
    # ==================================================================
    def update_score(self, score: int) -> None:
        """Update score in pannel."""
        self.score_panel.update_value(score)

    def update_lives(self, lives: int) -> None:
        """Update lives in pannel."""
        self.lives_panel.update_count(lives)

    def update_highscore(self, highscore: int) -> None:
        """Update highscore in pannel."""
        self.highscore_panel.update_value(highscore)

    # ==================================================================
    #   DAW PANNELS
    # ==================================================================
    def draw(self, screen: Surface) -> None:
        """Disegna i pannelli.

        Score/Highscore occupano la fascia superiore del pannello laterale
        (1 - ratio). Lives/Logo occupano la fascia inferiore (ratio),
        ancorata al fondo del labirinto.
        """
        # Panel layout --------------------------------------------------
        self.score_panel.draw(screen)      # LEFT  TOP    : ScorePanel
        self.lives_panel.draw(screen)      # LEFT  BOTTOM : LivesPanel
        self.highscore_panel.draw(screen)  # RIGHT TOP    : HighscorePanel
        self.logo_panel.draw(screen)       # RIGHT BOTTOM : LogoPanel

    # ==================================================================
    #   Relayout
    # ==================================================================
    def relayout(self, layout: GameLayout, tile_size: int) -> None:
        """Repositions existing panels without losing their state.

        Updates the rects of each panel based on the new layout.
        If `tile_size` is changed, the iconic panels reload their
        icons at the new size (score, lives, and highscore remain).

        Called by GamePage.on_resize(). DO NOT recreate the panels:
        recreating them would reset the current score/lives/highscore.

        Args:
            layout: new GameLayout calculated upon resize.
            tile_size: new tile size in pixels.
        """
        self.layout = layout
        self.tile_size = tile_size

        left_top, left_bottom = self.layout.left_panel.split_bottom(
            self.LIVES_BOTTOM_RATIO
        )
        right_top, right_bottom = self.layout.right_panel.split_bottom(
            self.LOGO_BOTTOM_RATIO
        )

        self.score_panel.rect = left_top.to_pygame_rect()
        self.lives_panel.rect = left_bottom.to_pygame_rect()
        self.highscore_panel.rect = right_top.to_pygame_rect()
        self.logo_panel.rect = right_bottom.to_pygame_rect()
        # -------------------------------------------------------------------
        #   Icone ricaricate solo se il tile_size è cambiato.
        # --------------------------------------------------------------------
        self.lives_panel.set_icon_size(tile_size)

    # ==================================================================
    #   CREATION OF PANELS
    # ==================================================================
    def _create_panels(self) -> None:
        """Instantiate the four panels from the two columns of the layout."""
        # PANEL LAYOUT --------------------------------------------------------
        left_top, left_bottom = self.layout.left_panel.split_bottom(
            self.LIVES_BOTTOM_RATIO
        )
        right_top, right_bottom = self.layout.right_panel.split_bottom(
            self.LOGO_BOTTOM_RATIO
        )
        # Score/Highscore at the top, Lives/Logo anchored to the bottom.
        # Same split as `relayout`, so the first frame is consistent
        # with the state after a resize.
        # SCORE PANNEL --------------------------------------------------------
        self.score_panel = ScorePanel(
            left_top.to_pygame_rect(),
            font_value=self.fonts.font_value_big,
            font_title=self.fonts.font_title_big,
        )
        # LIVES PANNEL --------------------------------------------------------
        self.lives_panel = LivesPanel(
            left_bottom.to_pygame_rect(),
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
        # HIGHTSCORE PANNEL ---------------------------------------------------
        self.highscore_panel = HighscorePanel(
            right_top.to_pygame_rect(),
            font_value=self.fonts.font_value_big,
            font_title=self.fonts.font_title_big,
        )
        # LOGO PANNEL ---------------------------------------------------------
        self.logo_panel = LogoPanel(
            right_bottom.to_pygame_rect(),
            font=self.fonts.font_white,
            title_font=self.fonts.font_title_small,
            logo_path=(
                    self.assets_base
                    / "logo"
                    / "42_logo"
                    / "42_logo_light.png"
            ),
        )
        # ----------------------------------------------------------------------
        #   START: Valori iniziali.
        # ----------------------------------------------------------------------
        self.update_score(0)
        self.update_lives(3)
        self.update_highscore(0)
