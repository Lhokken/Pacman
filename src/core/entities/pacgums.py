"""Management of pacgums and super-pacgums.

This class is responsible for tracking which cells have been eaten
and to carry out the necessary checks before eating a pacgum.
"""

#   Chapter VI - Game specifications  VI.2 Player -----------------------------
#
#   • Pacgums are small dots placed in most corridors.
#   • Super-pacgums (power pellets) are larger dots placed in the 4 corners
#     of the maze.
#   • Eating a pacgum increases the score by X points.
#   • Eating a super-pacgum increases the score by Y points and makes ghosts
#     edible for a short time.

from typing import Callable
import logging
from src.core.entities.ghost import GhostBase

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


class PacgumsManagement:
    """Manages the status of pacgums in the maze.

    Attributes:
        eaten      : Set of coordinates (x, y) of the cells
                     whose pacgum it has already been eaten.
        maze_width : Width of the maze in cells.
        maze_height: Height of the maze in cells.
        walkable_fn: Function that receives (x, y) and returns
                     True if the cell is walkable (not wall).
    """

    def __init__(
        self,
        maze_width: int,
        maze_height: int,
        walkable_fn: Callable[[int, int], bool],
    ) -> None:
        """Initialize the pacgum manager.

        Args:
            maze_width: Width of the maze.
            maze_height: Height of the maze.
            walkable_fn: Callable to check walkability.
        """
        # Set of coordinates (x, y) of eaten pacgums
        self.eaten: set[tuple[int, int]] = set()
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.walkable_fn = walkable_fn

        # ==============================================================
        # Public methods
        # ==============================================================

    def try_to_eat(
        self,
        ghosts: list[GhostBase],
        unit_x: int,
        unit_y: int,
        # ghost_positions: list[tuple[int, int]],
    ) -> int:
        """Try to eat a pacgum in the indicated cell.

        Performs limit, walkability, already eaten and checks
        occupation by a ghost. If everything is ok, he adds
        the cell to the `eaten` set and returns the score (10).
        Otherwise it returns 0 without changing the state.

        Args:
            unit_x: Column of the cell.
            unit_y: Cell row.
            ghost_positions: List of current ghost positions.

        Returns:
            Score earned (10 if eaten, 0 otherwise).
        """
        ghost_positions = [
            (ghosts[0].grid_x, ghosts[0].grid_y),
            (ghosts[1].grid_x, ghosts[1].grid_y),
            (ghosts[2].grid_x, ghosts[2].grid_y),
            (ghosts[3].grid_x, ghosts[3].grid_y)
        ]
        # Check if the cell is within the maze limits --------------
        self.eaten
        if not (
            0 <= unit_x < self.maze_width
            and 0 <= unit_y < self.maze_height
        ):
            logger.debug(
                "Attempted to eat pacgum out of bounds at (%d, %d)",
                unit_x,
                unit_y,
            )
            return 0

        # Check if the cell is walkable --------------------------------
        if not self.walkable_fn(unit_x, unit_y):
            logger.debug(
                "Attempted to eat pacgum at non-walkable cell (%d, %d)",
                unit_x,
                unit_y,
            )
            return 0

        # Check if the cell is already eaten ----------------------------
        if (unit_x, unit_y) in self.eaten:
            logger.debug(
                "Attempted to eat already eaten pacgum at (%d, %d)",
                unit_x,
                unit_y,
            )
            return 0

        # Check if the cell is occupied by a ghost -----------------------
        if (unit_x, unit_y) in ghost_positions:
            logger.debug(
                "Attempted to eat pacgum at cell occupied by ghost "
                "(%d, %d)",
                unit_x,
                unit_y,
            )
            return 0

        # If all checks passed, mark the pacgum as eaten ------------------
        self.eaten.add((unit_x, unit_y))
        if (unit_x, unit_y) in [
                (0, 0),
                (self.maze_width - 1, 0),
                (0, self.maze_height - 1),
                (self.maze_width - 1, self.maze_height - 1)]:
            GhostBase.frighten_ghosts(ghosts)
        if len(self.eaten) == (self.maze_width * self.maze_height) - 18:
            print("Next level")
        logger.debug(
            "Pacgum eaten at (%d, %d). Score increased: %d",
            unit_x,
            unit_y,
            len(self.eaten),
        )
        return 10
