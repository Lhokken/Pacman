"""Game scene featuring the maze, the player, and side panels.

The page comprises:

    - the responsive layout (`GamePageLayout`);
    - managers for fonts, assets, and side panels;
    - game entities (maze, Pac-Man, ghosts, pellets);
    - renderers for the maze and entities;
    - the level timer and the HUD.

The `update()` method synchronizes the visual state with the state calculated
by the core; `draw()` delegates rendering to specialized renderers.
"""

from __future__ import annotations

import logging
from pathlib import Path
from time import sleep

import pygame
from pygame.surface import Surface

from mazegenerator import MazeGenerator

from ..scene import Scene

from ..managers.font_manager import FontManager
from ..managers.asset_manager import AssetManager
from ..managers.panel_manager import PanelManager

from ..app import GameApp

from ..layout.game_page_layout import GamePageLayout, GamePageMetrics

from .end_screen import GameOverPage, VictoryPage
from ..renderers.maze_renderer import MazeRenderer
from ..renderers.entity_renderer import EntityRenderer

from ..components.hud import HUD
from ...core.timer import Timer
from ...core.entities.ghost import GhostBase as Ghost, GhostState
from ...core.entities.pacman import PacmanPlayer
from ...core.entities.pacgums import PacgumsManagement as PacgumManager


logger = logging.getLogger(__name__)


class GamePage(Scene):
    """Featuring the maze, player, and side panels.

    Constructs the entire game hierarchy based on the `GameApp`
    configuration, calculate metrics via `GamePageLayout`, and
    recalculates them upon resizing without recreating the managers.
    """

    # ------------------------------------------------------------
    #   BITMASK
    # ------------------------------------------------------------
    WALL_NONE = 0
    WALL_ALL = 15
    WALL_LEFT = 8
    WALL_RIGHT = 2
    WALL_BOTTOM = 4
    WALL_TOP = 1

    # ------------------------------------------------------------
    #   TIMER
    # -------------------------------------------------------------
    DEFAULT_LEVEL_DURATION_S = 180.0

    def __init__(self, app: GameApp, level: int = 0) -> None:
        """Inizializza la scena di gioco.

        Args:
            app: Istanza di `GameApp` che fornisce configurazione,
                surface e switch di scena.
        """
        super().__init__(app)

        if level == 0:
            self.config = app.config
            self.assets_base = (
                Path(__file__).resolve().parents[3] / "assets" / "img"
            )
            # --------------------------------------------------------
            #   GAME GRID
            # --------------------------------------------------------
            self.maze_width = self.config.levels[level].width
            self.maze_height = self.config.levels[level].height
            self.maze_dim = (self.maze_height, self.maze_width)
            # INTEGRAZIONE: corners in (row, col), come richiesto da
            # PacgumsManagement.try_to_eat -> `if (row, col) in
            # self.corners`. La versione precedente usava (0, H-1) /
            # (W-1, 0) / (W-1, H-1), cioè (col, row) — da cui il
            # "bug gomma in alto a destra talvolta non viene mangiata".
            self.maze_corners = [
                (0, 0),
                (0, self.maze_width - 1),
                (self.maze_height - 1, 0),
                (self.maze_height - 1, self.maze_width - 1),
            ]
            # --------------------------------------------------------
            #   LAYOUT
            # --------------------------------------------------------
            self._layout = GamePageLayout()
            self.metrics: GamePageMetrics = self._layout.compute(
                *app.screen.get_size(),
                self.maze_width,
                self.maze_height,
            )
            self.tile_size = self.metrics.tile_size
            # --------------------------------------------------------
            #   MANAGER
            # --------------------------------------------------------
            # FontManager e AssetManager restano locali alla pagina:
            # AssetManager è legato al tile_size corrente e non può
            # essere condiviso con altre scene.
            self.fonts = FontManager(self.assets_base)
            self.assets = AssetManager(self.assets_base, self.tile_size)
        # --------------------------------------------------------
        #   GAME ENTITY
        # --------------------------------------------------------
        self.maze = self._generate_maze()
        spawn = PacmanPlayer.find_spawn(self.maze)
        if level == 0:
            self.player = PacmanPlayer(spawn[0], spawn[1], self.maze)
            self.current_level: int = 0
            self.level_start_reset = 7
            self.level_start: int = 0
            self.player.maze = self.maze
            self.player.maze_dim = self.maze_dim
            self.player.maze_corners = self.maze_corners
        else:
            self.player.maze = self.maze
            self.player.p_row = spawn[0]
            self.player.p_col = spawn[1]
            self.player.from_row = spawn[0]
            self.player.from_col = spawn[1]
            self.player.to_row = spawn[0]
            self.player.to_col = spawn[1]
        # INTEGRAZIONE: GhostBase.__init__(g_row, g_col) -> passare
        # (row, col). La versione precedente passava (x, y).
        self.ghosts = [Ghost(row, col) for row, col in self._ghost_spawn()]
        for ghost in self.ghosts:
            ghost.maze = self.maze
            ghost.maze_dim = self.maze_dim
        self.pacgums = PacgumManager(
            self.maze_dim,
            self.is_walkable,
            {"pacgum": self.app.config.points_per_pacgum,
                "super_pacgum": self.app.config.points_per_super_pacgum,
                "ghost": self.config.points_per_ghost}
        )
        self.pacgums.corners = self.maze_corners
        if level == 0:
            self.score = 0
        # --------------------------------------------------------
        #   Renderer / Pannels
        # --------------------------------------------------------
        self.panel_manager = PanelManager(
            self.metrics.panel_layout,
            self.fonts,
            self.assets_base,
            self.tile_size,
        )
        self.maze_renderer = MazeRenderer(self.maze, self.assets)
        self.entity_renderer = EntityRenderer(self.assets)
        # --------------------------------------------------------
        #   Timer + HUD
        # --------------------------------------------------------
        self.level_timer = Timer(
            duration=self.DEFAULT_LEVEL_DURATION_S
        )
        self.hud = HUD(
            font_title=self.fonts.font_title_small,
            font_value=self.fonts.font_white,
            timer=self.level_timer,
        )
        # --------------------------------------------------------
        #   Adapter ghost
        # --------------------------------------------------------
        self._frame = 0

        # TODO(core-integration): Keep the live match/core object here when
        # the game orchestration refactor provides one. `apply_cheats()`
        # should delegate to that object instead of implementing gameplay
        # rules in this UI scene.

    # Public methods -------------------------------------------------------
    # ======================================================================
    #   Life cycle
    # ======================================================================

    def apply_cheats(self, cheats: dict[str, bool]) -> None:
        """Insert given data in player argument."""
        self.player.cheat_sync(cheats)

    def handle_events(self) -> None:
        """Handle game scene input events.

        Forwards keyboard events to the player, handles
        window resizing, and opens the pause menu
        when ESC is pressed.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.on_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from .pause_menu import PauseMenu
                    self.app.switch_scene(PauseMenu(self.app, self))
                    return
                self.player.handle_event(event)

    def on_pause(self) -> None:
        """Pauses the level timer."""
        self.level_timer.pause()

    def on_resume(self) -> None:
        """Resume timer when you push resumes button."""
        self.level_timer.resume()

    def update(self) -> None:
        """Update the game state for the current frame.

        Synchronize visual ghosts with the positions calculated by the
        core, delegate the logic update to the player, and update the
        side panel if the score has changed.
        """
        # UPDATE DEAD_STATUS -----------------------------------------
        if self.current_level >= 10:
            self.app.switch_scene(VictoryPage(self.app, self.score))
        if self.player.lives <= 0 or self.level_timer.remaining <= 0:
            i: float = 0.2
            while i < 3:
                sleep(i)
                print("\a")
                i = i * 1.5
            # TODO: LOGIC pending - Raccolta dati reali del user
            self.app.switch_scene(GameOverPage(self.app, score=123))

        # CHEATING - extra lifes -------------------------------------
        if self.player.CHEAT_DATA["extra_lives"] is True:
            self.player.lives += 2
            self.player.CHEAT_DATA["extra_lives"] = False
            if self.player.lives > 3:
                self.player.lives = 3

        while self.level_start > 0:
            self.level_notifier()
        score_gain = self.player.update(
            self.ghosts, self.pacgums, self.player
        )
        self.panel_manager.update_lives(self.player.lives)
        if score_gain:
            self.score += score_gain
            self.panel_manager.update_score(self.score)
        if self.pacgums.all_eaten is True:
            self.next_level()
        self._frame += 1

    def level_notifier(self) -> None:
        """Play an audio notification for Pac-Man life loss.

        When a Pac-Man life is lost, the user receives an audio
        notification.
        """
        print("\a")
        sleep(self.level_start / 20)
        self.level_start = int(self.level_start)
        self.level_start -= 1

    def next_level(self) -> None:
        """Set all data in order to begin a new game level.

        This occurs after eating all pacgums, pacman lives and score
        remain unchanged
        """
        self.config.seed += 17
        self.maze = self.player.maze = self._generate_maze()
        self.pacgums = PacgumManager(
            self.maze_dim,
            self.is_walkable,
            {"pacgum": self.app.config.points_per_pacgum,
                "super_pacgum": self.app.config.points_per_super_pacgum,
                "ghost": self.config.points_per_ghost}
        )
        self.pacgums.corners = self.maze_corners
        # bug gomma in alto a destra talvolta non viene mangiata
        # INTEGRAZIONE: risolto a monte dal fix di `maze_corners` /
        # `is_walkable`. Il commento resta come promemoria.
        self.maze_renderer = MazeRenderer(self.maze, self.assets)
        for ghost in self.ghosts:
            ghost.g_row, ghost.g_col = ghost.corner
            ghost.state = GhostState.NORMAL
            ghost.set_timer = ghost.set_timer
            ghost.maze = self.maze
        self.current_level += 1
        self.player.p_row, self.player.p_col = \
            self.player.from_row, self.player.from_col = \
            self.player.to_row, self.player.to_col = self.player.respawn
        self.player.level = self.current_level
        self.level_timer.reset(self.DEFAULT_LEVEL_DURATION_S)
        self.level_start = self.level_start_reset

    def on_resize(self, width: int, height: int) -> None:
        """Recalculate layout and update managers without recreating them.

        Args:
            new_width : New window width in px.
            new_height: New window height in px.
        """
        new_width = width
        new_height = height
        self.metrics = self._layout.compute(
            new_width, new_height,
            self.maze_width, self.maze_height,
        )

        new_tile = self.metrics.tile_size
        if new_tile != self.tile_size:
            self.tile_size = new_tile
            self.assets.set_tile_size(new_tile)
        # --------------------------------------------------------------
        #   Pannelli
        # --------------------------------------------------------------
        # I pannelli si riposizionano con il nuovo layout, senza
        # perdere lo stato (score/lives correnti restano).
        self.panel_manager.relayout(self.metrics.panel_layout, new_tile)

    def draw(self, screen: Surface) -> None:
        """Draw the scene by delegating to the renderers.

        Args:
            screen: Destination surface.
        """
        screen.fill((20, 20, 30))

        if self.metrics.too_small:
            self._draw_too_small_hint(screen)
            return

        # ===========================================================
        #   SCENE
        # -----------------------------------------------------------
        # 1) LATERALS PANNELS
        # -----------------------------------------------------------
        self.panel_manager.draw(screen)
        # -----------------------------------------------------------
        # 2) HUD
        # -----------------------------------------------------------
        self.hud.draw(screen)
        # ------------------------------------------------------------
        # 3) MAZE
        # ------------------------------------------------------------
        ox, oy = self.metrics.maze_origin
        self.maze_renderer.draw(screen, ox, oy, self.tile_size)
        # -----------------------------------------------------------
        # 4) PLAYER
        # -----------------------------------------------------------
        player_center, player_progress = (
            self._player_pixel_state(ox, oy)
        )
        # ------------------------------------------------------------
        # 5) GHOST
        # ------------------------------------------------------------
        ghost_infos = self._build_ghost_infos()

        # RIPRISTINATO: la chiave e di fatto dove dovrebbe essere
        self.entity_renderer.draw_ghosts(
            screen, ox, oy, self.tile_size, ghost_infos,
            frightened_flash=self._is_frightened_flash(),
        )
        # ------------------------------------------------------------
        # 6) PACGUM
        # ------------------------------------------------------------
        ghost_positions = [(g.g_col, g.g_row) for g in self.ghosts]
        self.entity_renderer.draw(
            screen,
            ox,
            oy,
            self.tile_size,
            player_center,
            ghost_positions,
            self.maze,
            self.pacgums.eaten,
            self.player.is_moving,
            player_progress,
            self.player.direction
        )

    # ==================================================================
    #   RENDERNG HELPER
    # ==================================================================
    def _player_pixel_state(
        self, origin_x: int, origin_y: int
    ) -> tuple[tuple[float, float], float]:
        """Return the player's position and progress in pixels.

        If the player is stationary, progress is 0. If moving,
        it linearly interpolates between `from_*` and `to_*` based on
        the time elapsed since the start of the move.

        Args:
            origin_x : X-coordinate of the top corner of the maze.
            origin_y : Y-coordinate of the top corner of the maze.

        Returns:
            A tuple `((cx, cy), progress)` containing the player's
            center in pixels and the interpolation progress in
            the range `[0.0, 1.0]`.
        """
        tile = self.tile_size
        half = tile // 2

        if not self.player.is_moving:
            cx = origin_x + self.player.p_col * tile + half
            cy = origin_y + self.player.p_row * tile + half
            return (cx, cy), 0.0

        elapsed = (
            pygame.time.get_ticks() - self.player.move_started_ms
        )
        progress = (
            min(elapsed / self.player.MOVE_DURATION_MS, 1.0)
        )

        from_cx = origin_x + self.player.from_col * tile + half
        from_cy = origin_y + self.player.from_row * tile + half

        to_cx = origin_x + self.player.to_col * tile + half
        to_cy = origin_y + self.player.to_row * tile + half

        cx = int(from_cx + (to_cx - from_cx) * progress)
        cy = int(from_cy + (to_cy - from_cy) * progress)

        return (cx, cy), progress

    def _is_frightened_flash(self) -> bool:
        """Indicate whether frightened ghosts should flash.

        `power_timer` is not yet exposed by `PacmanPlayer`; using `getattr`
        with a default of 0 preserves existing behavior until the
        core populates it.

        Returns:
            `True` if the power timer is running low and the current
            frame is in the "off" phase of the flashing cycle.
        """
        return self.ghosts[0].flashing
        # power_timer = getattr(self.player, "power_timer", 0)
        # return (
        #     power_timer > 0
        #     and power_timer < 120
        #     and (power_timer // 10) % 2 == 0
        # )

    def _draw_too_small_hint(self, screen: Surface) -> None:
        """Mostra un messaggio centrale se la finestra è troppo piccola.

        TODO: Traduci in inglese
        Args:
            screen: Surface su cui disegnare il messaggio.
        """
        msg = self.fonts.font_white.render(
            "Enlarge window to see the game"
        )
        rect = msg.get_rect(center=(
            screen.get_width() // 2, screen.get_height() // 2
        ))
        screen.blit(msg, rect)

    # ==================================================================
    #   Generazione maze
    # ==================================================================
    def _generate_maze(self) -> list[list[int]]:
        """Generate and validates the maze used by the page.

        Returns:
            The maze grid as a list of rows, where each row is
            a list of integers (wall bitmasks).

        Raises:
            RuntimeError: If generation fails or the grid does not
            match the expected dimensions.
        """
        try:
            generator = MazeGenerator(
                size=(self.maze_width, self.maze_height),
                perfect=False,
                seed=self.config.seed,
            )
            maze = generator.maze
            if len(maze) != self.maze_height or any(
                len(row) != self.maze_width for row in maze
            ):
                raise ValueError(
                    "Maze dimensions mismatch: "
                    f"expected {self.maze_width}x{self.maze_height}, "
                    f"got {len(maze[0]) if maze else 0}x{len(maze)}"
                )
            return maze
        except Exception as e:
            logger.error("Maze generation failed: %s", e)
            raise RuntimeError(f"Failed to generate maze: {e}") from e

    def is_walkable(self, row: int, col: int) -> bool:
        """Indicate whether the cell `(row, col)` is walkable.

        INTEGRAZIONE: la firma è (row, col) perché PacgumsManagement
        chiama `walkable_fn(row, col)`. Il corpo accede a
        `maze[row][col]`. La versione precedente usava (x, y) e
        `maze[y][x]`, invertendo gli indici.

        Args:
            row: row coordinate of the cell (in cells).
            col: column coordinate of the cell (in cells).

        Returns:
            `True` if the cell is within the boundaries and is not a solid
            wall; `False` otherwise.
        """
        if row < 0 or col < 0 or row >= self.maze_height or \
                col >= self.maze_width:
            return False
        return self.maze[row][col] != 15

    # Private Methods ------------------------------------------------------
    # ======================================================================
    #   Helper methods
    # ======================================================================
    # def _sync_ghosts_from_player(self) -> None:
    #     # NOTE: RIDONDANTE - RISOLTO
    def _build_ghost_infos(self) -> list[dict[str, object]]:
        """Construct ghost info for `EntityRenderer.draw_ghosts`.

        INTEGRAZIONE: le coordinate sono in PIXEL, perché
        `EntityRenderer.draw_ghosts` le usa direttamente come
        `center` (la conversione cella->pixel è stata spostata nel
        chiamante, vedi le righe commentate nel renderer).

        L'interpolazione usa `Ghost.MOVE_STARTED_MS` /
        `Ghost.GHOST_MOVE_DURATION`, aggiornati dal core in
        `GhostBase.team_ghost`. `from_*` / `to_*` sono settati in
        `GhostBase.blinky/clyde/inky/pinky`.

        Il nome è letto con `getattr`: `GhostBase.name` è solo
        un'annotazione di tipo in `__init__`, viene assegnato lazy
        al primo `team_ghost`. Senza fallback, il primo frame
        solleva `AttributeError`.

        Returns:
            Una lista di dict con le chiavi attese dal renderer.
        """
        names_fallback = ("blinky", "pinky", "inky", "clyde")

        tile = self.tile_size
        half = tile // 2
        origin_col, origin_row = self.metrics.maze_origin

        infos: list[dict[str, object]] = []
        for ghost in self.ghosts:
            progress = 0.0
            if not Ghost.MOVING:
                col = origin_col + ghost.g_col * tile + half
                row = origin_row + ghost.g_row * tile + half
            else:
                elapsed = (
                    pygame.time.get_ticks() - Ghost.MOVE_STARTED_MS
                )
                progress = (
                    min(elapsed / Ghost.GHOST_MOVE_DURATION, 1.0)
                )

                from_col = origin_col + ghost.from_col * tile + half
                from_row = origin_row + ghost.from_row * tile + half

                to_cx = origin_col + ghost.to_col * tile + half
                to_cy = origin_row + ghost.to_row * tile + half

                col = int(from_col + (to_cx - from_col) * progress)
                row = int(from_row + (to_cy - from_row) * progress)

            infos.append({
                "name": ghost.name,
                "x": float(col),
                "y": float(row),
                "facing": getattr(ghost, "direction", None) or "right",
                "moving": True,
                "move_progress": progress,
                "state": ghost.state.value,
            })

        return infos

    def _ghost_spawn(self) -> list[tuple[int, int]]:
        """Return the initial spawn positions of the four ghosts.

        The coordinates are expressed as `(int, int)` in cells and
        correspond to the four corners of the maze

        Returns:
            A list of four `(int, int)` tuples.
        """
        return self.maze_corners
