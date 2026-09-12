"""Asset-related exceptions for the Pac-Man UI layer."""

from __future__ import annotations

from pathlib import Path


class AssetError(Exception):
    """Base class for all asset-related errors.

    Attributes:
        message: User-friendly error message.
    """

    def __init__(self, message: str) -> None:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        return self.message


class AssetNotFoundError(AssetError):
    """Raised when a required asset file cannot be found or loaded."""

    def __init__(self, asset_path: str | Path) -> None:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        self.asset_path = asset_path
        super().__init__(
            f"[WARNING] Asset not found or unreadable: {asset_path}"
        )


class UnsupportedGlyphError(AssetError):
    """Raised when a requested font glyph is not available in the font."""

    def __init__(self, glyph: str, font_name: str = "") -> None:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        self.glyph = glyph
        self.font_name = font_name
        where = f" in font '{font_name}'" if font_name else ""
        super().__init__(
            f"[WARNING] Unsupported glyph '{glyph}'{where}"
        )
