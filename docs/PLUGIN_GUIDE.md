# Plugin Development Guide

## Plugin System Overview

The OpenSCENARIO Builder plugin system allows you to extend the application with custom functionality through well-defined interfaces.

## Plugin Location

Plugins can be placed in two locations:

1. **Built-in plugins**: `src/openscenario_builder/core/plugins/`
2. **External plugins**: `plugins/` directory in your project root (create if needed)

The plugin manager automatically discovers and loads plugins from both locations.

## Plugin Types

### 1. Element Plugins
Define custom XML elements with validation and UI support.

### 2. Validator Plugins
Add custom validation rules for scenarios.

### 3. Export Plugins
Support exporting scenarios to different file formats.

### 4. Import Plugins
Support importing scenarios from different file formats.

### 5. UI Plugins
Extend the user interface with custom widgets.

---

## Creating Plugins

### Element Plugin

Create custom XML elements with attributes and validation:

```python
from openscenario_builder.interfaces import IElementPlugin
from openscenario_builder.core.plugins.plugin_metadata import PluginMetadata
from typing import List, Dict

class MyCustomElementPlugin(IElementPlugin):
    """Plugin for a custom OpenSCENARIO element"""

    def __init__(self):
        self._activated = True

    @property
    def activated(self) -> bool:
        """Whether this plugin is activated"""
        return self._activated

    @activated.setter
    def activated(self, value: bool) -> None:
        """Set activation state"""
        self._activated = value

    @property
    def metadata(self) -> PluginMetadata:
        """Plugin metadata"""
        return PluginMetadata(
            name="My Custom Element Plugin",
            version="1.0.0",
            description="Adds support for custom elements",
            author="Your Name",
            license="MIT",
            tags=["element", "custom"]
        )

    def get_element_name(self) -> str:
        """Return the element tag name"""
        return "MyCustomElement"

    def get_category(self) -> str:
        """Return the category for UI grouping"""
        return "Custom"

    def get_attributes(self) -> List[Dict[str, str]]:
        """Define element attributes"""
        return [
            {"name": "id", "type": "string", "required": True},
            {"name": "value", "type": "double", "required": False}
        ]

    def get_allowed_children(self) -> List[str]:
        """Define allowed child elements"""
        return ["ChildElement1", "ChildElement2"]

    def get_description(self) -> str:
        """Description for UI"""
        return "A custom element for special purposes"

    def validate(self, element) -> List[str]:
        """Custom validation logic"""
        errors = []

        # Example: Check value range
        if "value" in element.attrs:
            try:
                value = float(element.attrs["value"])
                if value < 0 or value > 100:
                    errors.append(f"Value must be between 0 and 100, got {value}")
            except ValueError:
                errors.append(f"Value must be a number")

        return errors
```

---

### Validator Plugin

Add custom validation rules that run when validating scenarios:

```python
from openscenario_builder.interfaces import IValidatorPlugin, IElement, ISchemaInfo
from openscenario_builder.core.plugins.plugin_metadata import PluginMetadata
from typing import List, Optional

class MyValidatorPlugin(IValidatorPlugin):
    """Custom validation plugin"""

    def __init__(self):
        self._activated = True

    @property
    def activated(self) -> bool:
        return self._activated

    @activated.setter
    def activated(self, value: bool) -> None:
        self._activated = value

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Custom Validator",
            version="1.0.0",
            description="Validates custom business rules",
            author="Your Name",
            tags=["validation", "custom"]
        )

    def get_name(self) -> str:
        """Validator name"""
        return "My Custom Validator"

    def validate(self, element: IElement,
                        schema_info: Optional[ISchemaInfo] = None) -> List[str]:
        """
        Validate element and return list of error messages.

        Args:
            element: Root element to validate
            schema_info: Schema information (optional)

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Example: Check for required FileHeader
        if element.tag == "OpenSCENARIO":
            has_header = any(child.tag == "FileHeader" for child in element.children)
            if not has_header:
                errors.append("ERROR: FileHeader is required in OpenSCENARIO")

        # Recursively validate children
        for child in element.children:
            errors.extend(self.validate(child, schema_info))

        return errors
```

---

### Export Plugin

Support exporting scenarios to custom formats:

```python
from openscenario_builder.interfaces import IExportPlugin, IElement
from openscenario_builder.core.plugins.plugin_metadata import PluginMetadata
from typing import List
import json

class JSONExportPlugin(IExportPlugin):
    """Export scenarios to JSON format"""

    def __init__(self):
        self._activated = True

    @property
    def activated(self) -> bool:
        return self._activated

    @activated.setter
    def activated(self, value: bool) -> None:
        self._activated = value

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="JSON Export Plugin",
            version="1.0.0",
            description="Exports scenarios to JSON format",
            author="Your Name",
            tags=["export", "json"]
        )

    def export_scenario(self, scenario: IElement, output_path: str) -> bool:
        """
        Export scenario to file.

        Args:
            scenario: Root element to export
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert element to dictionary
            data = self._element_to_dict(scenario)

            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False

    def get_supported_formats(self) -> List[str]:
        """Return supported file extensions"""
        return [".json"]

    def get_format_description(self, format_ext: str) -> str:
        """Return description for format"""
        if format_ext == ".json":
            return "JSON format (.json)"
        return "Unknown format"

    def _element_to_dict(self, element: IElement) -> dict:
        """Convert element to dictionary"""
        return {
            "tag": element.tag,
            "attributes": element.attrs,
            "children": [self._element_to_dict(child) for child in element.children]
        }
```

---

### Import Plugin

Support importing scenarios from custom formats:

```python
from openscenario_builder.interfaces import IImportPlugin, IElement
from openscenario_builder.core.plugins.plugin_metadata import PluginMetadata
from openscenario_builder.core.model.element import Element
from typing import List, Optional
import json

class JSONImportPlugin(IImportPlugin):
    """Import scenarios from JSON format"""

    def __init__(self):
        self._activated = True

    @property
    def activated(self) -> bool:
        return self._activated

    @activated.setter
    def activated(self, value: bool) -> None:
        self._activated = value

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="JSON Import Plugin",
            version="1.0.0",
            description="Imports scenarios from JSON format",
            author="Your Name",
            tags=["import", "json"]
        )

    def import_scenario(self, file_path: str) -> Optional[IElement]:
        """
        Import scenario from file.

        Args:
            file_path: Input file path

        Returns:
            Root element if successful, None otherwise
        """
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert dictionary to element
            return self._dict_to_element(data)
        except Exception as e:
            print(f"Import failed: {e}")
            return None

    def get_supported_formats(self) -> List[str]:
        """Return supported file extensions"""
        return [".json"]

    def get_format_description(self, format_ext: str) -> str:
        """Return description for format"""
        if format_ext == ".json":
            return "JSON format (.json)"
        return "Unknown format"

    def _dict_to_element(self, data: dict) -> Element:
        """Convert dictionary to element"""
        element = Element(
            tag=data["tag"],
            attrs=data.get("attributes", {})
        )

        for child_data in data.get("children", []):
            child = self._dict_to_element(child_data)
            element.add_child(child)

        return element
```

---

## Installing Plugins

### Method 1: Built-in Plugin
Place your plugin in `src/openscenario_builder/core/plugins/`:

```
src/openscenario_builder/core/plugins/
├── my_custom_plugin.py          # Your plugin here
├── plugin_manager.py
└── ...
```

### Method 2: External Plugin
Create a `plugins/` directory in your project root:

```bash
mkdir plugins
# Place your plugin file here
```

```
openscenario-builder/
├── plugins/                      # External plugins
│   └── my_custom_plugin.py      # Your plugin
├── src/
└── ...
```

### Method 3: Multiple Plugin Paths
Programmatically add plugin paths:

```python
from openscenario_builder.core.plugins.plugin_manager import PluginManager

manager = PluginManager()
manager.add_plugin_path("/path/to/my/plugins")
manager.load_plugins()
```

---

## Testing Your Plugin

### Basic Test
```python
from my_custom_plugin import MyValidatorPlugin
from openscenario_builder.core.model.element import Element

# Create plugin instance
plugin = MyValidatorPlugin()

# Create test element
element = Element("OpenSCENARIO")

# Validate
errors = plugin.validate(element)
print(f"Validation errors: {errors}")
```

### Full Integration Test
```python
from openscenario_builder.core.plugins.plugin_manager import PluginManager
from openscenario_builder.core.schema.parser import parse_openscenario_schema

# Initialize plugin manager
manager = PluginManager()
manager.add_plugin_path("./plugins")
loaded = manager.load_plugins()
print(f"Loaded plugins: {loaded}")

# Load schema
schema_info = parse_openscenario_schema("path/to/schema.xsd")

# Validate scenario
errors = manager.validate_scenario(scenario, schema_info)
```

---

## Debugging Plugins

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Plugin Loading
```python
from openscenario_builder.core.plugins.plugin_manager import PluginManager

manager = PluginManager()
manager.add_plugin_path("./plugins")

# Discover without loading
discovered = manager.discover_plugins()
print(f"Discovered plugins: {discovered}")

# Load and check
loaded = manager.load_plugins()
print(f"Loaded plugins: {loaded}")

# Get plugin info
info = manager.get_plugin_info()
print(f"Plugin info: {info}")
```

---

## Examples

See the built-in plugins for complete examples:
- `src/openscenario_builder/core/plugins/xosc_scenario_validator_plugin.py`
- `src/openscenario_builder/core/plugins/xosc_min_occur_validator.py`
- `src/openscenario_builder/core/plugins/export_plugin.py`
- `src/openscenario_builder/core/plugins/import_plugin.py`

---

## 🤝 Contributing Plugins

To contribute your plugin to the main repository:

1. Ensure it follows the plugin interface
2. Add comprehensive tests
3. Document usage in docstrings
4. Create a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.
