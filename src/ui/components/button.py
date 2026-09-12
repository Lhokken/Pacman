"""Reusable button component for menu and cheat page."""

from __future__ import annotations

import logging
from typing import Callable, Optional

import pygame
from pygame.surface import Surface

from src.ui.components.bitmap_font import BitmapFont

logger = logging.getLogger(__name__)


class Button:
    """Create a simple text button with selected state.

    The button does not draw a background; it only draws centered text
    using the provided bitmap font. This keeps it MLX-compatible
    (only blitting pre-rendered surfaces, no draw primitives).

    Attributes:
        rect: The clickable/hoverable area of the button.
        text: The label displayed on the button.
        font_normal: Font used when the button is not selected.
        font_selected: Font used when the button is selected.
        on_select: Optional callback invoked when the button is activated.
        selected: Boolean indicating whether the button is currently selected.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font_normal: BitmapFont,
        font_selected: BitmapFont,
        on_select: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize the button.

        Args:
            rect: Area of the button (used for centering text and hit tests).
            text: Label text.
            font_normal: Font for unselected state.
            font_selected: Font for selected state.
            on_select: Callback called when button is activated.
        """
        self.rect = rect
        self.text = text
        self.font_normal = font_normal
        self.font_selected = font_selected
        self.on_select = on_select
        self.selected = False

    def set_selected(self, selected: bool) -> None:
        """Set the selected state of the button."""
        self.selected = selected

    def set_text(self, text: str) -> None:
        """Update the button text."""
        self.text = text

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a single pygame event.

        If the button is selected and the Return key is pressed,
        the on_select callback is invoked (if defined).

        Returns:
            True if the event was consumed by the button, False otherwise.
        """
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.selected and self.on_select is not None:
                self.on_select()
                return True
        return False

    def draw(self, surface: Surface) -> None:
        """Draw the button text centered in its rectangle.

        Args:
            surface: The target pygame surface.
        """
        font = self.font_selected if self.selected else self.font_normal
        text_surface = font.render(self.text)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
