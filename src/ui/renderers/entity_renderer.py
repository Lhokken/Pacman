"""Renders game entities (player, ghosts, pacgums) on the screen."""

from __future__ import annotations

import time

from pygame import transform
from pygame.surface import Surface
from ..managers.asset_manager import AssetManager


class EntityRenderer:
    """Draws Pac-Man, ghosts, and pacgums using loaded sprites.

    Nota: dopo la migrazione al nuovo `AssetManager.ghosts` /
    `AssetManager.ghost_shared`, il rendering dei ghost è interamente
    in `draw_ghosts()` + `_pick_ghost_frame()`. Il vecchio metodo
    `draw()` è ora responsabile solo di super-pacgum, pacgum e player.
    """

    # Durata di un frame dell'animazione idle dei ghost (ms).
    GHOST_IDLE_FRAME_MS = 300

    def __init__(self, assets: AssetManager) -> None:
        """Initialize with asset manager.

        Args:
            assets: AssetManager containing entity images.
        """
        self.assets = assets

    # PUBBLIC METHODS ---------------------------------------------------------
    # =========================================================================
    #   DRAW — player, pacgum, super-pacgum
    # =========================================================================
    def draw(
        self,
        screen: Surface,
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
        """Draw player, pacgums, and super-pacgums.

        Il disegno dei ghost è delegato a `draw_ghosts()`.

        Args:
            screen: Target surface.
            origin_x, origin_y: Pixel coordinates of maze top-left.
            tile_size: Size of each cell.
            player_pixel_center: (x, y) pixel coordinates of player center.
            ghost_positions: Lista di (x, y) per ogni ghost.
                Usata SOLO per escludere i pacgum sotto i ghost.
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

        # self._draw_super_pacgums(screen, origin_x, origin_y, tile_size, maze)
        self._draw_pacgums(
            screen, origin_x, origin_y, tile_size, maze,
            ghost_positions, eaten_pacgums,
        )
        self._draw_player(
            screen, player_pixel_center,
            player_moving, player_move_progress,
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
        ghost_positions: list[tuple[int, int]],
        eaten_pacgums: set[tuple[int, int]],
    ) -> None:
        """Disegna i pacgum nelle celle walkable non occupate né mangiate."""
        img = self.assets.pacgum_img
        if img is None:
            return

        occupied = set(ghost_positions)
        half = tile_size // 2

        for y, row in enumerate(maze):
            for x, _cell in enumerate(row):
                if (x, y) in occupied or (x, y) in eaten_pacgums:
                    continue
                if not self._is_walkable(x, y, maze):
                    continue

                # superpacgum drawing
                if (x, y) in [
                        (0, 0),
                        (len(maze) - 1, 0),
                        (0, len(maze) - 1),
                        (len(maze) - 1, len(maze) - 1)
                        ]:
                    xl_img = transform.smoothscale(img, (13, 13))
                    self._draw_centered(
                        screen, xl_img,
                        origin_x + x * tile_size + half,
                        origin_y + y * tile_size + half,
                    )
                # normal pacgum drawing
                else:
                    self._draw_centered(
                        screen, img,
                        origin_x + x * tile_size + half,
                        origin_y + y * tile_size + half,
                    )

    # -------------------------------------------------------------------------
    def _draw_player(
        self,
        screen: Surface,
        player_pixel_center: tuple[float, float],
        player_moving: bool,
        player_move_progress: float,
    ) -> None:
        """Disegna il player scegliendo il frame in base allo stato."""
        frames = self.assets.player_frames
        player_img: Surface | None
        if player_moving and frames:
            # Il progresso 0..1 scandisce i frame due volte più veloce.
            idx = int(player_move_progress * len(frames) * 2) % len(frames)
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
        origin_x: int,
        origin_y: int,
        tile_size: int,
        ghost_infos: list[dict],
        *,
        frightened_flash: bool = False,
    ) -> None:
        """Disegna i ghost usando descrittori ricchi.

        Args:
            screen: Surface di destinazione.
            origin_x, origin_y: Pixel coord del top-left del labirinto.
            tile_size: Dimensione cella in pixel.
            ghost_infos: Lista di dict prodotti da GhostTeamAdapter.
                Ogni dict contiene:
                    name, x, y (float, in CELLE), facing,
                    moving, move_progress, state
            frightened_flash: True negli ultimi istanti del power pellet:
                usa i frame "fear_flash" invece di "fear".
        """
        half = tile_size // 2
        for info in ghost_infos:
            img = self._pick_ghost_frame(info, frightened_flash)
            if img is None:
                continue
            cx = int(origin_x + info["x"] * tile_size + half)
            cy = int(origin_y + info["y"] * tile_size + half)
            self._draw_centered(screen, img, cx, cy)

    # ------------------------------------------------------------------
    def _pick_ghost_frame(
        self,
        info: dict,
        frightened_flash: bool,
    ) -> Surface | None:
        """Sceglie il frame corretto in base allo stato del ghost.

        Ordine di priorità:
            1. state == "eaten"      → sprite "dead" (occhi)
            2. state == "frightened" → fear / fear_flash (condivisi)
            3. altrimenti            → frames per direzione (facing)
        """
        name = info.get("name", "")
        sprites = self.assets.ghosts.get(name)
        if sprites is None:
            return None

        state = info.get("state", "normal")
        # 1) Mangiato → occhi
        if state == "eaten":
            if sprites.dead:
                if isinstance(sprites.dead[0], Surface):
                    return sprites.dead[0]
            return sprites.first_frame()

        # 2) Spaventato → fear / fear_flash (condivisi tra tutti i ghost)
        if state == "frightened":
            key = "fear_flash" if frightened_flash else "fear"
            frames = self.assets.ghost_shared.get(key) or []
            if not frames:
                # Fallback: se mancano i frame flash, prova "fear".
                frames = self.assets.ghost_shared.get("fear") or []
            if frames:
                return frames[self._frame_idx(info, len(frames))]

        # 3) Normale → per direzione
        facing = info.get("facing", "right")
        frames = sprites.frames_for_direction(facing)
        if not frames:
            return sprites.first_frame()

        return frames[self._frame_idx(info, len(frames))]

    # ------------------------------------------------------------------
    def _frame_idx(self, info: dict, n_frames: int) -> int:
        """Sceglie l'indice del frame da mostrare.

        - Se il ghost si muove: il progresso 0..1 scandisce i frame.
        - Se è fermo: idle loop basato sul tempo reale (monotonic).
        """
        if n_frames <= 1:
            return 0
        if info.get("moving"):
            p = float(info.get("move_progress", 0.0))
            return int(p * n_frames) % n_frames
        elapsed_ms = int(time.monotonic() * 1000)
        return (elapsed_ms // self.GHOST_IDLE_FRAME_MS) % n_frames

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
