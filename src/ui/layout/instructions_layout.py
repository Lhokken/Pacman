"""Layout for the InstructionsAnimation scene.

Follows the same pattern as IntroLayout, MenuLayout, and PauseLayout:
a return dataclass, a `compute()` method, and class ratios that can be
overridden via `__init__(**overrides)`.

Provides only screen-relative metrics. Calculations dependent on
`max_sprite_w` (parade_left/right, content_width, gum_x) remain within
the scene itself, as they rely on loaded assets.
"""

from __future__ import annotations

from dataclasses import dataclass


# ======================================================================
#   Returned dataclass
# ======================================================================
@dataclass(frozen=True)
class CharacterRowMetrics:
    """Metrics for the character (ghost) row.

    Attributes:
        title_center_y  : Y-coordinate of the title center.
        sprite_center_y : Y-coordinate of the sprite center.
        sprite_height   : Height of the sprites in pixels.
        slot_centers    : X-coordinates of the slot centers.
    """

    title_center_y: int
    sprite_center_y: int
    sprite_height: int
    slot_centers: tuple[int, ...]


@dataclass(frozen=True)
class ScoreRowMetrics:
    """Metrics for the score row (pellets + fear).

    Attributes:
        title_center_y      : Y-coordinate of the title center.
        sprite_center_y     : Y-coordinate of the sprite centers.
        pacgum_height       : Height in pixels of the Pac-Dot.
        super_pacgum_height : Height in pixels of the Power Pellet.
        fear_height         : Height in pixels of the fear sprite.
        slot_centers        : X-coordinates of the slot centers.
        caption_center_y    : Y-coordinate of the explanatory caption.
    """

    title_center_y: int
    sprite_center_y: int
    pacgum_height: int
    super_pacgum_height: int
    fear_height: int
    slot_centers: tuple[int, ...]
    caption_center_y: int


@dataclass(frozen=True)
class InstructionsMetrics:
    """Complete metrics for the static instructions page.

    Attributes:
        characters: Metrics for the characters row.
        scores: Metrics for the scores row.
        footer_center_y: Y-coordinate of the footer center.
    """

    characters: CharacterRowMetrics
    scores: ScoreRowMetrics
    footer_center_y: int


# ======================================================================
#   Layout
# ======================================================================
class InstructionsLayout:
    """Screen-relative layout for the static instructions page.

    Class attributes (ratios) that can be overridden via
    `__init__(**overrides)`.
    """

    # -------------------------------------------------------------------
    #    Sezione 1: CHARACTERS
    # -------------------------------------------------------------------
    CHAR_TITLE_Y_RATIO: float = 0.06
    CHAR_SPRITE_CENTER_Y_RATIO: float = 0.22
    CHAR_SPRITE_H_RATIO: float = 0.10
    # -------------------------------------------------------------------
    #    Sezione 2: SCORE POINTS
    # -------------------------------------------------------------------
    SCORE_TITLE_Y_RATIO: float = 0.52
    SCORE_SPRITE_CENTER_Y_RATIO: float = 0.66
    SCORE_PACGUM_H_RATIO: float = 0.030
    SCORE_SUPER_PACGUM_H_RATIO: float = 0.045
    SCORE_FEAR_H_RATIO: float = 0.10
    # -------------------------------------------------------------------
    #    Caption (super-pacgum -> fear) e footer
    # -------------------------------------------------------------------
    SCORE_CAPTION_Y_RATIO: float = 0.87
    FOOTER_Y_RATIO: float = 0.95
    # -------------------------------------------------------------------
    #    Gap fissi (px) tra elementi impilati
    # -------------------------------------------------------------------
    SPRITE_TO_NICK_GAP: int = 14
    NICK_TO_NAME_GAP: int = 6
    SPRITE_TO_LABEL_GAP: int = 14
    LABEL_TO_SUBLABEL_GAP: int = 6

    # ------------------------------------------------------------------
    #   Init
    # ------------------------------------------------------------------
    def __init__(self, **overrides: object) -> None:
        """Initialize the layout, applying any overrides.

        Args:
            **overrides: Alternative values for the layout's class
                         attributes. Keys must match attribute names
                         of `InstructionsLayout`.

        Raises:
            AttributeError: If an override key does not match any
                            class attribute.
        """
        for key, value in overrides.items():
            if not hasattr(type(self), key):
                raise AttributeError(
                    f"Unknown layout ratio: {key!r}. "
                    f"Valid keys are InstructionsLayout class attributes."
                )
            setattr(self, key, value)

    # ------------------------------------------------------------------
    #   API principale
    # ------------------------------------------------------------------
    def compute(
        self,
        screen_w: int,
        screen_h: int,
        *,
        n_characters: int,
        n_scores: int,
    ) -> InstructionsMetrics:
        """Calculate page metrics.

        Args:
            screen_w     : Screen width in pixels.
            screen_h     : Screen height in pixels.
            n_characters : Number of ghosts (row 1 slots).
            n_scores     : Number of gum/fear items (row 2 slots).

        Returns:
            An `InstructionsMetrics` object with the calculated metrics.
        """
        return InstructionsMetrics(
            characters=CharacterRowMetrics(
                title_center_y=int(
                    screen_h * self.CHAR_TITLE_Y_RATIO
                ),
                sprite_center_y=int(
                    screen_h * self.CHAR_SPRITE_CENTER_Y_RATIO
                ),
                sprite_height=int(
                    screen_h * self.CHAR_SPRITE_H_RATIO
                ),
                slot_centers=self._slot_centers(
                    screen_w, n_characters
                ),
            ),
            scores=ScoreRowMetrics(
                title_center_y=int(
                    screen_h * self.SCORE_TITLE_Y_RATIO
                ),
                sprite_center_y=int(
                    screen_h * self.SCORE_SPRITE_CENTER_Y_RATIO
                ),
                pacgum_height=int(
                    screen_h * self.SCORE_PACGUM_H_RATIO
                ),
                super_pacgum_height=int(
                    screen_h * self.SCORE_SUPER_PACGUM_H_RATIO
                ),
                fear_height=int(
                    screen_h * self.SCORE_FEAR_H_RATIO
                ),
                slot_centers=self._slot_centers(screen_w, n_scores),
                caption_center_y=int(
                    screen_h * self.SCORE_CAPTION_Y_RATIO
                ),
            ),
            footer_center_y=int(screen_h * self.FOOTER_Y_RATIO),
        )

    # ------------------------------------------------------------------
    #   Helper
    # ------------------------------------------------------------------
    @staticmethod
    def _slot_centers(screen_w: int, n: int) -> tuple[int, ...]:
        """Return the X-centers of the slots, evenly spaced.

        With n = 4 and width W: W/5, 2W/5, 3W/5, 4W/5.

        Args:
            screen_w : Screen width in pixels.
            n        : Number of slots to arrange.

        Returns:
            A tuple of X-coordinates, one per slot. Empty if `n <= 0`.
        """
        if n <= 0:
            return ()
        step = screen_w // (n + 1)
        return tuple(step * (i + 1) for i in range(n))
