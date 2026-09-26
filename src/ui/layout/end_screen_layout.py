"""Layout for end-of-game screens (Game Over, Victory).

Defines the vertical and horizontal metrics used by the
end-of-game screens and calculates element positions based
on screen size.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from ..configUI.ui_config import Palette


@dataclass(frozen=True)
class EndScreenMetrics:
    """Metrics calculated for a game-over screen.

    Attributes:
        title_y       : Y-coordinate of the title.
        message_y     : Y-coordinate of the message.
        score_label_y : Y-coordinate of the score label.
        score_value_y : Y-coordinate of the score value.
        name_label_y  : Y-coordinate of the name label.
        name_value_y  : Y-coordinate of the name value.
        credits_y     : Y-coordinate of the credits.
        content_cx    : X-coordinate of the center of the content area.
        content_left  : X-coordinate of the left edge of the content.
        content_right : X-coordinate of the right edge of the content.
        button_rect   : Rectangle of the main button.
    """

    title_y: int
    message_y: int
    score_label_y: int
    score_value_y: int
    name_label_y: int
    name_value_y: int
    credits_y: int
    button_rect: pygame.Rect
    content_cx: int
    content_left: int
    content_right: int


class EndScreenLayout:
    """Screen-relative metrics for end-of-game screens."""

    # -----------------------------------------------------
    #   NOTE: Logic Proportions.
    # -----------------------------------------------------
    #   Proportions are expressed as fractions of the screen
    #   width or height and can be overridden at creation
    #   time via keyword arguments.
    # -----------------------------------------------------
    #    BackGround / container
    # -----------------------------------------------------
    BACKGROUND: tuple[int, int, int] | None = Palette.BLACK
    MARGIN_X_RATIO: float = 0.10
    MARGIN_Y_RATIO: float = 0.05
    # -----------------------------------------------------
    #    vertical Ratio
    # -----------------------------------------------------
    TITLE_Y_RATIO: float = 0.16
    MESSAGE_Y_RATIO: float = 0.30
    SCORE_LABEL_Y_RATIO: float = 0.44
    SCORE_VALUE_Y_RATIO: float = 0.50
    NAME_LABEL_Y_RATIO: float = 0.62
    NAME_VALUE_Y_RATIO: float = 0.67
    CREDITS_Y_RATIO: float = 0.80

    BUTTON_BOTTOM_MARGIN_RATIO: float = 0.06
    BUTTON_WIDTH_RATIO: float = 0.40
    BUTTON_HEIGHT_RATIO: float = 0.09
    CENTER_CONTENT: bool = True
    CREDITS_GAP_RATIO: float = 0.02

    def __init__(self, **overrides: object) -> None:
        """Initialize the layout, applying any overrides.

        Args:
            **overrides: Alternative values for the layout's class
            attributes. Keys must match attribute names of
            `EndScreenLayout`.

        Raises:
            AttributeError: If an override key does not match
                            any class attribute.
        """
        for key, value in overrides.items():
            if not hasattr(type(self), key):
                raise AttributeError(
                    f"Unknown layout ratio: {key!r}. "
                    f"Valid keys are EndScreenLayout class attributes."
                )
            setattr(self, key, value)

    def compute(
        self,
        screen_w: int,
        screen_h: int,
        *,
        show_message: bool,
        show_credits: bool,
    ) -> EndScreenMetrics:
        """Calculate metrics for the specified screen.

        Args:
            screen_w     : Screen width in pixels.
            screen_h     : Screen height in pixels.
            show_message : If `True`, reserves space for the message.
            show_credits : If `True`, reserves space for the credits.

        Returns:
            An `EndScreenMetrics` object with the calculated coordinates.
        """
        if show_message:
            score_label_ratio = self.SCORE_LABEL_Y_RATIO
            score_value_ratio = self.SCORE_VALUE_Y_RATIO
        else:
            score_label_ratio = (
                self.SCORE_LABEL_Y_RATIO + self.MESSAGE_Y_RATIO
            ) / 2
            score_value_ratio = (
                self.SCORE_VALUE_Y_RATIO + self.MESSAGE_Y_RATIO
            ) / 2
        # -----------------------------------------------------
        #    Conteiner
        # -----------------------------------------------------
        margin_x = int(screen_w * self.MARGIN_X_RATIO)
        margin_y = int(screen_h * self.MARGIN_Y_RATIO)
        content_left = margin_x
        content_right = screen_w - margin_x
        content_cx = (content_left + content_right) // 2
        # -----------------------------------------------------
        #    Button
        # -----------------------------------------------------
        btn_h = int(screen_h * self.BUTTON_HEIGHT_RATIO)
        btn_w = int(screen_w * self.BUTTON_WIDTH_RATIO)
        btn_w = min(btn_w, content_right - content_left)
        btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
        btn_rect.center = (
            content_cx,
            screen_h
            - int(screen_h * self.BUTTON_BOTTOM_MARGIN_RATIO)
            - btn_h // 2,
        )
        # -----------------------------------------------------
        #    Y
        # -----------------------------------------------------
        title_y = int(screen_h * self.TITLE_Y_RATIO)
        message_y = int(screen_h * self.MESSAGE_Y_RATIO)
        score_label_y = int(screen_h * score_label_ratio)
        score_value_y = int(screen_h * score_value_ratio)
        name_label_y = int(screen_h * self.NAME_LABEL_Y_RATIO)
        name_value_y = int(screen_h * self.NAME_VALUE_Y_RATIO)
        credits_y = int(screen_h * self.CREDITS_Y_RATIO)

        if self.CENTER_CONTENT:
            block_top = title_y
            block_bottom = btn_rect.centery
            mid = (block_top + block_bottom) / 2
            desired_mid = screen_h / 2
            delta = int(desired_mid - mid)

            title_y += delta
            message_y += delta
            score_label_y += delta
            score_value_y += delta
            name_label_y += delta
            name_value_y += delta
            credits_y += delta
            btn_rect.centery += delta
        # -----------------------------------------------------
        #    Vertical Clamp
        # -----------------------------------------------------
        y_min = margin_y
        y_max = screen_h - margin_y

        title_y = max(y_min, min(title_y, y_max))
        message_y = max(y_min, min(message_y, y_max))

        score_label_y = max(y_min, min(score_label_y, y_max))
        score_value_y = max(y_min, min(score_value_y, y_max))

        name_label_y = max(y_min, min(name_label_y, y_max))
        name_value_y = max(y_min, min(name_value_y, y_max))

        credits_y = max(y_min, min(credits_y, y_max))

        return EndScreenMetrics(
            title_y=title_y,
            message_y=message_y,
            score_label_y=score_label_y,
            score_value_y=score_value_y,
            name_label_y=name_label_y,
            name_value_y=name_value_y,
            credits_y=credits_y,
            button_rect=btn_rect,
            content_cx=content_cx,
            content_left=content_left,
            content_right=content_right,
        )
