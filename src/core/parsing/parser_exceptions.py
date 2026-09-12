"""Custom exceptions for configuration parsing errors."""


# --------------------------------------------------------------------------
#   CLI configuration errors
# --------------------------------------------------------------------------
class ConfigError(Exception):
    """Base exception for configuration errors.

    Attributes:
        message: Explanation of the error.
        line_nbr: Optional line number where the error occurred.
    """

    def __init__(self, message: str, line_nbr: int | None = None) -> None:
        """Initialize the exception.

        Args:
            message: A description of the error.
            line_nbr: The line number where the error occurred (optional).
        """
        if line_nbr is not None:
            super().__init__(f"Line {line_nbr}: {message}")
        else:
            super().__init__(message)


class ConfigFileNotFound(ConfigError):
    """Raised when the configuration file cannot be found."""


class ConfigParserError(ConfigError):
    """Raised when the configuration file cannot be parsed."""


# --------------------------------------------------------------------------
#   Data invalidity errors
# --------------------------------------------------------------------------
class MissingLevelError(ConfigError):
    """Raised if configuration file does not contain the required nbr of lv.

    This covers both the case where no levels are defined at all and the
    case where fewer than the minimum required levels are present.
    """


class InvalidLevelError(ConfigError):
    """Raised when a level contains missing or invalid data."""


class InvalidConfigValueError(ConfigError):
    """Raised when a configuration value has an invalid type or range."""
