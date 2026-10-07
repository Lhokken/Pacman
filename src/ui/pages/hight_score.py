"""Static Pac-Man high scores page.

It displays a leaderboard with columns (RANK, NAME, SCORE) and
a minimum number of rows, filling empty slots with placeholders.
The footer consists of an "ESC TO RETURN TO MENU" button that
returns the user to the main menu.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

from ..scene import Scene
from ..components.button import Button
from ..configUI.ui_config import FontRole
from ..layout.hight_score_layout import (
    HighscoreLayout,
    HighscoreMetrics,
)

if TYPE_CHECKING:
    from ..app import GameApp
    from ..components.bitmap_font import BitmapFont

logger = logging.getLogger(__name__)


class HighScorePage(Scene):
    """Static high scores page.

    Layout and content are calculated in `_rebuild()` and cached
    until the screen size changes. The footer is a permanently
    selected button that responds to Esc and Enter.
    """

    MIN_ROWS = 10
    PLACEHOLDER_NAME = "---"
    PLACEHOLDER_SCORE = "0"

    # ==================================================================
    #   Init
    # ==================================================================
    def __init__(self, app: GameApp) -> None:
        """Initialize the high scores page.

        Args:
            app: Instance of `GameApp` from which to access the screen
                 and handle scene switching.
        """
        super().__init__(app)

        # ------------------------------------------------------------
        # --- Font
        # ------------------------------------------------------------
        self._font_section = (
            self.theme.font_config(
                FontRole.HEADING
            )
        )
        self._font_header = (
            self.theme.font_config(
                FontRole.SECTION_TITLE
            )
        )
        self._font_row = (
            self.theme.font_config(
                FontRole.OPTION
            )
        )
        self._font_footer = (
            self.theme.font_config(
                FontRole.OPTION
            )
        )
        self._font_footer_selected = (
            self.theme.font_config(
                FontRole.OPTION_SELECTED
            )
        )
        # ------------------------------------------------------------
        #   Layout
        # ------------------------------------------------------------
        self._layout = HighscoreLayout()

        # ------------------------------------------------------------
        #   CACHE
        # ------------------------------------------------------------
        self._metrics: HighscoreMetrics | None = None
        self._metrics_size: tuple[int, int] = (0, 0)
        self._rows: list[tuple[str, str, str]] = []
        self._rebuild()
        # ------------------------------------------------------------
        # --- Bottone back
        # ------------------------------------------------------------
        self._back_button = Button(
            pygame.Rect(0, 0, 400, 50),
            "ESC TO RETURN TO MENU",
            self._font_footer,
            self._font_footer_selected,
            on_select=self._go_back,
        )
        self._back_button.set_selected(True)

    # ==================================================================
    #   Lifecycle
    # ==================================================================
    def handle_events(self) -> None:
        """Handle the page's input events.

        ESC returns to the main menu; Enter activates the
        Back button (which is always selected).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._go_back()
                elif event.key == pygame.K_RETURN:
                    self._back_button.handle_event(event)

    def update(self) -> None:
        """Recalculate the metrics if the screen size changes."""
        if self.app.screen.get_size() != self._metrics_size:
            self._rebuild()

    def draw(self, screen: Surface) -> None:
        """Draws the title, headers, rows, and footer.

        Args:
            screen: Destination surface.
        """
        screen.fill(
            self.theme.palette.DARK
        )
        assert self._metrics is not None
        m = self._metrics
        cx = m.content_cx
        # ------------------------------------------------------------
        #   TITLE
        # ------------------------------------------------------------
        title = self._font_section.render("HIGH SCORES")
        self.render.blit_center(
            screen,
            title,
            cx,
            m.title_center_y
        )
        # ------------------------------------------------------------
        #   HEADER
        # ------------------------------------------------------------
        self._draw_cell(
            screen,
            "RANK",
            m.col_rank_x,
            m.header_center_y,
            self._font_header,
        )
        self._draw_cell(
            screen,
            "NAME",
            m.col_name_x,
            m.header_center_y,
            self._font_header,
        )
        self._draw_cell(
            screen,
            "SCORE",
            m.col_score_x,
            m.header_center_y,
            self._font_header,
        )
        # ------------------------------------------------------------
        #   ROW
        # ------------------------------------------------------------
        for i, (rank, name, score) in enumerate(self._rows):
            y = m.rows_top_y + i * m.row_height
            self._draw_cell(
                screen,
                rank,
                m.col_rank_x,
                y,
                self._font_row
            )
            self._draw_cell(
                screen,
                name,
                m.col_name_x,
                y,
                self._font_row
            )
            self._draw_cell(
                screen,
                score,
                m.col_score_x,
                y,
                self._font_row
            )
        # ------------------------------------------------------------
        #   FOOTER
        # ------------------------------------------------------------
        self._back_button.rect.center = (
            m.content_cx,
            m.footer_center_y
        )
        self._back_button.set_selected(True)
        self._back_button.draw(screen)

    # ==================================================================
    #   NAVIGATION
    # ==================================================================
    def _go_back(self) -> None:
        """Torna al menu principale."""
        from .main_menu import MainMenu
        self.app.switch_scene(MainMenu(self.app))

    # ==================================================================
    #   METRICS
    # ==================================================================
    def _rebuild(self) -> None:
        """Recalculate metrics and rows for the current dimension."""
        w, h = self.app.screen.get_size()
        self._metrics_size = (w, h)
        self._metrics = (
            self._layout.compute(
                w,
                h,
                n_rows=self.MIN_ROWS
            )
        )
        self._rows = self._build_rows()

    def _build_rows(self) -> list[tuple[str, str, str]]:
        """Construct at least `MIN_ROWS` leaderboard rows.

        The initial rows come from the actual store (if available);
        missing positions are filled with placeholders.

        TODO: HOOK UP TO CORE

        Returns:
            A list of `(rank, name, score)` tuples of length `MIN_ROWS`.
        """
        # store = (
        #     getattr(self.app, "highscore_store", None)
        # )
        # entries = (
        #     store.top(self.MIN_ROWS) if store is not None else []
        # )
        # # -------------------------------------------------------------
        # # Lista dei Nomi delle persone.
        # # -------------------------------------------------------------
        # rows: list[tuple[str, str, str]] = []
        # for i in range(self.MIN_ROWS):
        #     rank = str(i + 1)
        #     if i < len(entries):
        #         e = entries[i]
        #         rows.append((rank, e.name, str(e.score)))
        #     else:
        #         rows.append((
        #             rank,
        #             self.PLACEHOLDER_NAME,
        #             self.PLACEHOLDER_SCORE,
        #         ))
        # ---------------------------------------------
        # Lista dei Nomi delle persone.
        # -------------------------------------------------------------
        rows: list[tuple[str, str, str]] = []
        for i, key in enumerate(self.app.HIGHSCORE):
            rank = str(i + 1)
            rows.append((rank, key, str(self.app.HIGHSCORE[key])))
        while len(rows) < 10:
            rows.append((
                str(len(rows) + 1),
                self.PLACEHOLDER_NAME,
                self.PLACEHOLDER_SCORE,
            ))
        return rows

    # ==================================================================
    #   Draw helpers
    # ==================================================================
    def _draw_cell(
        self,
        screen: Surface,
        text: str,
        cx: int,
        cy: int,
        font: BitmapFont,
    ) -> None:
        """Draws a cell centered on `(cx, cy)`.

        Args:
            screen : Target surface.
            text   : Text to render.
            cx     : X coordinate of the cell center.
            cy     : Y coordinate of the cell center.
            font   : Font to render the text in.
        """
        surf = font.render(text)
        self.render.blit_center(screen, surf, cx, cy)
