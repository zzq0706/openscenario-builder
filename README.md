# OpenSCENARIO Builder

A professional, extensible tool for creating and editing and validating OpenSCENARIO files with a modern Python architecture.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- **Schema-Driven**: Automatically generates element definitions from OpenSCENARIO XSD schemas
- **Plugin Architecture**: Extensible through custom plugins for validation, import/export, and UI
- **Qt-based UI**: Modern desktop application with intuitive interface
- **Real-time Validation**: Comprehensive scenario validation against schema with detailed error messages
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Video Demos

### Validation Demo

Watch how to validate OpenSCENARIO scenario files using the `openscenario-validate` command-line tool:

[![Validation Demo](./sources/validation/validate_scenario_example.mp4)](./sources/validation/validate_scenario_example.mp4)

**Direct link**: [Validation Demo Video](./sources/validation/validate_scenario_example.mp4)


## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/your-org/openscenario-builder.git
cd openscenario-builder

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### From PyPI (once published)

```bash
pip install openscenario-builder
```

## Quick Start

### Run the QT-based application
```bash
python -m openscenario_builder
```

### Validate OpenSCENARIO files
```bash
# Validate a single file
openscenario-validate scenario.xosc

# Validate multiple files
openscenario-validate file1.xosc file2.xosc file3.xosc

# Validate all files in a directory (recursive)
openscenario-validate scenarios/

# With verbose output for detailed errors
openscenario-validate --verbose scenario.xosc
```

For more CLI options and examples, see the [CLI Quick Reference](docs/CLI_QUICK_REFERENCE.md).

## Validation

OpenSCENARIO Builder includes a comprehensive validation system that checks scenarios against the XSD schema. The validation is performed by **7 specialized validators** that work together:

### Validator Types

1. **Schema Structure Validator** (`XoscSchemaStructureValidator`)
   - Validates elements, attributes, and children against XSD schema definitions
   - Checks for unknown elements/attributes, required attributes, attribute data types, and enumerated values

2. **Reference Validator** (`XoscReferenceValidator`)
   - Validates all references can be resolved to their declarations
   - Checks entity references (`entityRef`, `objectRef`, `actorRef`), variable references, parameter references, and storyboard element references

3. **Data Type Validator** (`XoscDataTypeValidator`)
   - Validates data type constraints and domain-specific rules
   - Ensures non-negative values (speeds, distances, times), positive values (durations), and valid probability ranges (0-1)

4. **Structure Validator** (`XoscStructureValidator`)
   - Validates OpenSCENARIO document structure requirements
   - Checks for required `FileHeader` element and required attributes

5. **Uniqueness Validator** (`XoscUniquenessValidator`)
   - Validates name uniqueness constraints within scope
   - Ensures unique names within the same parent scope

6. **Minimum Occurrence Validator** (`XoscMinOccurValidator`)
   - Validates minimum occurrence constraints for elements
   - Ensures required elements are present and choice groups have exactly one option selected

7. **Sequence Order Validator** (`XoscSequenceOrderValidator`)
   - Validates element ordering for sequence content models
   - Ensures child elements appear in the correct order as defined by the schema

These validators run in an optimized order to catch fundamental issues before more specific validations. For detailed information, see the [Validator Architecture documentation](docs/VALIDATOR_ARCHITECTURE.md).

## Examples

- **create_simple_scenario.py**: Basic OpenSCENARIO file creation
- **create_validated_scenario.py**: Schema-aware element creation with validation
- **validate_scenario.py**: Validate existing XOSC files

```bash
# Basic creation
python examples/create_simple_scenario.py

# Schema-aware creation
python examples/create_validated_scenario.py

# Validate a scenario
python examples/validate_scenario.py scenario.xosc schemas/OpenSCENARIO_v1_3.xsd
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenSCENARIO](https://www.asam.net/standards/detail/openscenario/) community
- [Qt/PySide6](https://doc.qt.io/qtforpython/) team

---

**Note**: This package is currently in private development. It will be open sourced in the future.
