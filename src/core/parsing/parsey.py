"""Parses a JSON configuration file with comment support.

Lines starting with ``#`` are treated as comments and ignored.
The parser is designed to be robust: invalid values are replaced with
safe defaults, unknown keys are logged and ignored, and all errors are
reported through custom exceptions without tracebacks.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .parser_exceptions import (
    ConfigFileNotFound,
    ConfigParserError
)

logger = logging.getLogger(__name__)


class ConfigHelper:
    """Utility class for configuration parsing operations."""

    @staticmethod
    def safe_int(
        value: Any,
        default: int,
        key: str,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int | Any:
        """Convert a value to int, falling back to default on error/range.

        If the value is not an integer (e.g., float, string, None), it is
        considered invalid and the default is returned with a warning.
        Floats that represent whole numbers are also rejected to keep the
        configuration strict and predictable.

        Args:
            value: The raw value from the configuration file.
            default: The default value to use if conversion or range fails.
            key: The name of the key being parsed, for log messages.
            min_value: Optional minimum allowed value.
            max_value: Optional maximum allowed value.

        Returns:
            The parsed int, or default if invalid.
        """
        # Strict type check: reject bool (subclass of int) and float
        if isinstance(value, bool) or not isinstance(value, int):
            logger.warning(
                "Invalid type for %s: %r (expected int). Using default %d.",
                key,
                value,
                default,
            )
            return default

        int_value = value
        if min_value is not None and int_value < min_value:
            logger.warning(
                "Value for %s out of range: %d < %d. Using default %d.",
                key,
                int_value,
                min_value,
                default,
            )
            return default

        if max_value is not None and int_value > max_value:
            logger.warning(
                "Value for %s out of range: %d > %d. Using default %d.",
                key,
                int_value,
                max_value,
                default,
            )
            return default

        return int_value

    @staticmethod
    def strip_comments(text: str) -> str:
        """Remove lines that start with ``#`` after optional whitespace.

        Args:
            text: The raw text of the configuration file.

        Returns:
            Text with comment lines removed.
        """
        lines = []
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            lines.append(line)
        return "\n".join(lines)


@dataclass
class LevelConfig:
    """Configuration for a single level.

    Attributes:
        width: Width of the maze (must be >= 1).
        height: Height of the maze (must be >= 1).
    """

    DEFAULT_WIDTH = 21
    DEFAULT_HEIGHT = 21
    MIN_DIMENSION = 1
    MAX_DIMENSION = 100

    width: int
    height: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LevelConfig":
        """Create a LevelConfig from a dictionary, applying defaults.

        Args:
            data: Dictionary containing optional 'width' and 'height' keys.

        Returns:
            A LevelConfig instance with validated values.
        """
        return cls(
            width=ConfigHelper.safe_int(
                data.get("width"),
                cls.DEFAULT_WIDTH,
                "width",
                min_value=cls.MIN_DIMENSION,
                max_value=cls.MAX_DIMENSION,
            ),
            height=ConfigHelper.safe_int(
                data.get("height"),
                cls.DEFAULT_HEIGHT,
                "height",
                min_value=cls.MIN_DIMENSION,
                max_value=cls.MAX_DIMENSION,
            ),
        )


@dataclass
class GameConfig:
    """Global game configuration with robust defaults.

    Attributes:
        lives: Number of starting lives (>= 1).
        seed: Random seed for level generation (>= 0).
        pacgum: Total number of pacgums per level (>= 0).
        points_per_pacgum: Points awarded for each pacgum (>= 0).
        points_per_super_pacgum: Points for super pacgums (>= 0).
        points_per_ghost: Points for edible ghosts (>= 0).
        level_max_time: Time limit per level in seconds (>= 1).
        # TODO: Add frightened_duration and frightened_flash_duration here.
        highscore_filename: Name of the highscore file.
        levels: List of validated LevelConfig objects.
    """

    # -------------------------------------------------------
    # NOTE: STATO FLASH NON FUNZIONANTE - VEDI ANCHE PACAN.PY
    # -------------------------------------------------------
    # TODO: Add frightened_duration and frightened_flash_duration here.
    # These values will configure the frightened timer and its final
    # flashing phase for the UI.

    DEFAULT_LIVES = 3
    DEFAULT_PACGUM = 42
    DEFAULT_POINTS_PER_PACGUM = 10
    DEFAULT_POINTS_PER_SUPER_PACGUM = 50
    DEFAULT_POINTS_PER_GHOST = 200
    DEFAULT_SEED = 42
    DEFAULT_LEVEL_MAX_TIME = 90
    DEFAULT_HIGHSCORE_FILENAME = "highscores.json"

    # -------------------------------------------------------
    # Validity ranges
    # -------------------------------------------------------
    MIN_LIVES = 1
    MAX_LIVES = 99
    MIN_PACGUM = 0
    MAX_PACGUM = 1000
    MIN_POINTS = 0
    MAX_POINTS = 100000
    MIN_SEED = 0
    MAX_SEED = 2**32 - 1
    MIN_TIME = 1
    MAX_TIME = 3600

    lives: int
    seed: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    level_max_time: int
    highscore_filename: str
    levels: list[LevelConfig]

    @classmethod
    def _parse_levels(cls, data: dict[str, Any]) -> list[LevelConfig]:
        """Parse and validate the 'levels' key from config data.

        Handles missing key, empty list, non-list values, and invalid
        entries by falling back to a single default level.

        Args:
            data: The parsed configuration dictionary.

        Returns:
            A list of LevelConfig objects (never empty).
        """
        levels_data = data.get("levels")

        # Case 1: Missing or empty levels
        if not isinstance(levels_data, list) or len(levels_data) == 0:
            logger.warning(
                "No valid 'levels' found. Using one default level (%dx%d).",
                LevelConfig.DEFAULT_WIDTH,
                LevelConfig.DEFAULT_HEIGHT,
            )
            return [LevelConfig.from_dict({})]

        # Case 2: Filter out non-dict entries
        valid_levels = [lv for lv in levels_data if isinstance(lv, dict)]

        if len(valid_levels) == 0:
            logger.warning(
                "All level entries were invalid. Using one default level "
                "(%dx%d).",
                LevelConfig.DEFAULT_WIDTH,
                LevelConfig.DEFAULT_HEIGHT,
            )
            return [LevelConfig.from_dict({})]

        if len(valid_levels) < len(levels_data):
            logger.warning(
                "Ignoring %d invalid level entries (not objects).",
                len(levels_data) - len(valid_levels),
            )

        # Case 3: Parse all valid levels
        levels = []
        for i, lv in enumerate(valid_levels):
            try:
                levels.append(LevelConfig.from_dict(lv))
            except Exception as e:  # Defensive: should not happen
                logger.error(
                    "Unexpected error parsing level %d: %s. Using default.",
                    i,
                    e,
                )
                levels.append(LevelConfig.from_dict({}))

        return levels

    @classmethod
    def _parse_highscore_filename(cls, data: dict[str, Any]) -> str:
        """Parse and validate the highscore filename.

        Args:
            data: The parsed configuration dictionary.

        Returns:
            A valid filename string (never empty).
        """
        raw_highscore = data.get(
            "highscore_filename", cls.DEFAULT_HIGHSCORE_FILENAME
        )

        # Must be a non-empty string
        if not isinstance(raw_highscore, str) or not raw_highscore.strip():
            logger.warning(
                "Invalid highscore_filename (must be non-empty string). "
                "Using default '%s'.",
                cls.DEFAULT_HIGHSCORE_FILENAME,
            )
            return cls.DEFAULT_HIGHSCORE_FILENAME

        # Sanitize: strip whitespace, ensure .json extension
        filename = raw_highscore.strip()
        if not filename.endswith(".json"):
            logger.warning(
                "highscore_filename '%s' should end with .json. "
                "Appending extension.",
                filename,
            )
            filename += ".json"

        return filename

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GameConfig":
        """Create a GameConfig from a dictionary, applying defaults.

        This method is defensive: any missing key, wrong type, or
        out-of-range value results in a safe default and a warning log.
        The resulting GameConfig is always valid.

        Args:
            data: Dictionary with configuration keys.

        Returns:
            A fully validated GameConfig instance.
        """
        # Parse levels first (most complex)
        levels = cls._parse_levels(data)

        # Parse highscore filename (special string handling)
        highscore_filename = cls._parse_highscore_filename(data)

        # Parse all integer values with range validation
        # -------------------------------------------------------
        # NOTE: STATO FLASH NON FUNZIONANTE
        # -------------------------------------------------------
        # NOTE: New frightened timing values must follow this path:
        # config.json -> data.get(...) -> ConfigHelper.safe_int(...)
        # -> GameConfig field -> core timer/UI consumer.
        return cls(
            lives=ConfigHelper.safe_int(
                data.get("lives"),
                cls.DEFAULT_LIVES,
                "lives",
                min_value=cls.MIN_LIVES,
                max_value=cls.MAX_LIVES,
            ),
            seed=ConfigHelper.safe_int(
                data.get("seed"),
                cls.DEFAULT_SEED,
                "seed",
                min_value=cls.MIN_SEED,
                max_value=cls.MAX_SEED,
            ),
            pacgum=ConfigHelper.safe_int(
                data.get("pacgum"),
                cls.DEFAULT_PACGUM,
                "pacgum",
                min_value=cls.MIN_PACGUM,
                max_value=cls.MAX_PACGUM,
            ),
            points_per_pacgum=ConfigHelper.safe_int(
                data.get("points_per_pacgum"),
                cls.DEFAULT_POINTS_PER_PACGUM,
                "points_per_pacgum",
                min_value=cls.MIN_POINTS,
                max_value=cls.MAX_POINTS,
            ),
            points_per_super_pacgum=ConfigHelper.safe_int(
                data.get("points_per_super_pacgum"),
                cls.DEFAULT_POINTS_PER_SUPER_PACGUM,
                "points_per_super_pacgum",
                min_value=cls.MIN_POINTS,
                max_value=cls.MAX_POINTS,
            ),
            points_per_ghost=ConfigHelper.safe_int(
                data.get("points_per_ghost"),
                cls.DEFAULT_POINTS_PER_GHOST,
                "points_per_ghost",
                min_value=cls.MIN_POINTS,
                max_value=cls.MAX_POINTS,
            ),
            level_max_time=ConfigHelper.safe_int(
                data.get("level_max_time"),
                cls.DEFAULT_LEVEL_MAX_TIME,
                "level_max_time",
                min_value=cls.MIN_TIME,
                max_value=cls.MAX_TIME,
            ),
            highscore_filename=highscore_filename,
            levels=levels,
        )


class ConfigLoader:
    """Handles file I/O and JSON parsing, then delegates to GameConfig.

    This class is responsible for:
    - Reading the configuration file
    - Stripping comment lines (starting with #)
    - Parsing JSON content
    - Validating the top-level structure (must be a JSON object)
    - Delegating detailed field validation to GameConfig

    All errors are raised as ConfigError subclasses, never as raw
    exceptions, ensuring the CLI can handle them cleanly.
    """

    def __init__(self, filepath: str | Path) -> None:
        """Initialize with the configuration file path.

        Args:
            filepath: Path to the JSON configuration file.

        Raises:
            TypeError: If filepath is not a string or Path.
        """
        if not isinstance(filepath, (str, Path)):
            raise TypeError(
                "filepath must be str or Path, got "
                f"{type(filepath).__name__}"
            )
        self.filepath = Path(filepath)

    def _strip_comments(self, text: str) -> str:
        """Remove comment lines from the text (delegates to ConfigHelper).

        Args:
            text: The raw text content of the file.

        Returns:
            Text with comment lines removed.
        """
        return ConfigHelper.strip_comments(text)

    def load(self) -> GameConfig:
        """Parse the configuration file and return a GameConfig object.

        Returns:
            A GameConfig instance with validated values.

        Raises:
            ConfigFileNotFound:
                If the file does not exist or cannot be read.
            ConfigParserError:
                If the content is not valid JSON or not an object.
        """
        # --------------------------------------------------------------------
        # Step 1: Read file
        # --------------------------------------------------------------------

        # In ConfigLoader.load(), prima del try di lettura file:
        # Note: CLIValidator already checks file existence, but ConfigLoader
        # is designed to be usable independently (e.g., in tests or other
        # entry points). This is defense-in-depth, not redundancy.

        try:
            raw_txt = self.filepath.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise ConfigFileNotFound(
                f"Configuration file not found: {self.filepath}"
            ) from e
        except PermissionError as e:
            raise ConfigFileNotFound(
                f"Cannot read configuration file "
                f"(permission denied): {self.filepath}"
            ) from e
        except IsADirectoryError as e:
            raise ConfigFileNotFound(
                f"Configuration path is a directory, not a file: "
                f"{self.filepath}"
            ) from e
        except UnicodeDecodeError as e:
            raise ConfigParserError(
                f"Configuration file must be UTF-8 encoded: {self.filepath}"
            ) from e
        except OSError as e:
            raise ConfigFileNotFound(
                f"Cannot read configuration file {self.filepath}: {e}"
            ) from e

        # --------------------------------------------------------------------
        # Step 2: Strip comments and parse JSON
        # --------------------------------------------------------------------
        try:
            json_txt = self._strip_comments(raw_txt)
            data = json.loads(json_txt)
        except json.JSONDecodeError as e:
            raise ConfigParserError(
                f"Invalid JSON in file {self.filepath} "
                f"at line {e.lineno}, column {e.colno}: {e.msg}"
            ) from e

        # --------------------------------------------------------------------
        # Step 3: Validate top-level structure
        # --------------------------------------------------------------------
        if not isinstance(data, dict):
            raise ConfigParserError(
                "Configuration file must contain a JSON object "
                "(dictionary), not an array or scalar value."
            )

        # --------------------------------------------------------------------
        # Step 4: Log unknown keys but do not fail
        # --------------------------------------------------------------------
        known_keys = {
            "lives",
            "seed",
            "pacgum",
            "points_per_pacgum",
            "points_per_super_pacgum",
            "points_per_ghost",
            "level_max_time",
            "highscore_filename",
            "levels",
        }
        unknown_keys = set(data.keys()) - known_keys
        if unknown_keys:
            logger.warning(
                "Ignoring unknown config keys: %s",
                ", ".join(sorted(unknown_keys)),
            )

        # --------------------------------------------------------------------
        # Step 5: Delegate to GameConfig for detailed validation
        # --------------------------------------------------------------------
        config = GameConfig.from_dict(data)

        # --------------------------------------------------------------------
        # Step 6: Post-validation for cross-field constraints
        # --------------------------------------------------------------------
        from .parser_validator import PostValidation

        post_validator = PostValidation()
        issues_found = post_validator.validate(config)

        if issues_found:
            logger.info(
                "Post-validation found %d warning(s)",
                len(issues_found)
            )
            for issue in issues_found:
                logger.info(
                    "   %s",
                    issue
                )

        return config
