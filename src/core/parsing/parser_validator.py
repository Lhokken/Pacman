"""Post-parsing validation for game configuration.

This module provides a final validation layer that runs after the
configuration has been parsed and defaults applied. It checks semantic
constraints that cannot be verified field-by-field (e.g., cross-field
relationships between pacgum count and maze dimensions).

Critical violations raise exceptions; non-critical issues are logged
as warnings and collected for reporting.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto

from .parser_exceptions import (
    InvalidConfigValueError,
    InvalidLevelError,
    MissingLevelError,
)
from .parsey import GameConfig

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Severity level for validation issues."""

    WARNING = auto()
    ERROR = auto()


@dataclass
class ValidationIssue:
    """Represents a single non-critical validation problem.

    Attributes:
        message: Human-readable description of the issue.
        severity: The severity level (always WARNING for non-critical).
    """

    message: str
    severity: Severity


class PostValidation:
    """Validator for post-parsing configuration checks.

    Performs cross-field validation that cannot be done during
    individual field parsing. Critical violations raise exceptions;
    non-critical issues are collected as warnings.
    """

    # Minimum playable maze dimensions
    MIN_MAZE_WIDTH = 5
    MIN_MAZE_HEIGHT = 5

    # Minimum number of levels required by the game specification
    MIN_LEVELS = 10

    # Fraction of maze area that can reasonably be filled with pacgums
    PACGUM_AREA_FRACTION = 3  # 1/3 of total area

    def __init__(self) -> None:
        """Initialize the post-validator."""
        self.issues: list[ValidationIssue] = []

    def validate(self, config: GameConfig) -> list[ValidationIssue]:
        """Validate a parsed GameConfig.

        Performs cross-field checks. Critical violations raise
        exceptions; non-critical issues are collected and returned.

        Args:
            config: The configuration to validate.

        Returns:
            A list of ValidationIssue objects (non-critical only).

        Raises:
            MissingLevelError: If the number of levels is below the
                minimum required.
            InvalidLevelError: If a level has dimensions too small to
                generate a playable maze.
            InvalidConfigValueError: If pacgum count exceeds the maximum
                possible for any level.
        """
        self.issues = []
        self._check_minimum_levels(config)
        self._check_level_dimensions_critical(config)
        self._check_pacgum_capacity(config)
        self._check_time_reasonable(config)
        self._check_dimensions_odd(config)
        return self.issues

    def _check_minimum_levels(self, config: GameConfig) -> None:
        """Raise MissingLevelError if fewer than MIN_LEVELS levels exist.

        Raises:
            MissingLevelError: If the configuration defines fewer than
                the required number of levels.
        """
        if len(config.levels) < self.MIN_LEVELS:
            raise MissingLevelError(
                f"configuration must define at least {self.MIN_LEVELS} "
                f"levels, found {len(config.levels)}"
            )

    def _check_level_dimensions_critical(self, config: GameConfig) -> None:
        """Raise InvalidLevelError if dimensions are too small to play.

        Raises:
            InvalidLevelError: If width or height is below the minimum.
        """
        for i, level in enumerate(config.levels):
            if (
                level.width < self.MIN_MAZE_WIDTH
                or level.height < self.MIN_MAZE_HEIGHT
            ):
                raise InvalidLevelError(
                    f"Level {i}: dimensions {level.width}x{level.height} "
                    f"are too small for a playable maze "
                    f"(minimum: {self.MIN_MAZE_WIDTH}x{self.MIN_MAZE_HEIGHT})"
                )

    def _check_pacgum_capacity(self, config: GameConfig) -> None:
        """Raise InvalidConfigValueError if pacgum exceeds maze capacity.

        Raises:
            InvalidConfigValueError: If pacgum count cannot fit in any level.
        """
        for i, level in enumerate(config.levels):
            # Estimate corridor cells: roughly 1/3 of total area
            max_capacity = (
                (level.width * level.height) // self.PACGUM_AREA_FRACTION
            )
            if config.pacgum > max_capacity:
                raise InvalidConfigValueError(
                    f"pacgum count ({config.pacgum}) exceeds maximum "
                    f"capacity for level {i} "
                    f"({level.width}x{level.height}, max {max_capacity})"
                )

    def _check_time_reasonable(self, config: GameConfig) -> None:
        """Log warning if time limit seems too short for maze size."""
        for i, level in enumerate(config.levels):
            maze_area = level.width * level.height
            # Rough heuristic: 1 second per 4 cells, minimum 30s
            min_reasonable = max(30, maze_area // 4)
            if config.level_max_time < min_reasonable:
                issue = ValidationIssue(
                    f"Level {i}: time limit ({config.level_max_time}s) "
                    f"may be too short for {level.width}x{level.height} "
                    f"maze (suggested: {min_reasonable}s)",
                    Severity.WARNING,
                )
                self.issues.append(issue)
                logger.warning("%s", issue)

    def _check_dimensions_odd(self, config: GameConfig) -> None:
        """Log warning if dimensions are even (maze generators prefer odd)."""
        for i, level in enumerate(config.levels):
            if level.width % 2 == 0 or level.height % 2 == 0:
                issue = ValidationIssue(
                    f"Level {i}: dimensions {level.width}x{level.height} "
                    f"are even; maze generators typically require odd "
                    f"dimensions",
                    Severity.WARNING,
                )
                self.issues.append(issue)
                logger.warning("%s", issue)
