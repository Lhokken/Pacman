"""Bitmap font renderer using PNG sprite glyphs."""

from __future__ import annotations

import logging
import pygame

from pathlib import Path
from pygame.surface import Surface

from ..managers.asset_exceptions import (
    AssetNotFoundError,
    UnsupportedGlyphError,
)


logger = logging.getLogger(__name__)


class BitmapFont:
    """Renders text using pre-rendered PNG glyphs.

    Each glyph is a separate PNG file organized in directories by color
    and type (lettere/numeri/segni). The class supports uppercase,
    lowercase, digits, and a set of punctuation characters.

    Attributes:
        color_name: The color subfolder name ("bianco" or "giallo").
        char_width: Width of each glyph in pixels (after scaling).
        char_height: Height of each glyph in pixels (after scaling).
        scale: Scaling factor applied to all glyphs.
        _glyphs: Mapping from character to scaled Surface.
    """

    # ----------------------------------------------------------------------
    #   1. Mapping Files
    # ----------------------------------------------------------------------
    # Mapping of characters to their subfolder and base filename. ----------

    _CHAR_MAP: dict[str, tuple[str, str]] = {}

    for _ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
        _CHAR_MAP[_ch] = ("lettere", _ch.upper())

    for _d in "0123456789":
        _CHAR_MAP[_d] = ("numeri", _d)

    _CHAR_MAP.update(
        {
            "+": ("segni", "piu"),
            "-": ("segni", "meno"),
            ";": ("segni", "punto_virgola"),
            # "_": ("segni", "_"),
            "#": ("segni", "cancelletto"),
            "%": ("segni", "percentuale"),
            "!": ("segni", "punto_esclamativo"),
            "?": ("segni", "punto_interrgativo"),
            ".": ("segni", "punto"),
            ",": ("segni", "virgola"),
            ":": ("segni", "due_punti"),
        }
    )

    # Alternative filenames for characters where the base name is not found.
    _FILENAME_ALIASES: dict[str, list[str]] = {}

    def __init__(
        self,
        color_name: str,
        assets_base: Path,
        scale: float = 1.0,
        char_size: tuple[int, int] = (8, 8),
    ) -> None:
        """Initialize the font and load glyphs.

        Args:
            color_name: "bianco" or "giallo" (subfolder under char/).
            assets_base: Root path containing char/ directory.
            scale: Scaling factor (1.0 = original size).
            char_size: Expected size (width, height) of each glyph file.
                Used to validate and scale if necessary.
        """
        self.color_name = color_name
        self.scale = scale
        self.char_width = int(char_size[0] * scale)
        self.char_height = int(char_size[1] * scale)
        self._glyphs: dict[str, Surface] = {}
        self._load_glyphs(assets_base)

    # Pubblic Methods ---------------------------------------------------------
    # =========================================================================
    #   RENDER
    # =========================================================================
    def render(self, text: str) -> pygame.Surface:
        """Render a string into a single transparent surface.

        Args:
            text: String to render.

        Returns:
            A pygame Surface with the text drawn left-to-right.
        """
        # Commento logica -------------------------------------------------
        # TODO: validate that text is a string before calling len().
        glyph_width = self.char_width
        glyph_height = self.char_height
        # TODO: handle pygame.error and MemoryError if surface allocation
        # fails.
        surface = pygame.Surface(
            (len(text) * glyph_width, glyph_height), pygame.SRCALPHA
        )
        x_offset = 0
        for char in text:
            if char == " ":
                x_offset += glyph_width
                continue
            glyph = self._glyphs.get(char)
            if not glyph:
                raise UnsupportedGlyphError(
                    f"Unsupported glyph: {char!r}"
                )
            try:
                surface.blit(glyph, (x_offset, 0))
                x_offset += glyph_width
            except pygame.error:
                raise UnsupportedGlyphError(
                    f"Failed to render glyph: {char!r}"
                )
        return surface

    # =========================================================================
    #   SIZE
    # =========================================================================
    def get_text_size(self, text: str) -> tuple[int, int]:
        """Return the pixel size of the rendered text.

        Args:
            text: String to measure.

        Returns:
            Width and height of the rendered string.
        """
        return (len(text) * self.char_width, self.char_height)

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   LOAD
    # =========================================================================
    def _load_glyphs(self, assets_base: Path) -> None:
        """Load all needed glyphs from the asset directory tree.

        Args:
            assets_base: Root path containing char/ directory.
        """
        base = assets_base / "char" / self.color_name
        # ---------------------------------------------------------------------
        # commento logica
        # ---------------------------------------------------------------------
        for char, (subdir, base_filename) in self._CHAR_MAP.items():
            # space (handled separately) --------------------------------------
            if subdir is None:
                continue
            # Commento logica -------------------------------------------------
            candidate_filenames = [base_filename] + self._FILENAME_ALIASES.get(
                char, []
            )
            glyph: Surface | None = None
            for filename in candidate_filenames:
                for ext in (
                    ".png",
                    ".png.png",
                ):
                    path = base / subdir / f"{filename}{ext}"
                    # TODO: handle OSError raised by exists() on inaccessible
                    # paths.
                    if path.exists():
                        try:
                            img = pygame.image.load(path).convert_alpha()
                            if img.get_size() != (
                                self.char_width,
                                self.char_height,
                            ):
                                img = pygame.transform.scale(
                                    img,
                                    (self.char_width, self.char_height),
                                )
                            glyph = img
                            break
                        # TODO: include OSError and MemoryError for filesystem
                        # and allocation failures.
                        except (pygame.error, OSError, MemoryError) as e:
                            raise UnsupportedGlyphError(
                                f"Failed to load glyph {path}: {e}"
                            ) from e
                if glyph is not None:
                    break
            # Commento logica -------------------------------------------------
            if not glyph:
                # TODO: report the missing character and all paths attempted.
                raise UnsupportedGlyphError(
                    f"Unsupported glyph: {char!r}"
                )
            try:
                self._glyphs[char] = glyph
            except pygame.error as e:
                raise AssetNotFoundError(path) from e
