# Schema-Aware Element Creation - Summary

## What Was Added

This feature addresses the problem of creating invalid OpenSCENARIO elements that only fail during validation. Now you can create elements with immediate schema validation.

## Key Components

### 1. ElementFactory
**File:** `src/openscenario_builder/core/model/element_factory.py`

Factory for creating schema-validated elements with immediate error detection.

```python
factory = ElementFactory(schema_info, strict=True)
element = factory.create("FileHeader", {...})  # Validates immediately
```

### 2. ElementBuilder  
**File:** `src/openscenario_builder/core/model/element_builder.py`

Fluent API for building elements with validation.

```python
element = (builder
    .element("FileHeader")
    .attr("revMajor", "1")
    .build())  # Validates on build
```

## Examples

### Simplified Examples

Both examples were simplified and print output reduced:

1. **`examples/create_validated_scenario.py`**
   - Shows ElementFactory and ElementBuilder usage
   - Minimal, focused output

2. **`examples/demo_schema_aware.py`**
   - Demonstrates manual vs schema-aware creation
   - Shows discovery API
   - Cleaner output

Run them:
```bash
python examples/create_validated_scenario.py
python examples/demo_schema_aware.py
```

## Documentation

### Single Focused Document

**`docs/SCHEMA_AWARE_CREATION.md`** - Complete guide covering:
- Quick start
- Two approaches (Factory & Builder)
- Schema discovery API
- Validation modes
- Common patterns
- API reference
- Examples

## What Changed

### Removed
- ❌ ScenarioBuilder class (too high-level, removed per user request)
- ❌ Redundant documentation files
- ❌ Excessive print statements in examples
- ❌ Duplicate content across docs

### Kept
- ✅ ElementFactory - Low-level with explicit validation
- ✅ ElementBuilder - Fluent API with validation
- ✅ Schema discovery API
- ✅ Both validation modes (strict/permissive)

### Updated
- ✅ README.md - Added schema-aware creation section
- ✅ Examples - Simplified and focused
- ✅ Documentation - Consolidated into one clear guide

## Usage

### Basic Pattern

```python
from openscenario_builder.core.schema.parser import parse_openscenario_schema
from openscenario_builder.core.model.element_factory import ElementFactory

# Load schema
schema_info = parse_openscenario_schema("OpenSCENARIO_v1_3.xsd")

# Create factory
factory = ElementFactory(schema_info, strict=True)

# Create validated elements
element = factory.create("FileHeader", {
    "revMajor": "1",
    "revMinor": "3",
    "date": "2025-10-12T00:00:00",
    "description": "My scenario",
    "author": "John Doe"
})
```

### Fluent Pattern

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

### Discovery Pattern

```python
# Query schema before creating
required = factory.get_required_attributes("FileHeader")
children = factory.get_allowed_children("OpenSCENARIO")
info = factory.get_element_info("ScenarioObject")

# Create based on discovery
element = factory.create("ScenarioObject", {
    attr: "value" for attr in info['required_attributes']
})
```

## Benefits

| Feature | Manual Creation | Schema-Aware Creation |
|---------|----------------|----------------------|
| Error Detection | Late (validation phase) | Early (creation time) |
| Invalid Elements | Accepted | Rejected immediately |
| Invalid Attributes | Accepted | Rejected immediately |
| Missing Required | Not detected | Detected immediately |
| Type Safety | None | At creation time |
| Developer Experience | Frustrating | Pleasant |

## Files Overview

### Core Implementation
- `src/openscenario_builder/core/model/element_factory.py` - Factory with validation
- `src/openscenario_builder/core/model/element_builder.py` - Fluent builder

### Examples
- `examples/create_validated_scenario.py` - Factory & Builder usage
- `examples/demo_schema_aware.py` - Interactive demonstration

### Documentation
- `docs/SCHEMA_AWARE_CREATION.md` - Complete guide
- `README.md` - Updated with quick start

## Next Steps

1. Try the examples:
   ```bash
   python examples/demo_schema_aware.py
   python examples/create_validated_scenario.py
   ```

2. Read the documentation:
   - See `docs/SCHEMA_AWARE_CREATION.md` for complete guide

3. Use in your code:
   - Replace manual `Element()` creation with `ElementFactory`
   - Use `ElementBuilder` for fluent API
   - Query schema with discovery methods

## Migration

### Before (Manual Creation)
```python
from openscenario_builder.core.model.element import Element

element = Element("FileHeader", {...})  # No validation
```

### After (Schema-Aware)
```python
from openscenario_builder.core.model.element_factory import ElementFactory

factory = ElementFactory(schema_info, strict=True)
element = factory.create("FileHeader", {...})  # Immediate validation
```
