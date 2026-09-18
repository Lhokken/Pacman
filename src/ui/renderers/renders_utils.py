"""Utility di rendering condivise tra Scene e AnimationScene.

Funzioni libere, niente classi: sono 2-3 righe ciascuna, un mixin
sarebbe sovradimensionato. Chi vuole le importa direttamente.

    from ..render_utils import blit_centered

    blit_centered(screen, sprite, x, y)
"""

from __future__ import annotations

import pygame
from pygame.surface import Surface


def blit_centered(
    screen: Surface,
    img: pygame.Surface | None,
    x: float,
    y: float,
) -> None:
    """Disegna `img` centrata su (x, y). No-op se `img` è None.

    Args:
        screen: superficie di destinazione.
        img: immagine da disegnare; se None, la funzione non fa nulla.
        x, y: coordinate del centro (float accettati, arrotondati a int).
    """
    if img is None:
        return
    screen.blit(img, img.get_rect(center=(int(x), int(y))))


def render_text(font, text: str) -> Surface:
    """Renderizza `text` con `font`. Wrapper di `font.render(text)`.

    Esiste per uniformare i call-site e per avere un unico punto in
    cui aggiungere opzioni (antialias, colore di sfondo) se servirà.
    """
    return font.render(text)
