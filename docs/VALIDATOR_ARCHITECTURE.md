# XOSC Validator Plugin Architecture

## Architecture

### Folder Structure

```
src/openscenario_builder/core/
├── plugins/
│   ├── xosc_scenario_validator_plugin.py  # Main orchestrator (auto-loaded)
│   └── plugin_manager.py
└── utils/
    ├── validators/                         # Specialized validators (not plugins)
    │   ├── schema_structure_validator.py
    │   ├── reference_validator.py
    │   ├── datatype_validator.py
    │   ├── structure_validator.py
    │   ├── uniqueness_validator.py
    │   └── min_occur_validator.py          # Minimum occurrence validator
    └── validation_helpers/                 # Shared utilities
        ├── type_validators.py
        ├── element_collectors.py
        └── recursive_validator.py
```

### Main Orchestrator

**`XoscScenarioValidatorPlugin`** (v3.1.0)
- Comprehensive validator that orchestrates all specialized validators
- Runs validators in optimal order for error detection

### Specialized Validators

#### 1. **XoscSchemaStructureValidator**
**Purpose**: Validates elements, attributes, and children against XSD schema definitions

**Validates**:
- Unknown elements
- Unknown attributes
- Required attributes
- Attribute data types
- Enumerated attribute values
- Valid child elements
- Group references

**Example Errors**:
- `SCHEMA_ERROR`: Unknown element 'InvalidElement'
- `ATTRIBUTE_ERROR`: Unknown attribute 'invalidAttr'
- `REQUIRED_ATTRIBUTE_ERROR`: Missing required attribute 'name'
- `TYPE_ERROR`: Invalid type for attribute 'speed', expected double
- `VALUE_ERROR`: Invalid enumerated value
- `STRUCTURE_ERROR`: Invalid child element

---

#### 2. **XoscReferenceValidator**
**Purpose**: Validates all references can be resolved to their declarations

**Validates**:
- Entity references (`entityRef`, `objectRef`, `actorRef`)
- Variable references (`variableRef`)
- Parameter references (values starting with `$`)
- Storyboard element references (`actRef`, `maneuverRef`, `eventRef`, `actionRef`)
- Traffic signal controller references
- Traffic signal ID references

**Example Errors**:
- `REFERENCE_ERROR`: Entity reference 'Ego' cannot be resolved
- `REFERENCE_ERROR`: Parameter reference 'Speed' not found
- `REFERENCE_ERROR`: Variable reference 'Distance' not declared

---

#### 3. **XoscDataTypeValidator**
**Purpose**: Validates data type constraints and domain-specific rules

**Validates**:
- Non-negative values (transition times, speeds, distances, times)
- Positive values (durations)
- Probability ranges (0-1)
- Numeric values (accelerations can be negative)

**Example Errors**:
- `DATA_TYPE_ERROR`: Transition time must be non-negative
- `DATA_TYPE_ERROR`: Duration must be positive
- `DATA_TYPE_ERROR`: Probability must be between 0 and 1
- `DATA_TYPE_ERROR`: Speed must be non-negative

---

#### 4. **XoscStructureValidator**
**Purpose**: Validates OpenSCENARIO document structure requirements

**Validates**:
- Required `FileHeader` element
- Required FileHeader attributes (`revMajor`, `revMinor`, `date`, `description`)
- Document hierarchy

**Example Errors**:
- `STRUCTURE_ERROR`: FileHeader element is required
- `STRUCTURE_ERROR`: FileHeader missing required attribute 'revMajor'

---

#### 5. **XoscUniquenessValidator**
**Purpose**: Validates name uniqueness constraints within scope

**Validates**:
- Unique names within the same parent scope
- Reports all duplicate names with counts

**Example Errors**:
- `UNIQUENESS_ERROR`: Duplicate name 'Act1' found in 2 elements

---

#### 6. **XoscMinOccurValidator**
**Purpose**: Validates minimum occurrence constraints for elements

**Validates**:
- Required elements (minOccurs ≥ 1) are present
- Choice groups have exactly one option selected
- Sequence and all content models have all required children
- Nested group references are properly expanded

**Validation Rules**:
- **Sequence/All Groups**: All required children (minOccurs > 0) must be present
- **Choice Groups**: Exactly one choice must be selected (not zero, not multiple)
- **Group References**: Recursively validates nested group requirements

**Example Errors**:
- `OCCURRENCE_ERROR`: Missing required element 'Act' at path 'OpenSCENARIO/Storyboard/Story'. This element is mandatory and must be present exactly once.
- `OCCURRENCE_ERROR`: Missing required choice from group 'ActionGroup' at path 'OpenSCENARIO/Storyboard/Story/Act/ManeuverGroup/Maneuver/Event/Action'. Must select one of: PrivateAction, GlobalAction.
- `OCCURRENCE_ERROR`: Invalid choice selection at path 'Story/Act'. Found multiple choice groups satisfied: PrivateAction, GlobalAction. Only one choice is allowed.
- `OCCURRENCE_ERROR`: Insufficient occurrences of element 'Waypoint' at path 'Route'. Found 1 instances but 2 are required.

---

### Shared Utilities

**`validation_helpers/`**
Contains reusable utility modules organized by responsibility:

#### `type_validators.py` - ValidationUtils
- `is_valid_attribute_value()`: Check if value is non-empty
- `is_valid_parameter_pattern()`: Validate `$` parameter syntax
- `validate_attribute_type()`: Type validation (int, double, boolean, etc.)
- `get_type_validation_hint()`: User-friendly type hints
- `expand_children_with_groups()`: Expand schema group references

#### `element_collectors.py` - ElementCollector
- `collect_entities()`: Collect all entity declarations
- `collect_variables()`: Collect variable declarations
- `collect_parameters()`: Collect parameter declarations
- `collect_storyboard_elements()`: Collect Acts, Events, Actions, etc.
- `collect_traffic_elements()`: Collect traffic signals and controllers

#### `recursive_validator.py` - RecursiveValidator
- `traverse_and_validate()`: Apply validation function to element tree

## Validation Order

The orchestrator runs validators in this order:

1. **Schema Structure** - Catches basic structural errors first
2. **Document Structure** - Validates OpenSCENARIO requirements
3. **Minimum Occurrence** - Validates required elements are present
4. **References** - Ensures all references can be resolved
5. **Data Types** - Validates domain-specific constraints
6. **Uniqueness** - Checks name uniqueness

This order optimizes error detection by catching fundamental issues before more specific validations.

## Usage

```python
from openscenario_builder.core.plugins.xosc_scenario_validator_plugin import XoscScenarioValidatorPlugin

# Create validator instance
validator = XoscScenarioValidatorPlugin()

# Validate a scenario
errors = validator.validate(element, schema_info)

# Process errors
for error in errors:
    print(error)
```

## Testing

Comprehensive test suites are provided for each validator:

- `test_validator_utils.py` - Utility functions and helpers
- `test_xosc_schema_structure_validator.py` - Schema validation
- `test_xosc_reference_validator.py` - Reference validation
- `test_xosc_datatype_validator.py` - Data type validation
- `test_xosc_structure_validator.py` - Structure validation
- `test_xosc_uniqueness_validator.py` - Uniqueness validation
- `test_xosc_scenario_validator_plugin.py` - Orchestrator

**Note**: All validators (including `XoscMinOccurValidator`) are integrated into the orchestrator and tested through comprehensive test suites.

Run all tests:
```bash
pytest tests/unit/core/plugins/ -v
```

## Future Enhancements

Potential improvements for future versions:

1. **Parallel Validation**: Run independent validators concurrently
2. **Configurable Validators**: Allow users to enable/disable specific validators
3. **Custom Validators**: Plugin system for user-defined validators
4. **Error Recovery**: Suggestions and auto-fix capabilities
5. **Performance Metrics**: Detailed timing for each validator
6. **Incremental Validation**: Validate only changed portions of scenarios

## Contributing

When adding new validation logic:

1. Determine which specialized validator should handle it
2. Add the validation logic to that validator
3. Add comprehensive tests
4. Update documentation
5. Ensure backward compatibility

If the validation doesn't fit existing validators, consider creating a new specialized validator following the same pattern.

## License

See main project LICENSE file.

---

**Version**: 3.1.0  
**Last Updated**: October 17, 2025  
**Author**: Ziqi Zhou
