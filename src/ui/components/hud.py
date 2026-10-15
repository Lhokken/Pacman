"""Render the in-game level indicator and remaining-time HUD.

The HUD uses pre-rendered bitmap glyphs rather than TTF fonts or drawing
primitives. Its timer is provided by the caller and uses a monotonic clock.
"""

from __future__ import annotations

from pygame.surface import Surface

from .bitmap_font import BitmapFont
from ...core.timer import Timer


class HUD:
    """Displays the current level and remaining time of a `Timer`.

    Attributes:
        font_title : BitmapFont for the "TIME" label.
        font_value : BitmapFont for the numeric value.
        timer      : The Timer to display.
    """

    MARGIN_PX = 10
    LABEL_VALUE_GAP_PX = 12

    def __init__(
        self,
        font_title: BitmapFont,
        font_value: BitmapFont,
        timer: Timer,
        current_level: int = 1,
    ) -> None:
        """Initialize the HUD.

        Args:
            font_title    : Font for the label.
            font_value    : Font for the numerical value.
            timer         : The Timer to display. The HUD does not modify it.
            current_level : One-based level number to display.
        """
        self.font_title = font_title
        self.font_value = font_value
        self.timer = timer
        self.current_level = current_level

    # Pubblic ----------------------------------------------------------
    def set_level(self, current_level: int) -> None:
        """Update the one-based level number shown in the HUD."""
        self.current_level = current_level

    # ==================================================================
    #   Rendering
    # ==================================================================
    def draw(self, screen: Surface) -> None:
        """Draw 'LEVEL n TIME M:SS' centered at the top of the screen."""
        # label level---------------------------------------------------
        level_label = self.font_title.render("LEVEL")
        level_value = self.font_value.render(str(self.current_level))
        # label value ---------------------------------------------------=
        time_label = self.font_title.render("TIME")
        time_value = self.font_value.render(self._format_remaining())

        gap = self.LABEL_VALUE_GAP_PX
        section_gap = self.LABEL_VALUE_GAP_PX * 3
        total_w = (
            level_label.get_width() + gap + level_value.get_width()
            + section_gap + time_label.get_width() + gap
            + time_value.get_width()
        )
        total_h = max(
            level_label.get_height(),
            level_value.get_height(),
            time_label.get_height(),
            time_value.get_height(),
        )

        x0 = (screen.get_width() - total_w) // 2
        y0 = self.MARGIN_PX
        items = (
            (level_label, x0),
            (level_value, x0 + level_label.get_width() + gap),
            (
                time_label,
                x0 + level_label.get_width() + gap
                + level_value.get_width() + section_gap,
            ),
            (
                time_value,
                x0 + level_label.get_width() + gap
                + level_value.get_width() + section_gap
                + time_label.get_width() + gap,
            ),
        )
        for surface, x in items:
            screen.blit(
                surface,
                (x, y0 + (total_h - surface.get_height()) // 2),
            )

    # Private ----------------------------------------------------------
    # ==================================================================
    #   FORMAT
    # ==================================================================
    def _format_remaining(self) -> str:
        """Use the Format the remaining time as M:SS."""
        total = int(self.timer.remaining)
        minutes, seconds = divmod(total, 60)
        return f"{minutes}:{seconds:02d}"
