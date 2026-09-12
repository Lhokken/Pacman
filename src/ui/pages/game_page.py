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
from ..renderers.maze_renderer import MazeRenderer
from ..layout.game_layout import GameLayout
from ..renderers.entity_renderer import EntityRenderer

from src.core.entities.ghost import GhostBase as Ghost
from src.core.entities.pacman import PacmanPlayer as Player
from src.core.entities.pacgums import PacgumsManagement as PacgumManager
from src.core.entities.entity_exceptions import EntityError

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class GamePage(Scene):
    """Game scene with maze, player, and side panels."""

    WALL_NONE = 0
    WALL_ALL = 15
    WALL_LEFT = 8
    WALL_RIGHT = 2
    WALL_BOTTOM = 4
    WALL_TOP = 1

    def __init__(self, app: GameApp) -> None:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        super().__init__(app)

        self.config = app.config
        # PLACEHOLDER -----------------------------------------------------
        # TODO: Replace local FontManager/AssetManager creation with cached
        # instances:
        # self.fonts = app.font_manager
        # self.assets = app.asset_manager
        self.maze_width = self.config.levels[0].width
        self.maze_height = self.config.levels[0].height
        self.assets_base = (
            Path(__file__).resolve().parents[3] / "assets" / "img"
        )
        self.fonts = FontManager(self.assets_base)

        screen_w, screen_h = app.screen.get_size()
        self.layout = GameLayout(
            screen_w,
            screen_h,
            self.maze_width,
            self.maze_height,
            min_tile_size=16,
            side_panel_ratio=0.2,
        )
        self.tile_size = self.layout.tile_size

        self.maze = self.generate_maze()
        player_spawn = Player.find_spawn(self.maze)
        self.player = Player(player_spawn[0], player_spawn[1], self.maze)

        # TODO: Decidere dove istanziare -------------------------------
        ghost_spawns = self._ghost_spawn()
        self.ghosts = [Ghost(x, y) for x, y in ghost_spawns]
        self.pacgums = PacgumManager(
            self.maze_width, self.maze_height, self.is_walkable
        )
        self.score = 0

        self.assets = AssetManager(self.assets_base, self.tile_size)
        self.panel_manager = PanelManager(
            self.layout, self.fonts, self.assets_base, self.tile_size
        )
        self.maze_renderer = MazeRenderer(self.maze, self.assets)
        self.entity_renderer = EntityRenderer(self.assets)

    # Public methods -------------------------------------------------------
    # ======================================================================
    #   Public methods
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

    def update(self) -> None:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        try:
            if len(self.player.ghosts_positions) > 0:
                for ghost, (y, x) in zip(
                    self.ghosts, self.player.ghosts_positions
                ):
                    ghost.grid_y = y
                    ghost.grid_x = x
        except IndexError as e:
            raise EntityError(
                f"Error in self.ghosts.grid coordinates update {e}"
            )

        score_gain = self.player.update(self.ghosts, self.pacgums)
        if score_gain:
            self.score += score_gain
            self.panel_manager.update_score(self.score)

    def on_resize(self, new_width: int, new_height: int) -> None:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        self.layout.resize(new_width, new_height)
        new_tile_size = self.layout.tile_size
        if new_tile_size != self.tile_size:
            self.tile_size = new_tile_size
            self.assets.set_tile_size(new_tile_size)
        self.panel_manager = PanelManager(
            self.layout, self.fonts, self.assets_base, self.tile_size
        )

    def draw(self, screen: Surface) -> None:
        """Render the full game scene."""
        screen.fill((20, 20, 30))
        if self.layout.is_too_small():
            msg = "Enlarge window to see the game"
            text_surface = self.fonts.font_white.render(msg)
            text_rect = text_surface.get_rect(
                center=(screen.get_width() // 2, screen.get_height() // 2)
            )
            screen.blit(text_surface, text_rect)
            return

        self.panel_manager.draw(screen)

        origin_x, origin_y = self.layout.get_maze_origin()
        self.maze_renderer.draw(screen, origin_x, origin_y, self.tile_size)

        if self.player.is_moving:
            now = pygame.time.get_ticks()
            elapsed = now - self.player.move_started_ms
            progress = min(elapsed / self.player.MOVE_DURATION_MS, 1.0)
            from_center_x = (
                origin_x
                + self.player.from_x * self.tile_size
                + self.tile_size // 2
            )
            from_center_y = (
                origin_y
                + self.player.from_y * self.tile_size
                + self.tile_size // 2
            )
            to_center_x = (
                origin_x
                + self.player.to_x * self.tile_size
                + self.tile_size // 2
            )
            to_center_y = (
                origin_y
                + self.player.to_y * self.tile_size
                + self.tile_size // 2
            )
            player_center_x = (
                from_center_x + (to_center_x - from_center_x) * progress
            )
            player_center_y = (
                from_center_y + (to_center_y - from_center_y) * progress
            )
            player_pixel_center = (player_center_x, player_center_y)
            player_progress = progress
        else:
            player_center_x = (
                origin_x
                + self.player.grid_x * self.tile_size
                + self.tile_size // 2
            )
            player_center_y = (
                origin_y
                + self.player.grid_y * self.tile_size
                + self.tile_size // 2
            )
            player_pixel_center = (player_center_x, player_center_y)
            player_progress = 0.0

        ghost_positions = [(g.grid_x, g.grid_y) for g in self.ghosts]

        self.entity_renderer.draw(
            screen,
            origin_x,
            origin_y,
            self.tile_size,
            player_pixel_center,
            ghost_positions,
            self.maze,
            self.pacgums.eaten,
            self.player.is_moving,
            player_progress,
        )

    def generate_maze(self) -> list[list[int]]:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        try:
            generator = MazeGenerator(
                size=(self.maze_width, self.maze_height),
                perfect=False,
                seed=self.config.seed,
            )
            generator.generate(seed=self.config.seed)
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
    # ---------------------------------------------------------------------
    # Private Methods ------------------------------------------------------
    # ======================================================================
    #   Helper methods
    # ======================================================================

    def _ghost_spawn(self) -> list[tuple[int, int]]:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        return [
            (0, 0),
            (self.maze_width - 1, 0),
            (0, self.maze_height - 1),
            (self.maze_width - 1, self.maze_height - 1),
        ]

    def _has_wall(self, x: int, y: int, wall_bit: int) -> bool:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        if x < 0 or y < 0 or x >= self.maze_width or y >= self.maze_height:
            return True
        return (self.maze[y][x] & wall_bit) != 0
