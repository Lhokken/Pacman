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
import secrets

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

    def __init__(self, app: GameApp, level: int = 0) -> None:
        """Initialize the game scene for the requested level.

        Args:
            app   : Application providing configuration, display,
                    and navigation.
            level : Zero-based level index; zero starts a new game.
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
            # INTEGRATION: corners in (row, col), as requested by
            # PacgumsManagement.try_to_eat -> `if (row, col) in
            # self.corners`.
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
            # FontManager and AssetManager remain local to the page:
            # AssetManager is tied to the current tile_size and cannot
            # be shared with other scenes.
            self.fonts = FontManager(self.assets_base)
            self.assets = AssetManager(self.assets_base, self.tile_size)
        # --------------------------------------------------------
        #   GAME ENTITY
        # --------------------------------------------------------
        self._maze_seed = self.config.seed
        self.maze = self._generate_maze(seed=self._maze_seed)
        spawn = PacmanPlayer.find_spawn(self.maze)
        if level == 0:
            self.player = PacmanPlayer(spawn[0], spawn[1], self.maze)
            self.current_level: int = 0
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
            self.player.respawn = spawn
        # UPDATE: GhostBase.__init__(g row, g col) -> pass # (row, col).
        #         The previous version passed (x, y).
        self.ghosts = [Ghost(row, col) for row, col in self._ghost_spawn()]
        ghost_names = (
            "blinky",
            "clyde",
            "inky",
            "pinky"
        )
        for ghost, name in zip(self.ghosts, ghost_names):
            ghost.name = name
            ghost.maze = self.maze
            ghost.maze_dim = self.maze_dim
        self.pacgums = PacgumManager(
            self.maze_dim,
            self.is_walkable,
            {
                "pacgum": self.app.config.points_per_pacgum,
                "super_pacgum": self.app.config.points_per_super_pacgum,
                "ghost": self.config.points_per_ghost
            },
            coverage_percent=self.config.pacgum_coverage,
            corners=self.maze_corners,
            seed=self._maze_seed,
            excluded_cells={spawn},
        )
        self._debug_pacgum_baseline = 0
        # SCORE LV 0 ---------------------------------------------
        if level == 0:
            self.score = 0
        # ========================================================
        #   Renderer / Pannels
        # ========================================================
        self.panel_manager = PanelManager(
            self.metrics.panel_layout,
            self.fonts,
            self.assets_base,
            self.tile_size,
        )
        self.maze_renderer = MazeRenderer(self.maze, self.assets)
        self.entity_renderer = EntityRenderer(self.assets)
        # ========================================================
        #   Timer + HUD
        # ========================================================
        self.level_timer = Timer(
            duration=self.config.level_max_time
        )
        self.hud = HUD(
            font_title=self.fonts.font_title_small,
            font_value=self.fonts.font_white,
            timer=self.level_timer,
            current_level=self.current_level + 1,
        )
        # --------------------------------------------------------
        #   Adapter ghost
        # --------------------------------------------------------
        self._frame = 0

    # Public methods -------------------------------------------------------
    # ======================================================================
    #   Life cycle
    # ======================================================================

    def apply_cheats(self, cheats: dict[str, bool]) -> None:
        """Insert given data in player argument."""
        debug_was_enabled = self.player.CHEAT_DATA["data_debug"]
        self.player.cheat_sync(cheats)
        if (
            not debug_was_enabled
            and self.player.CHEAT_DATA["data_debug"]
        ):
            self._debug_pacgum_baseline = len(self.pacgums.eaten)

    def handle_events(self) -> None:
        """Handle game scene input events.

        Forwards keyboard events to the player, handles window resizing,
        and opens the pause menu when ESC is pressed.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.app.handle_window_resize(
                    event.w,
                    event.h
                )
            elif self.player.is_dying:
                continue
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
        if self.player.is_dying:
            death_duration = (
                len(self.assets.player_death_frames)
                * self.entity_renderer.PLAYER_DEATH_FRAME_DURATION_MS
            )
            # TODO: Usare time, get_ticks() e proibita
            death_elapsed = (
                pygame.time.get_ticks() - self.player.death_started_ms
            )
            if death_elapsed < death_duration:
                return
            if self.player.lives <= 0 or self.level_timer.remaining <= 0:
                self.app.switch_scene(
                    GameOverPage(
                        self.app, score=self.score
                    )
                )
                return
            self.player.finish_death()
        elif self.level_timer.remaining <= 0:
            self.app.switch_scene(GameOverPage(self.app, score=self.score))
            return

        # CHEATING - extra lifes -------------------------------------
        if self.player.CHEAT_DATA["extra_lives"] is True:
            self.player.lives += 2
            self.player.CHEAT_DATA["extra_lives"] = False
            if self.player.lives > 3:
                self.player.lives = 3

        score_gain = self.player.update(
            self.ghosts, self.pacgums, self.player
        )
        # CONTROLLO: se entri in DEBUG il conteggio delle 10 pacgums
        #            comincia, non prima.
        if (
            self.player.CHEAT_DATA["data_debug"]
            and len(self.pacgums.eaten) - self._debug_pacgum_baseline >= 10
        ):
            self.pacgums.all_eaten = True
        self.panel_manager.update_lives(self.player.lives)
        if score_gain:
            self.score += score_gain
            self.panel_manager.update_score(self.score)
        if self.pacgums.all_eaten is True:
            self.next_level()
        self._frame += 1

        self.metrics = self._layout.compute(
            *self.app.screen.get_size(),
            self.maze_width,
            self.maze_height,
        )

    def next_level(self) -> None:
        """Set all data in order to begin a new game level.

        This occurs after eating all pacgums, pacman lives and
        score remain unchanged
        """
        self.current_level += 1
        if self.current_level >= len(self.config.levels):
            self.app.switch_scene(VictoryPage(self.app, self.score))
            return
        self.hud.set_level(self.current_level + 1)
        self.player.level = self.current_level
        self.player.maze_height = self.maze_height = \
            self.config.levels[self.current_level].height
        self.player.maze_width = self.maze_width = \
            self.config.levels[self.current_level].width
        self.player.maze_dim = self.maze_dim = \
            (self.maze_height, self.maze_width)
        self.maze_corners = [
            (0, 0),
            (0, self.maze_width - 1),
            (self.maze_height - 1, 0),
            (self.maze_height - 1, self.maze_width - 1),
        ]
        # GENERATE SEED randomly ---------------------------------
        self._maze_seed = secrets.randbits(32)
        self.maze = self.player.maze = self._generate_maze(
            seed=self._maze_seed
        )

        spawn = PacmanPlayer.find_spawn(self.maze)
        self.player.respawn = spawn
        self.player.p_row, self.player.p_col = \
            self.player.from_row, self.player.from_col = \
            self.player.to_row, self.player.to_col = \
            spawn

        # COVERAGE PUCGUMS ---------------------------------------
        self.pacgums = PacgumManager(
            self.maze_dim,
            self.is_walkable,
            {
                "pacgum": self.app.config.points_per_pacgum,
                "super_pacgum": self.app.config.points_per_super_pacgum,
                "ghost": self.config.points_per_ghost,
            },
            coverage_percent=self.config.pacgum_coverage,
            corners=self.maze_corners,
            seed=self._maze_seed,
            excluded_cells={spawn},
        )
        self._debug_pacgum_baseline = 0
        # BUG RESOLVED: the pellet in the top right corner sometimes doesn't
        #               get eaten
        # INTEGRATION : resolved upstream by the fix for `maze_corners` /
        #              `is_walkable`. The comment remains as a reminder.
        self.maze_renderer = MazeRenderer(self.maze, self.assets)
        self.on_resize(*self.app.screen.get_size())
        for i, ghost in enumerate(self.ghosts):
            ghost.corner = self.maze_corners[i]
            ghost.g_row, ghost.g_col = ghost.corner
            ghost.state = GhostState.NORMAL
            ghost.timer = ghost.set_timer - self.current_level
            ghost.maze = self.maze
            ghost.maze_dim = self.maze_dim

        self.level_timer.reset(self.config.level_max_time)

    def on_resize(self, width: int, height: int) -> None:
        """Recalculate layout and update managers without recreating them.

        Args:
            width : New window width in pixels.
            height: New window height in pixels.
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
            screen : Destination surface.
        """
        # TODO: USARE assets manager
        screen.fill((20, 20, 30))

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
        player_center = self._player_pixel_state(ox, oy)
        # -----------------------------------------------------------
        # 5) PACGUM + PLAYER
        # -----------------------------------------------------------
        self.entity_renderer.draw(
            screen,
            ox,
            oy,
            self.tile_size,
            player_center,
            self.maze,
            self.pacgums.eaten,
            self.player.is_moving,
            self.player.direction,
            pacgum_cells=self.pacgums.placed,
            player_dying=self.player.is_dying,
            death_elapsed_ms=(
                pygame.time.get_ticks() - self.player.death_started_ms
                if self.player.is_dying else 0
            ),
        )
        # -----------------------------------------------------------
        # 6) GHOSTS on top of Pac-Man when sprites overlap
        # -----------------------------------------------------------
        ghost_infos = self._build_ghost_infos()
        self.entity_renderer.draw_ghosts(
            screen, ghost_infos,
            frightened_flash=self._is_frightened_flash(),
        )

    # ==================================================================
    #   RENDERNG HELPER
    # ==================================================================
    def _player_pixel_state(
        self, origin_x: int, origin_y: int
    ) -> tuple[float, float]:
        """Return the player's interpolated position in pixels.

        If moving, it linearly interpolates between `from_*` and `to_*`
        based on the time elapsed since the start of the move.

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

        if self.player.is_dying:
            death_row, death_col = self.player.death_position
            return (
                origin_x + int(round(death_col * tile + half)),
                origin_y + int(round(death_row * tile + half)),
            )

        if not self.player.is_moving:
            cx = origin_x + self.player.p_col * tile + half
            cy = origin_y + self.player.p_row * tile + half
            return (cx, cy)

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

        return (cx, cy)

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

    # ==================================================================
    #   Generazione maze
    # ==================================================================
    def _generate_maze(
        self, seed: int | None = None
    ) -> list[list[int]]:
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
                seed=self.config.seed if seed is None else seed,
            )
            maze = [
                [int(wall_mask) for wall_mask in row]
                for row in generator.maze
            ]
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
            logger.error(
                "Maze generation failed: %s",
                e
            )
            raise RuntimeError(
                f"Failed to generate maze: {e}"
            ) from e

    def is_walkable(self, row: int, col: int) -> bool:
        """Indicate whether the cell `(row, col)` is walkable.

        The argument order matches the callback expected by
        ``PacgumsManagement`` and indexes the maze as ``maze[row][col]``.

        Args:
            row : row coordinate of the cell (in cells).
            col : column coordinate of the cell (in cells).

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
    def _build_ghost_infos(self) -> list[dict[str, object]]:
        """Construct ghost info for `EntityRenderer.draw_ghosts`.

        Coordinates are converted to pixels here because the renderer uses
        them directly as sprite centers.

        Interpolation uses ``Ghost.MOVE_STARTED_MS`` and
        ``Ghost.GHOST_MOVE_DURATION``, updated by ``GhostBase.team_ghost``.
        Movement endpoints are set by the ghost movement methods.

        Ghost names are assigned when the game is created, before the first
        render descriptor is built.

        Returns:
            A list of descriptors consumed by the ghost renderer.
        """
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
                progress = min(
                    elapsed / Ghost.GHOST_MOVE_DURATION,
                    1.0,
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
