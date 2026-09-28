"""Pagina istruzioni di Pac-Man.

Struttura e navigazione: prima UI (Button, Scene, switch_scene).
Contenuto e layout: seconda UI (CHARACTERS, SCORE POINTS, caption).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pygame
from pygame.surface import Surface

from ..scene import Scene
from ..configUI.ui_config import FontRole
from ..components.button import Button
from ..layout.instructions_layout import (
    InstructionsLayout,
    InstructionsMetrics,
)

if TYPE_CHECKING:
    from ..app import GameApp

logger = logging.getLogger(__name__)


class InstructionPage(Scene):
    """Static instructions page: characters + score points.

    Displays two sections (a row of ghosts with nicknames and names,
    a row of scoring elements with labels and subtitles) and an
    "ESC TO RETURN TO MENU" button at the bottom of the screen.
    Layout and metrics are handled by `InstructionsLayout`; window
    resizing is detected by comparing the current size with that of
    the last rebuild.
    """

    _FEAR_CAPTION = "EAT A SUPER PAC-GUM TO SCARE THE GHOSTS"

    def __init__(self, app: GameApp) -> None:
        """Initialize the instructions page.

        Args:
            app: Instance of `GameApp` from which to take the screen and
                 handle scene switching.
        """
        super().__init__(app)
        # -----------------------------------------------------------
        # --- Font --------------------------------------------------
        # -----------------------------------------------------------
        self._font_section = self.theme.font_config(FontRole.HEADING)
        self._font_name = (
            self.theme.font_config(FontRole.SECTION_TITLE)
        )
        self._font_nick = self.theme.font_config(FontRole.OPTION)
        self._font_label = self.theme.font_config(FontRole.OPTION)
        self._font_sub = self.theme.font_config(FontRole.SMALL)
        self._font_caption = self.theme.font_config(FontRole.OPTION)
        # -----------------------------------------------------------
        # --- Layout ------------------------------------------------
        # -----------------------------------------------------------
        self._layout = InstructionsLayout()
        # -----------------------------------------------------------
        # --- Dati riga 1 -------------------------------------------
        # -----------------------------------------------------------
        self._characters: list[tuple[Path, str, str]] = [
            (self._ghost_path("blinky"), "SHADOW", "BLINKY"),
            (self._ghost_path("pinky"), "SPEEDY", "PINKY"),
            (self._ghost_path("inky"), "BASHFUL", "INKY"),
            (self._ghost_path("clyde"), "POKEY", "CLYDE"),
        ]
        # -----------------------------------------------------------
        # --- Dati riga 2 -------------------------------------------
        # -----------------------------------------------------------
        self._scores: list[tuple[Path, str, str]] = [
            (self._gum_path("pacgum"), "PAC-GUM", "10 PTS"),
            (self._gum_path("super_pacgum"), "SUPER", "50 PTS"),
            (self._fear_path(), "FEAR MODE", "EAT THEM"),
        ]
        # -----------------------------------------------------------
        # --- Back button (stile prima UI)
        # -----------------------------------------------------------
        self.back_button = Button(
            pygame.Rect(0, 0, 300, 50),
            "ESC TO RETURN TO MENU",
            self.fonts.font_white,
            self.fonts.font_title_small,
            on_select=self._go_back,
        )
        self.buttons = [self.back_button]
        # -----------------------------------------------------------
        # --- Asset + cache scalata ---------------------------------
        # -----------------------------------------------------------
        self._raw_chars = [
            self._load_png(p) for p, _, _ in self._characters
        ]
        self._raw_scores = [
            self._load_png(p) for p, _, _ in self._scores
        ]
        self._scaled_chars: list[Surface | None] = []
        self._scaled_scores: list[Surface | None] = []
        self._metrics: InstructionsMetrics | None = None
        self._metrics_size: tuple[int, int] = (0, 0)
        self._rebuild_metrics()

    # ==================================================================
    #   Lifecycle
    # ==================================================================
    def handle_events(self) -> None:
        """Gestisce gli eventi di input della pagina istruzioni.

        Invio attiva il bottone di ritorno (sempre selezionato), ESC
        torna al menu principale, QUIT chiude l'applicazione.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.back_button.handle_event(event)
                elif event.key == pygame.K_ESCAPE:
                    self._go_back()

    def update(self) -> None:
        """Ricalcola le metriche se la dimensione dello schermo cambia."""
        if self.app.screen.get_size() != self._metrics_size:
            self._rebuild_metrics()

    def draw(self, screen: Surface) -> None:
        """Disegna la pagina istruzioni.

        Args:
            screen: Surface di destinazione.
        """
        screen.fill(self.theme.palette.DARK)
        self._draw_characters(screen)
        self._draw_scores(screen)
        self._layout_buttons(screen.get_width(), screen.get_height())
        self.back_button.draw(screen)

    # ==================================================================
    #   Navigazione
    # ==================================================================
    def _go_back(self) -> None:
        """Torna al menu principale."""
        from .main_menu import MainMenu
        self.app.switch_scene(MainMenu(self.app))

    def _layout_buttons(self, screen_w: int, screen_h: int) -> None:
        """Places the back button at the bottom of the screen.

        Args:
            screen_w : Current screen width in pixels.
            screen_h : Current screen height in pixels.
        """
        self.back_button.rect.center = (
            screen_w // 2, screen_h - 60
        )
        self.back_button.set_selected(True)

    # ==================================================================
    #   Path asset
    # ==================================================================
    def _ghost_path(self, key: str) -> Path:
        """Return the path to a ghost's sprite.

        Args:
            key: Name of the ghost

        Returns:
            The path to the associated sprite.
        """
        return (
            self.assets_img_base / "ghost" / key / "ghost.png"
        )

    def _gum_path(self, key: str) -> Path:
        """Return the path to the sprite of a Pac-Gum.

        Args:
            key: Name of the pac-gum

        Returns:
            The path to the associated sprite.
        """
        return self.assets_img_base / "gum" / f"{key}.png"

    def _fear_path(self) -> Path:
        """Return the path of the "fear mode" sprite.

        Returns:
            The path of the first frame of the `fear_going` state.
        """
        return (
            self.assets_img_base
            / "ghost" / "status_fear" / "fear_going" / "fear_1.png"
        )

    # ==================================================================
    #   Metriche & asset scalati
    # ==================================================================
    def _rebuild_metrics(self) -> None:
        """Recalculate metrics and scaled sprites for the current size.

        Stores the new size in `_metrics_size`, updates `_metrics` via
        `InstructionsLayout.compute()`, and rescales the sprites for the
        two rows based on the heights required by the layout.
        """
        w, h = self.app.screen.get_size()
        self._metrics_size = (w, h)

        self._metrics = self._layout.compute(
            w, h,
            n_characters=len(self._characters),
            n_scores=len(self._scores),
        )

        char_h = self._metrics.characters.sprite_height
        self._scaled_chars = [
            self._scale_to_height(s, char_h) for s in self._raw_chars
        ]

        score_heights = (
            self._metrics.scores.pacgum_height,
            self._metrics.scores.super_pacgum_height,
            self._metrics.scores.fear_height,
        )
        self._scaled_scores = [
            self._scale_to_height(s, hh)
            for s, hh in zip(self._raw_scores, score_heights)
        ]

    @staticmethod
    def _scale_to_height(
        img: Surface | None, target_h: int,
    ) -> Surface | None:
        """Scale `img` to `target_h`, maintaining the aspect ratio.

        Args:
            img      : Surface to scale, or `None`.
            target_h : Desired height in pixels.

        Returns:
            The scaled surface, or `None` if `img` is `None` or
            `target_h <= 0`.
        """
        if img is None or target_h <= 0:
            return None
        w = max(1, int(img.get_width() * target_h / img.get_height()))
        return pygame.transform.smoothscale(img, (w, target_h))

    @staticmethod
    def _load_png(path: Path) -> Surface | None:
        """Load a PNG with an alpha channel, returning `None` on error.

        Args:
            path: Path to the image to load.

        Returns:
            The loaded surface with an alpha channel, or `None` if the
            file does not exist or loading fails.
        """
        if not path.exists():
            logger.warning(
                "InstructionPage: asset mancante %s", path
            )
            return None
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            logger.error(
                "InstructionPage: errore caricando %s: %s", path, e,
            )
            return None

    # ==================================================================
    #   Draw
    # ==================================================================
    def _draw_characters(self, screen: Surface) -> None:
        """Draws the CHARACTERS section (title, sprites, names).

        Args:
            screen: Target surface.
        """
        assert self._metrics is not None
        m = self._metrics.characters
        cx_screen = screen.get_width() // 2

        title = self._font_section.render("CHARACTERS")
        screen.blit(
            title,
            title.get_rect(center=(cx_screen, m.title_center_y)),
        )

        for i, ((_, nickname, name), sprite) in enumerate(
            zip(self._characters, self._scaled_chars)
        ):
            cx = m.slot_centers[i]

            if sprite is not None:
                r = sprite.get_rect(center=(cx, m.sprite_center_y))
                screen.blit(sprite, r)
                y = r.bottom + self._layout.SPRITE_TO_NICK_GAP
            else:
                y = (
                    m.sprite_center_y
                    + m.sprite_height // 2
                    + self._layout.SPRITE_TO_NICK_GAP
                )

            nick = self._font_nick.render(nickname)
            nr = nick.get_rect(midtop=(cx, y))
            screen.blit(nick, nr)
            y = nr.bottom + self._layout.NICK_TO_NAME_GAP

            name_surf = self._font_name.render(name)
            screen.blit(name_surf, name_surf.get_rect(midtop=(cx, y)))

    def _draw_scores(self, screen: Surface) -> None:
        """Disegna la sezione SCORE POINTS (titolo, sprite, etichette).

        Args:
            screen: Surface di destinazione.
        """
        assert self._metrics is not None
        m = self._metrics.scores
        cx_screen = screen.get_width() // 2

        title = self._font_section.render("SCORE POINTS")
        screen.blit(
            title,
            title.get_rect(center=(cx_screen, m.title_center_y)),
        )

        for i, ((_, label, sub), sprite) in enumerate(
            zip(self._scores, self._scaled_scores)
        ):
            cx = m.slot_centers[i]

            if sprite is not None:
                r = sprite.get_rect(center=(cx, m.sprite_center_y))
                screen.blit(sprite, r)
                y = r.bottom + self._layout.SPRITE_TO_LABEL_GAP
            else:
                y = (
                    m.sprite_center_y
                    + self._layout.SPRITE_TO_LABEL_GAP
                )

            label_surf = self._font_label.render(label)
            lr = label_surf.get_rect(midtop=(cx, y))
            screen.blit(label_surf, lr)
            y = lr.bottom + self._layout.LABEL_TO_SUBLABEL_GAP

            sub_surf = self._font_sub.render(sub)
            screen.blit(sub_surf, sub_surf.get_rect(midtop=(cx, y)))

        self._draw_fear_caption(screen)

    def _draw_fear_caption(self, screen: Surface) -> None:
        """Disegna la caption esplicativa sotto la riga punteggi.

        Args:
            screen: Surface di destinazione.
        """
        if self._metrics is None:
            return
        cx_screen = screen.get_width() // 2
        caption = self._font_caption.render(self._FEAR_CAPTION)
        screen.blit(
            caption,
            caption.get_rect(
                center=(
                    cx_screen, self._metrics.scores.caption_center_y
                )
            ),
        )
