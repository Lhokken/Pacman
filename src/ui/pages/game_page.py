"""Game scene with maze, player, and side panels."""

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
    """Game scene with maze, player, and side panels."""

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

    def __init__(self, app: GameApp) -> None:
        """FA TODO: Docstring."""
        super().__init__(app)

        self.config = app.config
        self.assets_base = (
            Path(__file__).resolve().parents[3] / "assets" / "img"
        )
        # --------------------------------------------------------
        #   Griglia di gioco
        # --------------------------------------------------------
        self.maze_width = self.config.levels[0].width
        self.maze_height = self.config.levels[0].height
        # --------------------------------------------------------
        #  --- Layout: tutte le metriche grafiche in un posto ---
        # --------------------------------------------------------
        self._layout = GamePageLayout()
        self.metrics: GamePageMetrics = self._layout.compute(
            *app.screen.get_size(),
            self.maze_width,
            self.maze_height,
        )
        self.tile_size = self.metrics.tile_size
        # --------------------------------------------------------
        #   Manager
        # --------------------------------------------------------
        # FontManager e AssetManager restano locali alla pagina:
        # AssetManager è legato al tile_size corrente e non può
        # essere condiviso con altre scene.
        self.fonts = FontManager(self.assets_base)
        self.assets = AssetManager(self.assets_base, self.tile_size)
        # --------------------------------------------------------
        #   Entità di gioco
        # --------------------------------------------------------
        self.maze = self._generate_maze()
        spawn = Player.find_spawn(self.maze)
        self.player = Player(spawn[0], spawn[1], self.maze)
        self.ghosts = [Ghost(x, y) for x, y in self._ghost_spawn()]
        self.pacgums = PacgumManager(
            self.maze_width, self.maze_height, self.is_walkable
        )
        self.score = 0
        # --------------------------------------------------------
        # --- Renderer / pannelli ---
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
        # --- Timer + HUD ---
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
        #   Adapter ghost (dipendenza esterna)
        # --------------------------------------------------------
        self._frame = 0

    # Public methods -------------------------------------------------------
    # ======================================================================
    #   Life cycle
    # ======================================================================
    def handle_events(self) -> None:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
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
        """Gestisce la pausa."""
        self.level_timer.pause()

    # RESUME -----------------------------------------------------------------
    def on_resume(self) -> None:
        """Gestisce il resume."""
        self.level_timer.resume()

    # UPDATE GHOST -----------------------------------------------------------
    def update(self) -> None:
        """Sincronizza i ghost sulle posizioni calcolate dal core."""
        self._sync_ghosts_from_player()
        
        score_gain = self.player.update(
            self.ghosts, self.pacgums, self.player
        )
        if score_gain:
            self.score += score_gain
            self.panel_manager.update_score(self.score)

        self._frame += 1

    def on_resize(self, new_width: int, new_height: int) -> None:
        """Ricalcola layout e aggiorna i manager senza ricrearli."""
        self.metrics = self._layout.compute(
            new_width, new_height,
            self.maze_width, self.maze_height,
        )

        new_tile = self.metrics.tile_size
        if new_tile != self.tile_size:
            self.tile_size = new_tile
            self.assets.set_tile_size(new_tile)

        # I pannelli si riposizionano con il nuovo layout, senza
        # perdere lo stato (score/lives correnti restano).
        self.panel_manager.relayout(self.metrics.panel_layout, new_tile)

    def draw(self, screen: Surface) -> None:
        """Draw the scene by delegating to the renderers."""
        screen.fill((20, 20, 30))

        if self.metrics.too_small:
            self._draw_too_small_hint(screen)
            return

        # -----------------------------------------------------------
        #   SCENE
        # -----------------------------------------------------------
        # 1) Pannelli laterali --------------------------------------
        self.panel_manager.draw(screen)

        # 2) HUD (countdown) — autoposizionante ---------------------
        self.hud.draw(screen)

        # 3) Maze ---------------------------------------------------
        ox, oy = self.metrics.maze_origin
        self.maze_renderer.draw(screen, ox, oy, self.tile_size)

        # 4) Player: pixel center + progresso interpolazione --------
        player_center, player_progress = (
            self._player_pixel_state(ox, oy)
        )

        # 5) Ghost — info costruite direttamente dai ghost UI --------
        ghost_infos = self._build_ghost_infos()

        self.entity_renderer.draw_ghosts(
            screen, ox, oy, self.tile_size, ghost_infos,
            frightened_flash=self._is_frightened_flash(),
        )

        # 6) Pacgum, super-pacgum, player -----------------------------
        ghost_positions = [(g.grid_x, g.grid_y) for g in self.ghosts]
        
        self.entity_renderer.draw(
            screen, ox, oy, self.tile_size,
            player_center, ghost_positions,
            self.maze, self.pacgums.eaten,
            self.player.is_moving, player_progress,
            self.player.direction
        )

    # ==================================================================
    #   Helper di rendering
    # ==================================================================
    def _player_pixel_state(
        self, origin_x: int, origin_y: int
    ) -> tuple[tuple[float, float], float]:
        """Ritorna ((cx, cy), progress) per il player.

        Se fermo: progress = 0. Se in movimento: interpola tra from_*
        e to_* in base al tempo trascorso.
        """
        tile = self.tile_size
        half = tile // 2

        if not self.player.is_moving:
            cx = origin_x + self.player.grid_x * tile + half
            cy = origin_y + self.player.grid_y * tile + half
            return (cx, cy), 0.0

        elapsed = pygame.time.get_ticks() - self.player.move_started_ms
        progress = min(elapsed / self.player.MOVE_DURATION_MS, 1.0)

        from_cx = origin_x + self.player.from_x * tile + half
        from_cy = origin_y + self.player.from_y * tile + half

        to_cx = origin_x + self.player.to_x * tile + half
        to_cy = origin_y + self.player.to_y * tile + half

        cx = int(from_cx + (to_cx - from_cx) * progress)
        cy = int(from_cy + (to_cy - from_cy) * progress)
        return (cx, cy), progress

    def _is_frightened_flash(self) -> bool:
        """Imposta end frightened se power timer è agli sgoccioli.

        `power_timer` non è ancora esposto da PacmanPlayer: getattr
        con default 0 mantiene il comportamento invariato finché il
        core non lo popolerà.
        """
        power_timer = getattr(self.player, "power_timer", 0)
        return (
            power_timer > 0
            and power_timer < 120
            and (power_timer // 10) % 2 == 0
        )

    def _draw_too_small_hint(self, screen: Surface) -> None:
        """Gestisce la logica relativa alla riduzione della finestra."""
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
        """Generate and validate the maze used by the game page."""
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
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        if x < 0 or y < 0 or x >= self.maze_width or y >= self.maze_height:
            return False
        return self.maze[y][x] != 15

    # Private Methods ------------------------------------------------------
    # ======================================================================
    #   Helper methods
    # ======================================================================
    def _sync_ghosts_from_player(self) -> None:
        """Copia le posizioni calcolate dal player sui ghost UI.

        `player.ghosts_positions` è popolato dal core durante
        `player.update()`. Qui lo leggiamo e lo applichiamo agli
        oggetti Ghost visivi. Al primo frame la lista è vuota:
        zip su lista vuota è no-op.
        """
        positions = getattr(self.player, "ghosts_positions", None)
        if not positions:
            return
        for ghost, (gy, gx) in zip(self.ghosts, positions):
            ghost.grid_y = gy
            ghost.grid_x = gx

    def _build_ghost_infos(self) -> list[dict]:
        """Costruisce le info ghost per EntityRenderer.draw_ghosts.

        Formato atteso dal renderer:
            name, x, y, facing, moving, move_progress, state

        Fonti:
            - x, y         : `ghost.grid_x`, `ghost.grid_y` (in celle)
            - facing       : `ghost.direction` se popolato dal core,
                             altrimenti "right"
            - moving       : False (il core non lo espone ancora)
            - move_progress: 0.0
            - state        : "normal" (frightened/eaten li popolerà
                             il core quando esisterà)

        L'idle animation (ghost fermi che "pulsano") è gestita dal
        renderer via tempo reale: non serve muoverli qui.
        """
        names = (
            "blinky",
            "pinky",
            "inky",
            "clyde"
        )
        infos: list[dict] = []
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
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        return [
            (0, 0),
            (0, self.maze_width - 1),
            (self.maze_height - 1, 0),
            (self.maze_width - 1, self.maze_height - 1),
        ]
