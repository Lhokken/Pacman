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
from src.core.entities.ghost import GhostBase, GhostState

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
        maze_dim: tuple[int, int],
        walkable_fn: Callable[[int, int], bool],
        dict_point: dict[str, int]
    ) -> None:
        """Initialize the pacgum manager.

        Args:
            maze_width: Width of the maze.
            maze_height: Height of the maze.
            walkable_fn: Callable to check walkability.
        """
        # Set of coordinates (x, y) of eaten pacgums
        self.eaten: set[tuple[int, int]] = set()
        self.maze_width = maze_dim[1]
        self.maze_height = maze_dim[0]
        self.walkable_fn = walkable_fn
        self.all_eaten: bool = False
        self.dict_point: dict[str, int] = dict_point
        self.corners: list[tuple[int, int]]

        # ==============================================================
        # Public methods
        # ==============================================================

    def try_to_eat(
        self,
        ghosts: list[GhostBase],
        row: int,
        col: int,
        # ghost_positions: list[tuple[int, int]],
    ) -> int:
        """Try to eat a pacgum in the indicated cell.

        Performs limit, walkability, already eaten and checks
        occupation by a ghost. If everything is ok, he adds
        the cell to the `eaten` set and returns the score (10).
        Otherwise it returns 0 without changing the state.

        Args:
            row: Cell row.
            col: Column of the cell.
            ghost_positions: List of current ghost positions.

        Returns:
            Score earned (10 if eaten, 0 otherwise).
        """
        turn_score: int = 0
        # Check if the cell is within the maze limits --------------
        self.eaten
        if not (
            0 <= col < self.maze_width
            and 0 <= row < self.maze_height
        ):
            logger.debug(
                "Attempted to eat pacgum out of bounds at (%d, %d)",
                col,
                row,
            )
            return 0

        # Check if the cell is walkable --------------------------------
        if not self.walkable_fn(row, col):
            logger.debug(
                "Attempted to eat pacgum at non-walkable cell (%d, %d)",
                col,
                row,
            )
            return 0

        # Check if the cell is already eaten ----------------------------
        if (col, row) in self.eaten:
            logger.debug(
                "Attempted to eat already eaten pacgum at (%d, %d)",
                col,
                row,
            )
            return 0

        # Check if the cell is occupied by a ghost -----------------------

        for ghost in ghosts:

            if ghost.coord == (row, col):
                if ghost.state is not GhostState.NORMAL:
                    logger.debug(
                        "Attempted to eat pacgum at cell occupied by ghost "
                        "(%d, %d)",
                        col,
                        row,
                    )
                    return 0

        # If all checks passed, mark the pacgum as eaten ------------------
        self.eaten.add((col, row))
        if (row, col) in self.corners:
            GhostBase.frighten_ghosts(ghosts)
            turn_score = self.dict_point["super_pacgum"]
        turn_score = self.dict_point["pacgum"]
        if len(self.eaten) == (self.maze_width * self.maze_height) - 18:
            self.all_eaten = True
        logger.debug(
            "Pacgum eaten at (%d, %d). Score increased: %d",
            col,
            row,
            len(self.eaten),
        )
        return turn_score
