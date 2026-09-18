"""Game layout calculator for three-column Pac-Man screen."""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class PanelRect:
    """Fa TODO: Docstring."""

    x: int
    y: int
    width: int
    height: int

    def to_pygame_rect(self) -> pygame.Rect:
        """Fa TODO: Docstring."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def split_horizontal(
        self, ratio: float = 0.5
    ) -> tuple["PanelRect", "PanelRect"]:
        """Dividi in alto (ratio) e basso (1-ratio)."""
        top_h = int(self.height * ratio)
        top = PanelRect(self.x, self.y, self.width, top_h)
        bottom = PanelRect(
            self.x, self.y + top_h, self.width, self.height - top_h
        )
        return top, bottom

    def split_vertical(
        self, ratio: float = 0.5
    ) -> tuple["PanelRect", "PanelRect"]:
        """Dividi in sinistra (ratio) e destra (1-ratio)."""
        left_w = int(self.width * ratio)
        left = PanelRect(self.x, self.y, left_w, self.height)
        right = PanelRect(
            self.x + left_w, self.y, self.width - left_w, self.height
        )
        return left, right

    def split_bottom(
        self, ratio: float
    ) -> tuple["PanelRect", "PanelRect"]:
        """Dividi in top (1-ratio) e bottom (ratio).

        Il bottom ha altezza `ratio * height` ed è ancorato al fondo
        del rect. Utile per pannelli "fissati in basso" (vite, logo).
        """
        bottom_h = int(self.height * ratio)
        top = PanelRect(
            self.x, self.y, self.width, self.height - bottom_h
        )
        bottom = PanelRect(
            self.x,
            self.y + self.height - bottom_h,
            self.width,
            bottom_h,
        )
        return top, bottom


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
        min_maze_margin: int = 8,
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
            min_maze_margin: Minimum margin (in pixels) around the maze.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.min_tile_size = min_tile_size
        self.side_panel_ratio = side_panel_ratio
        self.top_padding = top_padding
        self.bottom_padding = bottom_padding
        self.min_maze_margin = min_maze_margin
        self.left_panel: PanelRect = PanelRect(0, 0, 0, 0)
        self.right_panel: PanelRect = PanelRect(0, 0, 0, 0)
        self.center_panel: PanelRect = PanelRect(0, 0, 0, 0)
        self.maze_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.tile_size = 0
        self.too_small = False
        self.compute()

    def compute(self) -> None:
        """Compute the panel rectangles, maze rect, and tile size.

        Ordine:
          1. Dimensioni colonne (left / center / right).
          2. Tile size: min tra vincolo orizzontale e verticale.
          3. Clamp per garantire `min_maze_margin` attorno al maze.
          4. maze_rect (centrato nell'area).
          5. Pannelli laterali allineati al top del maze.
        """
        side_width = int(self.screen_width * self.side_panel_ratio)
        center_x = side_width
        center_width = self.screen_width - 2 * side_width

        # --- 1. Area disponibile (con padding) ---
        avail_width = center_width
        avail_height = (
            self.screen_height - self.top_padding - self.bottom_padding
        )

        # --- 2. Tile size base ---
        if self.maze_width > 0 and self.maze_height > 0:
            self.tile_size = min(
                avail_width // self.maze_width,
                avail_height // self.maze_height,
            )
        else:
            self.tile_size = 0

        # --- 3. Clamp: margine minimo attorno al maze ---
        margin = self.min_maze_margin
        if self.maze_height > 0 and avail_height > 2 * margin:
            max_by_v = (avail_height - 2 * margin) // self.maze_height
            self.tile_size = min(self.tile_size, max_by_v)
        if self.maze_width > 0 and avail_width > 2 * margin:
            max_by_h = (avail_width - 2 * margin) // self.maze_width
            self.tile_size = min(self.tile_size, max_by_h)

        # --- 4. too_small + floor ---
        if self.tile_size < self.min_tile_size:
            self.too_small = True
            self.tile_size = self.min_tile_size
        else:
            self.too_small = False

        # --- 5. maze_rect (centrato nell'area disponibile) ---
        maze_pixel_width = self.maze_width * self.tile_size
        maze_pixel_height = self.maze_height * self.tile_size
        maze_x = center_x + (center_width - maze_pixel_width) // 2
        maze_y = (
            self.top_padding + (avail_height - maze_pixel_height) // 2
        )
        self.maze_rect = pygame.Rect(
            maze_x, maze_y, maze_pixel_width, maze_pixel_height
        )

        # --- 6. Pannelli allineati al top del maze ---
        # Alto e altezza dei pannelli = alto e altezza del maze.
        # Così score/lives/highscore/logo partono dalla stessa Y del
        # labirinto e finiscono insieme.
        panel_top = self.maze_rect.y
        panel_height = self.maze_rect.height
        self.left_panel = PanelRect(
            0, panel_top, side_width, panel_height
        )
        self.right_panel = PanelRect(
            self.screen_width - side_width,
            panel_top,
            side_width,
            panel_height,
        )
        self.center_panel = PanelRect(
            center_x, panel_top, center_width, panel_height
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
