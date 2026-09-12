"""Renders game entities (player, ghosts, pacgums) on the screen."""

from __future__ import annotations

import pygame

from ..managers.asset_manager import AssetManager


class EntityRenderer:
    """Draws Pac-Man, ghosts, and pacgums using loaded sprites."""

    def __init__(self, assets: AssetManager) -> None:
        """Initialize with asset manager.

        Args:
            assets: AssetManager containing entity images.
        """
        self.assets = assets

    @staticmethod
    def _draw_centered(
        screen: pygame.Surface,
        surface: pygame.Surface,
        center_x: int,
        center_y: int,
    ) -> None:
        """Blit a surface centered on a given point."""
        rect = surface.get_rect(center=(center_x, center_y))
        screen.blit(surface, rect)

    def draw(
        self,
        screen: pygame.Surface,
        origin_x: int,
        origin_y: int,
        tile_size: int,
        player_pixel_center: tuple[float, float],
        ghost_positions: list[tuple[int, int]],
        maze: list[list[int]],
        eaten_pacgums: set[tuple[int, int]] | None = None,
        player_moving: bool = False,
        player_move_progress: float = 0.0,
    ) -> None:
        """Draw all entities on the screen.

        Args:
            screen: Target surface.
            origin_x, origin_y: Pixel coordinates of maze top-left.
            tile_size: Size of each cell.
            player_pixel_center: (x, y) pixel coordinates of player center.
            ghost_positions: List of (x, y) for each ghost.
            maze: Maze matrix (to detect walkable cells for pacgums).
            eaten_pacgums: Set of (x, y) cells whose pacgum has been eaten.
                If None, all pacgums are drawn.
            player_moving: Whether the player is currently moving (controls
                animation). If False, an idle frame is shown.
            player_move_progress: Progress of current movement (0.0 to 1.0),
                used to select animation frame.
        """
        if eaten_pacgums is None:
            eaten_pacgums = set()
        # ---------------------------------------------------------------------
        #   Draw ghosts with idle animation
        # ---------------------------------------------------------------------
        frame_index = (pygame.time.get_ticks() // 300) % 3
        for i, (gx, gy) in enumerate(ghost_positions):
            ghost_frames = (
                self.assets.ghost_frames[i]
                if i < len(self.assets.ghost_frames)
                else []
            )
            frame: pygame.Surface | None
            if ghost_frames:
                frame = ghost_frames[frame_index % len(ghost_frames)]
            else:
                frame = (
                    self.assets.ghost_images[i]
                    if i < len(self.assets.ghost_images)
                    else None
                )
            if frame is not None:
                center_x = origin_x + gx * tile_size + tile_size // 2
                center_y = origin_y + gy * tile_size + tile_size // 2
                self._draw_centered(screen, frame, center_x, center_y)
        # ---------------------------------------------------------------------
        #   Draw super-pacgums at corners (offset inward)
        # ---------------------------------------------------------------------
        if self.assets.super_pacgum_img is not None:
            offset = max(4, tile_size // 3)
            maze_w = len(maze[0]) if maze else 0
            maze_h = len(maze)
            super_positions = [
                (0, 0, offset, offset),
                (maze_w - 1, 0, -offset, offset),
                (0, maze_h - 1, offset, -offset),
                (maze_w - 1, maze_h - 1, -offset, -offset),
            ]
            for cx, cy, dx, dy in super_positions:
                center_x = (
                    origin_x + cx * tile_size + tile_size // 2 + dx
                )
                center_y = (
                    origin_y + cy * tile_size + tile_size // 2 + dy
                )
                self._draw_centered(
                    screen,
                    self.assets.super_pacgum_img,
                    center_x,
                    center_y,
                )
        # ---------------------------------------------------------------------
        #   Draw pacgums only if the image is loaded (not None).
        # ---------------------------------------------------------------------
        if self.assets.pacgum_img is not None:
            occupied = set(ghost_positions)
            # Iterate through the maze to draw pacgums in walkable cells that
            # are not occupied or eaten.
            for y, row in enumerate(maze):
                for x, _cell in enumerate(row):
                    #   1. Check if the pacgum is eaten.
                    if (x, y) in occupied or (x, y) in eaten_pacgums:
                        continue
                    #   2. Check if the cell is walkable
                    if self._is_walkable(x, y, maze):
                        center_x = (
                            origin_x + x * tile_size + tile_size // 2
                        )
                        center_y = (
                            origin_y + y * tile_size + tile_size // 2
                        )
                        self._draw_centered(
                            screen,
                            self.assets.pacgum_img,
                            center_x,
                            center_y,
                        )

        # ---------------------------------------------------------------------
        #   Draw player with animation or idle
        # ---------------------------------------------------------------------
        player_frames = getattr(self.assets, "player_frames", [])

        # ---------------------------------------------------------------------
        #   1. Check if player is moving and player_frames is not empty.
        # ---------------------------------------------------------------------
        if player_moving and player_frames:
            frame_index = int(
                player_move_progress * len(player_frames) * 2
            ) % len(player_frames)
            player_img = player_frames[frame_index]

        # ---------------------------------------------------------------------
        #   2. Check if player_frames is not empty, if so use the second frame.
        # ---------------------------------------------------------------------
        elif player_frames:
            player_img = (
                player_frames[1]
                if len(player_frames) > 1
                else player_frames[0]
            )
        # ---------------------------------------------------------------------
        #   3. Check if player_frames is empty, if so use the player_img.
        # ---------------------------------------------------------------------
        else:
            player_img = getattr(
                self.assets, "player_img", None
            )

        # ---------------------------------------------------------------------
        #   4. Draw the player image if it's not None.
        # ---------------------------------------------------------------------
        if player_img is not None:
            # Centered at the player's pixel center,
            # rounded to the nearest integer for pixel alignment.
            center_x = int(round(player_pixel_center[0]))
            center_y = int(round(player_pixel_center[1]))
            self._draw_centered(
                screen,
                player_img,
                center_x,
                center_y
            )

    @staticmethod
    def _is_walkable(x: int, y: int, maze: list[list[int]]) -> bool:
        """Check if a cell is walkable (not completely walled)."""
        if x < 0 or y < 0 or x >= len(maze[0]) or y >= len(maze):
            return False
        return maze[y][x] != 15
