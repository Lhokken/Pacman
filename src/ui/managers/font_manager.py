"""Manages loading and providing bitmap fonts for UI."""

from __future__ import annotations

from pathlib import Path

from ..components.bitmap_font import BitmapFont


class FontManager:
    """Creates and stores bitmap font instances with preset scales.

    Attributes:
        font_white: Base white font (scale 2.0) for general text.
        font_title_small: Yellow font (scale 2.0) for lives/fruit titles.
        font_title_big: Yellow font (scale 3.0) for score/highscore titles.
        font_value_med: White font (scale 2.5) for score/highscore values.
    """

    def __init__(self, assets_base: Path) -> None:
        """Initialize all fonts.

        Args:
            assets_base: Root path containing char/ directory.
        """
        # -----------------------------------------------------------------
        # Base white font for general text
        # -----------------------------------------------------------------
        self.font_white = BitmapFont(
            "bianco",
            assets_base,
            scale=2.0
        )
        # -----------------------------------------------------------------
        # Yellow small font for titles of lives/fruit panels
        # -----------------------------------------------------------------
        self.font_title_small = BitmapFont(
            "giallo",
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
        # Yellow big font for score/highscore titles
        # -----------------------------------------------------------------
        self.font_title_big = BitmapFont(
            "giallo",
            assets_base,
            scale=3.0
        )
        # -----------------------------------------------------------------
        # Yellow Extra font for score/highscore titles
        # -----------------------------------------------------------------
        self.font_title_extra = BitmapFont(
            "giallo",
            assets_base,
            scale=5.0
        )
