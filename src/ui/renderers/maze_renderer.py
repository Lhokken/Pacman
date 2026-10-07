"""Renders the maze using preloaded tile surfaces."""

from __future__ import annotations

import pygame

from ..managers.asset_manager import AssetManager


class MazeRenderer:
    """Draws the maze walls and border using tile images.

    This class is independent from the game logic; it only needs the
    maze matrix and the asset manager.
    """

    # Wall bitmask: bit acceso se il muro esiste in quella direzione.
    WALL_TOP = 1
    WALL_RIGHT = 2
    WALL_BOTTOM = 4
    WALL_LEFT = 8
    WALL_MASK = 0xF     # 4 bit: top | right | bottom | left

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
        self._wall_grid = self._normalize_walls()

    # =========================================================================
    #   DRAW
    # =========================================================================
    def draw(
        self,
        screen: pygame.surface.Surface,
        origin_x: int,
        origin_y: int,
        tile_size: int,
    ) -> None:
        """Draw the complete maze (walls, intersections, border).

        Richiede che `assets.wall_tiles` e `assets.intersection_tiles`
        siano già validati: `AssetManager` solleva
        `MissingRequiredAssetsError` in `_ensure_assets_available()` se
        mancano. La cornice è opzionale (fallback all-or-nothing gestito
        dall'AssetManager).
        """
        wall_masks = self._get_wall_render_masks()
        self._draw_walls(screen, origin_x, origin_y, tile_size, wall_masks)
        self._draw_intersections(screen, origin_x, origin_y, tile_size)
        self._draw_border(screen, origin_x, origin_y, tile_size)

    # ------------------------------------------------------------------
    def _draw_walls(
        self,
        screen: pygame.surface.Surface,
        zero_x: int,
        zero_y: int,
        tile_size: int,
        wall_masks: list[list[int]],
    ) -> None:
        """Disegna i segmenti interni non sostituiti da un'intersezione."""
        connectors = self.assets.border_wall_tiles
        for y, row in enumerate(wall_masks):
            for x, cell in enumerate(row):
                if cell == 0:
                    continue

                connector_names = self._get_border_connector_names(x, y, cell)
                connector_mask = 0
                for name in connector_names:
                    connector_mask |= (
                        self.WALL_TOP if name in ("left", "right")
                        else self.WALL_LEFT
                    )

                if (
                    connector_names
                    and connector_mask == cell
                    and all(name in connectors for name in connector_names)
                ):
                    for name in connector_names:
                        screen.blit(
                            connectors[name],
                            (zero_x + x * tile_size, zero_y + y * tile_size),
                        )
                    continue

                tile = self.assets.wall_tiles.get(cell)
                if tile is None:
                    continue
                screen.blit(
                    tile,
                    (zero_x + x * tile_size, zero_y + y * tile_size),
                )

    def _get_border_connector_names(
        self, x: int, y: int, mask: int
    ) -> list[str]:
        """Return connector directions for wall arms ending at the frame."""
        connectors: list[str] = []
        if mask & self.WALL_TOP:
            if x == 0:
                connectors.append("right")
            elif x == self.width - 1:
                connectors.append("left")
        if mask & self.WALL_LEFT:
            if y == 0:
                connectors.append("down")
            elif y == self.height - 1:
                connectors.append("up")
        return connectors

    # ------------------------------------------------------------------
    def _draw_intersections(
        self,
        screen: pygame.surface.Surface,
        origin_x: int,
        origin_y: int,
        tile_size: int,
    ) -> None:
        """Disegna le tile di intersezione ai vertici interni della griglia."""
        for y_vert in range(1, self.height):
            for x_vert in range(1, self.width):
                mask = self._get_intersection_mask(x_vert, y_vert)
                if mask == 0:
                    continue
                tile = self.assets.intersection_tiles.get(mask)
                if tile is None:
                    continue
                screen.blit(
                    tile,
                    tile.get_rect(
                        center=(
                            origin_x + x_vert * tile_size,
                            origin_y + y_vert * tile_size,
                        )
                    ),
                )

    # ------------------------------------------------------------------
    def _draw_border(
        self,
        screen: pygame.surface.Surface,
        origin_x: int,
        origin_y: int,
        tile_size: int,
    ) -> None:
        """Disegna il bordo esterno (doppia linea): angoli + 4 lati."""
        border = self.assets.border_tiles
        last_col_x = origin_x + (self.width - 1) * tile_size
        last_row_y = origin_y + (self.height - 1) * tile_size

        screen.blit(border["corner_tl"], (origin_x, origin_y))
        screen.blit(border["corner_tr"], (last_col_x, origin_y))
        screen.blit(border["corner_bl"], (origin_x, last_row_y))
        screen.blit(border["corner_br"], (last_col_x, last_row_y))

        for x in range(1, self.width - 1):
            px = origin_x + x * tile_size
            screen.blit(border["top"], (px, origin_y))
            screen.blit(border["bottom"], (px, last_row_y))

        for y in range(1, self.height - 1):
            py = origin_y + y * tile_size
            screen.blit(border["left"], (origin_x, py))
            screen.blit(border["right"], (last_col_x, py))

    # =========================================================================
    #   INTERSECTION MASK
    # =========================================================================
    def _get_intersection_mask(self, x_vert: int, y_vert: int) -> int:
        """Calcola la maschera di intersezione a un vertice interno."""
        nw = self._wall_grid[y_vert - 1][x_vert - 1]
        sw = self._wall_grid[y_vert][x_vert - 1]
        ne = self._wall_grid[y_vert - 1][x_vert]

        mask = 0
        if nw & self.WALL_RIGHT:
            mask |= 0b0001
        if sw & self.WALL_RIGHT:
            mask |= 0b0010
        if nw & self.WALL_BOTTOM:
            mask |= 0b0100
        if ne & self.WALL_BOTTOM:
            mask |= 0b1000

        return mask

    def _normalize_walls(self) -> list[list[int]]:
        """Return a maze copy with shared edges consistent on both cells."""
        walls = [
            [cell & self.WALL_MASK for cell in row]
            for row in self.maze
        ]
        for row in walls:
            for x in range(self.width - 1):
                has_wall = bool(
                    row[x] & self.WALL_RIGHT
                    or row[x + 1] & self.WALL_LEFT
                )
                if has_wall:
                    row[x] |= self.WALL_RIGHT
                    row[x + 1] |= self.WALL_LEFT
                else:
                    row[x] &= ~self.WALL_RIGHT
                    row[x + 1] &= ~self.WALL_LEFT

        for y in range(self.height - 1):
            for x in range(self.width):
                has_wall = bool(
                    walls[y][x] & self.WALL_BOTTOM
                    or walls[y + 1][x] & self.WALL_TOP
                )
                if has_wall:
                    walls[y][x] |= self.WALL_BOTTOM
                    walls[y + 1][x] |= self.WALL_TOP
                else:
                    walls[y][x] &= ~self.WALL_BOTTOM
                    walls[y + 1][x] &= ~self.WALL_TOP
        return walls

    def _get_wall_render_masks(self) -> list[list[int]]:
        """Assign each wall segment to one renderer without double-drawing."""
        masks = [row[:] for row in self._wall_grid]

        # Double tiles own the outside frame; single tiles own the interior.
        for y, row in enumerate(masks):
            for x in range(self.width):
                if y == 0:
                    row[x] &= ~self.WALL_TOP
                if y == self.height - 1:
                    row[x] &= ~self.WALL_BOTTOM
                if x == 0:
                    row[x] &= ~self.WALL_LEFT
                if x == self.width - 1:
                    row[x] &= ~self.WALL_RIGHT
                if x < self.width - 1:
                    row[x] &= ~self.WALL_RIGHT
                if y < self.height - 1:
                    row[x] &= ~self.WALL_BOTTOM

        # An intersection replaces a full segment only if both endpoint
        # sprites contain the matching arm; otherwise single remains fallback.
        for x_vert in range(1, self.width):
            for y_cell in range(1, self.height - 1):
                if (
                    self._has_intersection_arm(x_vert, y_cell, 0b0010)
                    and self._has_intersection_arm(
                        x_vert, y_cell + 1, 0b0001
                    )
                ):
                    masks[y_cell][x_vert] &= ~self.WALL_LEFT

        for y_vert in range(1, self.height):
            for x_cell in range(1, self.width - 1):
                if (
                    self._has_intersection_arm(x_cell, y_vert, 0b1000)
                    and self._has_intersection_arm(
                        x_cell + 1, y_vert, 0b0100
                    )
                ):
                    masks[y_vert][x_cell] &= ~self.WALL_TOP

        return masks

    def _has_intersection_arm(
        self, x_vert: int, y_vert: int, arm: int
    ) -> bool:
        """Whether the matching loaded intersection tile draws this arm."""
        mask = self._get_intersection_mask(x_vert, y_vert)
        return bool(mask & arm and mask in self.assets.intersection_tiles)
