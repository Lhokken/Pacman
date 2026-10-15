"""Management of pacgums and super-pacgums.

This class is responsible for tracking which cells have been eaten
and to carry out the necessary checks before eating a pacgum.
"""

import logging
from random import Random
from typing import Callable
from src.core.entities.ghost import (
    GhostBase,
    GhostState
)

logger = logging.getLogger(__name__)


class PacgumsManagement:
    """Manages the status of pacgums in the maze.

    Attributes:
        eaten       : Set of coordinates (x, y) of the cells
                      whose pacgum it has already been eaten.
        maze_width  : Width of the maze in cells.
        maze_height : Height of the maze in cells.
        walkable_fn : Function that receives (x, y) and returns
                      True if the cell is walkable (not wall).
    """

    def __init__(
        self,
        maze_dim: tuple[int, int],
        walkable_fn: Callable[[int, int], bool],
        dict_point: dict[str, int] | None = None,
        coverage_percent: int = 100,
        corners: list[tuple[int, int]] | None = None,
        seed: int | None = None,
        excluded_cells: set[tuple[int, int]] | None = None,
    ) -> None:
        """Initialize the pacgum manager.

        Args:
            maze_dim         : Maze dimensions as (rows, columns).
            walkable_fn      : Callable to check walkability.
            dict_point       : Points awarded for each pacgum type.
            coverage_percent : Percentage of walkable cells that receive
                               pacgums, from 1 to 100.
            corners          : Walkable corner cells reserved for
                               super-pacgums.
            seed             : Seed for reproducible pellet placement.
            excluded_cells   : Walkable cells intentionally left without
                               pellets.
        """
        self.eaten: set[tuple[int, int]] = set()
        self.maze_width = maze_dim[1]
        self.maze_height = maze_dim[0]
        self.walkable_fn = walkable_fn
        self.dict_point: dict[str, int] = {
            "pacgum": 10,
            "super_pacgum": 50,
        }
        if dict_point is not None:
            self.dict_point.update(dict_point)

        self.corners = corners or [
            (0, 0),
            (0, self.maze_width - 1),
            (self.maze_height - 1, 0),
            (self.maze_height - 1, self.maze_width - 1),
        ]
        walkable_cells = [
            (row, col)
            for row in range(self.maze_height)
            for col in range(self.maze_width)
            if self.walkable_fn(row, col)
            and (excluded_cells is None or (row, col) not in excluded_cells)
        ]
        required_corners = [
            corner for corner in self.corners if corner in walkable_cells
        ]
        coverage_percent = min(100, max(1, coverage_percent))
        target_count = (
            len(walkable_cells) * coverage_percent + 99
        ) // 100
        target_count = max(target_count, len(required_corners))
        if target_count >= len(walkable_cells):
            self.placed = set(walkable_cells)
        else:
            candidates = [
                cell for cell in walkable_cells
                if cell not in required_corners
            ]
            extra_count = target_count - len(required_corners)
            self.placed = set(required_corners)
            self.placed.update(
                Random(seed).sample(candidates, extra_count)
            )
        self.all_eaten = not self.placed

        # ==============================================================
        # Public methods
        # ==============================================================

    def try_to_eat(
        self,
        ghosts: list[GhostBase],
        row: int,
        col: int,
    ) -> int:
        """Try to eat a pacgum in the indicated cell.

        Performs limit, walkability, already eaten and checks
        occupation by a ghost. If everything is ok, he adds
        the cell to the `eaten` set and returns the score.
        Otherwise it returns 0 without changing the state.

        Args:
            row             : Cell row.
            col             : Column of the cell.
            ghost           : List of current ghost.

        Returns:
            Score earned by eating the pacgum:
                10, 50 or 0 if it was not eaten.
        """
        turn_score: int = 0
        # Check if the cell is within the maze limits --------------
        self.eaten
        if not (
            0 <= col < self.maze_width
            and 0 <= row < self.maze_height
        ):
            return 0

        # Check if the cell is walkable --------------------------------
        if not self.walkable_fn(row, col):
            return 0

        if (row, col) not in self.placed:
            return 0

        # Check if the cell is already eaten ----------------------------
        if (row, col) in self.eaten:
            return 0

        # Check if the cell is occupied by a ghost -----------------------

        for ghost in ghosts:

            if ghost.coord == (row, col):
                if ghost.state is GhostState.NORMAL:
                    return 0

        # If all checks passed, mark the pacgum as eaten ------------------
        self.eaten.add((row, col))
        if (row, col) in self.corners:
            GhostBase.frighten_ghosts(ghosts)
            turn_score = self.dict_point["super_pacgum"]
        else:
            turn_score = self.dict_point["pacgum"]

        self.all_eaten = self.placed.issubset(self.eaten)
        logger.debug(
            "Pacgum eaten at (%d, %d). Score increased: %d",
            row,
            col,
            len(self.eaten),
        )
        return turn_score
