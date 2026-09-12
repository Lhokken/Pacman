"""Asset-related exceptions for the Pac-Man UI layer."""

from __future__ import annotations

from pathlib import Path


class CoreError(Exception):
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


class EntityError(CoreError):
    """Raised when a required asset file cannot be found or loaded."""

    def __init__(self, asset_path: str | Path) -> None:
        """Crea Titolo docstring.

        TODO: Inserisci descrizione.
        """
        self.asset_path = asset_path
        super().__init__(
            f"[WARNING] Entity Error: {asset_path}"
        )
