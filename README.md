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
python -m openscenario_builder

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
