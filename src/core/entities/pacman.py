"""Pac-Man player status and behavior.

The class maintains only the state necessary for waypoint movement:
current location, start/finish cells, queuing direction and
movement start timestamp. Contains no collision logic either
of time progression.
"""

from __future__ import annotations
import logging
import pygame
from src.core.entities.ghost import GhostBase, GhostState
from typing import TYPE_CHECKING
from random import randint

if TYPE_CHECKING:
    from src.core.entities.pacgums import PacgumsManagement

logger = logging.getLogger(__name__)


class PacmanPlayer:
    """Represents the player's state during the game.

    Attributes:
        p_col: Current column in the maze grid.
        p_row: Current row in the maze grid.
        from_col: Starting column of the movement in progress.
        from_row: Starting line of the movement in progress.
        to_col  : Destination column of the movement in progress.
        to_row  : Destination row of the movement in progress.
        queued_direction: Direction requested by the input ('up', 'down',
                      'left', 'right') waiting to be applied. Persistent:
                      remains active until overwritten by new input.
        is_moving      : True if there is movement between two cells.
        move_started_ms: Timestamp in milliseconds of the start of
                         current movement (0 if stopped).
        direction      : Current direction (for future use, not yet
                         used by the motion logic).
    """

    MOVE_DURATION_MS = 200

    WALL_LEFT = 8
    WALL_RIGHT = 2
    WALL_BOTTOM = 4
    WALL_TOP = 1

    INIT_DATA: dict[str, int] = {
        "Lives": 0
    }

    CHEAT_DATA: dict[str, bool] = {
        "invincible": False,
        "data_debug": False,
        "ghost_freeze": False,
        "extra_lives": False,
        "increased_speed": False
    }

    def __init__(self, row: int, col: int,
                 maze: list[list[int]]) -> None:
        """Initialize the player with a starting position.

        Args:
            row: Starting row in the maze grid.
            col: Starting column in the maze grid.
            maze: Maze represented as a grid of wall bitmasks.
        """
        self.respawn = (row, col)
        self.p_row = row
        self.p_col = col
        self.from_row = row
        self.from_col = col
        self.to_row = row
        self.to_col = col
        self.debug = False
        self.lives = self.INIT_DATA["Lives"]
        if self.CHEAT_DATA["extra_lives"] is True:
            self.lives += 2
        if self.CHEAT_DATA["increased_speed"] is True:
            self.MOVE_DURATION_MS = 100
        if self.CHEAT_DATA["data_debug"] is True:
            self.debug = True
        self.queued_direction: str | None = None
        self.is_moving = False
        self.move_started_ms = 0
        self.is_dying = False
        self.death_started_ms = 0
        self.death_position = (float(row), float(col))
        self.direction: None | str = None
        self.maze = maze
        self.maze_height = len(maze)
        self.maze_width = len(maze[0]) if maze else 0
        self.maze_dim: tuple[int, int]
        self.maze_corners: list[
            tuple[int, int]
            ]
        self.level: int = 0

    # Public methods -------------------------------------------------------
    # ======================================================================
    #   INPUT PLAYER
    # ======================================================================

    @classmethod
    def cheat_sync(cls, parameter: dict[str, bool]) -> None:
        """Update the shared cheat flags.

        Args:
            parameter: Mapping of cheat names to their enabled states.
        """
        for key, value in parameter.items():
            if value is False:
                cls.CHEAT_DATA[key] = False
            elif value is True:
                cls.CHEAT_DATA[key] = True

    @classmethod
    def init_data_set(cls, lives: int) -> None:
        """Set the starting number of lives for new players.

        Args:
            lives: Configured starting number of lives.
        """
        cls.INIT_DATA["Lives"] = lives

    @staticmethod
    def find_spawn(maze: list[list[int]]) -> tuple[int, int]:
        """Find a walkable cell close to the maze center."""
        if len(maze) < 5:
            raise RuntimeError("Maze too small")
        row = int((len(maze) - 5) / 2) + 2
        col = int((len(maze[0]) - 7) / 2) + 3
        if maze[row][col] != 15:
            return row, col
        else:
            for _ in range(0, 42):
                row = row + randint(-1, 1)
                if maze[row][col] != 15:
                    return row, col
                col = col + randint(-1, 1)
                if maze[row][col] != 15:
                    return row, col
        raise RuntimeError(
            "No walkable cell found near center for player spawn"
        )

    def can_move(
        self, current_row: int, current_col: int, new_row: int, new_col: int
    ) -> bool:
        """Check whether the player may move to a target cell."""
        if (
            new_col < 0
            or new_row < 0
            or new_col >= self.maze_width
            or new_row >= self.maze_height
        ):
            return False
        if new_col < current_col:
            return (
                not self._has_wall(current_row, current_col, self.WALL_LEFT)
                and not self._has_wall(new_row, new_col, self.WALL_RIGHT)
            )
        if new_col > current_col:
            return (
                not self._has_wall(current_row, current_col, self.WALL_RIGHT)
                and not self._has_wall(new_row, new_col, self.WALL_LEFT)
            )
        if new_row < current_row:
            return (
                not self._has_wall(current_row, current_col, self.WALL_TOP)
                and not self._has_wall(new_row, new_col, self.WALL_BOTTOM)
            )
        if new_row > current_row:
            return (
                not self._has_wall(current_row, current_col, self.WALL_BOTTOM)
                and not self._has_wall(new_row, new_col, self.WALL_TOP)
            )
        return False

    def _has_wall(self, row: int, col: int, wall_bit: int) -> bool:
        if col < 0 or row < 0 or col >= self.maze_width or \
                row >= self.maze_height:
            return True
        return (self.maze[row][col] & wall_bit) != 0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Store a movement request from a keyboard event."""
        if self.is_dying:
            return
        if event.type != pygame.KEYDOWN:
            return
        directions = {
            pygame.K_UP: "up",
            pygame.K_w: "up",
            pygame.K_DOWN: "down",
            pygame.K_s: "down",
            pygame.K_LEFT: "left",
            pygame.K_a: "left",
            pygame.K_RIGHT: "right",
            pygame.K_d: "right",
        }
        if event.key in directions:
            self.queued_direction = directions[event.key]

    # ======================================================================
    #   MOVIMENTO PLAYER
    # ======================================================================
    def update(self, ghosts: list[GhostBase],
               pacgums: PacgumsManagement,
               pacman: PacmanPlayer) -> int:
        """Advance movement and eat a pacgum when a move is complete."""
        if self.is_dying:
            return 0
        score_gain: int = 0
        if self.CHEAT_DATA["ghost_freeze"] is False:
            ghost_time = (
                pygame.time.get_ticks() - GhostBase.MOVE_STARTED_MS
            )
            if ghost_time >= GhostBase.GHOST_MOVE_DURATION:
                GhostBase.team_ghost(
                    ghosts,
                    (pacman.p_row, pacman.p_col),
                    rand=(50 + (self.level * 3)),
                    debug=self.CHEAT_DATA["data_debug"]
                    )
            if self.is_dying:
                return score_gain
        if self.is_moving:
            elapsed_time = (
                pygame.time.get_ticks() - self.move_started_ms
            )
            if elapsed_time >= self.MOVE_DURATION_MS:
                self.debug_print(pacman)

                self.is_moving = False
                self.move_started_ms = 0
                score_gain += pacgums.try_to_eat(
                    ghosts,
                    self.p_row,
                    self.p_col,
                )
        score_gain += self.collision_check(ghosts, pacgums)
        if self.is_dying:
            return score_gain
        if not self.is_moving:
            self._try_start_move()
        return score_gain

    def collision_check(
            self,
            ghosts: list[GhostBase],
            pacgums: PacgumsManagement,
            ) -> int:
        """Resolve interpolated contact with ghosts.

        Args:
            ghosts  : Ghosts currently active in the maze.
            pacgums : Manager providing the points for eaten ghosts.

        Returns:
            Points earned for ghosts eaten during this check.
        """
        if self.is_dying:
            return 0
        now = pygame.time.get_ticks()
        if self.is_moving:
            player_progress = min(
                max((now - self.move_started_ms) / self.MOVE_DURATION_MS, 0),
                1,
            )
            player_row = (
                self.from_row
                + (self.to_row - self.from_row) * player_progress
            )
            player_col = (
                self.from_col
                + (self.to_col - self.from_col) * player_progress
            )
        else:
            player_row = float(self.p_row)
            player_col = float(self.p_col)

        score_gain = 0
        for ghost in ghosts:
            if now < ghost.collision_immune_until_ms:
                continue
            if GhostBase.MOVING:
                ghost_progress = min(
                    max(
                        (now - GhostBase.MOVE_STARTED_MS)
                        / GhostBase.GHOST_MOVE_DURATION,
                        0,
                    ),
                    1,
                )
                ghost_row = (
                    ghost.from_row
                    + (ghost.to_row - ghost.from_row) * ghost_progress
                )
                ghost_col = (
                    ghost.from_col
                    + (ghost.to_col - ghost.from_col) * ghost_progress
                )
            else:
                ghost_row = float(ghost.g_row)
                ghost_col = float(ghost.g_col)

            row_distance = player_row - ghost_row
            col_distance = player_col - ghost_col
            overlaps = row_distance**2 + col_distance**2 < 0.8**2
            if overlaps:
                if ghost.state == GhostState.FRIGHTENED:
                    ghost.state = GhostState.EATEN
                    score_gain += pacgums.dict_point["ghost"]
                elif ghost.state == GhostState.EATEN:
                    pass
                elif ghost.state == GhostState.NORMAL and \
                        self.CHEAT_DATA["invincible"] is False:
                    self.life_loss()
                    self.pacman_respawn(ghosts)
                    break
        return score_gain

    def debug_print(self, pacman: PacmanPlayer) -> None:
        """Print player diagnostics when data-debug mode is enabled.

        Args:
            pacman: Player instance whose position and lives are reported.
        """
        if self.CHEAT_DATA["data_debug"] is True:
            print(
                f"Pacman pos: {pacman.p_row, pacman.p_col} "
                f"lives: {pacman.lives}"
                )

    def _try_start_move(self) -> None:
        """Start a movement if a direction is queued and the move is valid."""
        direction = self.queued_direction
        self.direction = direction
        if direction is None:
            return

        d_row, d_col = 0, 0
        if direction == "up":
            d_row = -1
        elif direction == "down":
            d_row = 1
        elif direction == "left":
            d_col = -1
        elif direction == "right":
            d_col = 1

        current_row = self.p_row
        current_col = self.p_col
        new_row = current_row + d_row
        new_col = current_col + d_col

        if self.can_move(current_row, current_col, new_row, new_col):
            self.from_row = current_row
            self.from_col = current_col
            self.to_row = new_row
            self.to_col = new_col
            self.p_row = new_row
            self.p_col = new_col
            self.is_moving = True
            self.direction = direction
            self.move_started_ms = pygame.time.get_ticks()

    def pacman_respawn(self, ghosts: list[GhostBase]) -> None:
        """Give each ghost it's original corner position."""
        for g in ghosts:
            g.from_row, g.from_col = g.to_row, g.to_col = \
                g.g_row, g.g_col = g.corner

    def ghosts_places(self, ghosts: list[GhostBase]) -> list[tuple[int, int]]:
        """Return the row and column of each ghost.

        Args:
            ghosts: Ghosts whose positions are collected.

        Returns:
            A list of ``(row, column)`` positions.
        """
        ghosts_list: list[tuple[int, int]] = []
        for ghost in ghosts:
            ghosts_list.append((ghost.g_row, ghost.g_col))
        return ghosts_list

    def life_loss(self) -> None:
        """Start the death animation and decrement one life."""
        if self.is_dying:
            return
        now = pygame.time.get_ticks()
        if self.is_moving:
            progress = min(
                (now - self.move_started_ms) / self.MOVE_DURATION_MS,
                1.0,
            )
            row = self.from_row + (self.to_row - self.from_row) * progress
            col = self.from_col + (self.to_col - self.from_col) * progress
            self.death_position = (row, col)
        else:
            self.death_position = (float(self.p_row), float(self.p_col))

        print("\a", end="", flush=True)
        self.lives -= 1
        self.is_dying = True
        self.death_started_ms = now
        self.is_moving = False
        self.move_started_ms = 0
        self.queued_direction = None

    def finish_death(self) -> None:
        """Respawn at the maze center after the death animation."""
        if self.lives <= 0:
            return
        row, col = self.respawn
        self.p_row = self.from_row = self.to_row = row
        self.p_col = self.from_col = self.to_col = col
        self.death_position = (float(row), float(col))
        self.direction = None
        self.queued_direction = None
        self.is_moving = False
        self.move_started_ms = 0
        self.death_started_ms = 0
        self.is_dying = False
