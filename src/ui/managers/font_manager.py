"""Manages loading and providing bitmap fonts for UI."""

from __future__ import annotations

from pathlib import Path

from ..components.bitmap_font import BitmapFont


class FontManager:
    """Stores the ready-to-use bitmap fonts for the UI.

    The manager creates a consistent set of preset font instances in white and
    yellow, each with a fixed scale suited for labels, values, and headings in
    the game screens.

    Attributes:
        font_white: Standard white font used for general text.
        font_value_med: White font used for medium-sized numeric values.
        font_value_big: White font used for large values.
        font_title_small: Yellow font used for smaller titles.
        font_value_med_y: Yellow font used for medium-sized values.
        font_title_big: Yellow font used for larger titles.
        font_title_extra: Yellow font used for emphasized headings.
        font_title_extraLarge: Yellow font used for very large headings.
    """

    def __init__(self, assets_base: Path) -> None:
        """Initialize all fonts.

        Args:
            assets_base: Root path containing char/ directory.
        """
        # TODO: VERIFICARE che tutti i font sono stati usati, delete if not
        # =================================================================
        #   FONT BIANCO
        # =================================================================

        # -----------------------------------------------------------------
        # Base white font for general text
        # -----------------------------------------------------------------
        self.font_white = BitmapFont(
            "bianco",
            assets_base,
            scale=2.0
        )
        # -----------------------------------------------------------------
        # White medium font for score/highscore values
        # -----------------------------------------------------------------
        self.font_value_med = BitmapFont(
            "bianco",
            assets_base,
            scale=2.5
        )
        # -----------------------------------------------------------------
        #   White big font
        # -----------------------------------------------------------------
        self.font_value_big = BitmapFont(
            "bianco",
            assets_base,
            scale=3.5
        )
        # =================================================================
        #   FONT GIALLO
        # =================================================================
        # -----------------------------------------------------------------
        # Yellow small font for titles of lives/fruit panels
        # -----------------------------------------------------------------
        self.font_title_small = BitmapFont(
            "giallo",
            assets_base,
            scale=2.0
        )
        # -----------------------------------------------------------------
        #   Yellow medium font for score/highscore values
        # -----------------------------------------------------------------
        self.font_value_med_y = BitmapFont(
            "giallo",
            assets_base,
            scale=2.5
        )
        # -----------------------------------------------------------------
        #   Yellow big font
        # -----------------------------------------------------------------
        self.font_title_big = BitmapFont(
            "giallo",
            assets_base,
            scale=3.0
        )
        # -----------------------------------------------------------------
        #   Yellow Extra
        # -----------------------------------------------------------------
        self.font_title_extra = BitmapFont(
            "giallo",
            assets_base,
            scale=5.0
        )
        # -----------------------------------------------------------------
        #   Yellow ExtraLarge
        # -----------------------------------------------------------------
        self.font_title_extraLarge = BitmapFont(
            "giallo",
            assets_base,
            scale=10.0
        )
