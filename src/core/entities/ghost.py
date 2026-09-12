"""Ghost base state.

The class contains only the data common to all ghosts: position,
current direction, behavioral state and corner position (used
for respawn).
"""

# TODO: Implementare lo stato comune dei ghost: posizione, direzione,
# velocita e stato comportamentale (normale, frightened, eaten).
# TODO: Delegare il movimento su griglia al modulo comune di movement.

# classe base:
# proprietà fisiche comuni (posizione, direzione corrente, velocità base),
# riferimento composto allo stato comportamentale attivo
# (non eredita, lo possiede),
# e il Direction Resolver come metodo/funzione condivisa — dato che è puro
# algoritmo
# identico per tutti e quattro i fantasmi, ha senso viva qui come
# comportamento di base piuttosto che duplicato altrove.

from __future__ import annotations
from enum import Enum
from random import randint
from collections import deque
from typing import Deque
import math
import sys


class Direction():
    """Possible directions"""
    NORD = "nord"
    EST = "est"
    SUD = "sud"
    OVEST = "ovest"


class GhostState(Enum):
    """Possible behavioral states of a ghost."""

    NORMAL = "normal"
    FRIGHTENED = "frightened"
    EATEN = "eaten"


class GhostBase:
    """It represents a ghost in the labyrinth.

    Attributes:
        grid_x   : Current column.
        grid_y   : Current row.
        direction: Current direction(None if stopped).
        speed    : Base speed (units of cells per second,
                   per hour constant and not used).
        state    : Behavioral state (default GhostState.NORMAL).
        corner   : Tuple (x, y) of the corner cell assigned to
                   ghost for respawn.
    """

    def __init__(
            self,
            start_x: int,
            start_y: int,
            ) -> None:
        self.grid_x = start_x              # Current position x
        self.grid_y = start_y              # Current position y
        self.direction: str | None = None  # Current direction
        self.speed = 1.0                   # Base speed
        self.state = GhostState.NORMAL     # Default behavioral state
        self.corner = (start_x, start_y)   # Corner cell for respawn
        self.ghosts: tuple[int, int] | bool = (0, 0)
        self.set_timer: int = 30
        self.timer: int = self.set_timer

    @classmethod  # nord ovest
    def blinky(
            cls,
            ghost: GhostBase,
            player_pos: tuple[int, int],
            maze: list[list[int]],
            height: int,
            width: int,
            rand: int
            ) -> tuple[int, int]:
        y = ghost.grid_y
        x = ghost.grid_x
        if ghost.state == GhostState.NORMAL:
            y, x = cls.hunting(
                maze, rand, player_pos, y, x, width, height)
        elif ghost.state == GhostState.FRIGHTENED:
            y, x = cls.get_flight_run(
                (y, x), player_pos, width, height, maze, rand)
            cls.ghost_timer(ghost)
        elif ghost.state == GhostState.EATEN:
            if ghost.corner == (y, x):
                ghost.state = GhostState.NORMAL
            else:
                result = cls.bfs(maze, ghost.corner, (y, x))
                if isinstance(result, tuple):
                    y, x = result
        cls.get_direction(ghost, y, x)
        print(ghost.direction)
        return (y, x)

    @classmethod  # nord est
    def clyde(
            cls,
            ghost: GhostBase,
            player_pos: tuple[int, int],
            maze: list[list[int]],
            height: int,
            width: int,
            rand: int
            ) -> tuple[int, int]:
        y = ghost.grid_y
        x = ghost.grid_x
        if ghost.state == GhostState.NORMAL:
            y, x = cls.hunting(
                maze, rand, player_pos, y, x, width, height)
        elif ghost.state == GhostState.FRIGHTENED:
            y, x = cls.get_flight_run(
                (y, x), player_pos, width, height, maze, rand)
            cls.ghost_timer(ghost)
        elif ghost.state == GhostState.EATEN:
            if ghost.corner == (y, x):
                ghost.state = GhostState.NORMAL
            else:
                result = cls.bfs(maze, ghost.corner, (y, x))
                if isinstance(result, tuple):
                    y, x = result
        cls.get_direction(ghost, y, x)
        print(ghost.direction)
        return (y, x)

    @classmethod  # sud ovest
    def inky(
            cls,
            ghost: GhostBase,
            player_pos: tuple[int, int],
            maze: list[list[int]],
            height: int,
            width: int,
            rand: int
            ) -> tuple[int, int]:
        y = ghost.grid_y
        x = ghost.grid_x
        if ghost.state == GhostState.NORMAL:
            y, x = cls.hunting(
                maze, rand, player_pos, y, x, width, height)
        elif ghost.state == GhostState.FRIGHTENED:
            y, x = cls.get_flight_run(
                (y, x), player_pos, width, height, maze, rand)
            cls.ghost_timer(ghost)
        elif ghost.state == GhostState.EATEN:
            if ghost.corner == (y, x):
                ghost.state = GhostState.NORMAL
            else:
                result = cls.bfs(maze, ghost.corner, (y, x))
                if isinstance(result, tuple):
                    y, x = result
        cls.get_direction(ghost, y, x)
        print(ghost.direction)
        return (y, x)

    @classmethod  # sud est
    def pinky(
            cls,
            ghost: GhostBase,
            player_pos: tuple[int, int],
            maze: list[list[int]],
            height: int,
            width: int,
            rand: int
            ) -> tuple[int, int]:
        y = ghost.grid_y
        x = ghost.grid_x
        if ghost.state == GhostState.NORMAL:
            y, x = cls.hunting(
                maze, rand, player_pos, y, x, width, height)
        elif ghost.state == GhostState.FRIGHTENED:
            y, x = cls.get_flight_run(
                (y, x), player_pos, width, height, maze, rand)
            cls.ghost_timer(ghost)
        elif ghost.state == GhostState.EATEN:
            if ghost.corner == (y, x):
                ghost.state = GhostState.NORMAL
            else:
                result = cls.bfs(maze, ghost.corner, (y, x))
                if isinstance(result, tuple):
                    y, x = result
        cls.get_direction(ghost, y, x)
        print(ghost.direction)
        return (y, x)

    @classmethod
    def team_ghost(
            cls,
            ghosts: list[GhostBase],
            player_pos: tuple[int, int],
            maze: list[list[int]],
            height: int,
            width: int,
            rand: int = 4
            ) -> list[tuple[int, int]]:
        return [
            cls.blinky(
                ghosts[0],
                player_pos, maze, height, width, rand
                ),
            cls.clyde(
                ghosts[1],
                player_pos, maze, height, width, rand
                ),
            cls.inky(
                ghosts[2],
                player_pos, maze, height, width, rand
                ),
            cls.pinky(
                ghosts[3],
                player_pos, maze, height, width, rand
                )
            ]

    @classmethod
    def get_neighbours(
            cls, y: int, x: int, maze: list[list[int]]
            ) -> list[tuple[int, int]]:
        result: list[tuple[int, int]] = []
        if cls.wall_check(y, x, maze, Direction.NORD):
            result.append((y - 1, x))
        if cls.wall_check(y, x, maze, Direction.SUD):
            result.append((y + 1, x))
        if cls.wall_check(y, x, maze, Direction.OVEST):
            result.append((y, x - 1))
        if cls.wall_check(y, x, maze, Direction.EST):
            result.append((y, x + 1))
        return result

    @classmethod
    def wall_check(
            cls,
            y: int,
            x: int,
            maze: list[list[int]],
            direction: str
            ) -> bool:
        if direction == Direction.NORD:
            if maze[y][x] not in (1, 3, 5, 7, 9, 11, 13):
                return True
        elif direction == Direction.SUD:
            if maze[y][x] not in (4, 5, 6, 7, 12, 13, 14):
                return True
        elif direction == Direction.OVEST:
            if maze[y][x] not in (8, 9, 10, 11, 12, 13, 14):
                return True
        elif direction == Direction.EST:
            if maze[y][x] not in (2, 3, 6, 7, 10, 11, 14):
                return True
        return False

    @classmethod
    def bfs(
            cls, maze: list[list[int]],
            start: tuple[int, int],
            end: tuple[int, int]
            ) -> bool | tuple[int, int]:
        """
        Find the shortest path from start to end using breadth-first search.

        Performs a standard BFS over the passable cell graph, writing
        increasing step counts into index [0] of each visited cell. On
        reaching the end, back-traces via decreasing step values to recover
        the optimal path, storing it in cls.way (end → start order).

        Returns:
            bool: Always returns False. Returns early with False if no path
                exists (end is unreachable).

        Side effects:
            cls.way (list[list[int]]): Set to the list of cell coordinates
                along the shortest path, ordered from end to start.
        """
        if cls.get_distance(start, end) > 25:
            return False
        max_pos = sys.maxsize
        maz_path = [[max_pos for _ in row] for row in maze]

        queue: Deque[tuple[int, int]] = deque()
        cr = start  # cr = current position
        queue.append(cr)
        visited = [cr]
        maz_path[cr[0]][cr[1]] = 0
        while queue:
            cr = queue.popleft()
            if cr == end:
                break
            neighbours = cls.get_neighbours(cr[0], cr[1], maze)
            for n in neighbours:
                if n not in visited:
                    maz_path[n[0]][n[1]] = maz_path[cr[0]][cr[1]] + 1
                    queue.append(n)
                    visited.append(n)
        if cr != end:
            return False
        way = [cr]
        while cr != start:
            neighbours = cls.get_neighbours(cr[0], cr[1], maze)
            for n in neighbours:
                if maz_path[n[0]][n[1]] == maz_path[cr[0]][cr[1]] - 1:
                    way.append(n)
                    cr = n
                    # break
        if len(way) < 2:
            return False
        return way[1]

    @classmethod
    def get_distance(
            cls,
            player_pos: tuple[int, int],
            ghost_pos: tuple[int, int]
            ) -> float:
        distance: float = 0
        distance = int(math.sqrt(
            (player_pos[0] - ghost_pos[0])**2 +
            (player_pos[1] - ghost_pos[1])**2
            ))
        return distance

    @classmethod
    def next_step(cls, y: int, x: int, maze, width, height) -> tuple[int, int]:
        directions = [
            Direction.NORD,
            Direction.SUD,
            Direction.OVEST,
            Direction.SUD
            ]
        while True:
            new_dir = directions[randint(0, 3)]
            if new_dir == Direction.NORD and \
                cls.wall_check(y, x, maze, new_dir) \
                    and (y - 1) >= 0:
                y -= 1
                break
            elif new_dir == Direction.SUD and \
                cls.wall_check(y, x, maze, new_dir) \
                    and (y + 1) < width:
                y += 1
                break
            elif new_dir == Direction.OVEST and \
                cls.wall_check(y, x, maze, new_dir) \
                    and (x - 1) >= 0:
                x -= 1
                break
            elif new_dir == Direction.EST and \
                cls.wall_check(y, x, maze, new_dir) \
                    and (x + 1) < height:
                x += 1
                break
        return (y, x)

    @classmethod
    def get_flight_run(
            cls,
            ghost: tuple[int, int],
            player: tuple[int, int],
            width: int,
            height: int,
            maze: list[list[int]],
            rand: int
            ) -> tuple[int, int]:
        y = ghost[0]
        x = ghost[1]
        if randint(0, 100) > rand:
            if player[0] > y:
                y = max(y - 1, 0)
            elif player[0] < y:
                y = min(y + 1, width - 1)

            if player[1] > x:
                x = max(x - 1, 0)
            elif player[1] < x:
                x = min(x + 1, height - 1)

            if maze[y][x] == 15:
                return ghost
            esc = cls.bfs(maze, (y, x), ghost)
            if isinstance(esc, tuple):
                return esc
            else:
                return ghost
        else:
            y, x = cls.next_step(y, x, maze, width, height)
            return (y, x)

    @classmethod
    def hunting(cls,
                maze: list[list[int]],
                rand: int,
                player_pos: tuple[int, int],
                y: int,
                x: int,
                width: int,
                height: int
                ) -> tuple[int, int]:
        result: tuple[int, int] | bool = False
        if randint(0, 100) > rand:
            result = cls.bfs(maze, player_pos, (y, x))
        if isinstance(result, tuple):
            y = result[0]
            x = result[1]
        else:
            y, x = cls.next_step(y, x, maze, width, height)
        return (y, x)

    @classmethod
    def ghost_timer(cls, ghost: GhostBase) -> None:
        ghost.timer -= 1
        if ghost.timer <= 0:
            ghost.timer = ghost.set_timer
            ghost.state = GhostState.NORMAL

    @classmethod
    def get_direction(cls, ghost: GhostBase, y: int, x: int) -> None:
        y_start = ghost.grid_y
        x_start = ghost.grid_x
        if x_start - x == 1:
            ghost.direction = Direction.OVEST
        elif x_start - x == -1:
            ghost.direction = Direction.EST
        elif y_start - y == 1:
            ghost.direction = Direction.NORD
        elif y_start - y == -1:
            ghost.direction = Direction.SUD
