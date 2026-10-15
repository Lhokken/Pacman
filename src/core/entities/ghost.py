"""Ghost base state.

The class contains only the data common to all ghosts: position,
current direction, behavioral state and corner position (used
for respawn).
"""

from __future__ import annotations
from enum import Enum
from random import choice, randint
from collections import deque
from typing import Deque
import math
import sys
import pygame


class Direction():
    """Possible directions."""

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
        g_col     : Current column. x
        g_row     : Current row. y
        direction : Current direction(None if stopped).
        speed     : Base speed (units of cells per second,
                   per hour constant and not used).
        state     : Behavioral state (default GhostState.NORMAL).
        corner    : Tuple (x, y) of the corner cell assigned to
                   ghost for respawn.
    """

    MOVING = True
    # The duration of a single ghost move, in milliseconds.
    GHOST_MOVE_DURATION = 800
    # The time in milliseconds when the ghost started moving.
    MOVE_STARTED_MS = 0
    # The duration of immunity after respawn, in milliseconds.
    RESPAWN_IMMUNITY_DURATION_MS = 3000

    def __init__(
            self,
            g_row: int,
            g_col: int,
            ) -> None:
        """Initialize a ghost at a maze cell.

        Args:
            g_row : Starting row.
            g_col : Starting column.
        """
        self.name: str                     # Ghost name
        self.g_row = g_row                 # Current row
        self.g_col = g_col                 # Current column
        self.to_row = g_row                # Destination row
        self.to_col = g_col                # Destination column
        self.from_row = g_row
        self.from_col = g_col
        self.coord = (g_row, g_col)
        self.direction: str | None = None  # Current direction
        self.speed = 1.0                   # Base speed
        self.state = GhostState.NORMAL     # Default behavioral state
        self.flashing: bool = False        # Used to show frightenind end
        self.flashing_duration: int = 10
        self.corner = (g_row, g_col)       # Corner cell for respawn
        self.ghosts: list[GhostBase]       # tuple[int, int] | bool = (0, 0)
        self.set_timer: int = 30
        self.timer: int = self.set_timer
        self.collision_immune_until_ms: int = 0
        self.maze: list[list[int]]
        self.maze_dim: tuple[int, int]

    @classmethod  # nord ovest
    def blinky(
            cls,
            ghosts: list[GhostBase],
            player_pos: tuple[int, int],
            rand: int,
            debug: bool
            ) -> None:
        """Manage ghost movement, chosing normal, frightened or eaten."""
        ghost = ghosts[0]
        gh_places = ghost.ghost_check(ghosts[1], ghosts[2], ghosts[3])
        if not hasattr(ghost, "name"):
            ghost.name = "blinky"
        row, col = (ghost.g_row, ghost.g_col)
        if ghost.state == GhostState.NORMAL:
            row, col, = ghost.hunting(
                ghost.maze,
                rand,
                player_pos,
                row, col,
                ghost.maze_dim
            )
        elif ghost.state == GhostState.FRIGHTENED:
            row, col = cls.get_flight_run(
                (row, col),
                player_pos,
                ghost.maze_dim,
                ghost.maze,
                rand
            )
            ghost.ghost_timer(ghost)
        elif ghost.state == GhostState.EATEN:
            row, col = ghost.eaten_mod(
                ghost,
                ghost.maze,
                row,
                col
            )
        row, col = cls._resolve_single_step(
            ghost, (row, col), gh_places
        )
        ghost.row_col_update(row, col)
        if debug is True:
            ghost.debug_ghost(ghost)
        ghost.get_direction(ghost, row, col)

    @classmethod  # nord est
    def clyde(
            cls,
            ghosts: list[GhostBase],
            player_pos: tuple[int, int],
            rand: int,
            debug: bool
            ) -> None:
        """Manage ghost movement, chosing normal, frightened or eaten."""
        ghost = ghosts[1]
        gh_places = ghost.ghost_check(ghosts[0], ghosts[2], ghosts[3])
        if not hasattr(ghost, "name"):
            ghost.name = "clyde"
        row, col = (ghost.g_row, ghost.g_col)
        if ghost.state == GhostState.NORMAL:
            row, col, = ghost.hunting(
                ghost.maze,
                rand,
                player_pos,
                row,
                col,
                ghost.maze_dim
            )
        elif ghost.state == GhostState.FRIGHTENED:
            row, col = cls.get_flight_run(
                (row, col),
                player_pos,
                ghost.maze_dim,
                ghost.maze,
                rand
            )
            ghost.ghost_timer(ghost)
        elif ghost.state == GhostState.EATEN:
            row, col = ghost.eaten_mod(ghost, ghost.maze, row, col)
        row, col = cls._resolve_single_step(
            ghost, (row, col), gh_places
        )
        ghost.row_col_update(row, col)
        if debug is True:
            ghost.debug_ghost(ghost)
        ghost.get_direction(ghost, row, col)

    @classmethod  # sud ovest
    def inky(
            cls,
            ghosts: list[GhostBase],
            player_pos: tuple[int, int],
            rand: int,
            debug: bool
            ) -> None:
        """Manage ghost movement, chosing normal, frightened or eaten."""
        ghost = ghosts[2]
        gh_places = ghost.ghost_check(ghosts[0], ghosts[1], ghosts[3])
        if not hasattr(ghost, "name"):
            ghost.name = "inky"
        row, col = (ghost.g_row, ghost.g_col)
        if ghost.state == GhostState.NORMAL:
            row, col, = ghost.hunting(
                ghost.maze, rand, player_pos, row, col, ghost.maze_dim)
        elif ghost.state == GhostState.FRIGHTENED:
            row, col = cls.get_flight_run(
                (row, col), player_pos, ghost.maze_dim, ghost.maze, rand)
            ghost.ghost_timer(ghost)
        elif ghost.state == GhostState.EATEN:
            row, col = ghost.eaten_mod(ghost, ghost.maze, row, col)
        row, col = cls._resolve_single_step(
            ghost, (row, col), gh_places
        )
        ghost.row_col_update(row, col)
        if debug is True:
            ghost.debug_ghost(ghost)
        ghost.get_direction(
            ghost,
            row,
            col
        )

    @classmethod  # sud est
    def pinky(
            cls,
            ghosts: list[GhostBase],
            player_pos: tuple[int, int],
            rand: int,
            debug: bool
            ) -> None:
        """Manage ghost movement, chosing normal, frightened or eaten."""
        ghost = ghosts[3]
        gh_places = ghost.ghost_check(ghosts[0], ghosts[1], ghosts[2])
        if not hasattr(ghost, "name"):
            ghost.name = "pinky"
        row, col = (
            ghost.g_row,
            ghost.g_col
        )
        if ghost.state == GhostState.NORMAL:
            row, col, = ghost.hunting(
                ghost.maze,
                rand,
                player_pos,
                row,
                col,
                ghost.maze_dim
            )
        elif ghost.state == GhostState.FRIGHTENED:
            row, col = cls.get_flight_run(
                (row, col),
                player_pos,
                ghost.maze_dim,
                ghost.maze,
                rand
            )
            ghost.ghost_timer(ghost)
        elif ghost.state == GhostState.EATEN:
            row, col = ghost.eaten_mod(
                ghost,
                ghost.maze,
                row,
                col
            )
        row, col = cls._resolve_single_step(
            ghost, (row, col), gh_places
        )
        ghost.row_col_update(row, col)
        if debug is True:
            ghost.debug_ghost(ghost)
        ghost.get_direction(ghost, row, col)

    def row_col_update(self, row: int, col: int) -> None:
        """Record a ghost's current cell and movement endpoints.

        Args:
            row : Destination row.
            col : Destination column.
        """
        self.from_row = self.g_row
        self.from_col = self.g_col
        self.to_row = row
        self.to_col = col
        self.g_row = row
        self.g_col = col
        self.coord = (row, col)

    @classmethod
    def _resolve_single_step(
        cls,
        ghost: GhostBase,
        target: tuple[int, int],
        occupied: tuple[tuple[int, int], ...],
    ) -> tuple[int, int]:
        """Keep each ghost move to one free, orthogonal maze cell."""
        current = (ghost.g_row, ghost.g_col)
        if target == current:
            return current

        candidates = [
            cell for cell in cls.get_neighbours(
                current[0], current[1], ghost.maze
            )
            if cell not in occupied
        ]
        if target in candidates:
            return target
        if not candidates:
            return current

        best_distance = min(
            abs(cell[0] - target[0]) + abs(cell[1] - target[1])
            for cell in candidates
        )
        best_candidates = [
            cell for cell in candidates
            if abs(cell[0] - target[0]) + abs(cell[1] - target[1])
            == best_distance
        ]
        return choice(best_candidates)

    def ghost_check(
        self,
        ghost1: GhostBase,
        ghost2: GhostBase,
        ghost3: GhostBase) -> tuple[
            tuple[int, int],
            tuple[int, int],
            tuple[int, int]
            ]:
        """Return the positions of the other three ghosts."""
        return (
            (ghost1.g_row, ghost1.g_col),
            (ghost2.g_row, ghost2.g_col),
            (ghost3.g_row, ghost3.g_col)
        )

    def debug_ghost(self, ghost: GhostBase) -> None:
        """Monitor ghost data."""
        print(
            ghost.state,
            ghost.name,
            ghost.g_row,
            ghost.g_col
            )

    def eaten_mod(
            self,
            ghost: GhostBase,
            maze: list[list[int]],
            row: int,
            col: int
            ) -> tuple[int, int]:
        """Move an eaten ghost one step toward its assigned corner.

        Args:
            ghost: Ghost returning to its corner.
            maze : Maze wall-bitmask grid.
            row  : Current row.
            col  : Current column.

        Returns:
            The next row and column.
        """
        if ghost.corner == (row, col):
            ghost.state = GhostState.NORMAL
            ghost.timer = ghost.set_timer
            ghost.collision_immune_until_ms = (
                pygame.time.get_ticks()
                + ghost.RESPAWN_IMMUNITY_DURATION_MS
            )
        else:
            result = ghost.bfs(maze, ghost.corner, (row, col))
            if isinstance(result, tuple):
                row, col = result
        return (row, col)

    @classmethod
    def team_ghost(
            cls,
            ghosts: list[GhostBase],
            player_pos: tuple[int, int],
            rand: int,
            debug: bool
            ) -> None:
        """Update each ghost once using the shared player position."""
        cls.blinky(ghosts, player_pos, rand, debug)
        cls.clyde(ghosts, player_pos, rand, debug)
        cls.inky(ghosts, player_pos, rand, debug)
        cls.pinky(ghosts, player_pos, rand, debug)
        cls.MOVE_STARTED_MS = pygame.time.get_ticks()

    @classmethod
    def get_neighbours(
            cls, row: int, col: int, maze: list[list[int]]
            ) -> list[tuple[int, int]]:
        """Return reachable orthogonal neighbors of a maze cell.

        Args:
            row  : Current row.
            col  : Current column.
            maze : Maze wall-bitmask grid.

        Returns:
            Reachable neighboring cells as ``(row, column)`` pairs.
        """
        result: list[tuple[int, int]] = []
        if cls.wall_check(row, col, maze, Direction.NORD):
            result.append((row - 1, col))
        if cls.wall_check(row, col, maze, Direction.SUD):
            result.append((row + 1, col))
        if cls.wall_check(row, col, maze, Direction.OVEST):
            result.append((row, col - 1))
        if cls.wall_check(row, col, maze, Direction.EST):
            result.append((row, col + 1))
        return result

    @classmethod
    def wall_check(
            cls,
            row: int,
            col: int,
            maze: list[list[int]],
            direction: str
            ) -> bool:
        """Check if the direction is open or closed."""
        if direction == Direction.NORD:
            if maze[row][col] not in (1, 3, 5, 7, 9, 11, 13):
                return True
        elif direction == Direction.SUD:
            if maze[row][col] not in (4, 5, 6, 7, 12, 13, 14):
                return True
        elif direction == Direction.OVEST:
            if maze[row][col] not in (8, 9, 10, 11, 12, 13, 14):
                return True
        elif direction == Direction.EST:
            if maze[row][col] not in (2, 3, 6, 7, 10, 11, 14):
                return True
        return False

    @classmethod
    def bfs(
            cls, maze: list[list[int]],
            start: tuple[int, int],
            end: tuple[int, int]
            ) -> tuple[int, int]:
        """Return the next cell along a shortest path to the target.

        The search uses breadth-first search and backtracks from the target
        to recover the first move from the starting cell.

        Args:
            maze  : Maze wall-bitmask grid.
            start : Starting cell as ``(row, column)``.
            end   : Target cell as ``(row, column)``.

        Returns:
            The next cell from ``start`` toward ``end``.
        """
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
            return end
        way = [cr]
        while cr != start:
            neighbours = cls.get_neighbours(cr[0], cr[1], maze)
            for n in neighbours:
                if maz_path[n[0]][n[1]] == maz_path[cr[0]][cr[1]] - 1:
                    way.append(n)
                    cr = n
        if len(way) < 2:
            return end
        return way[1]

    @classmethod
    def get_distance(
            cls,
            player_pos: tuple[int, int],
            ghost_pos: tuple[int, int]
            ) -> float:
        """Calculate distance between two location."""
        distance: float = 0
        distance = int(math.sqrt(
            (player_pos[0] - ghost_pos[0])**2 +
            (player_pos[1] - ghost_pos[1])**2
            ))
        return distance

    @classmethod
    def next_step(
            cls,
            row: int,
            col: int,
            maze: list[list[int]],
            maze_dim: tuple[int, int]
            ) -> tuple[int, int]:
        """Determine a valid single step move."""
        directions = [
            Direction.NORD,
            Direction.SUD,
            Direction.OVEST,
            Direction.EST
            ]
        while True:
            new_dir = directions[randint(0, 3)]
            if (row - 1) >= 0 and \
                new_dir == Direction.NORD and \
                    cls.wall_check(row, col, maze, new_dir):
                row -= 1
                break
            elif (row + 1) < maze_dim[0] and \
                new_dir == Direction.SUD and \
                    cls.wall_check(row, col, maze, new_dir):
                row += 1
                break
            elif (col - 1) >= 0 and \
                new_dir == Direction.OVEST and \
                    cls.wall_check(row, col, maze, new_dir):
                col -= 1
                break
            elif (col + 1) < maze_dim[1] and \
                new_dir == Direction.EST and \
                    cls.wall_check(row, col, maze, new_dir):
                col += 1
                break
        return (row, col)

    @classmethod
    def get_flight_run(
            cls,
            ghost: tuple[int, int],
            player: tuple[int, int],
            maze_dim: tuple[int, int],
            maze: list[list[int]],
            rand: int
            ) -> tuple[int, int]:
        """Choose a legal step away from the player while frightened.

        Args:
            ghost    : Current ghost position.
            player   : Current player position.
            maze_dim : Maze dimensions as ``(rows, columns)``.
            maze     : Maze wall-bitmask grid.
            rand     : Randomness threshold controlling escape behavior.

        Returns:
            The next row and column for the ghost.
        """
        row = ghost[0]
        col = ghost[1]
        if randint(0, 100) > rand:
            if player[0] > row:
                row = max(row - 2, 0)
            elif player[0] < row:
                row = min(row + 2, maze_dim[0] - 1)

            if player[1] > col:
                col = max(col - 2, 0)
            elif player[1] < col:
                col = min(col + 2, maze_dim[1] - 1)

            if maze[row][col] == 15:
                return ghost
            esc = cls.bfs(maze, (row, col), ghost)
            if isinstance(esc, tuple):
                return esc
            else:
                return ghost
        else:
            row, col = cls.next_step(row, col, maze, maze_dim)
            return (row, col)

    def hunting(self,
                maze: list[list[int]],
                rand: int,
                player_pos: tuple[int, int],
                row: int,
                col: int,
                maze_dim: tuple[int, int]
                ) -> tuple[int, int]:
        """Choose a step toward the player with randomized movement.

        Args:
            maze       : Maze wall-bitmask grid.
            rand       : Randomness threshold controlling chase behavior.
            player_pos : Player position as ``(row, column)``.
            row        : Ghost's current row.
            col        : Ghost's current column.
            maze_dim   : Maze dimensions as ``(rows, columns)``.

        Returns:
            The next row and column for the ghost.
        """
        result: tuple[int, int] | bool = False
        if randint(0, 100) > rand:
            result = self.bfs(maze, player_pos, (row, col))
        if isinstance(result, tuple):
            row = result[0]
            col = result[1]
        else:
            row, col = self.next_step(row, col, maze, self.maze_dim)
        return (row, col)

    def ghost_timer(self, ghost: GhostBase) -> None:
        """Let ghosts turn back normal after set_timer."""
        ghost.timer -= 1
        if ghost.timer <= ghost.flashing_duration:
            ghost.flashing = True
        if ghost.timer <= 0:
            ghost.timer = ghost.set_timer
            ghost.state = GhostState.NORMAL
            ghost.flashing = False

    def get_direction(self, ghost: GhostBase, y: int, x: int) -> None:
        """Calculate and set ghosts movement direction."""
        y_start = ghost.from_row
        x_start = ghost.from_col
        if x_start - x == 1:
            ghost.direction = Direction.OVEST
        elif x_start - x == -1:
            ghost.direction = Direction.EST
        elif y_start - y == 1:
            ghost.direction = Direction.NORD
        elif y_start - y == -1:
            ghost.direction = Direction.SUD

    @classmethod
    def frighten_ghosts(cls, ghosts: list[GhostBase]) -> None:
        """Set all ghosts to frightened."""
        for ghost in ghosts:
            if ghost.state is not GhostState.EATEN:
                ghost.state = GhostState.FRIGHTENED
                ghost.flashing = False
                ghost.timer = ghost.set_timer
