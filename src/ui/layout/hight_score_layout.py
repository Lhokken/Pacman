"""High scores page layout (static - TODO: LOGIC PENDING)."""

from __future__ import annotations

from dataclasses import dataclass

from ..configUI.ui_config import Palette


@dataclass(frozen=True)
class HighscoreMetrics:
    """Metrics calculated for the high scores page.

    Attributes:
        title_center_y   : Y-coordinate of the title's center.
        header_center_y  : Y-coordinate of the header's center.
        rows_top_y       : Y-coordinate of the top edge of the rows.
        row_height       : Height of each row in pixels.
        col_rank_x       : X-coordinate of the "rank" column.
        col_name_x       : X-coordinate of the "name" column.
        col_score_x      : X-coordinate of the "score" column.
        footer_center_y  : Y-coordinate of the footer's center.
        content_cx       : X-coordinate of the center of the content area.
        content_left     : X-coordinate of the left edge of the content.
        content_right    : X-coordinate of the right edge of the content.
    """

    title_center_y: int
    header_center_y: int
    rows_top_y: int
    row_height: int
    col_rank_x: int
    col_name_x: int
    col_score_x: int
    footer_center_y: int
    content_cx: int
    content_left: int
    content_right: int


class HighscoreLayout:
    """Screen-relative layout of the high scores page.

    Proportions are expressed as fractions of the screen width
    or height and can be overridden at creation time via keyword
    arguments.
    """

    # -----------------------------------------------------
    #    BackGround / container
    # -----------------------------------------------------
    BACKGROUND: tuple[int, int, int] | None = Palette.BLACK
    MARGIN_X_RATIO: float = 0.05
    MARGIN_Y_RATIO: float = 0.05
    # -----------------------------------------------------
    #    vertical Ratio
    # -----------------------------------------------------
    TITLE_Y_RATIO: float = 0.08
    HEADER_Y_RATIO: float = 0.18
    ROWS_TOP_Y_RATIO: float = 0.25
    ROW_HEIGHT_RATIO: float = 0.055
    FOOTER_Y_RATIO: float = 0.88
    # -----------------------------------------------------
    #    Orizontal Ratio
    # -----------------------------------------------------
    COL_RANK_X_RATIO: float = 0.25
    COL_NAME_X_RATIO: float = 0.50
    COL_SCORE_X_RATIO: float = 0.75

    def __init__(self, **overrides: object) -> None:
        """Initialize the layout, applying any overrides.

        Args:
            **overrides: Alternative values for the layout's class
                        attributes. Keys must match attribute names
                        of `HighscoreLayout`.

        Raises:
            AttributeError: If an override key does not match any
                            class attribute.
        """
        for key, value in overrides.items():
            if not hasattr(type(self), key):
                raise AttributeError(
                    f"Unknown layout ratio: {key!r}. "
                    f"Valid keys are HighscoreLayout class attributes."
                )
            setattr(self, key, value)

    def compute(
        self,
        screen_w: int,
        screen_h: int,
        *,
        n_rows: int,
    ) -> HighscoreMetrics:
        """Calculate the metrics for the specified screen.

        Args:
            screen_w : Screen width in pixels.
            screen_h : Screen height in pixels.
            n_rows   : Number of high-score rows to arrange.

        Returns:
            A `HighscoreMetrics` object with the calculated coordinates.
        """
        # -----------------------------------------------------
        #    container
        # -----------------------------------------------------
        margin_x = int(
            screen_w * self.MARGIN_X_RATIO
        )
        margin_y = int(
            screen_h * self.MARGIN_Y_RATIO
        )
        content_left = margin_x
        content_right = screen_w - margin_x
        content_cx = (
            (content_left + content_right) // 2
        )
        content_w = content_right - content_left
        # --------------------------------------------------------
        #    Columns relating to the usable area.
        # --------------------------------------------------------
        col_rank_x = (
            content_left + int(
                content_w * self.COL_RANK_X_RATIO
            )
        )
        col_name_x = (
            content_left + int(
                content_w * self.COL_NAME_X_RATIO
            )
        )
        col_score_x = content_left + int(
            content_w * self.COL_SCORE_X_RATIO
        )
        # --------------------------------------------------------
        #   Y
        # --------------------------------------------------------
        title_center_y = (
            max(
                margin_y,
                int(
                    screen_h * self.TITLE_Y_RATIO
                ),
            )
        )
        header_center_y = (
            max(
                margin_y,
                int(
                    screen_h * self.HEADER_Y_RATIO
                ),
            )
        )
        rows_top_y = max(
            margin_y,
            int(
                screen_h * self.ROWS_TOP_Y_RATIO
            ),
        )
        row_height = (
            int(screen_h * self.ROW_HEIGHT_RATIO)
        )
        footer_center_y = (
            min(
                screen_h - margin_y,
                int(
                    screen_h * self.FOOTER_Y_RATIO
                ),
            )
        )

        return HighscoreMetrics(
            title_center_y=title_center_y,
            header_center_y=header_center_y,
            rows_top_y=rows_top_y,
            row_height=row_height,
            col_rank_x=col_rank_x,
            col_name_x=col_name_x,
            col_score_x=col_score_x,
            footer_center_y=footer_center_y,
            content_cx=content_cx,
            content_left=content_left,
            content_right=content_right,
        )
