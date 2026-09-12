"""Renders the maze using preloaded tile surfaces."""

from __future__ import annotations

import pygame

from ..managers.asset_manager import AssetManager


class MazeRenderer:
    """Draws the maze walls and border using tile images.

    This class is independent from the game logic; it only needs the
    maze matrix and the asset manager.
    """

    def __init__(self, maze: list[list[int]], assets: AssetManager) -> None:
        """Initialize with maze data and asset manager.

        Args:
            maze: 2D list of cell wall bitmasks.
            assets: AssetManager containing tile surfaces.
        """
        self.maze = maze
        self.assets = assets
        self.height = len(maze)
        self.width = len(maze[0]) if self.height > 0 else 0

    def draw(
        self,
        screen: pygame.Surface,
        origin_x: int,
        origin_y: int,
        tile_size: int,
    ) -> None:
        """Draw the complete maze (walls, intersections, border)."""
        # 1. Single-line wall segments
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                mask = cell & 15
                if mask == 0:
                    continue
                tile = self.assets.wall_tiles.get(mask)
                if tile is not None:
                    screen.blit(
                        tile,
                        (
                            origin_x + x * tile_size,
                            origin_y + y * tile_size,
                        ),
                    )

        # 2. Intersection tiles at internal vertices
        for y_vert in range(1, self.height):
            for x_vert in range(1, self.width):
                mask = self._get_intersection_mask(x_vert, y_vert)
                if mask == 0:
                    continue
                tile = self.assets.intersection_tiles.get(mask)
                if tile is not None:
                    tile_rect = tile.get_rect(
                        center=(
                            origin_x + x_vert * tile_size,
                            origin_y + y_vert * tile_size,
                        )
                    )
                    screen.blit(tile, tile_rect)

        # 3. Outer double-line border
        border = self.assets.border_tiles
        # Corners
        screen.blit(border["corner_tl"], (origin_x, origin_y))
        screen.blit(
            border["corner_tr"],
            (origin_x + (self.width - 1) * tile_size, origin_y),
        )
        screen.blit(
            border["corner_bl"],
            (origin_x, origin_y + (self.height - 1) * tile_size),
        )
        screen.blit(
            border["corner_br"],
            (
                origin_x + (self.width - 1) * tile_size,
                origin_y + (self.height - 1) * tile_size,
            ),
        )
        # Top/bottom edges
        for x in range(1, self.width - 1):
            px = origin_x + x * tile_size
            screen.blit(border["top"], (px, origin_y))
            screen.blit(
                border["bottom"],
                (px, origin_y + (self.height - 1) * tile_size),
            )
        # Left/right edges
        for y in range(1, self.height - 1):
            py = origin_y + y * tile_size
            screen.blit(border["left"], (origin_x, py))
            screen.blit(
                border["right"],
                (origin_x + (self.width - 1) * tile_size, py),
            )

    def _get_intersection_mask(self, x_vert: int, y_vert: int) -> int:
        """Calculate the intersection mask at a vertex."""
        # Reuse logic from GamePage._get_intersection_mask
        mask = 0
        # Direction constants (matching original)
        WALL_RIGHT = 2
        WALL_BOTTOM = 4

        if (
            x_vert > 0
            and y_vert > 0
            and (self.maze[y_vert - 1][x_vert - 1] & WALL_RIGHT)
        ):
            mask |= 1
        if (
            x_vert > 0
            and y_vert < self.height
            and (self.maze[y_vert][x_vert - 1] & WALL_RIGHT)
        ):
            mask |= 2
        if (
            x_vert > 0
            and y_vert > 0
            and (self.maze[y_vert - 1][x_vert - 1] & WALL_BOTTOM)
        ):
            mask |= 4
        if (
            x_vert < self.width
            and y_vert > 0
            and (self.maze[y_vert - 1][x_vert] & WALL_BOTTOM)
        ):
            mask |= 8
        return mask
