# OpenSCENARIO Builder Examples

This directory contains example scripts demonstrating how to use the OpenSCENARIO Builder library.

## Prerequisites

Make sure you have installed the package:

```bash
pip install -e .
```

## Examples

### 1. Create a Simple Scenario

Create a basic OpenSCENARIO file programmatically:

```bash
python examples/create_simple_scenario.py
```

This will generate a `simple_scenario.xosc` file with:
- FileHeader
- Parameter declarations
- Road network reference
- A single ego vehicle
- Basic initialization

### 2. Validate a Scenario

Validate an existing OpenSCENARIO file against the schema:

```bash
python examples/validate_scenario.py simple_scenario.xosc src/openscenario_builder/core/schema/OpenSCENARIO_v1_3.xsd
```

This will:
- Load the XSD schema
- Parse the XOSC file
- Run all validation plugins
- Report any errors found
