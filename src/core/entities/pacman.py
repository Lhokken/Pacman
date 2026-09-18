"""Pac-Man player status and behavior.

The class maintains only the state necessary for waypoint movement:
current location, start/finish cells, queuing direction and
movement start timestamp. Contains no collision logic either
of time progression.
"""

from __future__ import annotations
from random import randint
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
        grid_x: Current column in the maze grid.
        grid_y: Current row in the maze grid.
        from_x: Starting column of the movement in progress.
        from_y: Starting line of the movement in progress.
        to_x  : Destination column of the movement in progress.
        to_y  : Destination row of the movement in progress.
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

    def __init__(self, state_x: int, state_y: int,
                 maze: list[list[int]]) -> None:
        """Initialize the player with a starting position.

        Args:
            state_x: Starting column in the maze grid.
            state_y: Starting row in the maze grid.
        """
        self.respawn = (state_x, state_y)
        self.grid_x = state_x
        self.grid_y = state_y
        self.from_x = state_x
        self.from_y = state_y
        self.to_x = state_x
        self.to_y = state_y
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
        self.ghosts_positions: list[tuple[int, int]] = []

    # Public methods -------------------------------------------------------
    # ======================================================================
    #   INPUT PLAYER
    # ======================================================================

    @classmethod
    def cheat_sync(cls, parameter: dict[str, str]) -> None:
        for key, value in parameter.items():
            if value == "OFF":
                cls.CHEAT_DATA[key] = False
            elif value == "ON":
                cls.CHEAT_DATA[key] = True

    @classmethod
    def init_data_set(cls, lives: int) -> None:
        cls.INIT_DATA["Lives"] = lives

    @staticmethod
    def find_spawn(maze: list[list[int]]) -> tuple[int, int]:
        """Find a walkable cell close to the maze center."""
        maze_height = len(maze)
        maze_width = len(maze[0]) if maze else 0
        center_x = maze_width // 2
        center_y = maze_height // 2
        for offset in range(1, maze_height - center_y):
            y = center_y + offset
            if maze[y][center_x] != 15:
                return center_x, y
        for offset in range(1, center_y + 1):
            y = center_y - offset
            if maze[y][center_x] != 15:
                return center_x, y
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
               pacgums: PacgumsManagement) -> int:
        """Advance movement and eat a pacgum when a move is complete."""
        score_gain = 0
        player_position: tuple[int, int]
        if self.is_moving:
            elapsed_time = (
                pygame.time.get_ticks() - self.move_started_ms
            )
            if elapsed_time >= self.MOVE_DURATION_MS:
                player_position = (self.grid_y, self.grid_x)
                if self.debug is True:
                    print(
                        f"Pacman pos: {player_position} lives: {self.lives}"
                        )
                if self.CHEAT_DATA["ghost_freeze"] is False:
                    GhostBase.team_ghost(
                        ghosts,
                        player_position,
                        self.maze,
                        self.maze_height,
                        self.maze_width,
                        rand=4,
                        debug=self.debug
                        )
                    self.ghosts_positions = [
                        (g.grid_y, g.grid_x) for g in ghosts]
                self.is_moving = False
                self.move_started_ms = 0
                score_gain = pacgums.try_to_eat(
                    ghosts,
                    unit_x=self.grid_x,
                    unit_y=self.grid_y,
                )
                for ghost in ghosts:
                    if (ghost.grid_y, ghost.grid_x) in \
                            [(self.grid_y, self.grid_x),
                             (self.from_y, self.from_x)]:
                        if ghost.state == GhostState.FRIGHTENED:
                            ghost.state = GhostState.EATEN
                        elif ghost.state == GhostState.EATEN:
                            pass
                        elif ghost.state == GhostState.NORMAL and \
                                self.CHEAT_DATA["invincible"] is False:
                            self.life_loss()
                if score_gain > 0 and \
                    player_position in [
                        (0, 0),
                        (self.maze_width - 1, 0),
                        (0, self.maze_height - 1),
                        (self.maze_width - 1, self.maze_height - 1)]:
                    for ghost in ghosts:
                        ghost.state = GhostState.FRIGHTENED
                self._try_start_move()
        else:
            self._try_start_move()
        return score_gain

    def _try_start_move(self) -> None:
        """Start a movement if a direction is queued and the move is valid."""
        # ------------------------------------------------------------------
        #   DIREZIONE
        # ----------------1--------------------------------------------------
        # PLACEHOLDER ------------------------------------------------------
        # TODO: Trasferire la scelta della destinazione e l'avvio del
        # movimento nel modulo core/movement.
        # La direzione non viene consumata: rimane attiva finché non viene
        # sovrascritta da un nuovo input (direzione persistente).
        direction = self.queued_direction
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

        current_x = self.grid_x
        current_y = self.grid_y
        new_x = current_x + dx
        new_y = current_y + dy

        if self.can_move(current_x, current_y, new_x, new_y):
            self.from_x = current_x
            self.from_y = current_y
            self.to_x = new_x
            self.to_y = new_y
            self.grid_x = new_x
            self.grid_y = new_y
            self.is_moving = True
            self.direction = direction
            self.move_started_ms = pygame.time.get_ticks()

    def _has_wall(self, x: int, y: int, wall_bit: int) -> bool:
        if x < 0 or y < 0 or x >= self.maze_width or y >= self.maze_height:
            return True
        return (self.maze[y][x] & wall_bit) != 0

    def pacman_respawn(self) -> None:
        list_respawn: list[tuple[int, int]] = []
        for row in range(0, len(self.maze)):
            for col in range(0, len(self.maze[0])):
                flag: bool = True
                for g in self.ghosts_positions:
                    if GhostBase.get_distance((row, col), g) < 4:
                        flag = False
                if flag is True and self.maze[col][row] != 15:
                    list_respawn.append((row, col))
        self.respawn = list_respawn[randint(0, len(list_respawn))]

    def life_loss(self) -> None:
        """NOTE: life loss manager
        TODO: connect with game over page"""
        self.pacman_respawn()
        self.lives -= 1
        self.grid_x = self.respawn[0]
        self.grid_y = self.respawn[1]
        self.from_x = self.respawn[0]
        self.from_y = self.respawn[1]
        self.to_x = self.respawn[0]
        self.to_y = self.respawn[1]
