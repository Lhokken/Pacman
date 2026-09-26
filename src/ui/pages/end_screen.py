"""Abstract base class for end-of-game screens (static).

GameOverPage and VictoryPage share structure, layout, input handling,
and name entry logic; this file centralizes all of that.

Static version
    - No timer, no blinking: the cursor is always visible.
    - The cursor is an arrow (asset `char/giallo/segni/freccia.png`).
    - Metrics are calculated in `__init__` and recalculated only upon
      resizing (in `update`), not during every `draw` call.

Name entry:
    - The user types up to NAME_MAX_LEN alphanumeric characters.
    - Backspace deletes the last character.
    - ENTER (or the button) saves and returns to the menu.
    - ESC returns to the menu without saving.

Saving:
    If `app.save_highscore(name, score)` exists, it is called.
    Otherwise, it simply logs the action.
"""

from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

from ..components.button import Button
from ..configUI.ui_config import FontRole
from ..layout.end_screen_layout import EndScreenLayout, EndScreenMetrics
from ..scene import Scene

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class EndScreenPage(Scene, ABC):
    """Base class for static game-over and victory screens.

    The page displays the final score, accepts a short alphanumeric name,
    and returns to the main menu after submission or cancellation.
    """

    TITLE_TEXT: str = ""
    MESSAGE_TEXT: str = ""

    NAME_MAX_LEN: int = 5
    NAME_LABEL_TEXT: str = "ENTER YOUR NAME"
    NAME_PLACEHOLDER: str = "-"

    BUTTON_TEXT: str = "SAVE AND BACK TO MENU"

    CURSOR_GAP: int = 6
    CURSOR_ROTATE: int = -90

    SHOW_CREDITS: bool = False
    CREDIT_TEXT: str = "for 42 school project"

    def __init__(self, app: GameApp, score: int = 0) -> None:
        """Initialize the end screen and its fixed-size layout elements.

        Args:
            app: Application instance used for rendering, assets, and scene
                switching.
            score: Final score to display and optionally save.
        """
        super().__init__(app)
        self.score = score

        # --------------------------------------------------------------
        #   FONT
        # --------------------------------------------------------------
        # shared by Scenes. No local FontManager.
        self.font_title = (
            self.theme.font_config(
                FontRole.SCREEN_TITLE
            )
        )
        self.font_message = (
            self.theme.font_config(
                FontRole.HEADING
            )
        )
        self.font_score_label = (
            self.theme.font_config(
                FontRole.SMALL
            )
        )
        self.font_score_value = (
            self.theme.font_config(
                FontRole.VALUE_BIG
            )
        )
        self.font_name = (
            self.theme.font_config(
                FontRole.SECTION_TITLE
            )
        )
        self.font_label = (
            self.theme.font_config(
                FontRole.SMALL
            )
        )
        self.font_credits = (
            self.theme.font_config(
                FontRole.SMALL
            )
        )
        self.font_button = (
            self.theme.font_config(
                FontRole.OPTION
            )
        )
        self.font_button_selected = (
            self.theme.font_config(
                FontRole.OPTION_SELECTED
            )
        )

        self._layout = EndScreenLayout()
        self._name: str = ""
        self._submitted: bool = False

        self._raw_cursor = self._load_cursor_img()
        self._cursor_img: Surface | None = None

        self._button = Button(
            pygame.Rect(0, 0, 10, 10),
            self.BUTTON_TEXT,
            self.font_button,
            self.font_button_selected,
            on_select=self._submit,
        )
        self._button.set_selected(True)

        self._metrics: EndScreenMetrics | None = None
        self._metrics_size: tuple[int, int] = (0, 0)
        self._rebuild_metrics()

    # ==================================================================
    #   Lifecycle
    # ==================================================================
    def handle_events(self) -> None:
        """Process window and keyboard events for the name entry screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)

    def _handle_key(self, event: pygame.event.Event) -> None:
        """Update the entered name or trigger a navigation action.

        Args:
            event: Keyboard event containing the pressed key and character.
        """
        if event.key == pygame.K_ESCAPE:
            self._go_back()
            return
        if event.key == pygame.K_RETURN:
            self._submit()
            return
        if event.key == pygame.K_BACKSPACE:
            self._name = self._name[:-1]
            return
        ch = event.unicode
        if ch and ch.isalnum() and len(self._name) < self.NAME_MAX_LEN:
            self._name += ch.upper()

    def update(self) -> None:
        """Recalculate layout-dependent metrics after a resize."""
        if self.app.screen.get_size() != self._metrics_size:
            self._rebuild_metrics()

    def draw(self, screen: Surface) -> None:
        """Render the title, score, name entry, button, and optional credits.

        Args:
            screen: Surface on which the end screen is rendered.
        """
        screen.fill(self.theme.palette.DARK)
        assert self._metrics is not None
        m = self._metrics
        cx = screen.get_width() // 2

        self.render.blit_center(
            screen, self.font_title.render(self.TITLE_TEXT), cx, m.title_y
        )

        if self.MESSAGE_TEXT:
            self.render.blit_center(
                screen,
                self.font_message.render(self.MESSAGE_TEXT),
                cx, m.message_y,
            )

        self.render.blit_center(
            screen,
            self.font_score_label.render("FINAL SCORE"),
            cx, m.score_label_y,
        )
        self.render.blit_center(
            screen,
            self.font_score_value.render(str(self.score)),
            cx, m.score_value_y,
        )

        self._draw_name_entry(screen, cx, m.name_label_y, m.name_value_y)
        self._button.draw(screen)

        if self.SHOW_CREDITS and self.CREDIT_TEXT:
            credit_surf = self.font_credits.render(self.CREDIT_TEXT)
            gap = int(
                self.app.screen.get_height()
                * self._layout.CREDITS_GAP_RATIO
            )
            footer_y = (
                self._button.rect.bottom
                + credit_surf.get_height() // 2
                + gap
            )
            self.render.blit_center(
                screen,
                credit_surf,
                cx,
                footer_y
            )

    # ==================================================================
    #   Metriche
    # ==================================================================
    def _rebuild_metrics(self) -> None:
        """Recalculate screen metrics and resize the name-entry cursor."""
        w, h = self.app.screen.get_size()
        self._metrics_size = (w, h)
        self._metrics = self._layout.compute(
            w, h,
            show_message=bool(self.MESSAGE_TEXT),
            show_credits=bool(self.SHOW_CREDITS),
        )
        self._button.rect = self._metrics.button_rect

        if self._raw_cursor is not None:
            char_h = self.font_name.char_height
            self._cursor_img = self.render.scale_to_height(
                self._raw_cursor, char_h,
            )
            if self.CURSOR_ROTATE:
                self._cursor_img = pygame.transform.rotate(
                    self._cursor_img, self.CURSOR_ROTATE,
                )
        else:
            self._cursor_img = None

    # ==================================================================
    #   Name entry (statico, slot-per-slot)
    # ==================================================================
    def _draw_name_entry(
        self, screen: Surface, cx: int, label_y: int, value_y: int,
    ) -> None:
        """Render fixed-width name slots and the current cursor position.

        Args:
            screen: Surface on which the name entry is rendered.
            cx: Horizontal center of the name-entry block.
            label_y: Vertical center of the name label.
            value_y: Vertical center of the name slots.
        """
        self.render.blit_center(
            screen,
            self.font_label.render(self.NAME_LABEL_TEXT),
            cx, label_y,
        )

        sample = self.font_name.render(self.NAME_PLACEHOLDER)
        char_w = sample.get_width()
        char_h = sample.get_height()

        total_w = char_w * self.NAME_MAX_LEN
        start_x = cx - total_w // 2
        top_y = value_y - char_h // 2

        for i in range(self.NAME_MAX_LEN):
            ch = (
                self._name[i]
                if i < len(self._name)
                else self.NAME_PLACEHOLDER
            )
            glyph = self.font_name.render(ch)
            screen.blit(glyph, (start_x + i * char_w, top_y))

        current = len(self._name)
        if current < self.NAME_MAX_LEN and self._cursor_img is not None:
            slot_cx = start_x + current * char_w + char_w // 2
            arrow_y = top_y + char_h + self.CURSOR_GAP
            self.render.blit_midtop(
                screen, self._cursor_img, slot_cx, arrow_y,
            )

    # ==================================================================
    #   Caricamento asset cursore
    # ==================================================================
    def _load_cursor_img(self) -> Surface | None:
        """Load the arrow cursor asset used below the active name slot.

        Returns:
            The loaded cursor surface, or ``None`` when the asset is missing
            or cannot be decoded by Pygame.
        """
        path = (
            self.app.assets_base
            / "char" / "giallo" / "segni" / "freccia.png"
        )
        if not path.exists():
            logger.warning(
                "EndScreenPage: cursore freccia mancante %s", path
            )
            return None
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            logger.error(
                "EndScreenPage: errore caricando %s: %s", path, e
            )
            return None

    # ==================================================================
    #   Azioni
    # ==================================================================
    def _submit(self) -> None:
        """Save the entered name when supported and return to the menu."""
        if self._submitted:
            return
        name = self._name.strip().upper()
        if name:
            save = getattr(self.app, "save_highscore", None)
            if callable(save):
                save(name, self.score)
            else:
                logger.info(
                    "Name entry: name=%s score=%d "
                    "(no save_highscore on app)",
                    name, self.score,
                )
        self._submitted = True
        self._go_back()

    def _go_back(self) -> None:
        """Switch the application to a new main-menu scene."""
        from .main_menu import MainMenu
        self.app.switch_scene(MainMenu(self.app))


class GameOverPage(EndScreenPage):
    """Scene shown when the game is over."""

    TITLE_TEXT = "Game Over"
    MESSAGE_TEXT = ""
    SHOW_CREDITS = True


class VictoryPage(EndScreenPage):
    """Scene shown when the player wins."""

    TITLE_TEXT = "Victory!"
    MESSAGE_TEXT = "You have cleared all the levels!"
    SHOW_CREDITS = True
