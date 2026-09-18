"""Main application controller for Pac-Man."""

from __future__ import annotations

import logging
from pathlib import Path

import pygame

from .scene import Scene
from .pages.main_menu import MainMenu
from .managers.asset_manager import AssetManager
from .managers.font_manager import FontManager
from src.core.parsing.parsey import GameConfig

logger = logging.getLogger(__name__)


# TODO: leggere da GameConfig quando esporrà il valore.
ASSETS_TILE_SIZE = 40
ASSETS_SUBDIR = ("assets", "img")

# Numero di frame durante i quali gli input vengono scartati dopo uno
# switch di scena. Serve a evitare che il key repeat di pygame (attivo
# con set_repeat(200, 100)) faccia arrivare lo stesso KEYDOWN anche
# alla nuova scena. 15 frame @ 60 fps ≈ 250 ms, > 200 ms di delay.
SWITCH_INPUT_COOLDOWN_FRAMES = 15


def _find_assets_base(start: Path) -> Path:
    """Cerca `assets/img` risalendo da `start`. Fallback: CWD/assets/img."""
    for parent in (start, *start.parents):
        candidate = parent.joinpath(*ASSETS_SUBDIR)
        if candidate.is_dir():
            return candidate
    fallback = Path.cwd().joinpath(*ASSETS_SUBDIR)
    logger.warning("assets/img non trovato, fallback su %s", fallback)
    return fallback


class GameApp:
    """Main application controller.

    Handles pygame initialization, the main game loop, and scene
    switching. All pygame resources are properly cleaned up on exit.
    """

    def __init__(self, config: GameConfig) -> None:
        self.config = config

        if not config.levels:
            raise RuntimeError(
                "Configuration contains no levels. Cannot start game."
            )

        try:
            pygame.init()
            pygame.key.set_repeat(200, 100)
        except pygame.error as e:
            logger.error("Failed to initialize pygame: %s", e)
            raise RuntimeError(f"Pygame initialization failed: {e}") from e

        # --- Display ---
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

        # Cooldown di input post-switch. Vedi SWITCH_INPUT_COOLDOWN_FRAMES.
        self._input_cooldown = 0

        # --- Shared assets/fonts: creati UNA volta, riusati da tutti ---
        self.assets_base: Path = _find_assets_base(
            Path(__file__).resolve().parent
        )
        self.asset_manager = AssetManager(
            self.assets_base, tile_size=ASSETS_TILE_SIZE
        )
        self.font_manager = FontManager(self.assets_base)

        self.current_scene: Scene = MainMenu(self)

        logger.info(
            "GameApp initialized: %d level(s), screen %dx%d, assets=%s",
            len(config.levels), screen_width, screen_height, self.assets_base,
        )

    def toggle_fullscreen(self) -> None:
        """Toggle between windowed and fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode(
                (0, 0), pygame.FULLSCREEN
            )
        else:
            try:
                desktop_info = pygame.display.Info()
                desktop_width = desktop_info.current_w
                desktop_height = desktop_info.current_h
            except (IndexError, pygame.error):
                desktop_width, desktop_height = 1200, 800
            self.screen = pygame.display.set_mode(
                (int(desktop_width * 0.8), int(desktop_height * 0.8)),
                pygame.RESIZABLE,
            )
        logger.info("Fullscreen toggled: %s", self.is_fullscreen)

    def switch_scene(self, scene: Scene) -> None:
        """Change the current scene.

        Sequenza:
            1. Notifica alla vecchia scena che sta per essere abbandonata
            (hook `on_pause`, es. per congelare timer).
            2. Sostituisce la scena corrente.
            3. Attiva un breve cooldown di input (evita key repeat).
            4. Notifica alla nuova scena che è attiva (hook `on_resume`).
        """
        if self.current_scene is not None:
            self.current_scene.on_pause()
        self.current_scene = scene
        self._input_cooldown = SWITCH_INPUT_COOLDOWN_FRAMES
        scene.on_resume()
        logger.debug("Switched to scene: %s", type(scene).__name__)

    def run(self) -> None:
        """Run the main game loop until quit."""
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
            logger.info("Shutdown requested from terminal")
        except pygame.error as e:
            logger.error("Pygame error in main loop: %s", e)
        except Exception:
            logger.exception("Unexpected error in main loop")
        finally:
            pygame.quit()
            logger.info("GameApp shut down cleanly")

    # ==================================================================
    #   Interni
    # ==================================================================
    def _drain_events_during_cooldown(self) -> None:
        """Consuma la coda eventi senza consegnarli alla scena.

        Durante il cooldown post-switch vogliamo ignorare tastiera e
        mouse, ma dobbiamo comunque onorare QUIT: chiudere la finestra
        con la X deve terminare l'app anche in questa finestra di tempo.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
