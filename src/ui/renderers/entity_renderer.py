"""Renders game entities (player, ghosts, pacgums) on the screen."""

from __future__ import annotations

import time

from pygame.surface import Surface
from ..managers.asset_manager import AssetManager


class EntityRenderer:
    """Draws Pac-Man, ghosts, and pacgums using loaded sprites."""

    # ---------------------------------------------------------------
    #   Duration of a single frame of the ghosts' idle animation (ms).
    # ---------------------------------------------------------------
    GHOST_IDLE_FRAME_MS = 300
    # ---------------------------------------------------------------
    #   Both are entities of the same fluidity.
    # ---------------------------------------------------------------
    GHOST_FRAME_MOVE = 2
    PLAYER_FRAME_DURATION_MS = 80
    PLAYER_DEATH_FRAME_DURATION_MS = 90

    def __init__(self, assets: AssetManager) -> None:
        """Initialize with asset manager.

        Args:
            assets : AssetManager containing entity images.
        """
        self.assets = assets

    # PUBBLIC METHODS ---------------------------------------------------------
    # =========================================================================
    #   DRAW - player, pacgum, super-pacgum
    # =========================================================================
    def draw(
        self,
        screen: Surface,
        origin_x: int,
        origin_y: int,
        tile_size: int,
        player_pixel_center: tuple[float, float],
        maze: list[list[int]],
        eaten_pacgums: set[tuple[int, int]] | None = None,
        player_moving: bool = False,
        direction: str | None = "",
        pacgum_cells: set[tuple[int, int]] | None = None,
        player_dying: bool = False,
        death_elapsed_ms: int = 0,
    ) -> None:
        """Draw player, pacgums, and super-pacgums.

        Ghost rendering is delegated to `draw_ghosts()`.

        Args:
            screen: Destination surface.
            origin_x: Maze origin x-coordinate in pixels.
            origin_y: Maze origin y-coordinate in pixels.
            tile_size: Side length of a maze cell in pixels.
            player_pixel_center: Player center as an ``(x, y)`` pixel pair.
            maze: Wall-bitmask grid used to identify walkable cells.
            eaten_pacgums: Cells whose pacgums have already been eaten.
            player_moving: Whether to animate the player's normal movement.
            direction: Current player facing direction.
            pacgum_cells: Cells containing pacgums; defaults to every
                walkable cell when omitted.
            player_dying: Whether the one-shot death animation is active.
            death_elapsed_ms: Time elapsed since the death animation began.
        """
        if eaten_pacgums is None:
            eaten_pacgums = set()
        # -----------------------------------------------
        # self._draw_super_pacgums(
        #     screen, origin_x, origin_y, tile_size, maze
        # )
        # ------------------------------------------------
        self._draw_pacgums(
            screen, origin_x, origin_y, tile_size, maze,
            eaten_pacgums, pacgum_cells,
        )
        self._draw_player(
            screen, player_pixel_center,
            player_moving, direction, player_dying, death_elapsed_ms,
        )

    # -------------------------------------------------------------------------
    # def _draw_super_pacgums
    # -------------------------------------------------------------------------
    def _draw_pacgums(
        self,
        screen: Surface,
        origin_x: int,
        origin_y: int,
        tile_size: int,
        maze: list[list[int]],
        eaten_pacgums: set[tuple[int, int]],
        pacgum_cells: set[tuple[int, int]] | None,
    ) -> None:
        """Draw the Pac-Dots in the walkable cells."""
        pacgum_img = self.assets.pacgum_img
        super_pacgum_img = self.assets.super_pacgum_img
        if pacgum_img is None and super_pacgum_img is None:
            return

        half = tile_size // 2
        super_cells = {
            (0, 0),
            (len(maze[0]) - 1, 0),
            (0, len(maze) - 1),
            (len(maze[0]) - 1, len(maze) - 1),
        }

        for y, row in enumerate(maze):
            for x, _cell in enumerate(row):
                if (y, x) in eaten_pacgums:
                    continue
                if pacgum_cells is not None and (y, x) not in pacgum_cells:
                    continue
                if not self._is_walkable(x, y, maze):
                    continue
                image = (
                    super_pacgum_img
                    if (x, y) in super_cells and super_pacgum_img is not None
                    else pacgum_img
                )
                if image is None:
                    continue
                self._draw_centered(
                    screen,
                    image,
                    origin_x + x * tile_size + half,
                    origin_y + y * tile_size + half,
                )

    def _draw_player(
        self,
        screen: Surface,
        player_pixel_center: tuple[float, float],
        player_moving: bool,
        direction: str | None,
        player_dying: bool,
        death_elapsed_ms: int,
    ) -> None:
        """Draw the player frame matching its current animation state."""
        if player_dying and self.assets.player_death_frames:
            death_frames = self.assets.player_death_frames
            index = min(
                death_elapsed_ms // self.PLAYER_DEATH_FRAME_DURATION_MS,
                len(death_frames) - 1,
            )
            self._draw_centered(
                screen,
                death_frames[index],
                int(round(player_pixel_center[0])),
                int(round(player_pixel_center[1])),
            )
            return

        frames = self.assets.player_frames.get(direction or "right", [])
        if not frames:
            frames = self.assets.player_frames.get("right", [])
        player_img: Surface | None
        # -----------------------------------------------------------------
        #   GESTIONE PLAYER FLUIDO
        # -----------------------------------------------------------------
        if player_moving and len(frames) > 1:
            cycle_steps = (len(frames) - 1) * 2
            phase = int(
                time.monotonic() * 1000 / self.PLAYER_FRAME_DURATION_MS
            ) % cycle_steps
            idx = phase if phase < len(frames) else cycle_steps - phase
            player_img = frames[idx]
        elif frames:
            player_img = frames[1] if len(frames) > 1 else frames[0]
        else:
            player_img = self.assets.player_img
        if player_img is None:
            return
        self._draw_centered(
            screen, player_img,
            int(round(player_pixel_center[0])),
            int(round(player_pixel_center[1])),
        )

    # =========================================================================
    #   DRAW — ghosts (nuovo path)
    # =========================================================================
    def draw_ghosts(
        self,
        screen: Surface,
        ghost_infos: list[dict],
        frightened_flash: bool = False,
    ) -> None:
        """Draw the ghosts using rich descriptors.

        Args:
            screen             : Target surface.
            origin_x, origin_y : Pixel coordinates of the maze's top-left
                                 corner.
            tile_size          : Cell size in pixels.
            ghost_infos        : List of dicts produced by GhostTeamAdapter.
                                 Each dict contains :
                                        name, x, y (float, in CELLS), facing,
                                        moving, move_progress, state
            frightened_flash   : True during the final of the power pellet:
                                 use "fear_flash" frames instead of "fear".
        """
        for info in ghost_infos:
            img = (
                self._pick_ghost_frame(info, frightened_flash)
            )
            if img is None:
                continue
            self._draw_centered(screen, img, info["x"], info["y"])

    def _pick_ghost_frame(
        self,
        info: dict,
        frightened_flash: bool,
    ) -> Surface | None:
        """Select the ghost frame matching its state and direction.

        Priority order:
            1. ``eaten`` state: dead sprite.
            2. ``frightened`` state: fear or fear-flash frame.
            3. Active fear flash: flashing frame.
            4. Otherwise: frame matching the movement direction.
        """
        name = info.get("name", "")
        sprites = self.assets.ghosts.get(name)
        if sprites is None:
            return None

        state = info.get("state", "normal")
        # ----------------------------------------------------------
        # 1) Eaten: eyes
        # ----------------------------------------------------------
        if state == "eaten":
            if sprites.dead:
                if isinstance(sprites.dead[0], Surface):
                    return sprites.dead[0]
            return sprites.first_frame()
        # ---------------------------------------------------------
        # 2) frightened: fear / fear_flash
        # ---------------------------------------------------------
        if state == "frightened":

            # NOTE: Abbiamo la logica del fear...
            key = "fear_flash" if frightened_flash else "fear"
            frames = self.assets.ghost_shared.get(key) or []
            if not frames:
                # -------------------------------------------------
                # Fallback: se mancano i frame flash, prova "fear".
                # -------------------------------------------------
                frames = self.assets.ghost_shared.get("fear") or []
            if frames:
                return frames[self._frame_idx(info, len(frames))]
        # ----------------------------------------------------------
        # 3) Normale : per direzione
        # ----------------------------------------------------------
        facing = info.get("facing", "right")
        frames = sprites.frames_for_direction(facing)
        if not frames:
            return sprites.first_frame()

        return frames[self._frame_idx(info, len(frames))]

    def _frame_idx(self, info: dict, n_frames: int) -> int:
        """Select the index of the frame to display.

        - If the ghost is moving: progress cycles through the frames fast.
        - If it is stationary: an idle loop based on real time (monotonic).
        """
        if n_frames <= 1:
            return 0

        if info.get("moving"):
            p = float(info.get("move_progress", 0.0))
            # -------------------------------------------------------------
            #   GHOST: progress cycles through the frames twice as fast.
            # -------------------------------------------------------------
            # NOTE: NON Usiamo piu GHOST_IDLE_FRAME_MS ma GHOST_FRAME_MOVE
            idx = int(p * n_frames * self.GHOST_FRAME_MOVE) % n_frames
            return idx

        elapsed_ms = int(time.monotonic() * 1000)
        # gestione idle frames
        return (
            (elapsed_ms // self.GHOST_IDLE_FRAME_MS) % n_frames
        )

    # =========================================================================
    #   HELPERS
    # =========================================================================
    @staticmethod
    def _draw_centered(
        screen: Surface,
        surface: Surface,
        center_x: int,
        center_y: int,
    ) -> None:
        """Blit a surface centered on a given point."""
        rect = surface.get_rect(center=(center_x, center_y))
        screen.blit(surface, rect)

    @staticmethod
    def _is_walkable(x: int, y: int, maze: list[list[int]]) -> bool:
        """Check if a cell is walkable (not completely walled)."""
        if x < 0 or y < 0 or x >= len(maze[0]) or y >= len(maze):
            return False
        return maze[y][x] != 15
