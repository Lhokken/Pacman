"""Side panel components for Pac-Man HUD."""

from __future__ import annotations

import logging
from pathlib import Path

import pygame
from pygame.surface import Surface

from .bitmap_font import BitmapFont
from ..managers.asset_exceptions import AssetNotFoundError

logger = logging.getLogger(__name__)


class Panel:
    """Base class for all side panels.

    A panel draws a title (potentially multi-line) and content using
    bitmap fonts. No background is drawn; the panel is transparent.

    Attributes:
        rect: The panel's rectangle on screen.
        title_lines: List of title text lines (displayed top to bottom).
        font: BitmapFont instance for rendering content text.
        title_font: BitmapFont instance for rendering title lines.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        title_lines: list[str],
        font: BitmapFont,
        title_font: BitmapFont,
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
        y_offset = self.rect.y + 5
        line_spacing = 4
        title_bottom = y_offset

        for line in self.title_lines:
            title_surface = self.title_font.render(line)
            title_rect = title_surface.get_rect(
                midtop=(self.rect.centerx, y_offset)
            )
            screen.blit(title_surface, title_rect)
            y_offset += title_rect.height + line_spacing
            title_bottom = title_rect.bottom
        # --------------------------------------------------------
        #   2. Content area starts below the title block
        # --------------------------------------------------------
        content_rect = pygame.Rect(
            self.rect.x,
            title_bottom + 10,
            self.rect.width,
            self.rect.height - (title_bottom - self.rect.y + 10),
        )
        self._draw_content(screen, content_rect)

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    def _draw_content(
        self, screen: Surface, content_rect: pygame.Rect
    ) -> None:
        """Draw the panel-specific content.

        Subclasses must override this method.

        Args:
            screen: The pygame surface to draw on.
            content_rect: Rectangle where content should be drawn.
        """
        # TODO: Connetti gli errori al Cli
        raise NotImplementedError


class ScorePanel(Panel):
    """Panel displaying the current score."""

    def __init__(
        self,
        rect: pygame.Rect,
        font_value: BitmapFont,
        font_title: BitmapFont,
    ) -> None:
        """Initialize the score panel.

        Args:
            rect: Rectangle for the panel.
            font_value: Font for the score value (white, medium).
            font_title: Font for the title lines (yellow, large).
        """
        super().__init__(
            rect, ["GAME", "SCORE"],
            font_value,
            font_title
        )
        self.score = 0

    # Pubblic Methods ---------------------------------------------------------
    # =========================================================================
    #   UPDATE
    # =========================================================================
    def update_score(self, score: int) -> None:
        """Update the displayed score."""
        self.score = score

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    def _draw_content(
        self, screen: Surface, content_rect: pygame.Rect
    ) -> None:
        """Draw the score number centered in the content area."""
        score_text = self.font.render(f"{self.score:06d}")
        score_rect = score_text.get_rect(center=content_rect.center)
        screen.blit(score_text, score_rect)


class LivesPanel(Panel):
    """Panel displaying remaining lives as Pac-Man icons."""

    def __init__(
        self,
        rect: pygame.Rect,
        font_white: BitmapFont,
        font_title_small: BitmapFont,
        pacman_icon_path: Path,
        icon_size: int = 24,
    ) -> None:
        """Initialize the lives panel.

        Args:
            rect: Rectangle for the panel.
            font_white: Font for the label.
            pacman_icon_path: Path to the Pac-Man icon image.
            icon_size: Size (width/height) of each icon.
        """
        super().__init__(
            rect, ["LIVES"],
            font_white,
            font_title_small
        )
        self.icon_size = icon_size
        self.lives = 3
        self.pacman_icon = self._load_icon(pacman_icon_path, icon_size)

    def _load_icon(self, path: Path, size: int) -> Surface:
        """Load and scale the Pac-Man icon.

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
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (size, size))
        except pygame.error as e:
            raise AssetNotFoundError(path) from e

    # Pubblic Methods ---------------------------------------------------------
    # =========================================================================
    #   UPDATE
    # =========================================================================
    def update_lives(self, lives: int) -> None:
        """Update the number of lives to display.

        Args:
            lives: Number of lives remaining.
        """
        self.lives = max(0, lives)

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    def _draw_content(
        self, screen: Surface, content_rect: pygame.Rect
    ) -> None:
        """Draw life icons in a row, centered."""
        total_width = self.lives * self.icon_size + (self.lives - 1) * 5
        start_x = content_rect.centerx - total_width // 2
        y = content_rect.centery - self.icon_size // 2

        for i in range(self.lives):
            x = start_x + i * (self.icon_size + 5)
            screen.blit(self.pacman_icon, (x, y))


class HighscorePanel(Panel):
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
        """Draw the highscore number centered."""
        score_text = self.font.render(f"{self.highscore:05d}")
        score_rect = score_text.get_rect(center=content_rect.center)
        screen.blit(score_text, score_rect)


class FruitPanel(Panel):
    """Panel displaying remaining fruit as repeated icons."""

    def __init__(
        self,
        rect: pygame.Rect,
        font_white: BitmapFont,
        font_title_small: BitmapFont,
        fruit_icon_path: Path,
        icon_size: int = 24,
        initial_count: int = 3,
    ) -> None:
        """Initialize the fruit panel.

        Args:
            rect: Rectangle for the panel.
            font_white: Font for label.
            fruit_icon_path: Path to the fruit icon image.
            icon_size: Size of the fruit icon.
            initial_count: Initial number of fruit icons to show.
        """
        super().__init__(
            rect,
            ["FRUIT"],
            font_white,
            font_title_small
        )
        self.icon_size = icon_size
        self.count = initial_count
        self.fruit_icon = self._load_icon(fruit_icon_path, icon_size)

    # Pubblic Methods ---------------------------------------------------------
    # =========================================================================
    #   UPDATE
    # =========================================================================
    def update_count(self, count: int) -> None:
        """Update the number of fruit icons to display.

        Args:
            count: Number of fruits remaining.
        """
        self.count = max(0, count)

    # Private Methods ---------------------------------------------------------
    # =========================================================================
    #   LOAD ICONS
    # =========================================================================
    def _load_icon(self, path: Path, size: int) -> Surface:
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
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (size, size))
        except pygame.error as e:
            raise AssetNotFoundError(path) from e

    # =========================================================================
    #   DRAW CONTENT
    # =========================================================================
    def _draw_content(
        self,
        screen: Surface,
        content_rect: pygame.Rect,
    ) -> None:
        """Draw fruit icons stacked vertically, centered."""
        # ----------------------------------------------------------------------
        #   1. Calculate vertical layout
        # ----------------------------------------------------------------------
        spacing = 5
        total_height = self.count * self.icon_size + (self.count - 1) * spacing
        start_y = content_rect.centery - total_height // 2
        x = content_rect.centerx - self.icon_size // 2

        for i in range(self.count):
            y = start_y + i * (self.icon_size + spacing)
            screen.blit(self.fruit_icon, (x, y))
