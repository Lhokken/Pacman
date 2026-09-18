"""Layout per le schermate di fine hight score."""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class HightScoreMetrics:
    """FA TODO: Metriche."""

    title_y: int
    message_y: int
    score_y: int
    name_label_y: int
    name_value_y: int
    credits_y: int
    button_rect: pygame.Rect


class HightScoreLayout:
    """Metriche screen-relative per i 10 giocatori con score alto."""

    TITLE_Y_RATIO: float = 0.18
    MESSAGE_Y_RATIO: float = 0.32
    SCORE_Y_RATIO: float = 0.44
    NAME_LABEL_Y_RATIO: float = 0.56
    NAME_VALUE_Y_RATIO: float = 0.64
    CREDITS_Y_RATIO: float = 0.76

    BUTTON_BOTTOM_MARGIN_RATIO: float = 0.08
    BUTTON_WIDTH_RATIO: float = 0.30
    BUTTON_HEIGHT_RATIO: float = 0.07

    def __init__(self, **overrides: dict[str, dict]) -> None:
        """FA TODO: HIGHTSCORE dei 10 risutati."""
        for key, value in overrides.items():
            if not hasattr(type(self), key):
                raise AttributeError(
                    f"Unknown layout ratio: {key!r}. "
                    f"Valid keys are EndScreenLayout class attributes."
                )
            setattr(self, key, value)
