"""Manages loading and scaling of all game sprites."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pygame
from pygame.surface import Surface
from dataclasses import dataclass, field

from .asset_exceptions import (
    AssetNotFoundError,
    MissingRequiredAssetsError,
)
from .image_scaling import ImageScaler

logger = logging.getLogger(__name__)


@dataclass
class GhostSprites:
    """Ghost sprites, organized by state/direction."""

    # Sostituisce la vecchia coppia (ghost_images, ghost_frames).
    static: Optional[Surface] = None
    look_up:    list[Surface] = field(default_factory=list)
    look_down:  list[Surface] = field(default_factory=list)
    look_left:  list[Surface] = field(default_factory=list)
    look_right: list[Surface] = field(default_factory=list)
    dead:       list[Surface] = field(default_factory=list)

    def frames_for_direction(self, direction: str) -> list[Surface]:
        """Frame for the given direction ('up'|'down'|'left'|'right')."""
        return {
            "up":    self.look_up,
            "down":  self.look_down,
            "left":  self.look_left,
            "right": self.look_right,
        }.get(direction, self.look_right)

    def first_frame(self) -> Optional[Surface]:
        """First available frame, with fallbacks in order of priority."""
        for lst in (self.look_right, self.look_left,
                    self.look_up, self.look_down, self.dead):
            if lst:
                return lst[0]
        return self.static


class AssetManager:
    """Loads and caches sprite images scaled to the current tile size.

    Attributes:
        assets_base        : Root path containing all image assets.
        tile_size          : Current tile size in pixels.
        player_img         : Player sprite (None if missing).
        wall_tiles         : Dict mapping logical wall mask (0-15) to Surface.
        intersection_tiles : Dict mapping logical intersection mask
                            (0-15) to Surface.
        border_tiles       : Dict mapping border key to Surface.
        border_wall_tiles  : Dict mapping connector direction to Surface.
                             Blank if connectors are not present.
        ghost_images       : List of 4 ghost Surfaces (may contain None).
        pacgum_img         : Small dot sprite.
        super_pacgum_img   : Power pellet sprite.
        logo_icon          : logo icon for panel.
        pacman_icon        : Pac-Man icon for lives panel.
    """
    # ===================================================================
    #   ENTETIES AND WALL ASSETS
    # ===================================================================
    #   We use nearest_neighbor() For respect subject MLX mandatory fn
    #   for more details consult assets/Kanban Backlog/mlx_compliace.md

    _BORDER_FALLBACK_MASK: dict[str, int] = {
        "corner_tl": 2 | 4,   # E + S
        "corner_tr": 4 | 8,   # S + W
        "corner_bl": 1 | 2,   # N + E
        "corner_br": 1 | 8,   # N + W
        "top":       2 | 8,   # E + W (horizontal)
        "bottom":    2 | 8,   # E + W (horizontal)
        "left":      1 | 4,   # N + S (vertical)
        "right":     1 | 4,   # N + S (vertical)
    }

    def __init__(self, assets_base: Path, tile_size: int) -> None:
        """Initialize and load all assets.

        Args:
            assets_base: Root path containing image assets.
            tile_size: Initial tile size for scaling.
        """
        self.assets_base = assets_base
        self.tile_size = tile_size
        self.load_all()

    # ====================================================================
    #   LOAD - ALL ASSETS
    # ====================================================================
    def load_all(self) -> None:
        """Load all game sprites and validate required assets."""
        # LOADING PATH ASSETS ------------------------------------------------
        self.player_frames, self.player_img = self._load_player()
        self.player_death_frames = self._load_frame_list(
            self.assets_base / "player" / "animation_dead",
            ratio=0.8,
            min_size=12,
        )
        self.wall_tiles = self._load_wall_tiles()
        self.intersection_tiles = self._load_intersection_tiles()
        self.border_tiles = self._load_border_tiles()
        self.border_wall_tiles = self._load_border_wall_tiles()

        self.ghosts, self.ghost_shared = self._load_ghosts()

        self.ghost_images = [
            frame for n in ("blinky", "pinky", "inky", "clyde")
            if (frame := self.ghosts[n].first_frame()) is not None
        ]
        # Backwards compatibility: for older code that expects a list of
        # per-ghost animation frame lists named `ghost_frames`, provide
        # a best-effort mapping from the new `GhostSprites` structure.
        self.ghost_frames: list[list[Surface] | list[Surface | None]] = [
            (
                self.ghosts[n].look_right
                or self.ghosts[n].look_left
                or self.ghosts[n].look_up
                or self.ghosts[n].look_down
                or self.ghosts[n].dead
                or ([self.ghosts[n].static] if self.ghosts[n].static else [])
            )
            for n in ("blinky", "pinky", "inky", "clyde")
        ]

        self.pacgum_img = self._load_pacgum()
        self.super_pacgum_img = self._load_super_pacgum()
        self.pacman_icon = self._load_pacman_icon()
        self._ensure_assets_available()

    def set_tile_size(self, new_size: int) -> None:
        """Update tile size and reload assets if changed."""
        if new_size != self.tile_size:
            self.tile_size = new_size
            self.load_all()

    # ---------------------------------------------------------------
    #   Individual asset loaders
    # ---------------------------------------------------------------
    def _scale_entity_asset(
        self,
        image: Surface,
        ratio: float,
        min_size: int = 8,
    ) -> Surface:
        """Scale entity sprites proportionally to the active tile size."""
        size = max(min_size, int(self.tile_size * ratio))
        return ImageScaler.nearest_neighbor(image, (size, size))

    def _load_player(
        self,
    ) -> tuple[dict[str, list[Surface]], Optional[Surface]]:
        """Load pre-oriented player frames and the static reference sprite."""
        # ====================================================================
        #   FRAMES ENTETIES DIRECTION
        # ====================================================================
        #   We use nearest_neighbor() For respect subject MLX mandatory fn
        #   for more details consult assets/Kanban Backlog/mlx_compliace.md

        # LOADING PATH ASSETS ------------------------------------------------
        player_dir = self.assets_base / "player"
        animation_dir = player_dir / "animation"
        frames_by_direction = {
            direction: self._load_frame_list(
                animation_dir / f"look_{direction}",
                ratio=0.8,
                min_size=12,
            )
            for direction in ("right", "left", "up", "down")
        }
        if not frames_by_direction["right"]:
            frames_by_direction["right"] = self._load_frame_list(
                animation_dir,
                ratio=0.8,
                min_size=12,
            )
        # --------------------------------------------------------------------
        #   Player - Asset controls
        # --------------------------------------------------------------------
        reference_path = player_dir / "Player_img.png"
        reference: Optional[Surface] = None
        if reference_path.exists():
            try:
                image = pygame.image.load(reference_path).convert_alpha()
                reference = self._scale_entity_asset(
                    image,
                    ratio=0.8,
                    min_size=12,
                )
            except pygame.error as error:
                logger.error(
                    "Failed to load player reference image %s: %s",
                    reference_path,
                    error,
                )
        else:
            logger.warning(
                "Player reference image missing: %s", reference_path
            )

        if reference is None:
            reference = next(
                (
                    frames[0]
                    for frames in frames_by_direction.values()
                    if frames
                ),
                None,
            )
        return frames_by_direction, reference

    # ====================================================================
    #   Private helper methods for loading and scaling specific assets
    # ====================================================================
    #   We use nearest_neighbor() For respect subject MLX mandatory fn
    #   for more details consult assets/Kanban Backlog/mlx_compliace.md
    # --------------------------------------------------------------------
    #   Load wall tiles for each mask (0-15).
    # --------------------------------------------------------------------
    def _load_wall_tiles(self) -> dict[int, Surface]:
        """Load wall tiles for each mask.

        The ``wall_<mask>.png`` files live in ``wall/intersections/``.

        Returns:
            Dictionary mapping mask values to their corresponding
            tile surfaces.
        """
        # ====================================================================
        #   FRAMES WALL DIRECTION
        # ====================================================================
        # LOADING PATH ASSETS ------------------------------------------------
        assets_dir = self.assets_base / "wall" / "intersections"
        tiles: dict[int, Surface] = {}
        # --------------------------------------------------------------------
        #   wall - Asset controls
        # --------------------------------------------------------------------
        for mask in range(16):
            tile_path = assets_dir / f"wall_{mask}.png"
            if not tile_path.exists():
                logger.warning(
                    "%s not found. Wall tile for mask %d won't be drawn.",
                    tile_path,
                    mask,
                )
                continue
            try:
                tile = pygame.image.load(tile_path).convert_alpha()
                tile = ImageScaler.nearest_neighbor(
                    tile, (self.tile_size, self.tile_size)
                )
                tiles[mask] = tile
            except pygame.error as e:
                logger.error(
                    "Failed to load wall tile %s: %s", tile_path, e
                )
        return tiles

    # --------------------------------------------------------------------
    #   Load intersection tiles for each mask (0-15).
    # --------------------------------------------------------------------
    def _load_intersection_tiles(self) -> dict[int, Surface]:
        """Load intersection tiles for each mask.

        Returns:
            Dictionary mapping mask values to their corresponding
            tile surfaces.
        """
        candidate_dirs = [
            self.assets_base / "wall" / "intersection",
            self.assets_base / "wall" / "intersections",
        ]
        assets_dir = (
            next(
                (path for path in candidate_dirs if path.exists()),
                candidate_dirs[0]
            )
        )
        tiles: dict[int, Surface] = {}
        for mask in range(16):
            tile_path = assets_dir / f"intersection_{mask}.png"
            if not tile_path.exists():
                logger.warning(
                    "%s not found. Intersection tile for mask %d "
                    "won't be drawn.",
                    tile_path,
                    mask,
                )
                continue
            try:
                tile = pygame.image.load(tile_path).convert_alpha()
                tile = ImageScaler.nearest_neighbor(
                    tile, (self.tile_size, self.tile_size)
                )
                tiles[mask] = tile
            except pygame.error as e:
                logger.error(
                    "Failed to load intersection tile %s: %s", tile_path, e
                )
        return tiles

    # --------------------------------------------------------------------
    #   Load border tiles for the outer frame (with all-or-nothing fallback).
    # --------------------------------------------------------------------
    def _load_border_tiles(self) -> dict[str, Surface]:
        """Load the border frame using an all-or-nothing fallback policy.

        Policy:
            1. Attempt to load **all** files in ``wall/double/``.
            2. If even a single file is missing or unreadable, discard the
               entire set and reconstruct the frame using the corresponding
               wall masks (``self._BORDER_FALLBACK_MASK``).
            3. If a fallback wall is also missing, log a warning and
               proceed without that key (the border will not be drawn).

        This ensures the frame remains consistent: either entirely
        ``double`` or entirely ``wall``.

        Returns:
            Dictionary mapping the logical border key to a Surface.
        """
        assets_dir = self.assets_base / "wall" / "double"
        file_to_key = {
            "corner_tl": "corner_tl",
            "corner_tr": "corner_tr",
            "corner_bl": "corner_bl",
            "corner_br": "corner_br",
            "t_up":      "top",
            "t_down":    "bottom",
            "t_left":    "left",
            "t_right":   "right",
        }

        # ---------------------------------------------------------------
        # 1. Tentativo: carica tutti i file double.
        # ---------------------------------------------------------------
        double_tiles: dict[str, Surface] = {}
        missing_double: list[str] = []

        for file_name, key in file_to_key.items():
            path = assets_dir / f"{file_name}.png"
            if not path.exists():
                missing_double.append(str(path))
                continue
            try:
                tile = pygame.image.load(path).convert_alpha()
                tile = ImageScaler.nearest_neighbor(
                    tile, (self.tile_size, self.tile_size)
                )
                double_tiles[key] = tile
            except pygame.error as e:
                logger.error(
                    "Failed to load border tile %s: %s", path, e
                )
                missing_double.append(str(path))

        if not missing_double:
            return double_tiles

        # ----------------------------------------------------------------
        # 2. Fallback totale: ricostruisci tutta la cornice con le wall.
        # ----------------------------------------------------------------
        #   Fallback :  if a frame edge (``wall/double/*``) is missing, we
        #               try to replace it with the corresponding wall mask.
        # ----------------------------------------------------------------
        logger.warning(
            "Border frame incomplete (%d missing); rebuilding the whole "
            "frame from walls. Missing: %s",
            len(missing_double),
            missing_double,
        )

        tiles: dict[str, Surface] = {}
        for key, mask in self._BORDER_FALLBACK_MASK.items():
            if mask in self.wall_tiles:
                tiles[key] = self.wall_tiles[mask]
            else:
                logger.warning(
                    "Fallback wall mask %d missing for border key '%s'; "
                    "frame won't be drawn for this key.",
                    mask,
                    key,
                )
        return tiles

    # --------------------------------------------------------------------
    #   Load border wall connectors (optional).
    # --------------------------------------------------------------------
    def _load_border_wall_tiles(self) -> dict[str, Surface]:
        """Load optional wall connectors that meet the outer frame.

        The manager searches these directories in order:
        - ``wall/double/connectors/``
        - ``wall/border/connectors/``

        Expected files:
        - ``t_wall_up.png``, ``t_wall_down.png``,
        - ``t_wall_left.png``, ``t_wall_right.png``

        If neither directory exists, an empty mapping is returned and the
        maze renderer falls back to legacy wall tiles.

        Returns:
            Mapping of connector directions to surfaces, or an empty mapping.
        """
        # ====================================================================
        #   FRAMES WALL DOUBLE
        # ====================================================================
        # LOADING PATH ASSETS ------------------------------------------------
        candidate_dirs = [
            self.assets_base / "wall" / "double" / "connectors",
            self.assets_base / "wall" / "border" / "connectors",
        ]
        assets_dir = next(
            (p for p in candidate_dirs if p.exists()),
            None,
        )
        if assets_dir is None:
            logger.debug(
                "No border connector directory found; "
                "wall connectors disabled."
            )
            return {}

        file_to_key = {
            "t_wall_up":    "up",
            "t_wall_down":  "down",
            "t_wall_left":  "left",
            "t_wall_right": "right",
        }
        #   INFO ----------------------------------------------------------
        #   We use nearest_neighbor() For respect subject MLX mandatory fn
        #   for more details consult assets/Kanban Backlog/mlx_compliace.md
        tiles: dict[str, Surface] = {}
        for file_name, key in file_to_key.items():
            path = assets_dir / f"{file_name}.png"
            if not path.exists():
                logger.debug(
                    "Connector %s not found; skipping.", path
                )
                continue
            try:
                tile = pygame.image.load(path).convert_alpha()
                tile = ImageScaler.nearest_neighbor(
                    tile, (self.tile_size, self.tile_size)
                )
                tiles[key] = tile
            except pygame.error as e:
                logger.error(
                    "Failed to load connector %s: %s", path, e
                )
        return tiles

    # --------------------------------------------------------------------
    #   Load ghost sprites and animation frames.
    # --------------------------------------------------------------------
    def _load_ghosts(
        self
    ) -> tuple[dict[str, GhostSprites], dict[str, list[Surface]]]:
        """Load directional and state sprites for all ghosts.

        Returns:
            A mapping of ghost names to sprites and shared frightened frames.
        """
        # ====================================================================
        #   FRAMES GHOST
        # ====================================================================
        # LOADING PATH ASSETS ------------------------------------------------
        base = self.assets_base / "ghost"
        directions = [
            "look_up",
            "look_down",
            "look_left",
            "look_right",
        ]

        ghosts: dict[str, GhostSprites] = {}
        for name in ["blinky", "pinky", "inky", "clyde"]:
            sprites = GhostSprites()
            ghost_dir = base / name

            # Static ----------------------------------------------------------
            static_path = ghost_dir / "ghost.png"
            if static_path.exists():
                try:
                    img = pygame.image.load(static_path).convert_alpha()
                    sprites.static = self._scale_entity_asset(img, 0.8, 12)
                except pygame.error as e:
                    raise AssetNotFoundError(
                        f"Failed to load static ghost image {static_path}: {e}"
                    )
            # Per ogni direzione ----------------------------------------------
            for d in directions:
                frames = (
                    self._load_frame_list(
                        ghost_dir / d, ratio=0.8, min_size=12
                    )
                )
                setattr(sprites, d, frames)
                if not frames:
                    logger.debug("No %s frames for %s", d, name)

            # Dead -----------------------------------------------------------
            sprites.dead = self._load_frame_list(
                ghost_dir / "status_dead", ratio=0.8, min_size=12
            )

            ghosts[name] = sprites

        # Fear (condivisi) ----------------------------------------------------
        fear_dir = base / "status_fear" / "fear_status"
        fear_going = base / "status_fear" / "fear_going"
        shared = {
            "fear":       self._load_frame_list(fear_dir,   0.8, 12),
            "fear_flash": self._load_frame_list(fear_going, 0.8, 12),
        }
        if not shared["fear"]:
            logger.warning("Frightened ghost frames missing: %s", fear_dir)
        if not shared["fear_flash"]:
            logger.debug("Fear flashing frames missing: %s", fear_going)

        return ghosts, shared

    def _load_frame_list(
        self, folder: Path, ratio: float, min_size: int
    ) -> list[Surface]:
        """Load and scale PNG frames from a directory in filename order.

        Args:
            folder   : Directory containing animation frames.
            ratio    : Frame size as a fraction of the active tile size.
            min_size : Minimum width and height for each frame.

        Returns:
            Loaded frames sorted by filename.
        """
        if not folder.exists():
            return []
        frames: list[Surface] = []
        for f in sorted(folder.glob("*.png")):
            try:
                img = pygame.image.load(f).convert_alpha()
                img = self._scale_entity_asset(
                    img,
                    ratio=ratio,
                    min_size=min_size
                )
                frames.append(img)
            except pygame.error as e:
                logger.error(
                    "Failed to load %s: %s",
                    f,
                    e
                )
        return frames

    # --------------------------------------------------------------------
    #   Helper to scale gum assets (pacgum, super-pacgum) proportionally
    # --------------------------------------------------------------------
    def _scale_gum_asset(
        self,
        image: Surface,
        ratio: float,
        min_size: int = 4,
    ) -> Surface:
        """Scale a gum asset proportionally to the current tile size."""
        #   INFO ----------------------------------------------------------
        #   We use nearest_neighbor() For respect subject MLX mandatory fn
        #   for more details consult assets/Kanban Backlog/mlx_compliace.md
        size = max(min_size, int(self.tile_size * ratio))
        return ImageScaler.nearest_neighbor(image, (size, size))

    # -------------------------------------------------------------------
    #   Load pacgum (small dot) image and scale it.
    # -------------------------------------------------------------------
    def _load_pacgum(self) -> Optional[Surface]:
        # ===============================================================
        #   IMG - PACGUM
        # ===============================================================
        # LOADING PATH ASSETS -------------------------------------------
        path = (
            self.assets_base / "gum" / "pacgum.png"
        )
        if not path.exists():
            logger.warning(
                "%s not found. Pacgums won't be visible.",
                path,
            )
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            return self._scale_gum_asset(img, ratio=0.22, min_size=4)
        except pygame.error as e:
            logger.error("Failed to load pacgum image: %s", e)
            return None

    # -------------------------------------------------------------------
    #   Load super-pacgum image and scale it.
    # -------------------------------------------------------------------
    def _load_super_pacgum(self) -> Optional[Surface]:

        path = self.assets_base / "gum" / "super_pacgum.png"

        if not path.exists():
            logger.warning(
                "%s not found. Super-pacgums won't be visible.",
                path,
            )
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            return self._scale_gum_asset(
                img,
                ratio=0.4,
                min_size=8
            )
        except pygame.error as e:
            logger.error(
                "Failed to load super-pacgum image: %s",
                e,
            )
            return None

    # -------------------------------------------------------------------
    #   Load Pac-Man icon and scale it.
    # -------------------------------------------------------------------
    def _load_pacman_icon(self) -> Optional[Surface]:

        path = self.assets_base / "player" / "animation" / "Player_start.png"

        if not path.exists():
            logger.warning(
                "Pac-Man icon not found: %s",
                path,
            )
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            return self._scale_entity_asset(img, ratio=0.8, min_size=12)
        except pygame.error as e:
            logger.error(
                "Failed to load Pac-Man icon: %s",
                e,
            )
            return None

    # -------------------------------------------------------------------
    #   Asset availability check
    # -------------------------------------------------------------------
    def _ensure_assets_available(self) -> None:
        """Validate that all required rendering assets are present.

        Mandatory:
        - wall masks 0-15         (``wall/intersections/wall_*.png``)
        - intersection masks 0-15 (``wall/intersections/intersection_*.png``)

        The frame (``wall/double/*``) uses a fallback to the:
            wall assets : if missing, it does not prevent startup.

        Raises:
            MissingRequiredAssetsError : If a mandatory asset is missing.
        """
        missing_walls = [
            m for m in range(16) if m not in self.wall_tiles
        ]
        missing_intersections = [
            m for m in range(16) if m not in self.intersection_tiles
        ]

        details: list[str] = []
        if missing_walls:
            details.append(f"wall masks {missing_walls}")
        if missing_intersections:
            details.append(
                f"intersection masks {missing_intersections}"
            )

        if details:
            raise MissingRequiredAssetsError(details)
