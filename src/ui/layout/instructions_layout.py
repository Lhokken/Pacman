"""Layout della scena InstructionsAnimation.

Stessa forma di IntroLayout/MenuLayout/PauseLayout: dataclass di
ritorno, `compute()`, ratio di classe sovrascrivibili via
`__init__(**overrides)`.

Fornisce solo metriche screen-relative. I calcoli che dipendono da
`max_sprite_w` (parade_left/right, content_width, gum_x) restano
nella scena: dipendono dagli asset caricati.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstructionsMetrics:
    """Metriche screen-relative per la scena delle istruzioni."""

    presentation_y: int
    nick_offset: int
    name_offset: int
    ghost_spacing: int
    spawn_offset: int
    gum_distance: int            # distanza parade_right → gum
    sprite_height_ratio: float
    gum_height_ratio: float


class InstructionsLayout:
    """Metriche screen-relative della scena istruzioni."""

    # TODO: METTERE QUI LA LOGICA LAYOUT
    pass
