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
from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

from mazegenerator import MazeGenerator

from ..scene import Scene

from ..managers.font_manager import FontManager
from ..managers.asset_manager import AssetManager
from ..managers.panel_manager import PanelManager

from ..app import GameApp

from ..layout.game_page_layout import GamePageLayout, GamePageMetrics

from ..renderers.maze_renderer import MazeRenderer
from ..renderers.entity_renderer import EntityRenderer

from ..components.hud import HUD
from ...core.timer import Timer
from ...core.entities.ghost import GhostBase as Ghost
from ...core.entities.pacman import PacmanPlayer as Player
from ...core.entities.pacgums import PacgumsManagement as PacgumManager

if TYPE_CHECKING:
    from ..app import GameApp

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

    def __init__(self, app: GameApp, level: int=0) -> None:
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
        spawn = Player.find_spawn(self.maze)
        if level == 0:
            self.player = Player(spawn[0], spawn[1], self.maze)
        else:
            self.player.grid_x = spawn[0]
            self.player.grid_y = spawn[1]
            self.player.from_x = spawn[0]
            self.player.from_y = spawn[1]
            self.player.to_x = spawn[0]
            self.player.to_y = spawn[1]
        self.ghosts = [Ghost(x, y) for x, y in self._ghost_spawn()]
        self.pacgums = PacgumManager(
            self.maze_width, self.maze_height, self.is_walkable
        )
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
        self.current_level: int = 0

        # TODO(core-integration): Keep the live match/core object here when
        # the game orchestration refactor provides one. `apply_cheats()`
        # should delegate to that object instead of implementing gameplay
        # rules in this UI scene.

    # Public methods -------------------------------------------------------
    # ======================================================================
    #   Life cycle
    # ======================================================================
    # TODO(core-integration): Add `apply_cheats(cheats: dict[str, bool])`.
    # It must forward the complete cheat state to the core instance that
    # owns this match, including changes made while the match is paused.

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

    # PAUSE ------------------------------------------------------------------
    def on_pause(self) -> None:
        """Mette in pausa il timer di livello."""
        self.level_timer.pause()

    # RESUME -----------------------------------------------------------------
    def on_resume(self) -> None:
        """Riprende il timer di livello."""
        self.level_timer.resume()

    # UPDATE GHOST -----------------------------------------------------------
    def update(self) -> None:
        """Aggiorna lo stato della partita per il frame corrente.

        TODO: inglese
        Sincronizza i ghost visivi sulle posizioni calcolate dal core,
        delega al giocatore l'update logico e, se il punteggio è
        cambiato, aggiorna il pannello laterale.
        """
        # self._sync_ghosts_from_player()
        score_gain = self.player.update(
            self.ghosts, self.pacgums, self.player
        )
        self.panel_manager.update_lives(self.player.lives)
        # self.panel_manager
        if score_gain:
            self.score += score_gain
            self.panel_manager.update_score(self.score)
        if self.pacgums.next_level is True:
            self.next_level()
        self._frame += 1

    def next_level(self) -> None:
        self.config.seed += 17
        self.player.maze = self._generate_maze()
        self.maze = self.player.maze
        self.pacgums = PacgumManager(
            self.maze_width, self.maze_height, self.is_walkable
        )
        self.maze_renderer = MazeRenderer(self.maze, self.assets)
        for ghost in self.ghosts:
            ghost.grid_y, ghost.grid_x = ghost.corner
        self.current_level += 1

    def on_resize(self, width: int, height: int) -> None:
        """Ricalcola layout e aggiorna i manager senza ricrearli.

        TODO: tradurre in inglese
        Args:
            new_width : Nuova larghezza della finestra in px.
            new_height: Nuova altezza della finestra in px.
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
        #   Pannellis
        # --------------------------------------------------------------
        # I pannelli si riposizionano con il nuovo layout, senza
        # perdere lo stato (score/lives correnti restano).
        self.panel_manager.relayout(self.metrics.panel_layout, new_tile)

    def draw(self, screen: Surface) -> None:
        """Disegna la scena delegando ai renderer.

        TODO: tradurre in inglese
        Args:
            screen: Surface di destinazione.
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
        ghost_positions = [(g.grid_x, g.grid_y) for g in self.ghosts]
        self.entity_renderer.draw(
            screen, ox, oy, self.tile_size,
            player_center, ghost_positions,
            self.maze, self.pacgums.eaten,
            self.player.is_moving, player_progress, self.player.direction
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
            cx = origin_x + self.player.grid_x * tile + half
            cy = origin_y + self.player.grid_y * tile + half
            return (cx, cy), 0.0

        elapsed = (
            pygame.time.get_ticks() - self.player.move_started_ms
        )
        progress = (
            min(elapsed / self.player.MOVE_DURATION_MS, 1.0)
        )

        from_cx = origin_x + self.player.from_x * tile + half
        from_cy = origin_y + self.player.from_y * tile + half

        to_cx = origin_x + self.player.to_x * tile + half
        to_cy = origin_y + self.player.to_y * tile + half

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
        power_timer = getattr(self.player, "power_timer", 0)
        return (
            power_timer > 0
            and power_timer < 120
            and (power_timer // 10) % 2 == 0
        )

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

    def is_walkable(self, x: int, y: int) -> bool:
        """Indicate whether the cell `(x, y)` is walkable.

        Args:
            x: X-coordinate of the cell (in cells).
            y: Y-coordinate of the cell (in cells).

        Returns:
            `True` if the cell is within the boundaries and is not a solid
            wall; `False` otherwise.
        """
        if x < 0 or y < 0 or x >= self.maze_width or y >= self.maze_height:
            return False
        return self.maze[y][x] != 15

    # Private Methods ------------------------------------------------------
    # ======================================================================
    #   Helper methods
    # ======================================================================
    # def _sync_ghosts_from_player(self) -> None:
    #     # NOTE: RIDONDANTE
    #     """Copy the positions calculated by the player to the UI ghosts.

    #     `player.ghosts_positions` is populated by the core during
    #     `player.update()`. Here, we read it and apply it to the
    #     visual `Ghost` objects. On the first frame, the list is empty:
    #     `zip` on an empty list is a no-op.
    #     """
    #     positions = getattr(self.player, "ghosts_positions", None)
    #     if not positions:
    #         return
    #     for ghost, (gy, gx) in zip(self.ghosts, positions):
    #         ghost.grid_y = gy
    #         ghost.grid_x = gx

    def _build_ghost_infos(self) -> list[dict[str, object]]:
        """Construct ghost info for `EntityRenderer.draw_ghosts`.

        Format expected by the renderer:
        name, x, y, facing, moving, move_progress, state

        Sources:

            - `x`, `y`: `ghost.grid_x`, `ghost.grid_y` (in cells).
            - `facing`: `ghost.direction` if populated by the core,
            otherwise `"right"`.
            - `moving`: `False` (the core does not expose this yet).
            - `move_progress`: `0.0`.
            - `state`: current value of `ghost.state`.

        The idle animation (stationary ghosts that "pulse") is handled by
        the renderer using real-time data; no need to move them here.

        Returns:
            A list of dictionaries, one per ghost, containing the keys
            expected by the renderer.
        """
        names = (
            "blinky",
            "pinky",
            "inky",
            "clyde"
        )
        # NOTE : Abbiamo lo spazio per lo state... SEMBRA non esserci nulla di
        #        'rotto' in ui.
        infos: list[dict[str, object]] = []
        for ghost, name in zip(self.ghosts, names):
            infos.append({
                "name": name,
                "x": float(ghost.grid_x),
                "y": float(ghost.grid_y),
                "facing": getattr(ghost, "direction", None) or "right",
                "moving": False,
                "move_progress": 0.0,
                "state": ghost.state.value,
            })
        return infos

    def _ghost_spawn(self) -> list[tuple[int, int]]:
        """Return the initial spawn positions of the four ghosts.

        The coordinates are expressed as `(x, y)` in cells and
        correspond to the four corners of the maze

        Returns:
        A list of four `(x, y)` tuples.
        """
        return [
            (0, 0),
            (0, self.maze_width - 1),
            (self.maze_height - 1, 0),
            (self.maze_width - 1, self.maze_height - 1),
        ]
