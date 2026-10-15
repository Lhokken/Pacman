"""Pixel-buffer image operations with MLX-compatible semantics."""

from __future__ import annotations

import numpy as np
import pygame
from pygame.surface import Surface


class ImageScaler:
    """Provide image-scaling operations over RGBA pixel buffers."""

    @staticmethod
    def nearest_neighbor(
        image: Surface,
        size: tuple[int, int],
    ) -> pygame.surface.Surface:
        """Resize an RGBA image using nearest-neighbor pixel sampling.

        Args:
            image : Source image surface.
            size  : Target width and height in pixels.

        Returns:
            A new surface with the requested dimensions.

        Raises:
            ValueError y: If either target dimension is not positive.
        """
        target_width, target_height = size
        if target_width <= 0 or target_height <= 0:
            raise ValueError(
                "Target image dimensions must be positive"
            )

        source_width, source_height = image.get_size()
        if (source_width, source_height) == size:
            return image.copy()

        rgba = np.frombuffer(
            pygame.image.tobytes(image, "RGBA"),
            dtype=np.uint8,
        ).reshape((source_height, source_width, 4))
        source_x = (
            (2 * np.arange(target_width) + 1) * source_width
            // (2 * target_width)
        )
        source_y = (
            (2 * np.arange(target_height) + 1) * source_height
            // (2 * target_height)
        )
        source_x = np.minimum(source_x, source_width - 1)
        source_y = np.minimum(source_y, source_height - 1)
        resized = rgba[source_y[:, None], source_x[None, :]]

        result: Surface = pygame.image.frombytes(
            resized.tobytes(), size, "RGBA"
        )
        return result