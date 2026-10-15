"""Game page layout.

Compose `GameLayout` nd add the page metrics.
"""

from __future__ import annotations

import pygame

from dataclasses import dataclass
from .game_layout import GameLayout


@dataclass(frozen=True)
class GamePageMetrics:
    """Snapshot of the game page's calculated layout metrics."""

    panel_layout: GameLayout           # grid + maze (from GameLayout)
    maze_origin: tuple[int, int]       # top-left of the maze in pixels
    tile_size: int                     # side of a cell in pixels
    too_small: bool                    # True = window too small
    hud_rect: pygame.Rect              # HUD area (countdown)


class GamePageLayout:
    """Responsive metrics for the game page."""

    # ===============================================================
    #   Grid/panels (switched to GameLayout)
    # ===============================================================
    SIDE_PANEL_RATIO: float = 0.2
    MIN_TILE_SIZE: int = 16
    TOP_PADDING: int = 48
    BOTTOM_PADDING: int = 48
    MIN_MAZE_MARGIN: int = 8
    # ===============================================================
    #   HUD: position (screen fractions)
    # ===============================================================
    HUD_X_RATIO: float = 0.5
    HUD_Y_RATIO: float = 0.05
    HUD_W_RATIO: float = 0.4
    HUD_H_RATIO: float = 0.06

    def __init__(self, **overrides: dict) -> None:
        """Initialize the layout with optional class-attribute overrides.

        Args:
            overrides : Layout attribute names and replacement values.

        Raises:
            AttributeError : If an override name is not a layout attribute.
        """
        for key, value in overrides.items():
            if not hasattr(type(self), key):
                raise AttributeError(
                    f"Unknown layout ratio: {key!r}. "
                    f"Valid keys are GamePageLayout class attributes."
                )
            setattr(self, key, value)

    def compute(
        self,
        screen_w: int,
        screen_h: int,
        maze_w: int,
        maze_h: int,
    ) -> GamePageMetrics:
        """Calculate the grid and the derived metrics."""
        grid = GameLayout(
            screen_w,
            screen_h,
            maze_w,
            maze_h,
            min_tile_size=self.MIN_TILE_SIZE,
            side_panel_ratio=self.SIDE_PANEL_RATIO,
            top_padding=self.TOP_PADDING,
            bottom_padding=self.BOTTOM_PADDING,
        )

        hud_rect = pygame.Rect(0, 0, 0, 0)
        hud_rect.width = int(screen_w * self.HUD_W_RATIO)
        hud_rect.height = int(screen_h * self.HUD_H_RATIO)
        hud_rect.center = (
            int(screen_w * self.HUD_X_RATIO),
            int(screen_h * self.HUD_Y_RATIO),
        )

        return GamePageMetrics(
            panel_layout=grid,
            maze_origin=grid.get_maze_origin(),
            tile_size=grid.tile_size,
            too_small=grid.is_too_small(),
            hud_rect=hud_rect,
        )
