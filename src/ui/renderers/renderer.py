"""Shared rendering helpers in an OOP style.

A single `Renderer` class with pure methods. It has no internal
state for now, but it is the place to implement caching in the
future (e.g., rendered glyphs, repeated scaling operations) without
modifying the scenes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

if TYPE_CHECKING:
    from ..components.bitmap_font import BitmapFont


# ========================================================================
#   SHARED RENDERING
# ========================================================================
class Renderer:
    """Used rendering operations for scenes.

    All methods are `@staticmethod`: the class maintains no state
    and serves only as a cohesive namespace for drawing helpers.
    """

    # ------------------------------------------------------------------
    #   Blit
    # ------------------------------------------------------------------
    @staticmethod
    def blit_center(
        screen: Surface,
        img: Surface | None,
        x: float,
        y: float,
    ) -> None:
        """Draws `img` centered at `(x, y)`.

        If `img` is `None`, it does nothing; this allows call sites to
        pass the result of an optional load directly without
        additional checks.

        Args:
            screen: Destination surface.
            img: Image to draw, or `None`.
            x: X-coordinate of the image center.
            y: Y-coordinate of the image center.
        """
        if img is None:
            return
        screen.blit(img, img.get_rect(center=(int(x), int(y))))

    @staticmethod
    def blit_midtop(
        screen: Surface,
        img: Surface | None,
        x: float,
        y: float,
    ) -> None:
        """Draws `img` with the top edge centered on `(x, y)`.

        Args:
            screen: Target surface.
            img: Image to draw, or `None`.
            x: X coordinate of the midpoint of the top edge.
            y: Y coordinate of the top edge.
        """
        if img is None:
            # If `img` is `None`, it does nothing.
            return
        screen.blit(
            img,
            img.get_rect(midtop=(int(x), int(y)))
        )

    # ------------------------------------------------------------------
    #   Testo
    # ------------------------------------------------------------------
    @staticmethod
    def render_text(font: BitmapFont, text: str) -> Surface:
        """Render `text` using `font`.

        A wrapper for `font.render(text)`, useful for standardizing
        call sites and providing a single point to add options
        (such as antialiasing or background color) if needed.

        Args:
            font: The bitmap font used to render the text.
            text: The text to render.

        Returns:
            A `Surface` containing the rendered text.
        """
        return font.render(text)

    # ------------------------------------------------------------------
    #   Scale
    # ------------------------------------------------------------------
    @staticmethod
    def scale_to_height(img: Surface, target_h: int) -> Surface:
        """Scale `img` maintaining the aspect ratio, with `target_h`.

        Args:
            img       : Surface to scale.
            target_h  : Desired height in pixels.

        Returns:
            A new scaled `Surface`, or `img` if `target_h`
            is not positive.
        """
        if target_h <= 0:
            #  If `target_h <= 0`, it returns `img` unchanged.
            return img

        ratio = target_h / img.get_height()
        w = max(1, int(img.get_width() * ratio))

        return pygame.transform.smoothscale(img, (w, target_h))
