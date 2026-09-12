"""Manages loading and scaling of all game sprites."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pygame
from pygame.surface import Surface

logger = logging.getLogger(__name__)


class AssetManager:
    """Loads and caches sprite images scaled to the current tile size.

    Attributes:
        assets_base: Root path containing all image assets.
        tile_size: Current tile size in pixels.
        player_img: Player sprite (None if missing).
        wall_tiles: Dict mapping logical wall mask (0-15) to Surface.
        intersection_tiles: Dict mapping logical intersection mask (0-15)
            to Surface.
        border_tiles: Dict mapping border key to Surface.
        ghost_images: List of 4 ghost Surfaces (may contain None).
        pacgum_img: Small dot sprite.
        super_pacgum_img: Power pellet sprite.
        fruit_icon: Fruit icon for panel.
        pacman_icon: Pac-Man icon for lives panel.
    """

    def __init__(self, assets_base: Path, tile_size: int) -> None:
        """Initialize and load all assets.

        Args:
            assets_base: Root path containing image assets.
            tile_size: Initial tile size for scaling.
        """
        self.assets_base = assets_base
        self.tile_size = tile_size
        self.load_all()

    def load_all(self) -> None:
        """Load or reload all assets using current tile size."""
        self.player_frames, self.player_img = self._load_player()
        self.wall_tiles = self._load_wall_tiles()
        self.intersection_tiles = self._load_intersection_tiles()
        self.border_tiles = self._load_border_tiles()
        self.ghost_images, self.ghost_frames = self._load_ghosts()
        self.pacgum_img = self._load_pacgum()
        self.super_pacgum_img = self._load_super_pacgum()
        self.fruit_icon = self._load_fruit_icon()
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
        return pygame.transform.smoothscale(image, (size, size))

    def _load_player(self) -> tuple[list[Surface], Optional[Surface]]:
        """Load player animation frames.

        Returns:
            Tuple (frames, static_img).
            frames: List of 3 Surfaces for walk animation.
            static_img: First frame (for fallback/static display).
        """
        player_dir = self.assets_base / "player" / "animation"
        frame_files = [
            "Player_start.png",
            "Player_mid.png",
            "Player_end.png",
        ]
        frames: list[Surface] = []
        static_img: Optional[Surface] = None
        frame_files.sort()
        for idx, fname in enumerate(frame_files):
            path = player_dir / fname
            if not path.exists():
                logger.warning(
                    "%s not found. Player animation frame missing.",
                    path
                )
                continue
            try:
                img = pygame.image.load(path).convert_alpha()
                img = self._scale_entity_asset(img, ratio=0.8, min_size=12)
                frames.append(img)
                if idx == 0:
                    static_img = img
            except pygame.error as e:
                logger.error(
                    "Failed to load player frame %s: %s",
                    fname,
                    e
                )

        return frames, static_img

    # ====================================================================
    #   Private helper methods for loading and scaling specific assets
    # ====================================================================

    # --------------------------------------------------------------------
    #   Load wall tiles for each mask (0-15).
    # --------------------------------------------------------------------
    def _load_wall_tiles(self) -> dict[int, Surface]:
        """Load wall tiles for each mask.

        Returns:
            Dictionary mapping mask values to their corresponding
            tile surfaces.
        """
        assets_dir = self.assets_base / "wall" / "single"
        tiles: dict[int, Surface] = {}
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
                tile = pygame.transform.scale(
                    tile, (self.tile_size, self.tile_size)
                )
                tiles[mask] = tile
            except pygame.error as e:
                logger.error("Failed to load wall tile %s: %s", tile_path, e)
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
                tile = pygame.transform.scale(
                    tile, (self.tile_size, self.tile_size)
                )
                tiles[mask] = tile
            except pygame.error as e:
                logger.error(
                    "Failed to load intersection tile %s: %s", tile_path, e
                )
        return tiles

    # --------------------------------------------------------------------
    #   Load border tiles for each mask (corner and T-junctions).
    # --------------------------------------------------------------------
    def _load_border_tiles(self) -> dict[str, Surface]:
        """Load border tiles for each mask.

        Returns:
            Dictionary mapping mask values to their corresponding
            tile surfaces.
        """
        assets_dir = self.assets_base / "wall" / "double"
        file_to_key = {
            "corner_tl": "corner_tl",
            "corner_tr": "corner_tr",
            "corner_bl": "corner_bl",
            "corner_br": "corner_br",
            "t_up": "top",
            "t_down": "bottom",
            "t_left": "left",
            "t_right": "right",
        }
        tiles: dict[str, Surface] = {}
        for file_name, key in file_to_key.items():
            path = assets_dir / f"{file_name}.png"
            if not path.exists():
                logger.warning("Border tile %s not found.", path)
                continue
            try:
                tile = pygame.image.load(path).convert_alpha()
                tile = pygame.transform.scale(
                    tile, (self.tile_size, self.tile_size)
                )
                tiles[key] = tile
            except pygame.error as e:
                logger.error("Failed to load border tile %s: %s", path, e)
        return tiles

    # --------------------------------------------------------------------
    #   Load ghost sprites and animation frames.
    # --------------------------------------------------------------------
    def _load_ghosts(
        self
    ) -> tuple[list[Optional[Surface]], list[list[Surface]]]:
        """Load ghost sprites and animation frames.

        Returns:
            A tuple (static_images, animation_frames).
            static_images: first frame (or None) for each ghost.
            animation_frames: list of frame lists for idle animation.
        """
        assets_base = self.assets_base / "ghost"
        static_images: list[Optional[Surface]] = []
        animation_frames: list[list[Surface]] = []
        for name in [
            "blinky",
            "pinky",
            "inky",
            "clyde"
        ]:
            # -----------------------------------------------------------------
            #   1. Load static ghost.png
            # -----------------------------------------------------------------
            path = (
                assets_base / name / "ghost.png"
            )
            static_img = None
            if path.exists():
                try:
                    img = pygame.image.load(path).convert_alpha()
                    static_img = self._scale_entity_asset(
                        img,
                        ratio=0.8,
                        min_size=12,
                    )
                except pygame.error as e:
                    logger.error(
                        "Failed to load ghost %s: %s", name, e
                    )
            else:
                logger.warning(
                    "%s not found. Ghost %s won't be visible.",
                    path,
                    name
                )
            static_images.append(static_img)

            # -----------------------------------------------------------------
            #   2. Load animation frames from the actual ghost sprite folders.
            # -----------------------------------------------------------------
            animation_dirs = [
                assets_base / name / "look_right",
                assets_base / name / "look_right" / "direct",
                assets_base / name / "look_right" / "straight_ahead",
            ]
            frames: list[Surface] = []
            found_dir = False
            for animation_dir in animation_dirs:
                # commento
                if not animation_dir.exists():
                    continue
                # commento
                found_dir = True
                frame_files = sorted(
                    animation_dir.glob("*.png")
                )
                for frame_path in frame_files:
                    try:
                        frame = pygame.image.load(frame_path).convert_alpha()
                        frame = self._scale_entity_asset(
                            frame,
                            ratio=0.8,
                            min_size=12,
                        )
                        frames.append(frame)
                    except pygame.error as e:
                        logger.error(
                            "Failed to load animation frame %s: %s",
                            frame_path,
                            e,
                        )
            if not found_dir:
                logger.debug(
                    "No animation directory found for ghost %s in %s",
                    name,
                    assets_base / name,
                )
            animation_frames.append(frames)

        return static_images, animation_frames

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
        size = max(min_size, int(self.tile_size * ratio))
        return pygame.transform.smoothscale(image, (size, size))

    # -------------------------------------------------------------------
    #   Load pacgum (small dot) image and scale it.
    # -------------------------------------------------------------------
    def _load_pacgum(self) -> Optional[Surface]:

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
            return self._scale_gum_asset(img, ratio=0.4, min_size=8)
        except pygame.error as e:
            logger.error("Failed to load super-pacgum image: %s", e)
            return None

    # -------------------------------------------------------------------
    #   Load fruit icon and scale it.
    # -------------------------------------------------------------------
    def _load_fruit_icon(self) -> Optional[Surface]:
        path = self.assets_base / "fruit" / "cherry.png"
        if not path.exists():
            logger.warning("Fruit icon not found: %s", path)
            # Fallback red circle
            size = max(1, self.tile_size)
            fallback = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(
                fallback, (255, 0, 0), (size // 2, size // 2), size // 2
            )
            return fallback
        try:
            img = pygame.image.load(path).convert_alpha()
            size = max(1, self.tile_size)
            return pygame.transform.scale(img, (size, size))
        except pygame.error as e:
            logger.error("Failed to load fruit icon: %s", e)
            return None

    # -------------------------------------------------------------------
    #   Load Pac-Man icon and scale it.
    # -------------------------------------------------------------------
    def _load_pacman_icon(self) -> Optional[Surface]:

        path = self.assets_base / "player" / "animation" / "Player_start.png"
        if not path.exists():
            logger.warning(
                "Pac-Man icon not found: %s", path
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
        """Raise RuntimeError only if essential maze tiles are missing."""
        missing_walls = [m for m in range(16) if m not in self.wall_tiles]
        missing_intersections = [
            m for m in range(16) if m not in self.intersection_tiles
        ]
        required_border = {
            "corner_tl",
            "corner_tr",
            "corner_bl",
            "corner_br",
            "top",
            "bottom",
            "left",
            "right",
        }
        missing_border = required_border - set(self.border_tiles.keys())
        # CONTROLLO: Missing intersection
        if missing_intersections:
            logger.warning(
                "Intersection tiles are missing; continuing without them: %s",
                missing_intersections,
            )
        # CONTROLLO: Missing Walls
        if missing_walls or missing_border:
            details = []
            if missing_walls:
                details.append(
                    f"wall/single masks {missing_walls}"
                )
            if missing_border:
                details.append(
                    f"wall/double tiles {sorted(missing_border)}"
                )
            raise RuntimeError(
                "Missing required rendering assets: " + "; ".join(details)
            )
