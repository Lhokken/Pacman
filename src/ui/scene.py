"""Base class for all game scenes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pygame.surface import Surface
from .configUI.ui_config import Theme
from .renderers.renderer import Renderer

if TYPE_CHECKING:
    from pathlib import Path
    from .app import GameApp
    from .managers.asset_manager import AssetManager
    from .managers.font_manager import FontManager


class Scene:
    """Base class for all game scenes.

    A scene represents a single screen or game state
    (e.g., main menu, gameplay, pause menu, game over).

    It exposes shared managers (assets, fonts) created once by
    `GameApp`. Subclasses must not instantiate them again.

    Subclasses must override:

        handle_events : processes pygame events.
        update        : updates the scene logic (optional).
        draw          : draws the scene on the screen.
    """

    def __init__(self, app: GameApp) -> None:
        """Initialize the scene with shared managers.

        Args:
            app : Instance of `GameApp` from which to take shared
                  assets, fonts, and palettes.
        """
        self.app = app
        self.assets: AssetManager = app.asset_manager
        self.fonts: FontManager = app.font_manager
        self.assets_img_base: Path = app.assets_base
        self.theme = Theme(self.fonts)
        self.render = Renderer()

    def handle_events(self) -> None:
        """Process Pygame events. Override in subclasses."""
        pass

    def update(self) -> None:
        """Update the scene logic. Override in subclasses."""
        pass

    def draw(self, screen: Surface) -> None:
        """Draw the scene on the surface. Override in subclasses.

        Args:
            screen : Destination surface.
        """
        pass

    def on_resume(self) -> None:
        """Call the hook when the scene becomes active again.

        Default:
            no operation. Subclasses managing time-based resources
            (timers, clocks) can override this method to resynchronize
            state after a pause. It is invoked by `GameApp.switch_scene()`
            whenever a scene becomes the current one."
        """
        pass

    def on_pause(self) -> None:
        """Call the hook when the scene is about to be left.

        Default:
            no-op. Subclasses that maintain time-based resources
            (timers, clocks) can override this to pause the state
            before the switch. It is invoked by `GameApp.switch_scene()`
            before replacing the current scene.
        """
        pass

    def on_resize(self, width: int, height: int) -> None:
        """Call Hook when the window is resized.

        Default:
            no operation. Scenes with screen-relative layouts
            (e.g., `GamePage`) override this method to recalculate
            dimensions. It is invoked by `GameApp.toggle_fullscreen()`
            after a mode change and by scenes receiving the
            `pygame.VIDEORESIZE` event.

        Arguments:
            width  : New window width in pixels.
            height : New window height in pixels.
        """
        pass
