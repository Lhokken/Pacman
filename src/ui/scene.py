"""Base class for all game scenes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pygame.surface import Surface

if TYPE_CHECKING:
    from pathlib import Path
    from .app import GameApp
    from .managers.asset_manager import AssetManager
    from .managers.font_manager import FontManager


class Scene:
    """Base class for all game scenes.

    A scene represents a single screen or state in the game
    (e.g., main menu, game play, pause menu, game over).

    Espone i manager condivisi (asset, font) creati una volta sola da
    `GameApp`. Le sottoclassi non devono istanziarli di nuovo.

    Subclasses must override:
        handle_events: Process pygame events.
        update: Update scene logic (optional).
        draw: Draw the scene to the screen.
    """

    def __init__(self, app: GameApp) -> None:
        self.app = app
        self.assets: AssetManager = app.asset_manager
        self.fonts: FontManager = app.font_manager
        self.assets_img_base: Path = app.assets_base

    def handle_events(self) -> None:
        """Process pygame events. Override in subclasses."""
        pass

    def update(self) -> None:
        """Update scene logic. Override in subclasses."""
        pass

    def draw(self, screen: Surface) -> None:
        """Draw the scene. Override in subclasses."""
        pass

    def on_resume(self) -> None:
        """Hook called when the scene becomes active again.

        Default: no-op. The subclasses that maintain resources
        Temporals (timers, clocks) can be overridden to resynchronize
        the state after a pause. It is invoked by `GameApp.switch_scene()`
        every time a scene becomes the current one.
        """
        pass

    def on_pause(self) -> None:
        """Hook called when the scene becomes active again.

        Default: no-op. The subclasses that maintain resources
        Temporals (timers, clocks) can be overridden to resynchronize
        the state after a pause. It is invoked by `GameApp.switch_scene()`
        every time a scene becomes the current one.
        """
        pass
