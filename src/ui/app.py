"""Main controller for the Pac-Man application.

It manages Pygame initialization, the game loop, and scene switching.
All Pygame resources are properly released upon exit.
"""

from __future__ import annotations

import logging
import sys

from pathlib import Path

import pygame

from .scene import Scene
from .pages.main_menu import MainMenu
from .managers.asset_manager import AssetManager
from .managers.font_manager import FontManager
from src.core.parsing.parsey import GameConfig

logger = logging.getLogger(__name__)


class GameApp:
    """Main application controller.

    Manages Pygame initialization, the game loop, and scene switching.
    All Pygame resources are properly released upon exit.

    Attributes:
        config        : Game configuration loaded from `GameConfig`.
        screen        : Current window surface.
        clock         : Pygame clock used to cap the frame rate at 60 FPS.
        running       : `True` as long as the main loop should continue.
        is_fullscreen : Current screen mode state.
        debug         : If `True`, enables development shortcuts within scenes.
        assets_base   : Path to the `assets/img` folder.
        asset_manager : Shared assets, linked to `ASSETS_TILE_SIZE`.
        font_manager  : Fonts shared across all scenes.
        current_scene : Currently active scene.
    """

    ASSETS_TILE_SIZE = 40
    ASSETS_SUBDIR = ("assets", "img")
    SWITCH_INPUT_COOLDOWN_FRAMES = 15

    # ==================================================================
    #   Helper statici
    # ==================================================================
    @staticmethod
    def _find_assets_base(start: Path) -> Path:
        """Search for the `assets` folder by traversing from `start`.

        Args:
            start: The directory from which to start the search.

        Returns:
            The path to the `assets/img` folder.

        Raises:
            RuntimeError: If the folder is not found either by traversing
                          upwards from `start` or in `CWD/assets/img`.
        """
        for parent in (start, *start.parents):
            candidate = parent.joinpath(*GameApp.ASSETS_SUBDIR)
            if candidate.is_dir():
                return candidate

        fallback = Path.cwd().joinpath(*GameApp.ASSETS_SUBDIR)
        if fallback.is_dir():
            logger.warning(
                "assets/img not found from %s, using fallback %s",
                start,
                fallback,
            )
            return fallback

        raise RuntimeError(
            f"Asset folder not found: neither going up from {start} "
            f"not in {fallback}."
        )

    # ==================================================================
    #   Init
    # ==================================================================
    def __init__(
        self,
        config: GameConfig,
        *,
        debug: bool = False,
    ) -> None:
        """Initialize pygame, the window, and shared resources.

        Args:
            config  : The parsed game configuration.
            debug   : If `True`, enables development shortcuts in
                      scenes (G/V keys in the menu, C during pause).
                      Defaults to `False`.

        Raises:
            RuntimeError : If the configuration contains no levels, if
                           pygame fails to initialize, if the window
                           cannot be created, or if the assets folder
                           does not exist.
        """
        self.config = config
        self.debug = debug

        if not config.levels:
            raise RuntimeError(
                "Configuration contains no levels. Cannot start game."
            )

        try:
            pygame.init()
            pygame.key.set_repeat(200, 100)
        except pygame.error as e:
            logger.error(
                "Failed to initialize pygame: %s",
                e
                )
            raise RuntimeError(
                f"Pygame initialization failed: {e}"
            ) from e
        # --------------------------------------------------------------
        # --- Display
        # --------------------------------------------------------------
        try:
            desktop_info = pygame.display.Info()
            desktop_width = desktop_info.current_w
            desktop_height = desktop_info.current_h
        except (IndexError, pygame.error) as e:
            logger.warning(
                "Could not get desktop size, fallback 1200x800: %s", e
            )
            desktop_width, desktop_height = 1200, 800

        screen_width = int(desktop_width * 0.8)
        screen_height = int(desktop_height * 0.8)

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
        # --------------------------------------------------------------
        # Cooldown di input post-switch.
        # --------------------------------------------------------------
        self._input_cooldown = 0

        # ---------------------------------------------------------------
        # --- Shared assets/fonts: creati UNA volta, riusati da tutti ---
        # ---------------------------------------------------------------
        try:
            self.assets_base: Path = self._find_assets_base(
                Path(__file__).resolve().parent
            )
        except RuntimeError as e:
            logger.error(
                "Unable to start the game: %s",
                e
            )
            pygame.quit()
            sys.exit(1)

        self.asset_manager = AssetManager(
            self.assets_base, tile_size=self.ASSETS_TILE_SIZE
        )
        self.font_manager = FontManager(self.assets_base)
        # --------------------------------------------------------------
        # NOTE: `Scene.__init__` deve costruire `Theme(app.font_manager)`.
        # Se non lo fa, tutte le scene esplodono su `self.theme`.
        # --------------------------------------------------------------
        self.current_scene: Scene = MainMenu(self)
        # L'hook di resume deve partire anche per la scena iniziale,
        # altrimenti eventuale logica in `MainMenu.on_resume` non gira.
        self.current_scene.on_resume()

        logger.info(
            "GameApp initialized: %d level(s), screen %dx%d, assets=%s, "
            "debug=%s",
            len(config.levels),
            screen_width,
            screen_height,
            self.assets_base,
            self.debug,
        )

    # ==================================================================
    #   Fullscreen - scene switching
    # ==================================================================
    def toggle_fullscreen(self) -> None:
        """Toggles between windowed and full-screen modes."""
        # NOTE: After switching modes, notifies the current scene of
        #       the new dimensions via `on_resize`, ensuring that
        #       screen-relative metrics (maze, panels, HUD) are
        #       recalculated even if pygame does not emit a `VIDEORESIZE`
        #       event for the toggle.
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode(
                (0, 0), pygame.FULLSCREEN
            )
        else:
            try:
                desktop_info = pygame.display.Info()
                desktop_w = desktop_info.current_w
                desktop_h = desktop_info.current_h
            except (IndexError, pygame.error):
                desktop_w, desktop_h = 1200, 800
            self.screen = pygame.display.set_mode(
                (
                    int(desktop_w * 0.8),
                    int(desktop_h * 0.8)
                ),
                pygame.RESIZABLE,
            )
        # `set_mode` can change the surface size without!! --------
        # emitting VIDEORESIZE: Force the notification to the scene.
        new_w, new_h = self.screen.get_size()
        self.current_scene.on_resize(new_w, new_h)

        logger.info("Fullscreen toggled: %s", self.is_fullscreen)

    def switch_scene(self, scene: Scene) -> None:
        """Change the current scene.

            1. Notifies the old scene that it is about to be
               left (hook `on_pause`).
            2. Replaces the current scene.
            3. Activates a short input cooldown (prevents key repeat).
            4. Notifies the new scene that it is active (hook `on_resume`).

        Args:
            scene: The new scene to make active.
        """
        # PAUSE CONTROLL -----------------------------------------------
        if self.current_scene is not None:
            self.current_scene.on_pause()
        self.current_scene = scene
        self._input_cooldown = self.SWITCH_INPUT_COOLDOWN_FRAMES
        scene.on_resume()

    # ==================================================================
    #   Main loop
    # ==================================================================
    def run(self) -> None:
        """Run the main loop until shutdown.

        Always releases pygame in the `finally` block, even in the
        event of an error or a `KeyboardInterrupt`.
        """
        try:
            while self.running:
                if self._input_cooldown > 0:
                    self._input_cooldown -= 1
                    self._drain_events_during_cooldown()
                else:
                    self.current_scene.handle_events()

                self.current_scene.update()
                self.current_scene.draw(self.screen)
                pygame.display.flip()
                self.clock.tick(60)
        except KeyboardInterrupt:
            logger.info(
                "Shutdown requested from terminal"
            )
        except pygame.error as e:
            logger.error(
                "Pygame error in main loop: %s",
                e
            )
        except Exception:
            logger.exception(
                "Unexpected error in main loop"
            )
        finally:
            pygame.quit()
            logger.info(
                "GameApp shut down cleanly"
            )

    # ==================================================================
    #   Interni
    # ==================================================================
    def _drain_events_during_cooldown(self) -> None:
        """Consumes the event queue without passing events to the scene.

        During the post-switch cooldown, we want to ignore keyboard and
        mouse input, but we must still count QUIT events.
        """
        # closing the window via the 'X' button: -----------------------
        # IT MUST terminate the application, even during time window.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
