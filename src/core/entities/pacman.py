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

if TYPE_CHECKING:
    from src.core.entities.pacgums import PacgumsManagement

logger = logging.getLogger(__name__)
#   Chapter VI - Game specifications  VI.2 Player -----------------------------
#
#   • Can move through corridors only (no walls).
#   • Can move in 4 directions (up, down, left, right) using arrow keys or WASD
#     (depending on your keyboard).
#   • Starts with 3 lives.
#   • Loses a life when touched by a ghost.
#   • Respawns in the middle of the maze after losing a life.
#   • Game over when all lives are lost.
#   • Wins the level when all pacgums are eaten.
#   • Wins the game when all levels are completed.
#   • Eating a pacgum increases the score by X points.
#   • Eating a super-pacgum (power pellet) increases the score by Y points and
#     makes ghosts edible for a short time.
#   • Eating an edible ghost increases the score by Z points


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
            p_row : Starting row in the maze grid. y
            p_col : Starting column in the maze grid. x
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
            self.MOVE_DURATION_MS = 120
        if self.CHEAT_DATA["data_debug"] is True:
            self.debug = True
        self.queued_direction: str | None = None
        self.is_moving = False
        self.move_started_ms = 0
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
        """Fa TODO: docstring."""
        for key, value in parameter.items():
            if value is False:
                cls.CHEAT_DATA[key] = False
            elif value is True:
                cls.CHEAT_DATA[key] = True

    @classmethod
    def init_data_set(cls, lives: int) -> None:
        """Fa TODO: docstring."""
        cls.INIT_DATA["Lives"] = lives

    @staticmethod
    def find_spawn(maze: list[list[int]]) -> tuple[int, int]:
        """Find a walkable cell close to the maze center."""
        maze_height = len(maze)
        maze_width = len(maze[0]) if maze else 0
        center_col = maze_width // 2
        center_row = maze_height // 2
        for offset in range(1, maze_height - center_row):
            row = center_row + offset
            if maze[row][center_col] != 15:
                return row, center_col
        for offset in range(1, center_row + 1):
            row = center_row - offset
            if maze[row][center_col] != 15:
                return row, center_col
        raise RuntimeError(
            "No walkable cell found near center for player spawn"
        )

    def can_move(
        self, current_x: int, current_y: int, new_x: int, new_y: int
    ) -> bool:
        """Check whether the player may move to a target cell."""
        if (
            new_x < 0
            or new_y < 0
            or new_x >= self.maze_width
            or new_y >= self.maze_height
        ):
            return False
        if new_x < current_x:
            return (
                not self._has_wall(current_x, current_y, self.WALL_LEFT)
                and not self._has_wall(new_x, new_y, self.WALL_RIGHT)
            )
        if new_x > current_x:
            return (
                not self._has_wall(current_x, current_y, self.WALL_RIGHT)
                and not self._has_wall(new_x, new_y, self.WALL_LEFT)
            )
        if new_y < current_y:
            return (
                not self._has_wall(current_x, current_y, self.WALL_TOP)
                and not self._has_wall(new_x, new_y, self.WALL_BOTTOM)
            )
        if new_y > current_y:
            return (
                not self._has_wall(current_x, current_y, self.WALL_BOTTOM)
                and not self._has_wall(new_x, new_y, self.WALL_TOP)
            )
        return False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Store a movement request from a keyboard event."""
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
        score_gain = 0
        if self.CHEAT_DATA["data_debug"] is True and len(pacgums.eaten) > 9:
            pacgums.all_eaten = True
        if self.CHEAT_DATA["ghost_freeze"] is False:
            # TODO: Ghost movement is currently advanced only when
            # Pacman completes a tile. Give ghosts their own timed
            # movement/update so their speed and interpolation do not
            # depend on Pacman's move duration.
            if self.is_moving:
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
        if self.is_moving:
            elapsed_time = (
                pygame.time.get_ticks() - self.move_started_ms
            )
            if elapsed_time >= self.MOVE_DURATION_MS:
                self.debug_print(pacman)

                self.is_moving = False
                self.move_started_ms = 0
                score_gain = pacgums.try_to_eat(
                    ghosts,
                    self.p_row,
                    self.p_col,
                )
                for ghost in ghosts:
                    if (ghost.g_row, ghost.g_col) in \
                            [(self.p_row, self.p_col),
                             (self.from_row, self.from_col)]:
                        if ghost.state == GhostState.FRIGHTENED:
                            ghost.state = GhostState.EATEN
                            score_gain += pacgums.dict_point["ghost"]
                        elif ghost.state == GhostState.EATEN:
                            pass
                        elif ghost.state == GhostState.NORMAL and \
                                self.CHEAT_DATA["invincible"] is False:
                            self.life_loss()
                            self.pacman_respawn(ghosts)
                if score_gain > 0 and \
                    (pacman.p_row, pacman.p_col) in self.maze_corners:
                    # -------------------------------------------------------
                    # NOTE: STATO FLASH NON FUNZIONANTE - VEDI ANCHE PARSEY.PY
                    # -------------------------------------------------------
                    # RISOLTO!

                    for ghost in ghosts:
                        ghost.state = GhostState.FRIGHTENED
                self._try_start_move()
        else:
            self._try_start_move()
        return score_gain

    def debug_print(self, pacman: PacmanPlayer) -> None:
        """Print the debug."""
        if self.CHEAT_DATA["data_debug"] is True:
            print(
                f"Pacman pos: {pacman.p_row, pacman.p_col} "
                f"lives: {pacman.lives}"
                )

    def _try_start_move(self) -> None:
        """Start a movement if a direction is queued and the move is valid."""
        # ------------------------------------------------------------------
        #   DIREZIONE
        # ----------------1--------------------------------------------------
        # PLACEHOLDER ------------------------------------------------------
        # RISOLTO
        direction = self.queued_direction
        self.direction = direction
        if direction is None:
            return

        dx, dy = 0, 0
        if direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        elif direction == "left":
            dx = -1
        elif direction == "right":
            dx = 1

        current_x = self.p_col
        current_y = self.p_row
        new_x = current_x + dx
        new_y = current_y + dy

        if self.can_move(current_x, current_y, new_x, new_y):
            self.from_col = current_x
            self.from_row = current_y
            self.to_col = new_x
            self.to_row = new_y
            self.p_col = new_x
            self.p_row = new_y
            self.is_moving = True
            self.direction = direction
            self.move_started_ms = pygame.time.get_ticks()

    def _has_wall(self, x: int, y: int, wall_bit: int) -> bool:
        if x < 0 or y < 0 or x >= self.maze_width or y >= self.maze_height:
            return True
        return (self.maze[y][x] & wall_bit) != 0

    def pacman_respawn(self, ghosts: list[GhostBase]) -> None:
        """Give each ghost a random position in the maze.

        Given distance is far enough to let player continue game.
        """
        for i, _ in enumerate(ghosts):
            while GhostBase.get_distance(
                    (ghosts[i].g_row, ghosts[i].g_col),
                    self.respawn) < 7 or \
                        len(set(self.ghosts_places(ghosts))) != 4:
                (ghosts[i].g_row, ghosts[i].g_col) = GhostBase.next_step(
                    ghosts[i].g_row,
                    ghosts[i].g_col,
                    self.maze,
                    self.maze_dim
                )

    def ghosts_places(self, ghosts: list[GhostBase]) -> list[tuple[int, int]]:
        """Return a list of tuples with ghost coordinates
        """
        ghosts_list: list[tuple[int, int]] = []
        for ghost in ghosts:
            ghosts_list.append((ghost.g_row, ghost.g_col))
        return ghosts_list

    def life_loss(self) -> None:
        """Life loss manager.

        Notify to game over page when pacman lose the last life
        TODO: connect with game over page
        """
        print("\a")
        self.lives -= 1
        if self.lives > 0:
            self.p_row, self.p_col = self.from_row, self.from_col = \
                self.to_row, self.to_col = self.respawn
