"""Layout for the cheat page.

Defines the proportions and calculates the positions of the title
and buttons on the cheat screen.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from ..configUI.ui_config import Palette


@dataclass(frozen=True)
class CheatBlock:
    """Result of the cheat page layout calculation.

    Attributes:
        title_center_y : Y-coordinate of the title center.
        button_rects   : Tuple of button rectangles.
        content_cx     : X-coordinate of the content area center.
        content_left   : X-coordinate of the left edge of the content.
        content_right  : X-coordinate of the right edge of the content.
    """

    title_center_y: int
    button_rects: tuple[pygame.Rect, ...]
    content_cx: int
    content_left: int
    content_right: int


class CheatLayout:
    """Calculate the positions of the page, title and buttons.

    Proportions are expressed as fractions of the screen
    width or height and can be overridden at creation time
    via keyword arguments.
    """

    # screen -----------------------------------------------
    BACKGROUND: tuple[int, int, int] | None = Palette.DARK
    MARGIN_X_RATIO: float = 0.10
    MARGIN_Y_RATIO: float = 0.05

    # title ------------------------------------------------
    TITLE_Y_RATIO: float = 0.18

    # Button -----------------------------------------------
    BUTTON_WIDTH_RATIO: float = 0.45
    BUTTONS_CENTER_Y_RATIO: float = 0.52
    BUTTON_HEIGHT_RATIO: float = 0.06
    BUTTON_SPACE_RATIO: float = 0.075

    def __init__(self, **overrides: float) -> None:
        """Initialize the layout, applying any overrides.

        Args:
          **overrides: Alternative values for the proportions defined
          as class attributes. Keys must match
          `CheatLayout` attribute names.

        Raises:
          AttributeError: If an override key does not match
          any class attribute.
        """
        for key, value in overrides.items():
            if not hasattr(type(self), key):
                raise AttributeError(
                    f"Unknown layout ratio: {key!r}. "
                    f"Valid keys are CheatLayout class attributes."
                )
            setattr(self, key, float(value))

    def compute(
        self,
        screen_w: int,
        screen_h: int,
        *,
        n_buttons: int,
    ) -> CheatBlock:
        """Calculate the positions for the specified screen.

        Args:
            screen_w: Screen width in pixels.
            screen_h: Screen height in pixels.
            n_buttons: Number of buttons to arrange.

        Returns:
          A `CheatBlock` with the calculated coordinates.
        """
        # -----------------------------------------------------
        #   Screen
        # -----------------------------------------------------
        margin_x = int(
          screen_w * self.MARGIN_X_RATIO
        )
        margin_y = int(
          screen_h * self.MARGIN_Y_RATIO
        )
        content_left = margin_x
        content_right = (
            screen_w - margin_x
        )
        content_cx = (
          (content_left + content_right) // 2
        )
        # -----------------------------------------------------
        #   Title
        # -----------------------------------------------------
        title_center_y = int(
          screen_h * self.TITLE_Y_RATIO
        )
        title_center_y = max(
            margin_y,
            min(title_center_y, screen_h - margin_y)
        )
        # -----------------------------------------------------
        #   Buttons
        # -----------------------------------------------------
        btn_w = int(
          screen_w * self.BUTTON_WIDTH_RATIO
        )
        btn_w = min(
          btn_w, content_right - content_left
        )
        btn_h = int(
          screen_h * self.BUTTON_HEIGHT_RATIO
        )
        space = int(
          screen_h * self.BUTTON_SPACE_RATIO
        )
        center_y = int(
          screen_h * self.BUTTONS_CENTER_Y_RATIO
        )
        # -----------------------------------------------------
        #   PAGE
        # -----------------------------------------------------
        total_h = (n_buttons - 1) * space + btn_h
        first_y = center_y - total_h // 2 + btn_h // 2

        rects: list[pygame.Rect] = []
        for i in range(n_buttons):
            rect = pygame.Rect(0, 0, btn_w, btn_h)
            rect.center = (content_cx, first_y + i * space)
            rects.append(rect)

        return CheatBlock(
            title_center_y=title_center_y,
            button_rects=tuple(rects),
            content_cx=content_cx,
            content_left=content_left,
            content_right=content_right,
        )
