# Schema-Aware Element Creation

## Overview

Create OpenSCENARIO elements with automatic schema validation, catching errors at creation time instead of during later validation.

## Quick Start

```python
from openscenario_builder.core.schema.parser import parse_openscenario_schema
from openscenario_builder.core.model.element_factory import ElementFactory

# Load schema once
schema_info = parse_openscenario_schema("OpenSCENARIO_v1_3.xsd")
factory = ElementFactory(schema_info, strict=True)

# Create validated element
element = factory.create("FileHeader", {
    "revMajor": "1",
    "revMinor": "3",
    "date": "2025-10-12T00:00:00",
    "description": "My scenario",
    "author": "John Doe"
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

builder = ElementBuilder(schema_info)

element = (builder
    .element("FileHeader")
    .attr("revMajor", "1")
    .attr("revMinor", "3")
    .attr("date", "2025-10-12T00:00:00")
    .attr("description", "My scenario")
    .attr("author", "John Doe")
    .build())
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

## Common Patterns

### Basic Element Creation

```python
factory = ElementFactory(schema_info)
element = factory.create("FileHeader", {
    "revMajor": "1",
    "revMinor": "3",
    "date": "2025-10-12T00:00:00",
    "description": "Test",
    "author": "John"
})
```

### Nested Structure with Builder

```python
builder = ElementBuilder(schema_info)

scenario = builder.element("OpenSCENARIO").build()

header = (builder
    .element("FileHeader")
    .attrs({...})
    .build())

scenario.add_child(header)
```

### Discovery-Driven Creation

```python
# Check what's required first
info = factory.get_element_info("ScenarioObject")
print(f"Required attrs: {info['required_attributes']}")

# Create with required attributes
element = factory.create("ScenarioObject", {
    attr: "value" for attr in info['required_attributes']
})
```

## API Reference

### ElementFactory Methods

```python
# Create element
create(tag, attrs=None, children=None, strict=None) -> IElement

# Create with required attrs auto-filled
create_with_required_attrs(tag, attrs=None, auto_fill_defaults=False) -> IElement

# Discovery methods
get_required_attributes(tag) -> List[str]
get_optional_attributes(tag) -> List[str]
get_allowed_children(tag) -> List[str]
get_all_attributes(tag) -> Dict[str, Dict[str, Any]]
get_element_info(tag) -> Optional[Dict[str, Any]]

# Validation
validate_child_addition(parent_tag, child_tag) -> List[str]
get_validation_errors(element) -> List[str]
```

### ElementBuilder Methods

```python
# Set element type
element(tag) -> ElementBuilder

# Add attributes
attr(name, value) -> ElementBuilder
attrs(attributes_dict) -> ElementBuilder

# Add children
child(child_element) -> ElementBuilder
children(children_list) -> ElementBuilder

# Build
build() -> IElement
build_with_defaults() -> IElement

# Query (requires element() called first)
get_required_attrs() -> List[str]
get_optional_attrs() -> List[str]
get_allowed_children() -> List[str]
```

## Examples

See working examples:
- `examples/demo_schema_aware.py` - Interactive demonstration
- `examples/create_validated_scenario.py` - Complete examples

Run the demo:
```bash
python examples/demo_schema_aware.py
```

## Benefits

✅ **Early error detection** - Catch typos and mistakes immediately  
✅ **Better developer experience** - Know what's allowed before creating  
✅ **Higher code quality** - Impossible to create invalid structures  
✅ **Type safety** - Validation at creation time  
✅ **Backwards compatible** - Existing code still works  
