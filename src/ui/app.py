"""Main application controller for Pac-Man."""

from __future__ import annotations

import logging

import pygame

from .scene import Scene
from .pages.main_menu import MainMenu
from src.core.parsing.parsey import GameConfig

logger = logging.getLogger(__name__)


class GameApp:
    """Main application controller.

    Handles pygame initialization, the main game loop, and scene
    switching. All pygame resources are properly cleaned up on exit.

    Attributes:
        config: The validated game configuration.
        screen: The main pygame display surface.
        clock: The pygame clock for frame rate control.
        running: False to exit the game loop.
        current_scene: The currently active scene.
        is_fullscreen: Whether the window is currently fullscreen.
    """

    def __init__(self, config: GameConfig) -> None:
        """Initialize pygame and create the game window.

        The window is created resizable and initially sized to 80% of
        the desktop resolution. The user can toggle fullscreen with F11.

        Args:
            config: The validated game configuration.

        Raises:
            RuntimeError: If pygame initialization fails.
        """
        self.config = config

        # Validate that at least one level exists
        if not config.levels:
            raise RuntimeError(
                "Configuration contains no levels. Cannot start game."
            )

        # Initialize pygame
        try:
            pygame.init()
            pygame.key.set_repeat(200, 100)
        except pygame.error as e:
            logger.error("Failed to initialize pygame: %s", e)
            raise RuntimeError(f"Pygame initialization failed: {e}") from e

        # Get desktop resolution
        try:
            desktop_size = pygame.display.get_desktop_sizes()[0]
            desktop_width, desktop_height = desktop_size
        except (IndexError, pygame.error) as e:
            logger.warning(
                "Could not get desktop size, using fallback 1200x800: %s", e
            )
            desktop_width, desktop_height = 1200, 800

        # Start at 80% of desktop size
        screen_width = int(desktop_width * 0.8)
        screen_height = int(desktop_height * 0.8)

        # Set up display (resizable)
        try:
            self.screen = pygame.display.set_mode(
                (screen_width, screen_height), pygame.RESIZABLE
            )
            pygame.display.set_caption("Pac-Man")
        except pygame.error as e:
            logger.error("Failed to create display: %s", e)
            pygame.quit()
            raise RuntimeError(f"Display creation failed: {e}") from e

        self.clock = pygame.time.Clock()
        self.running = True
        self.is_fullscreen = False

        # TODO: Initialize asset_manager and font_manager cache here
        # These should be created once and reused by all scenes
        # self.asset_manager = AssetManager(assets_base, tile_size)
        # self.font_manager = FontManager(assets_base)

        self.current_scene: Scene = MainMenu(self)

        logger.info(
            "GameApp initialized with %d level(s), screen %dx%d",
            len(config.levels),
            screen_width,
            screen_height,
        )

    def toggle_fullscreen(self) -> None:
        """Toggle between windowed and fullscreen mode.

        Uses F11 or can be called programmatically.
        """
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode(
                (0, 0), pygame.FULLSCREEN
            )
        else:
            # Restore to 80% of desktop
            try:
                desktop_size = pygame.display.get_desktop_sizes()[0]
                desktop_width, desktop_height = desktop_size
            except (IndexError, pygame.error):
                desktop_width, desktop_height = 1200, 800
            screen_width = int(desktop_width * 0.8)
            screen_height = int(desktop_height * 0.8)
            self.screen = pygame.display.set_mode(
                (screen_width, screen_height), pygame.RESIZABLE
            )
        logger.info("Fullscreen toggled: %s", self.is_fullscreen)

    def switch_scene(self, scene: Scene) -> None:
        """Change the current scene.

        Args:
            scene: The new scene to display.
        """
        self.current_scene = scene

    def run(self) -> None:
        """Run the main game loop until quit."""
        try:
            while self.running:
                self.current_scene.handle_events()
                self.current_scene.update()
                self.current_scene.draw(self.screen)
                pygame.display.flip()
                self.clock.tick(60)
        except KeyboardInterrupt:
            logger.info("Shutdown requested from terminal")
        except pygame.error as e:
            raise
            logger.error("Pygame error in main loop: %s", e)
        except Exception:
            raise
            logger.exception("Unexpected error in main loop")
        finally:
            pygame.quit()
            logger.info("GameApp shut down cleanly")
