"""Layout for the main menu's [title + buttons] block.

Conventions aligned with `GameLayout`:
- return dataclass (`MenuBlock` <-|-> `PanelRect`)
- `compute()` as a public method
- ratios defined as class attributes, overridable via `__init__(**overrides)`
- pixel coordinates, fully calculated within `compute()`
"""
from __future__ import annotations

import pygame

from dataclasses import dataclass

# Unlike `GameLayout`, which receives all inputs via its constructor,
# `MenuLayout` is a pure calculator: the menu changes throughout its lifecycle:
# (attract → ready → menu)
# and dynamic values: ​
# ​(title height, brand Y-position, number of buttons)
# are not known in advance. Therefore, `compute()` accepts these values ​​on
# each call and returns a `MenuBlock`.


@dataclass(frozen=True)
class BlockMenu:
    """Calculate positions for Title Container + Buttons.

    Attributes:
    center_titolo_y : Y (px) of the center of the title box
    button_rect : Tuple of pygame.Rect
    """

    center_titolo_y: int
    button_rect: tuple[pygame.Rect, ...]


class MenuLayout:
    """Calculate the positions of the Title + Buttons Continer.

    Class Attributes:
        CENTER_Y_RATIO          : vertical center of the block
        TITLE_TO_BTN_GAP_RATIO  : Fraction of screen_heig
        BTN_SPACE_RATIO         : distance between button centers
        BTN_HEIGHT_RATIO        : height of the buttons
        BTN_WIDHT_RATIO         : width of the buttons
        BRAND_FLOOR_RATIO       : Impedisce invasione su 42SCHOOL

    Returns:
        BlockMenu: Bottone centrato.
    """

    # =====================================================================
    #   Ratio
    # =====================================================================
    # Fraction of screen_height: vertical center of the block. ------------
    CENTER_Y_RATIO: float = 0.70

    # Fraction of screen_height: title gap -> first button. ---------------
    TITLE_TO_BTN_GAP_RATIO: float = 0.025

    # Fraction of screen_width: width of the buttons. ---------------------
    BTN_WIDTH_RATIO: float = 0.40

    # Fraction of screen_height: height of the buttons. -------------------
    BTN_HEIGHT_RATIO: float = 0.07

    # Fraction of screen_height: distance between button centers. ---------
    BTN_SPACE_RATIO: float = 0.065

    # Fraction of screen_height: minimum margin under the brand. ----------
    BRAND_FLOOR_RATIO: float = 0.06  # Impedisce invasione su 42SCHOOL

    # =====================================================================
    #   INIT
    # =====================================================================
    def __init__(self, **overrides: float) -> None:
        """Create the layout, possibly overwriting some ratios.

        Args:
            **overrides: e.g. CENTER_Y_RATIO=0.65, BUTTON_HEIGHT_RATIO=0.08.

        Raises:
            AttributeError: if a key is not a known ratio.
        """
        for key, value in overrides.items():
            if not hasattr(type(self), key):
                raise AttributeError(
                    f"Unknown layout ratio: {key!r}"
                    "Valid keys are MenuLayout class Attribute"
                )
            setattr(self, key, float(value))

    # Pubblic methods -----------------------------------------------------
    # =====================================================================
    #   API Principale
    # =====================================================================
    def compute_block(
        self,
        screen_w: int,
        screen_h: int,
        *,
        title_h: int,
        brand_y: int,
        nbr_btn: int
    ) -> BlockMenu:
        """Calculate block positions.

        Args:
            screen_w: screen size in pixels.
            screen_h: screen size in pixels.
            title_h: title height (0 if absent).
            brand_y: Y of the top brand (0 if absent). Lower floor.
            nbr_btn: number of buttons.

        Returns:
            MenuBlock with the Y of the title and the rects of the buttons.
        """
        btn_h = int(screen_h * self.BTN_HEIGHT_RATIO)            # height
        btn_w = int(screen_w * self.BTN_WIDTH_RATIO)             # widht
        btn_s = int(screen_h * self.BTN_SPACE_RATIO)             # spacing
        btn_g = int(screen_h * self.TITLE_TO_BTN_GAP_RATIO)      # gap

        # Altezza totale del contenitore -----------------------------------
        buttons_h = nbr_btn * btn_h + max(0, nbr_btn - 1) * btn_s
        container_h = title_h + btn_g + buttons_h

        # Centro Target -> TOP container -----------------------------------
        target_center = int(screen_h * self.CENTER_Y_RATIO)
        container_top = target_center - container_h // 2

        # Floor: evita collisione con il brand, lasciando un margine.
        min_top = brand_y + int(screen_h * self.BRAND_FLOOR_RATIO)
        container_top = max(container_top, min_top)

        # Posizioni --------------------------------------------------------
        title_center_y = container_top + title_h // 2
        first_center_y = container_top + title_h + btn_g + btn_h // 2

        center_x = screen_w // 2
        rects: list[pygame.Rect] = []
        for i in range(nbr_btn):
            rect = pygame.Rect(0, 0, btn_w, btn_h)
            rect.center = (center_x, first_center_y + i * btn_s)
            rects.append(rect)

        return BlockMenu(
            center_titolo_y=title_center_y,
            button_rect=tuple(rects)
        )
