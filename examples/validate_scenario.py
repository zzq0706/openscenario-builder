"""
Example: Validate an OpenSCENARIO file
"""

import sys
from pathlib import Path
from openscenario_builder.core.schema.parser import parse_openscenario_schema
from openscenario_builder.core.plugins.plugin_manager import PluginManager
from openscenario_builder.core.plugins.import_plugin import ImportPlugin


def validate_scenario(file_path: str, schema_path: str):
    """Validate an OpenSCENARIO file against the schema"""

    print(f"Validating: {file_path}")
    print("-" * 50)

    # Parse schema
    print("Loading schema...")
    schema_info = parse_openscenario_schema(schema_path)
    print(f"✓ Schema loaded ({len(schema_info.elements)} elements)")

    # Import scenario
    print(f"\nImporting scenario...")
    importer = ImportPlugin()
    scenario = importer.import_scenario(file_path)

    if not scenario:
        print("✗ Failed to import scenario")
        return False

    print(f"✓ Scenario imported: {scenario.tag}")

    # Initialize plugin manager and load validators
    print(f"\nLoading validation plugins...")
    plugin_manager = PluginManager()

    # Add plugin path
    plugin_path = Path(__file__).parent.parent / "src" / "openscenario_builder" / "core" / "plugins"
    plugin_manager.add_plugin_path(str(plugin_path))

    # Load plugins
    loaded = plugin_manager.load_plugins()
    print(f"✓ Loaded {loaded['validator']} validator(s)")

    # Validate
    print(f"\nValidating scenario...")
    errors = plugin_manager.validate_scenario(scenario, schema_info)

    if errors:
        print(f"\n✗ Found {len(errors)} validation error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
        return False
    else:
        print("\n✓ Scenario is valid!")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python validate_scenario.py <scenario.xosc> <schema.xsd>")
        print("\nExample:")
        print("  python validate_scenario.py simple_scenario.xosc schemas/OpenSCENARIO_v1_3.xsd")
        sys.exit(1)

    scenario_file = sys.argv[1]
    schema_file = sys.argv[2]

    if not Path(scenario_file).exists():
        print(f"Error: Scenario file not found: {scenario_file}")
        sys.exit(1)

    if not Path(schema_file).exists():
        print(f"Error: Schema file not found: {schema_file}")
        sys.exit(1)

    success = validate_scenario(scenario_file, schema_file)
    sys.exit(0 if success else 1)
