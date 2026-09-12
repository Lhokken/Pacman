"""In-Game HUD for Pac-Man.

Displays current score, remaining lives, current level, and remaining
time per level, as specified in VI.8 User Interface.
"""

from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ui.app import GameApp


class HUD:
    """Heads-up display showing game state during gameplay.

    Attributes:
        app: The parent GameApp instance.
        font: The pygame font used for rendering text.
        padding: Space between HUD elements.
    """

    def __init__(self, app: GameApp) -> None:
        """Initialize the HUD.

        Args:
            app: The parent GameApp instance.
        """
        self.app = app
        self.font = pygame.font.Font(None, 24)
        self.padding = 10

    def draw(
        self,
        screen: pygame.Surface,
        score: int,
        lives: int,
        level: int,
        time_remaining: float,
    ) -> None:
        """Draw the HUD on the screen.

        Args:
            screen: The pygame surface to draw on.
            score: Current player score.
            lives: Remaining lives.
            level: Current level number.
            time_remaining: Remaining time in seconds.
        """
        # ----------------------------------------------------------------------
        # Score (top-left)
        # ----------------------------------------------------------------------
        score_text = self.font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (self.padding, self.padding))

        # ----------------------------------------------------------------------
        # Lives (top-right)
        # ----------------------------------------------------------------------
        lives_text = self.font.render(f"Lives: {lives}", True, (255, 255, 255))
        lives_rect = lives_text.get_rect(
            topright=(screen.get_width() - self.padding, self.padding)
        )
        screen.blit(lives_text, lives_rect)

        # ----------------------------------------------------------------------
        # Level (bottom-left)
        # ----------------------------------------------------------------------
        level_text = self.font.render(f"Level: {level}", True, (255, 255, 255))
        level_rect = level_text.get_rect(
            bottomleft=(self.padding, screen.get_height() - self.padding)
        )
        screen.blit(level_text, level_rect)

        # ----------------------------------------------------------------------
        # Time remaining (bottom-right)
        # ----------------------------------------------------------------------
        time_text = self.font.render(
            f"Time: {int(time_remaining)}s",
            True,
            (255, 255, 255),
        )
        time_rect = time_text.get_rect(
            bottomright=(
                screen.get_width() - self.padding,
                screen.get_height() - self.padding,
            )
        )
        screen.blit(time_text, time_rect)
