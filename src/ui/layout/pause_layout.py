"""Layout di titolo + bottoni per il menu pausa.

Differenza rispetto a MenuLayout:
    - MenuLayout:   titolo e bottoni formano un blocco unico, che
                    si sposta insieme (centrato su CENTER_Y_RATIO).
    - PauseLayout:  titolo ancorato in alto (TITLE_Y_RATIO), bottoni
                    centrati indipendentemente (BUTTONS_CENTER_Y_RATIO).

Stesso pattern di MenuLayout: dataclass di ritorno, `compute()`,
ratio di classe sovrascrivibili via `__init__(**overrides)`.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class PauseBlock:
    """Posizioni calcolate per il menu pausa.

    Attributi:
        title_center_y: Y (px) del centro del titolo.
        button_rects:   tupla di pygame.Rect, uno per bottone.
    """
    title_center_y: int
    button_rects: tuple[pygame.Rect, ...]


class PauseLayout:
    """Calcola le posizioni di titolo + bottoni del menu pausa."""

    # ===============================================================
    #   Class attributes (ratio), overridable per instance
    # ===============================================================
    # screen_width --------------------------------------------------
    BUTTON_WIDTH_RATIO: float = 0.35      # button width.

    # screen_height -------------------------------------------------
    BUTTONS_CENTER_Y_RATIO: float = 0.55  # vertical center of button block.
    TITLE_Y_RATIO: float = 0.15           # Y-coordinate of the title's center.
    BUTTON_HEIGHT_RATIO: float = 0.07    # button height.
    BUTTON_SPACE_RATIO: float = 0.09     # distance between the centers of btn.

    def __init__(self, **overrides: float) -> None:
        """Creates the layout, optionally overriding some ratios.

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
        """Calcola le posizioni di titolo e bottoni.

        Args:
            screen_w, screen_h: dimensioni schermo in pixel.
            n_buttons: numero di bottoni.

        Returns:
            PauseBlock con la Y del titolo e i rect dei bottoni.
        """
        title_center_y = int(screen_h * self.TITLE_Y_RATIO)
        # ======================================================
        # BTN
        # ======================================================
        # TODO: COMMENTO
        btn_w = int(
            screen_w * self.BUTTON_WIDTH_RATIO
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
        # Button container centered on center_y. --------------
        total_h = (n_buttons - 1) * space + btn_h
        first_y = center_y - total_h // 2 + btn_h // 2
        # TODO: COMMENTO
        cx = screen_w // 2
        rects: list[pygame.Rect] = []
        for i in range(n_buttons):
            rect = pygame.Rect(0, 0, btn_w, btn_h)
            rect.center = (cx, first_y + i * space)
            rects.append(rect)
        # TODO: COMMENTO
        return PauseBlock(
            title_center_y=title_center_y,
            button_rects=tuple(rects),
        )
