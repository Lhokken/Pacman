"""Asset-related exceptions for the Pac-Man UI layer."""

from __future__ import annotations

from pathlib import Path


class CoreError(Exception):
    """Base class for all asset-related errors.

    Attributes:
        message: User-friendly error message.
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


class EntityError(CoreError):
    """Raised when a required asset file cannot be found or loaded."""

    def __init__(self, asset_path: str | Path) -> None:
        """Initialize an error for an entity asset path.

        Args:
            asset_path : Path associated with the entity error.
        """
        self.asset_path = asset_path
        super().__init__(
            f"[WARNING] Entity Error: {asset_path}"
        )
