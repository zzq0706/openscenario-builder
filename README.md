# OpenSCENARIO Builder

A professional, extensible tool for creating and editing OpenSCENARIO files with a modern Python architecture.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- **Schema-Driven**: Automatically generates element definitions from OpenSCENARIO XSD schemas
- **Plugin Architecture**: Extensible through custom plugins for validation, import/export, and UI
- **Qt-based UI**: Modern desktop application with intuitive interface
- **Real-time Validation**: Comprehensive schema validation with detailed error messages
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Architecture

```
openscenario-builder/
├── src/
│   └── openscenario_builder/     # Main package
│       ├── __init__.py
│       ├── __main__.py           # Entry point
│       ├── interfaces/           # Interface definitions (contracts)
│       ├── core/                 # Core implementation
│       │   ├── schema/           # XSD schema parsing
│       │   ├── model/            # Element data models
│       │   └── plugins/          # Plugin system
│       └── ui/                   # User interface
│           └── qt/               # Qt-based UI components
├── tests/                        # Test suite
├── examples/                     # Example scripts
├── docs/                         # Documentation
├── .github/                      # GitHub workflows and templates
├── pyproject.toml                # Project configuration
├── README.md                     # This file
├── LICENSE                       # MIT License
├── CONTRIBUTING.md               # Contribution guidelines
├── CODE_OF_CONDUCT.md            # Code of conduct
└── CHANGELOG.md                  # Version history
```

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

Check out the `examples/` directory for more:

- **create_simple_scenario.py**: Create a basic OpenSCENARIO file programmatically
- **validate_scenario.py**: Validate an existing XOSC file against the schema

```bash
# Create a simple scenario
python examples/create_simple_scenario.py

# Validate a scenario
python examples/validate_scenario.py scenario.xosc src/openscenario_builder/core/schema/OpenSCENARIO_v1_3.xsd
```

## Plugin System

Create custom plugins to extend functionality:

```python
from openscenario_builder.interfaces import IElementPlugin

class MyPlugin(IElementPlugin):
    def get_element_name(self) -> str:
        return "MyElement"

    def validate_element(self, element) -> List[str]:
        # Custom validation
        return []
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenSCENARIO](https://www.asam.net/standards/detail/openscenario/) community
- [Qt/PySide6](https://doc.qt.io/qtforpython/) team

---

**Note**: This package is currently in private development. It will be open sourced in the future.
