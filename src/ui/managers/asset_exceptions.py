"""Asset-related exceptions for the Pac-Man UI layer."""

from __future__ import annotations

from pathlib import Path


class AssetError(Exception):
    """Base class for all asset-related errors.

    Attributes:
        message : User-friendly error message.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a user-facing message.

        Args:
            message : Error message suitable for logging or display.
        """
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """Return the user-facing error message."""
        return self.message


class AssetNotFoundError(AssetError):
    """Raised when a required asset file cannot be found or loaded."""

    def __init__(self, asset_path: str | Path) -> None:
        """Initialize an error for a missing or unreadable asset.

        Args:
            asset_path: Path to the asset that could not be loaded.
        """
        self.asset_path = asset_path
        super().__init__(
            f"Asset not found or unreadable: {asset_path}"
        )


class UnsupportedGlyphError(AssetError):
    """Raised when a requested font glyph is not available in the font."""

    def __init__(self, glyph: str, font_name: str = "") -> None:
        """Initialize an error for an unsupported bitmap glyph.

        Args:
            glyph     : Character unavailable in the selected font.
            font_name : Optional name of the font that lacks the glyph.
        """
        self.glyph = glyph
        self.font_name = font_name
        where = f" in font '{font_name}'" if font_name else ""
        super().__init__(
            f"[WARNING] Unsupported glyph '{glyph}'{where}"
        )


class MissingRequiredAssetsError(AssetError):
    """Raised when one or more required rendering assets are missing.

    Attributes:
        missing: List of human-readable descriptions of missing assets.
    """

    def __init__(self, missing: list[str]) -> None:
        """Initialize the exception.

        Args:
            missing: List of descriptions of the missing assets,
                e.g. ``["wall masks [0, 1]", "border tiles ['top']"]``.
        """
        self.missing = missing
        details = "; ".join(missing) if missing else "unknown assets"
        super().__init__(
            f"Missing required rendering assets: {details}"
        )
