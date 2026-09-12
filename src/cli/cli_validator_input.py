"""Post parsing validation for command line arguments.

This module checks that the configuration file path provided by
the user is valid and usable: the file must exist, be a regular
file, and have a ``.json`` extension.
"""

from __future__ import annotations

from pathlib import Path

from .cli_args_parser import CliArgs
from .cli_exceptions import CliValidationError


class CLIValidator:
    """Validate parsed command-line arguments."""

    def validate(self, args: CliArgs) -> None:
        """Validate the parsed CLI arguments.

        The validation is intentionally strict: any problem causes
        a :class:`CliValidationError` to be raised immediately.
        The program is expected to terminate after the first error,
        so no further checks are performed once a failure is found.

        The following checks are performed in order:

        1. File extension must be ``.json``
        2. File must exist
        3. Path must point to a regular file (not a directory)
        4. File must be readable with UTF-8 encoding

        Args:
            args: The parsed command line arguments.

        Raises:
            CliValidationError: If the configuration file path has the
                wrong extension, does not exist, is not a regular file,
                or is not readable.
        """
        config_path = Path(args.config_path)
        # ----------------------------------------------------------------
        # Step 1: Verify file extension is .json
        # ----------------------------------------------------------------
        if config_path.suffix.lower() != ".json":
            raise CliValidationError(
                "Configuration file must be a JSON file: "
                f"'{args.config_path}'"
            )

        if not config_path.exists():
            raise CliValidationError(
                "Configuration file not found: "
                f"'{args.config_path}'"
            )

        if not config_path.is_file():
            raise CliValidationError(
                "Configuration path is not a regular file: "
                f"'{args.config_path}'"
            )

        # ----------------------------------------------------------------
        # Step 2: Verify file is readable (permissions and encoding)
        # ----------------------------------------------------------------
        try:
            with config_path.open("r", encoding="utf-8"):
                pass
        except OSError as error:
            raise CliValidationError(
                "Cannot read configuration file "
                f"'{args.config_path}': {error}"
            ) from error
