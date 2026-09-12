"""Game layout calculator for three-column Pac-Man screen."""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class PanelRect:
    """Stores the rectangle for a side panel."""

    x: int
    y: int
    width: int
    height: int

    def to_pygame_rect(self) -> pygame.Rect:
        """Convert to pygame.Rect."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class GameLayout:
    """Calculates the layout for the game screen.

    The screen is divided into three columns:
    - Left panel (score, lives)
    - Center panel (maze)
    - Right panel (highscore, fruit)

    The maze is centered within the center panel while maintaining its
    aspect ratio. The tile size is computed dynamically based on the
    available space. If the window is too small to render a minimum
    tile size, `too_small` is set to True.

    Attributes:
        screen_width: Current window width.
        screen_height: Current window height.
        maze_width: Number of columns in the maze.
        maze_height: Number of rows in the maze.
        min_tile_size: Minimum acceptable tile size in pixels.
        side_panel_ratio: Fraction of screen width for each side panel.
        top_padding: Vertical padding (in pixels) above the maze.
        bottom_padding: Vertical padding (in pixels) below the maze.
        left_panel: Rectangle for the left panel.
        right_panel: Rectangle for the right panel.
        center_panel: Rectangle for the center area.
        maze_rect: Rectangle where the maze is drawn.
        tile_size: Size of each maze cell in pixels.
        too_small: True if the window is too small for min_tile_size.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        maze_width: int,
        maze_height: int,
        min_tile_size: int = 16,
        side_panel_ratio: float = 0.2,
        top_padding: int = 20,
        bottom_padding: int = 20,
    ) -> None:
        """Initialize layout parameters and compute rectangles.

        Args:
            screen_width: Current window width.
            screen_height: Current window height.
            maze_width: Number of columns in the maze.
            maze_height: Number of rows in the maze.
            min_tile_size: Minimum acceptable tile size in pixels.
            side_panel_ratio: Fraction of screen width for each side panel.
            top_padding: Vertical padding (in pixels) above the maze.
            bottom_padding: Vertical padding (in pixels) below the maze.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.min_tile_size = min_tile_size
        self.side_panel_ratio = side_panel_ratio
        self.top_padding = top_padding
        self.bottom_padding = bottom_padding
        self.left_panel: PanelRect = PanelRect(0, 0, 0, 0)
        self.right_panel: PanelRect = PanelRect(0, 0, 0, 0)
        self.center_panel: PanelRect = PanelRect(0, 0, 0, 0)
        self.maze_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.tile_size = 0
        self.too_small = False
        self.compute()

    def compute(self) -> None:
        """Compute the panel rectangles, maze rect, and tile size."""
        side_width = int(self.screen_width * self.side_panel_ratio)
        # ----------------------------------------------------------------
        # Left panel
        # ----------------------------------------------------------------
        self.left_panel = PanelRect(0, 0, side_width, self.screen_height)

        # ----------------------------------------------------------------
        # Right panel
        # ----------------------------------------------------------------
        self.right_panel = PanelRect(
            self.screen_width - side_width,
            0,
            side_width,
            self.screen_height,
        )

        # ----------------------------------------------------------------
        # Center panel (between side panels)
        # ----------------------------------------------------------------
        center_x = side_width
        center_width = self.screen_width - 2 * side_width
        self.center_panel = PanelRect(
            center_x, 0, center_width, self.screen_height
        )

        # ----------------------------------------------------------------
        # Available area for maze inside center panel, with padding
        # ----------------------------------------------------------------
        avail_width = center_width
        avail_height = (
            self.screen_height - self.top_padding - self.bottom_padding
        )
        if self.maze_width > 0 and self.maze_height > 0:
            self.tile_size = min(
                avail_width // self.maze_width,
                avail_height // self.maze_height,
            )
        else:
            self.tile_size = 0

        if self.tile_size < self.min_tile_size:
            self.too_small = True
            self.tile_size = self.min_tile_size
        else:
            self.too_small = False
        # ----------------------------------------------------------------
        # Maze rectangle (centered within the padded area)
        # ----------------------------------------------------------------
        maze_pixel_width = self.maze_width * self.tile_size
        maze_pixel_height = self.maze_height * self.tile_size
        maze_x = (
            center_x + (center_width - maze_pixel_width) // 2
        )
        maze_y = (
            self.top_padding + (avail_height - maze_pixel_height) // 2
        )
        self.maze_rect = pygame.Rect(
            maze_x, maze_y, maze_pixel_width, maze_pixel_height
        )

    def get_maze_origin(self) -> tuple[int, int]:
        """Return the top-left pixel of the maze."""
        return self.maze_rect.x, self.maze_rect.y

    def resize(self, screen_width: int, screen_height: int) -> None:
        """Recompute layout with new dimensions.

        Args:
            screen_width: New window width.
            screen_height: New window height.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.compute()

    def is_too_small(self) -> bool:
        """Return True if the window is too small to display the maze."""
        return self.too_small
