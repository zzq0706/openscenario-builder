# Schema-Aware Element Creation

## Overview

Create OpenSCENARIO elements with automatic schema validation, catching errors at creation time instead of during later validation.

## Quick Start

```python
from openscenario_builder.core.schema.parser import parse_openscenario_schema
from openscenario_builder.core.model.element_factory import ElementFactory

# Load schema once (reuse for multiple elements)
schema_info = parse_openscenario_schema("OpenSCENARIO_v1_3.xsd")
factory = ElementFactory(schema_info, strict=True)

# Create validated element - catches errors immediately
element = factory.create("FileHeader", {
    "revMajor": "1",
    "revMinor": "3",
    "date": "2025-10-12T00:00:00",
    "description": "My scenario",
    "author": "my author"
})
```

## Two Approaches

### 1. ElementFactory - Explicit Validation

```python
factory = ElementFactory(schema_info, strict=True)

# Create element with validation
element = factory.create("FileHeader", {...})

# These will raise ValueError:
invalid = factory.create("InvalidElement")  # Element not in schema
bad_attr = factory.create("FileHeader", {"wrongAttr": "value"})  # Invalid attribute
```

### 2. ElementBuilder - Fluent API

```python
from openscenario_builder.core.model.element_builder import ElementBuilder

builder = ElementBuilder(schema_info, strict=True)

# Create element with fluent chaining
element = (builder
    .element("FileHeader")
    .attr("revMajor", "1")
    .attr("revMinor", "3")
    .attr("date", "2025-10-12T00:00:00")
    .attr("description", "My scenario")
    .attr("author", "John Doe")
    .build())

# Child validation in strict mode
parent = builder.element("Parent").attr("name", "Test")

# Check if child is allowed before adding
if builder.is_child_allowed("Child"):
    child = builder.element("Child").attr("id", "child1").build()
    parent.child(child) 

story = parent.build()
```

## Schema Discovery API

Query schema constraints before creating elements:

```python
# Required attributes
required = factory.get_required_attributes("FileHeader")
# ['revMajor', 'revMinor', 'date', 'description', 'author']

# Allowed children
children = factory.get_allowed_children("OpenSCENARIO")
# ['FileHeader', 'GROUP:OpenScenarioCategory']

# Complete element info
info = factory.get_element_info("ScenarioObject")
# {'required_attributes': ['name'], 'allowed_children': [...], ...}

# Validate child addition
errors = factory.validate_child_addition("Parent", "Child")
```

## Validation Modes

**Strict (default)** - Raises exceptions on errors:
```python
factory = ElementFactory(schema_info, strict=True)
element = factory.create("InvalidElement")  # ❌ Raises ValueError
```

**Permissive** - Creates element but tracks errors:
```python
factory = ElementFactory(schema_info, strict=False)
element = factory.create("InvalidElement")  # ✓ Creates element
errors = factory.get_validation_errors(element)  # Check errors later
```

## Examples

See working examples:
- `examples/demo_schema_aware.py` - Interactive demonstration
- `examples/create_validated_scenario.py` - Complete examples

Run the demo:
```bash
python examples/demo_schema_aware.py
```

