"""
OpenSCENARIO Validator CLI
A command-line tool for validating OpenSCENARIO files against the schema.
Supports single files or batch validation of multiple files for CI/CD integration.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional
import glob

from openscenario_builder.core.schema.parser import parse_openscenario_schema
from openscenario_builder.core.plugins.plugin_manager import PluginManager


class ValidationResult:
    """Stores validation results for a single file"""

    def __init__(self, file_path: str, is_valid: bool, errors: List[str]):
        self.file_path = file_path
        self.is_valid = is_valid
        self.errors = errors


class ScenarioValidator:
    """Handles OpenSCENARIO file validation"""

    def __init__(self, schema_path: str, verbose: bool = False):
        """
        Initialize the validator

        Args:
            schema_path: Path to the OpenSCENARIO XSD schema file
            verbose: Enable verbose logging
        """
        self.schema_path = schema_path
        self.verbose = verbose
        self.schema_info = None
        self.plugin_manager = None

        # Setup logging
        log_level = logging.DEBUG if verbose else logging.WARNING
        logging.basicConfig(
            level=log_level,
            format="%(levelname)s: %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def initialize(self) -> bool:
        """
        Initialize schema and plugins

        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            # Parse schema
            if self.verbose:
                print(f"Loading schema from: {self.schema_path}")

            self.schema_info = parse_openscenario_schema(self.schema_path)

            if self.verbose:
                print(f"✓ Schema loaded ({len(self.schema_info.elements)} elements)")

            # Initialize plugin manager
            self.plugin_manager = PluginManager()

            # Add plugin path
            plugin_path = Path(__file__).parent.parent / "core" / "plugins"

            if plugin_path.exists():
                self.plugin_manager.add_plugin_path(str(plugin_path))

                # Load plugins
                loaded = self.plugin_manager.load_plugins()

                if self.verbose:
                    print(
                        f"✓ Loaded {loaded['validator']} validator plugin(s), "
                        f"{loaded['import']} import plugin(s)"
                    )
            else:
                self.logger.error(f"Plugin path not found: {plugin_path}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()
            return False

    def validate_file(self, file_path: str) -> ValidationResult:
        """
        Validate a single OpenSCENARIO file

        Args:
            file_path: Path to the scenario file

        Returns:
            ValidationResult object
        """
        try:
            # Check initialization
            if not self.plugin_manager or not self.schema_info:
                return ValidationResult(
                    file_path, False, ["Validator not properly initialized"]
                )

            # Import scenario using plugin manager
            scenario = self.plugin_manager.import_scenario(file_path)

            if not scenario:
                return ValidationResult(
                    file_path,
                    False,
                    ["Failed to import scenario - invalid XML or file not found"],
                )

            # Validate using plugins
            errors = self.plugin_manager.validate_scenario(scenario, self.schema_info)

            return ValidationResult(file_path, len(errors) == 0, errors)

        except Exception as e:
            self.logger.error(f"Validation error for {file_path}: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()
            return ValidationResult(
                file_path, False, [f"Validation exception: {str(e)}"]
            )

    def validate_files(self, file_paths: List[str]) -> List[ValidationResult]:
        """
        Validate multiple OpenSCENARIO files

        Args:
            file_paths: List of file paths to validate

        Returns:
            List of ValidationResult objects
        """
        results = []
        for file_path in file_paths:
            results.append(self.validate_file(file_path))
        return results


def find_default_schema() -> Optional[str]:
    """
    Find the default OpenSCENARIO schema file

    Returns:
        Path to schema file or None if not found
    """
    possible_paths = [
        "schemas/OpenSCENARIO_v1_3.xsd",
        "../schemas/OpenSCENARIO_v1_3.xsd",
        "../../schemas/OpenSCENARIO_v1_3.xsd",
    ]

    for path in possible_paths:
        if Path(path).exists():
            return str(Path(path).resolve())

    return None


def collect_files(patterns: List[str]) -> List[str]:
    """
    Collect files from glob patterns

    Args:
        patterns: List of file patterns (can include wildcards)

    Returns:
        List of resolved file paths
    """
    files = []
    for pattern in patterns:
        # If it's a directory, find all .xosc files
        if Path(pattern).is_dir():
            pattern = str(Path(pattern) / "**" / "*.xosc")

        matched = glob.glob(pattern, recursive=True)
        files.extend(matched)

    # Remove duplicates and return absolute paths
    return [str(Path(f).resolve()) for f in set(files)]


def print_results(results: List[ValidationResult], verbose: bool = False) -> None:
    """
    Print validation results

    Args:
        results: List of validation results
        verbose: Show detailed error messages
    """
    total = len(results)
    valid = sum(1 for r in results if r.is_valid)
    invalid = total - valid

    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    # Print individual results
    for result in results:
        status = "✓ VALID" if result.is_valid else "✗ INVALID"
        print(f"\n{status}: {result.file_path}")

        if not result.is_valid and result.errors:
            if verbose:
                for i, error in enumerate(result.errors, 1):
                    print(f"  {i}. {error}")
            else:
                print(
                    f"  {len(result.errors)} error(s) found (use --verbose for details)"
                )

    # Print summary
    print("\n" + "=" * 70)
    print(f"SUMMARY: {valid}/{total} files valid, {invalid} invalid")
    print("=" * 70)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Validate OpenSCENARIO files against the schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a single file
  openscenario-validate scenario.xosc

  # Validate multiple files
  openscenario-validate scenario1.xosc scenario2.xosc

  # Validate all .xosc files in a directory
  openscenario-validate scenarios/

  # Validate with pattern matching
  openscenario-validate "tests/**/*.xosc"

  # Validate with custom schema
  openscenario-validate --schema my_schema.xsd scenario.xosc

  # Verbose output for CI/CD
  openscenario-validate --verbose scenarios/

Exit Codes:
  0 - All files are valid
  1 - One or more files are invalid or validation failed
  2 - Command-line arguments error
        """,
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="OpenSCENARIO file(s) to validate (supports wildcards and directories)",
    )

    parser.add_argument(
        "-s",
        "--schema",
        help="Path to OpenSCENARIO XSD schema file (default: auto-detect)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed validation errors"
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Minimal output (only summary)"
    )

    parser.add_argument(
        "--fail-fast", action="store_true", help="Stop validation on first error"
    )

    parser.add_argument(
        "--version", action="version", version="openscenario-validate 1.0.0"
    )

    args = parser.parse_args()

    # Find schema file
    schema_path = args.schema
    if not schema_path:
        schema_path = find_default_schema()
        if not schema_path:
            print(
                "Error: Could not find default schema file. "
                "Please specify using --schema",
                file=sys.stderr,
            )
            sys.exit(2)

    if not Path(schema_path).exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(2)

    # Collect files to validate
    try:
        files_to_validate = collect_files(args.files)
    except Exception as e:
        print(f"Error collecting files: {e}", file=sys.stderr)
        sys.exit(2)

    if not files_to_validate:
        print("Error: No files found to validate", file=sys.stderr)
        sys.exit(2)

    # Check that all files exist
    missing_files = [f for f in files_to_validate if not Path(f).exists()]
    if missing_files:
        print("Error: The following files do not exist:", file=sys.stderr)
        for f in missing_files:
            print(f"  - {f}", file=sys.stderr)
        sys.exit(2)

    if not args.quiet:
        print(f"Validating {len(files_to_validate)} file(s) against schema...")
        if args.verbose:
            print(f"Schema: {schema_path}")

    # Initialize validator
    validator = ScenarioValidator(schema_path, verbose=args.verbose)

    if not validator.initialize():
        print("Error: Failed to initialize validator", file=sys.stderr)
        sys.exit(1)

    # Validate files
    results = []
    all_valid = True

    for file_path in files_to_validate:
        result = validator.validate_file(file_path)
        results.append(result)

        if not result.is_valid:
            all_valid = False

            # Fail fast if requested
            if args.fail_fast:
                if not args.quiet:
                    print(f"\n✗ Validation failed for: {file_path}")
                    if args.verbose and result.errors:
                        for error in result.errors:
                            print(f"  - {error}")
                print("\nStopping validation (--fail-fast)", file=sys.stderr)
                sys.exit(1)

    # Print results
    if not args.quiet:
        print_results(results, verbose=args.verbose)
    else:
        # Minimal output
        valid_count = sum(1 for r in results if r.is_valid)
        print(f"{valid_count}/{len(results)} valid")

    # Exit with appropriate code
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
