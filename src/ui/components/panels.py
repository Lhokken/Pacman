"""Side panel components for Pac-Man HUD."""

from __future__ import annotations

import logging

from abc import ABC, abstractmethod
from pathlib import Path

from typing import cast

import pygame
from pygame.surface import Surface

from .bitmap_font import BitmapFont
from ..managers.asset_exceptions import AssetNotFoundError

logger = logging.getLogger(__name__)


# ======================================================================
#   BASE
# ======================================================================
class Panel(ABC):
    """Base class for all side panels.

    A panel draws a title (potentially multi-line) and content using
    bitmap fonts. No background is drawn; the panel is transparent.
    """

    TITLE_MARGIN = 5
    TITLE_SPACING = 4
    TITLE_GAP = 14

    def __init__(
        self,
        rect: pygame.Rect,
        title_lines: list[str],
        font: BitmapFont,
        title_font: BitmapFont,
        align_x: str = "center",
    ) -> None:
        """Initialize the panel.

        Args:
            rect: Rectangle defining the panel area.
            title_lines: List of strings for the title (each on new line).
            font: Font used for content.
            title_font: Font used for title lines.
        """
        self.rect = rect
        self.title_lines = title_lines
        self.font = font
        self.title_font = title_font
        self.align_x = align_x

    # Pubblic Methods ---------------------------------------------------------
    # =========================================================================
    #   UPDATE
    # =========================================================================
    def draw(self, screen: Surface) -> None:
        """Draw the panel title and content (no background).

        Args:
            screen: The pygame surface to draw on.
        """
        # --------------------------------------------------------
        #   1. Draw each title line centered horizontally, from top
        # --------------------------------------------------------
        y_offset = self.rect.y + self.TITLE_MARGIN
        title_bottom = y_offset
        ancora_x, ancora_kw = self._title_ancora()

        for line in self.title_lines:
            title_surface = self.title_font.render(line)
            title_rect = title_surface.get_rect(
                **{ancora_kw: (ancora_x, y_offset)}
            )
            screen.blit(title_surface, title_rect)
            y_offset += title_rect.height + self.TITLE_SPACING
            title_bottom = title_rect.bottom

        # --------------------------------------------------------
        #   2. Content area starts below the title block
        # --------------------------------------------------------
        title_top = title_bottom + self.TITLE_GAP
        content_rect = pygame.Rect(
            self.rect.x,
            title_top,
            self.rect.width,
            self.rect.height - (title_top - self.rect.y),
        )
        self._draw_content(screen, content_rect)

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   ANCORE
    # =========================================================================
    def _title_ancora(self) -> tuple[int, str]:
        """Identify direction."""
        if self.align_x == "right":
            return self.rect.right, "topright"
        if self.align_x == "left":
            return self.rect.left, "topleft"
        return self.rect.centerx, "midtop"

    def _contenuto_ancora(
        self, contenuto_rect: pygame.Rect
    ) -> tuple[int, str]:
        """Identify content."""
        if self.align_x == "right":
            return contenuto_rect.right, "midright"
        if self.align_x == "left":
            return contenuto_rect.left, "midleft"
        return self.rect.centerx, "center"

    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    @abstractmethod
    def _draw_content(
        self, screen: Surface, content_rect: pygame.Rect
    ) -> None:
        """Draw the panel-specific content."""
        ...

    # =========================================================================
    #   CARICAMENTO
    # =========================================================================
    @staticmethod
    def _load_icon(path: Path, size: int) -> Surface:
        """Load and scale the icon.

        Args:
            path: Path to the icon file.
            size: Desired size in pixels.

        Returns:
            Scaled surface.

        Raises:
            AssetNotFoundError: If the icon file is missing or cannot be
                                loaded.
        """
        if not path.exists():
            raise AssetNotFoundError(path)
        try:
            img_icon = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img_icon, (size, size))
        except pygame.error as e:
            raise AssetNotFoundError(path) from e

    @staticmethod
    def _load_png(path: Path) -> Surface:
        """Load and scale the fruit icon.

        Args:
            path: Path to the icon file.
            size: Desired size in pixels.

        Returns:
            Scaled surface.

        Raises:
            AssetNotFoundError: If the icon file is missing or cannot be
                                loaded.
        """
        if not path.exists():
            raise AssetNotFoundError(path)
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            raise AssetNotFoundError(path) from e


# ======================================================================
#   VALUE PANNELS: titolo + valore score
# ======================================================================
class ValuePanel(Panel, ABC):
    """Panel displaying the current score.

    Multi-line title and columnar values.
    The value is anchored immediately below the score title,
    not centered vertically, so it stays close to the title.
    """

    VALORE_POSTAZIONI: int = 0
    VALORE_INIZIALE: int = 0

    def __init__(
        self,
        rect: pygame.Rect,
        title_lines: list[str],
        font_value: BitmapFont,
        font_title: BitmapFont,
        align_x: str = "center"
    ) -> None:
        """Initialize the score panel.

        Args:
            rect: Rectangle for the panel.
            title_lines: stringa per titolo,
            font_value: Font for the score value (white, medium).
            font_title: Font for the title lines (yellow, large).
            align_x: Valore centrato
        """
        super().__init__(
            rect,
            title_lines,
            font_value,
            font_title,
            align_x,
        )
        self.value = self.VALORE_INIZIALE

    # Pubblic Methods ---------------------------------------------------------
    # =========================================================================
    #   UPDATE
    # =========================================================================
    def update_value(self, value: int) -> None:
        """Update the displayed score."""
        self.value = value

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    def _draw_content(
        self, screen: Surface, content_rect: pygame.Rect
    ) -> None:
        """Draw the score number centered in the content area."""
        text = self.font.render(self._format_value())
        ancora, kw = self._contenuto_ancora(content_rect)

        # ANCORAGGIO TOP del content_rect: Titolo non centrato verticalmente
        if kw == "midright":
            rect = text.get_rect(
                topright=(ancora, content_rect.top)
            )
        elif kw == "midleft":
            rect = text.get_rect(
                topleft=(ancora, content_rect.top)
            )
        else:
            rect = text.get_rect(
                midtop=(ancora, content_rect.top)
            )
        screen.blit(text, rect)

    def _format_value(self) -> str:
        """Return the panel value formatted with the configured width."""
        if self.VALORE_POSTAZIONI <= 0:
            return str(self.value)
        return f"{self.value:0{self.VALORE_POSTAZIONI}d}"


class ScorePanel(ValuePanel):
    """Panel displaying the current score."""

    VALORE_POSTAZIONI: int = 6

    def __init__(
        self,
        rect: pygame.Rect,
        font_value: BitmapFont,
        font_title: BitmapFont,
    ) -> None:
        """Display Game Score."""
        super().__init__(
            rect,
            ["GAME", "SCORE"],
            font_value,
            font_title,
        )


class HighscorePanel(ValuePanel):
    """Panel displaying the high score."""

    def __init__(
        self,
        rect: pygame.Rect,
        font_value: BitmapFont,
        font_title: BitmapFont,
    ) -> None:
        """Initialize the highscore panel.

        Args:
            rect: Rectangle for the panel.
            font_value: Font for the highscore value (white, medium).
            font_title: Font for the title lines (yellow, large).
        """
        super().__init__(
            rect,
            ["HIGH", "SCORE"],
            font_value,
            font_title
        )
        self.highscore = 0

    # Pubblic Methods ---------------------------------------------------------
    # =========================================================================
    #   UPDATE
    # =========================================================================
    def update_highscore(self, highscore: int) -> None:
        """Update the displayed high score."""
        self.highscore = highscore

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    def _draw_content(
        self, screen: Surface, content_rect: pygame.Rect
    ) -> None:
        """Draw the highscore number below its title."""
        score_text = self.font.render(f"{self.highscore:05d}")
        ancora, kw = self._contenuto_ancora(content_rect)

        if kw == "midright":
            score_rect = score_text.get_rect(
                topright=(ancora, content_rect.top)
            )
        elif kw == "midleft":
            score_rect = score_text.get_rect(
                topleft=(ancora, content_rect.top)
            )
        else:
            score_rect = score_text.get_rect(
                midtop=(ancora, content_rect.top)
            )
        screen.blit(score_text, score_rect)


# ======================================================================
#   PANNELLI ICONE
# ======================================================================
class IconStripPanel(Panel, ABC):
    """Icon display."""

    DIR_ORIZZONTALE = "h"
    DIR_VERTICALE = "v"
    DIREZIONE: str = DIR_ORIZZONTALE
    ICON_SPACING = 5

    def __init__(
        self,
        rect: pygame.Rect,
        title_lines: list[str],
        font: BitmapFont,
        font_title: BitmapFont,
        icon_path: Path,
        icon_size: int,
        count_init: int,
        align_x: str = "center"
    ) -> None:
        """Initialize the Icon Stirp Pannel."""
        super().__init__(
            rect,
            title_lines,
            font,
            font_title,
            align_x,
        )
        self.icon_size = icon_size
        self.count = max(0, count_init)
        self._icon_path = icon_path
        self.icon = self._load_icon(icon_path, icon_size)

    # Pubblic Methods ---------------------------------------------------------
    # =========================================================================
    #   UPDATE
    # =========================================================================
    def update_count(self, count: int) -> None:
        """Update the displayed score."""
        self.count = max(0, count)

    # =========================================================================
    #   ICON SIZE
    # =========================================================================
    def set_icon_size(self, size: int) -> None:
        """Set the icon size."""
        if size == self.icon_size:
            return
        self.icon_size = size
        self.icon = self._load_icon(self._icon_path, size)

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    def _draw_content(
        self, screen: Surface, content_rect: pygame.Rect
    ) -> None:
        """Draw the score number centered in the content area."""
        if self.count <= 0:
            return

        step = self.icon_size + self.ICON_SPACING
        span = (
            self.count * self.icon_size
            + (self.count - 1) * self.icon_size
        )

        # ANCORAGGIO BOTTOM, del content_rect ---------------------------------
        if self.DIREZIONE == self.DIR_ORIZZONTALE:
            ancora, kw = self._contenuto_ancora(content_rect)
            if kw == "midright":
                start_x = ancora - span
            elif kw == "midleft":
                start_x = ancora
            else:
                start_x = ancora - span // 2
            y = content_rect.bottom - self.icon_size
            for i in range(self.count):
                screen.blit(self.icon, (start_x + i * step, y))
        else:
            x = content_rect.centerx - self.icon_size // 2
            start_y = content_rect.top
            for i in range(self.count):
                screen.blit(self.icon, (x, start_y + i * step))


class LivesPanel(IconStripPanel):
    """Panel displaying remaining lives as Pac-Man icons."""

    DIREZIONE = IconStripPanel.DIR_ORIZZONTALE

    def __init__(
        self,
        rect: pygame.Rect,
        font_white: BitmapFont,
        font_title_small: BitmapFont,
        pacman_icon_path: Path,
        icon_size: int = 24
    ) -> None:
        """Initialize the lives panel.

        Args:
            rect: Rectangle for the panel.
            font_white: Font for the label.
            pacman_icon_path: Path to the Pac-Man icon image.
            icon_size: Size (width/height) of each icon.
        """
        super().__init__(
            rect, [""],
            font_white,
            font_title_small,
            pacman_icon_path,
            icon_size,
            count_init=3,
        )


# ======================================================================
#   PANNELLI IMMAGINI
# ======================================================================
class ImagePanel(Panel, ABC):
    """Panel displaying con logo."""

    MAX_WIDHT_RATIO = 0.85
    MAX_HEIGHT_RATIO = 0.75

    ANCORA_CENTER = "center"
    ANCORA_BOTTOM = "botton"
    ANCORA = ANCORA_CENTER

    OFFSET_X: int = 0

    def __init__(
        self,
        rect: pygame.Rect,
        title_line: list[str],
        font: BitmapFont,
        title_font: BitmapFont,
        img_path: Path,
        align_x: str = "center"
    ) -> None:
        """Initialize the logo panel."""
        super().__init__(
            rect,
            title_line,
            font,
            title_font,
            align_x,
        )
        self._image = self._load_png(img_path)

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    def _draw_content(
        self, screen: Surface, content_rect: pygame.Rect
    ) -> None:
        """Draw the fitted image inside the panel content rectangle."""
        if self._image is None:
            return

        max_w = int(content_rect.width * self.MAX_WIDHT_RATIO)
        max_h = int(content_rect.height * self.MAX_HEIGHT_RATIO)
        img = self._fit(self._image, max_w, max_h)

        rect = self._place_image(img, content_rect)

        screen.blit(img, rect)

    # PLACE IMAGE ---------------------------------------------------------
    def _place_image(
        self, img: Surface, content_rect: pygame.Rect
    ) -> pygame.Rect:
        """Combina ANCHOR verticale e align_x orizzontale."""
        kwargs: dict = {}

        if self.ANCORA == self.ANCORA_BOTTOM:
            kwargs["bottom"] = content_rect.bottom

        if self.align_x == "left":
            kwargs["left"] = content_rect.left
        elif self.align_x == "right":
            kwargs["right"] = content_rect.right

        # Se non ho messo né bottom né left/right, get_rect usa (0,0):
        # forzo il centro.
        if not kwargs:
            kwargs["center"] = content_rect.center
        elif (
            "bottom" in kwargs and (
                "left" not in kwargs and "right" not in kwargs
            )
        ):
            # Solo bottom: centra orizzontalmente.
            kwargs["centerx"] = content_rect.centerx
        elif (
            "bottom" not in kwargs and (
                "left" in kwargs or "right" in kwargs
            )
        ):
            # Solo left/right: centra verticalmente.
            kwargs["centery"] = content_rect.centery
        rect = cast(pygame.Rect, img.get_rect(**kwargs))

        if self.OFFSET_X:
            rect.x += self.OFFSET_X
        return rect

    # FIT IMAGE -----------------------------------------------------------
    def _fit(
        self,
        img: Surface,
        max_widht: int,
        max_height: int,
    ) -> Surface:
        """Fit the img. TODO: docstring."""
        scale = min(
            max_widht / img.get_width(),
            max_height / img.get_height(),
            1.0,
        )

        if scale >= 1.0:
            return img

        size = (
            max(1, int(img.get_width() * scale)),
            max(1, int(img.get_height() * scale)),
        )
        return pygame.transform.smoothscale(img, size)


class LogoPanel(ImagePanel):
    """Anchored to the bottom.

    Both anchored to the bottom of the content_rect. `OFFSET_X` shifts
    the logo (and caption) a few pixels to compensate for the asset's
    asymmetrical padding.
    """

    # ==============================================================
    #   Variabili grafiche
    # ==============================================================
    ANCHOR = ImagePanel.ANCORA_BOTTOM
    OFFSET_X = 0                       # Rule for centering
    CAPTION = "SCHOOL"                 # Caption logo
    CAPTION_GAP = 4                    # px between logo and caption

    def __init__(
        self,
        rect: pygame.Rect,
        font: BitmapFont,
        title_font: BitmapFont,
        logo_path: Path,
    ) -> None:
        """Fa TODO: docstring."""
        super().__init__(
            rect,
            [],
            font,
            title_font,
            logo_path
        )

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    def _draw_content(
        self, screen: Surface, content_rect: pygame.Rect
    ) -> None:
        """Logo ancorato al fondo, con 'SCHOOL' sotto.

        Non usa `_place_image`: il layout è custom (logo + caption
        incolonnati e ancorati al fondo).
        """
        if self._image is None:
            return

        # Caption renderizzata con `font` (font_white passato dal
        # PanelManager).
        cap_surf = self.font.render(self.CAPTION)
        cap_h = cap_surf.get_height()

        # Caption: appoggiata al fondo. -------------------------
        cap_rect = cap_surf.get_rect(
            midbottom=(
                content_rect.centerx, content_rect.bottom
            )
        )
        if self.OFFSET_X:
            cap_rect.x += self.OFFSET_X

        screen.blit(cap_surf, cap_rect)
        # --------------------------------------------------------
        # Logo: area sopra la caption.
        # --------------------------------------------------------
        img_bottom = (
            content_rect.bottom - cap_h - self.CAPTION_GAP
        )
        img_area_h = img_bottom - content_rect.top

        if img_area_h <= 0:
            return

        max_w = int(content_rect.width * self.MAX_WIDHT_RATIO)
        max_h = int(img_area_h * self.MAX_HEIGHT_RATIO)
        img = self._fit(self._image, max_w, max_h)

        img_rect = img.get_rect(
            midbottom=(content_rect.centerx, img_bottom)
        )
        if self.OFFSET_X:
            img_rect.x += self.OFFSET_X
        screen.blit(img, img_rect)
