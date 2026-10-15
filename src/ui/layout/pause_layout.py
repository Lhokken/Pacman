"""Calculate title and button positions for the pause menu.

Unlike ``MenuLayout``, the pause layout anchors the title near the top and
centers the button group independently.

The layout returns a dataclass from ``compute()`` and accepts class-ratio
overrides through ``__init__(**overrides)``.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class PauseBlock:
    """Calculated positions for the pause menu.

    Attributes:
        title_center_y : Vertical center of the title in pixels.
        button_rects   : Rectangle for each menu button.
    """

    title_center_y: int
    button_rects: tuple[pygame.Rect, ...]


class PauseLayout:
    """Calculate title and button positions for the pause menu."""

    # ========================================================================
    #   Class attributes (ratio), overridable per instance
    # ========================================================================

    BTN_WIDTH_RATIO: float = 0.40         # button width.
    BTN_CENTER_Y_RATIO: float = 0.55      # vertical center of button block.
    BTN_HEIGHT_RATIO: float = 0.07        # button height.
    BTN_SPACE_RATIO: float = 0.065        # distance between the centers of btn.
    TITLE_Y_RATIO: float = 0.35           # Y-coordinate of the title's center.

    def __init__(self, **overrides: float) -> None:
        """Create the layout, optionally overriding some ratios.

        Raises:
            AttributeError: if a key is not a known ratio.
        """
        for key, value in overrides.items():
            if not hasattr(type(self), key):
                raise AttributeError(
                    f"Unknown layout ratio: {key!r}. "
                    f"Valid keys are PauseLayout class attributes."
                )
            setattr(self, key, float(value))

    def compute(
        self,
        screen_w: int,
        screen_h: int,
        *,
        n_buttons: int,
    ) -> PauseBlock:
        """Calculate the title and button positions.

        Args:
            screen_w  : Screen width in pixels.
            screen_h  : Screen height in pixels.
            n_buttons : Number of menu buttons.

        Returns:
            PauseBlock containing the title position and button rectangles.
        """
        title_center_y = int(screen_h * self.TITLE_Y_RATIO)
        # ======================================================
        # BTN
        # ======================================================
        btn_w = int(
            screen_w * self.BTN_WIDTH_RATIO
        )
        btn_h = int(
            screen_h * self.BTN_HEIGHT_RATIO
        )

        space = int(
            screen_h * self.BTN_SPACE_RATIO
        )
        center_y = int(
            screen_h * self.BTN_CENTER_Y_RATIO
        )

        # Button container centered on center_y. --------------
        total_h = (n_buttons - 1) * space + btn_h
        first_y = center_y - total_h // 2 + btn_h // 2

        cx = screen_w // 2
        rects: list[pygame.Rect] = []
        for i in range(n_buttons):
            rect = pygame.Rect(0, 0, btn_w, btn_h)
            rect.center = (cx, first_y + i * space)
            rects.append(rect)
        return PauseBlock(
            title_center_y=title_center_y,
            button_rects=tuple(rects),
        )
