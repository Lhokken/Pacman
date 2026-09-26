"""Centralized UI configuration.

Palette
    Define application's app colors.
FontRole
    Define semantic enum of typographic roles.
Theme
    Resolves a FontRole via a FontManager and
    exposes the palette as a single access point.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ..managers.font_manager import FontManager
    from ..components.bitmap_font import BitmapFont


# ======================================================================
#   Interface UI - Palette
# ======================================================================
class Palette:
    """Ccontains the color palette shared by all scenes.

    Class containing only constants: not to be instantiated.
    """

    # DARK COLOR - Terminal color --------------------------------------
    DARK: tuple[int, int, int] = (20, 20, 30)
    # BALCK COLOR ------------------------------------------------------
    BLACK: tuple[int, int, int] = (0, 0, 0)
    # DARK COLOR OVERLAY - with a transparent layer --------------------
    OVERLAY_RGBA: tuple[int, int, int, int] = (20, 20, 30, 180)

    def __new__(
        cls, *_: object, **__: object
    ) -> "Palette":
        """Prevents the instantiation of Class `Palette`.

        Raises:
            TypeError: If an attempt is made to instantiate `Palette`.
        """
        raise TypeError(
            "Palette is a class containing only constants; "
            "do not instantiate it."
        )


# ======================================================================
#   Interface UI - Typographic roles
# ======================================================================
class FontRole(str, Enum):
    """Ruoli semantici dei font.

    Il valore di ogni membro è il nome dell'attributo su `FontManager`.
    """

    SCREEN_TITLE = "font_title_extraLarge"                      # 10.0
    HEADING = "font_title_extra"                                # 5.0
    SECTION_TITLE = "font_title_big"                            # 3.0
    VALUE_BIG = "font_value_big"                                # 3.5
    OPTION = "font_value_med"                                   # 2.5
    OPTION_SELECTED = "font_value_med_y"                        # 2.5
    SMALL = "font_white"                                        # 2.0


# ======================================================================
#   Interface UI - THEMES
# ======================================================================
class Theme:
    """Controls the interface for accessing fonts and palettes.

    It resolves a `FontRole` via a `FontManager` and exposes the palette
    as a single point of access. Scenes receive a `Theme`, so they never
    need to know the attribute name used in the `FontManager` or the color
    tuples.
    """

    # ------------------------------------------------------------------
    #   Referencing the palette as a class attribute.
    # ------------------------------------------------------------------
    #  Usage :
    # `self.theme.palette.DARK` without importing Palette on every page.
    palette = Palette

    def __init__(self, fonts: FontManager) -> None:
        """Check and initializes the typeface using the font manager.

        Arguments:
            fonts: The font manager from which to resolve roles.
        """
        self._fonts = fonts

    def font_config(self, role: FontRole) -> BitmapFont:
        """Return the `BitmapFont` associated with the role.

        Args:
            role: The typographic role to resolve.

        Returns:
            The font corresponding to the role.
        """
        return cast(
            "BitmapFont", getattr(self._fonts, role.value)
        )

    def __getitem__(self, role: FontRole) -> BitmapFont:
        """Allow access to fonts by index.

        Args:
          role: The typographic role to resolve.

        Returns:
          The font corresponding to the role.
        """
        return self.font_config(role)
