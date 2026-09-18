"""In-Game HUD: tempo rimanente per il livello corrente.

Requisiti di progetto (MLX-compliance):
    - Nessun uso di pygame.font.Font, pygame.draw, o altre primitive
      che MLX non offre. Solo blit di superfici pre-renderizzate
      tramite BitmapFont.
    - Il tempo è calcolato in Python puro (time.monotonic), non via
      pygame.time: stesso approccio della guida (gettimeofday in C).

L'HUD non possiede il timer: lo riceve dal chiamante (GamePage) e
lo renderizza. Pausa e resume del timer sono responsabilità della Page.
"""

from __future__ import annotations

from pygame.surface import Surface

from .bitmap_font import BitmapFont
from ...core.timer import Timer


class HUD:
    """Displays the remaining time of a `Timer`.

    Attributes:
        font_title: BitmapFont for the "TIME" label.
        font_value: BitmapFont for the numeric value.
        timer: The Timer to display.
    """

    MARGIN_PX = 10
    LABEL_VALUE_GAP_PX = 8

    def __init__(
        self,
        font_title: BitmapFont,
        font_value: BitmapFont,
        timer: Timer,
    ) -> None:
        """Initialize the HUD..

        Args:
            font_title: Font for the label.
            font_value: Font for the numerical value.
            timer: The Timer to display. The HUD does not modify it.
        """
        self.font_title = font_title
        self.font_value = font_value
        self.timer = timer

    # ==================================================================
    #   Rendering
    # ==================================================================
    def draw(self, screen: Surface) -> None:
        """Draw 'TIME M:SS' centered at the top of the screen."""
        label = self.font_title.render("TIME")
        value = self.font_value.render(self._format_remaining())

        gap = self.LABEL_VALUE_GAP_PX
        total_w = label.get_width() + gap + value.get_width()
        total_h = max(label.get_height(), value.get_height())

        x0 = (screen.get_width() - total_w) // 2
        y0 = self.MARGIN_PX

        screen.blit(
            label,
            (
                x0,
                y0 + (total_h - label.get_height()) // 2
            ),
        )
        screen.blit(
            value,
            (
                x0 + label.get_width() + gap,
                y0 + (total_h - value.get_height()) // 2,
            ),
        )

    # ==================================================================
    #   Interni
    # ==================================================================
    def _format_remaining(self) -> str:
        """Use the Format the remaining time as M:SS."""
        total = int(self.timer.remaining)
        minutes, seconds = divmod(total, 60)
        return f"{minutes}:{seconds:02d}"
