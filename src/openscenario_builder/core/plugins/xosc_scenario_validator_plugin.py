"""
XOSC Scenario Validator Plugin for OpenSCENARIO Builder
Validates all elements in the scenario against XOSC schema
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re
try:
    from .plugin_metadata import PluginMetadata
except ImportError:
    # Fallback for when loaded directly by plugin manager
    from openscenario_builder.core.plugins.plugin_metadata import PluginMetadata
from openscenario_builder.interfaces import IValidatorPlugin, IElement, ISchemaInfo, IAttributeDefinition, IGroupDefinition


class XoscScenarioValidatorPlugin(IValidatorPlugin):
    """XOSC Scenario Validator Plugin - Validates all elements in the scenario against schema"""

    def __init__(self):
        self._activated = True  # Default to activated

    @property
    def activated(self) -> bool:
        """Whether this plugin is activated and should be loaded"""
        return self._activated

    @activated.setter
    def activated(self, value: bool) -> None:
        """Set the activation state of this plugin"""
        self._activated = value

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="XOSC Scenario Schema Validator",
            version="2.0.0",
            description="Validates all elements in the scenario against XOSC schema with comprehensive checks including references, parameters, and data types",
            author="Ziqi Zhou",
            tags=["validation", "schema", "xosc"]
        )

    def validate_element(self, element: IElement, schema_info: Optional[ISchemaInfo] = None) -> List[str]:
        """Main validation method that validates the entire scenario"""
        if schema_info is None:
            return ["CONFIGURATION_ERROR: Schema information required for XOSC validation. Fix: Ensure OpenSCENARIO schema is properly loaded before validation."]

        errors = []

        # Validate the root element and all its children recursively
        errors.extend(self._validate_element_recursively(element, schema_info))

        # Perform additional comprehensive validation checks
        errors.extend(self._validate_basic_structure(element))
        errors.extend(self._validate_references(element))
        errors.extend(self._validate_special_data_types(element))

        return errors

    def _validate_element_recursively(self, element: IElement, schema_info: ISchemaInfo) -> List[str]:
        """Recursively validate an element and all its children against schema"""
        errors = []

        # Validate current element against schema
        element_errors = self._validate_element_against_schema(
            element, schema_info)
        errors.extend(element_errors)

        # Recursively validate all children
        for child in element.children:
            child_errors = self._validate_element_recursively(
                child, schema_info)
            # Prefix child errors with parent element path for better error reporting
            # errors.extend([f"{element.tag}.{error}" for error in child_errors])
            errors.extend(child_errors)

        return errors

    def _validate_element_against_schema(self, element: IElement, schema_info: ISchemaInfo) -> List[str]:
        """Validate a single element against the schema"""
        errors = []

        # Get element definition from schema
        element_def = schema_info.elements.get(element.tag)
        if not element_def:

            error_msg = f"SCHEMA_ERROR: Unknown element '{element.tag}' is not defined in OpenSCENARIO schema."
            error_msg += f" Location: Element path contains '{element.tag}'. Fix: Replace with a valid OpenSCENARIO element name."

            errors.append(error_msg)
            return errors

        # Validate attributes
        errors.extend(self._validate_element_attributes(
            element, element_def, schema_info.simple_type_definitions))

        # Validate children structure
        errors.extend(self._validate_element_children(element, element_def, schema_info))

        return errors

    def _validate_element_attributes(self, element: IElement, element_def: Dict[str, Any], simple_type_definitions: Dict[str, List[str]]) -> List[str]:
        """Validate element attributes against schema definition"""
        errors = []
        # Check for unknown attributes
        for attr_name in element.attrs.keys():
            if not any(attr["name"] == attr_name for attr in element_def.attributes):
                valid_attrs = [attr["name"] for attr in element_def.attributes]

                error_msg = f"ATTRIBUTE_ERROR: Unknown attribute '{attr_name}' for element '{element.tag}'."
                error_msg += f" Valid attributes for '{element.tag}': {', '.join(valid_attrs)}."
                error_msg += f" Fix: Remove '{attr_name}' or replace with a valid attribute name."

                errors.append(error_msg)

        # Validate attribute values and check required attributes
        for attr_def in element_def.attributes:
            # Type cast to IAttributeDefinition for better type safety
            attr_def_typed: IAttributeDefinition = attr_def
            attr_name = attr_def_typed["name"]
            attr_value = element.attrs.get(attr_name)

            # Check required attributes
            if attr_def_typed.get("required", False) and not self._is_valid_attribute_value(attr_value):
                attr_type = attr_def_typed.get("type", "string")
                error_msg = f"REQUIRED_ATTRIBUTE_ERROR: Required attribute '{attr_name}' is missing, empty, or contains only whitespace for element '{element.tag}'."
                error_msg += f" Expected type: {attr_type}."
                error_msg += f" Fix: Add '{attr_name}=\"[appropriate_value]\"' to the '{element.tag}' element."
                errors.append(error_msg)
                continue

            # Validate attribute type if value exists and is valid
            if self._is_valid_attribute_value(attr_value):
                attr_type = attr_def_typed.get("type", "string")
                if not self._validate_attribute_type(attr_value, attr_type):
                    if attr_value.startswith('$'):
                        continue
                    else:
                        error_msg = f"TYPE_ERROR: Invalid type for attribute '{attr_name}' in element '{element.tag}': expected {attr_type}, got '{attr_value}'."

                    # Provide type-specific guidance
                    if attr_type == "double" or attr_type == "float":
                        error_msg += " Fix: Use a decimal number (e.g., '1.0', '3.14')."
                    elif attr_type == "int":
                        error_msg += " Fix: Use a whole number (e.g., '1', '42')."
                    elif attr_type == "unsignedInt":
                        error_msg += " Fix: Use a positive whole number (e.g., '0', '1', '42')."
                    elif attr_type == "boolean":
                        error_msg += " Fix: Use 'true', 'false'."
                    elif attr_type == "dateTime":
                        error_msg += " Fix: Use ISO format (e.g., '2023-12-01T10:30:00Z')."
                    else:
                        error_msg += f" Fix: Ensure value matches {attr_type} format."

                    errors.append(error_msg)

                # Case-insensitive lookup for attribute type definitions
                attr_key = next((key for key in simple_type_definitions.keys()
                                 if key.lower() == attr_name.lower()), None)
                if attr_key:
                    if attr_value not in simple_type_definitions[attr_key]:
                        valid_values = simple_type_definitions[attr_key]
                        error_msg = f"VALUE_ERROR: Invalid value '{attr_value}' for attribute '{attr_name}' in element '{element.tag}'."
                        error_msg += f" Valid values: {', '.join(valid_values)}."
                        error_msg += f" Fix: Replace '{attr_value}' with one of the valid values."
                        errors.append(error_msg)

        return errors

    def _validate_element_children(self, element: IElement, element_def: Dict[str, Any], schema_info: ISchemaInfo) -> List[str]:
        """Validate element children against schema definition"""
        errors = []

        # Expand group references to get all valid child elements
        valid_children = self._expand_children_with_groups(element_def.children, schema_info)

        for child in element.children:
            if child.tag not in valid_children:
                error_msg = f"STRUCTURE_ERROR: Child element '{child.tag}' is not allowed in '{element.tag}'."
                error_msg += f" Valid child elements for '{element.tag}': {', '.join(valid_children)}."
                error_msg += f" Fix: Remove '{child.tag}' or replace with a valid child element."

                errors.append(error_msg)

        return errors

    def _expand_children_with_groups(self, children: List[str], schema_info: ISchemaInfo) -> List[str]:
        """Expand group references to get all valid child element names"""
        expanded_children = []

        for child in children:
            if child.startswith("GROUP:"):
                group_name = child[6:]  # Remove "GROUP:" prefix
                group_def = schema_info.groups.get(group_name)
                if group_def:
                    # Recursively expand group children
                    expanded_children.extend(self._expand_group_recursively(group_def, schema_info))
                else:
                    # Group not found, keep the reference for error reporting
                    expanded_children.append(child)
            else:
                expanded_children.append(child)

        return expanded_children

    def _expand_group_recursively(self, group_def: IGroupDefinition, schema_info: ISchemaInfo) -> List[str]:
        """Recursively expand a group definition to get all valid element names"""
        elements = []

        for child in group_def.children:
            if child.startswith("GROUP:"):
                nested_group_name = child[6:]
                nested_group_def = schema_info.groups.get(nested_group_name)
                if nested_group_def:
                    elements.extend(self._expand_group_recursively(nested_group_def, schema_info))
            else:
                elements.append(child)

        return elements

    def _is_valid_attribute_value(self, value: str) -> bool:
        """Check if an attribute value is valid (not None, not empty, not whitespace-only)"""
        return value is not None and value != "" and value.strip() != ""

    def _validate_attribute_type(self, value: str, expected_type: str) -> bool:
        """Validate attribute value against expected type"""
        if not value:
            return True

        # First, check if it's a valid OpenSCENARIO parameter pattern
        # Parameters are valid for any type as they represent dynamic values
        if value.startswith('$'):
            return self._is_valid_parameter_pattern(value)

        try:
            if expected_type == "string":
                # Non-parameter strings are always valid
                return True
            elif expected_type == "int":
                int(value)
                return True
            elif expected_type == "unsignedInt":
                val = int(value)
                return val >= 0
            elif expected_type == "unsignedShort":
                val = int(value)
                return 0 <= val <= 65535
            elif expected_type == "double" or expected_type == "float":
                float(value)
                return True
            elif expected_type == "boolean":
                return value.lower() in ("true", "false", "1", "0")
            elif expected_type == "dateTime":
                # Handle ISO format dates with or without timezone
                if value.endswith('Z'):
                    value = value[:-1] + '+00:00'
                datetime.fromisoformat(value)
                return True
            else:
                # Unknown type, assume valid for extensibility
                return True
        except (ValueError, TypeError):
            return False

    def _is_valid_parameter_pattern(self, value: str) -> bool:
        """
        Check if a value matches the OpenSCENARIO parameter pattern:
        [$][A-Za-z_][A-Za-z0-9_]*

        This pattern represents OpenSCENARIO parameters that start with a dollar sign
        followed by an identifier (letter or underscore, then letters, digits, or underscores)
        """
        # Pattern: starts with $, followed by letter/underscore, then letters/digits/underscores
        pattern = r'^\$[A-Za-z_][A-Za-z0-9_]*$'
        return bool(re.match(pattern, value))

    def _validate_basic_structure(self, element: IElement) -> List[str]:
        """Validate basic OpenSCENARIO structure requirements"""
        errors = []

        if element.tag == "OpenSCENARIO" or element.tag == "OpenScenario":

            # Check for required FileHeader
            fileheader_found = False
            for child in element.children:
                if child.tag == "FileHeader":
                    fileheader_found = True
                    break

            if not fileheader_found:
                errors.append("STRUCTURE_ERROR: FileHeader element is required in OpenSCENARIO. Fix: Add a FileHeader element as a child of OpenSCENARIO.")

        return errors


    def _validate_references(self, element: IElement) -> List[str]:
        """Validate all reference-related checks"""
        errors = []

        entities = self._collect_entities(element)
        variables = self._collect_variables(element)
        parameters = self._collect_parameters(element)
        storyboard_elements = self._collect_storyboard_elements(element)

        errors.extend(self._validate_entity_references(element, entities))
        errors.extend(self._validate_variable_references(element, variables))
        errors.extend(self._validate_parameter_references(element, parameters))
        errors.extend(self._validate_storyboard_element_references(element, storyboard_elements))
        errors.extend(self._validate_unique_element_names(element))
        errors.extend(self._validate_traffic_signal_references(element))

        return errors

    def _collect_entities(self, element: IElement) -> Dict[str, IElement]:
        """Collect all entity definitions in the scenario"""
        entities = {}

        def collect_recursive(elem: IElement):
            if elem.tag in ["ScenarioObject", "EntityObject", "Vehicle", "Pedestrian", "MiscObject"]:
                name = elem.attrs.get("name")
                if name:
                    entities[name] = elem

            for child in elem.children:
                collect_recursive(child)

        collect_recursive(element)
        return entities

    def _collect_variables(self, element: IElement) -> Dict[str, IElement]:
        """Collect all variable declarations"""
        variables = {}

        def collect_recursive(elem: IElement):
            if elem.tag == "VariableDeclaration":
                name = elem.attrs.get("name")
                if name:
                    variables[name] = elem

            for child in elem.children:
                collect_recursive(child)

        collect_recursive(element)
        return variables

    def _collect_parameters(self, element: IElement) -> Dict[str, IElement]:
        """Collect all parameter declarations"""
        parameters = {}
        def collect_recursive(elem: IElement):
            if elem.tag == "ParameterDeclaration":
                name = elem.attrs.get("name")
                if name:
                    parameters[name] = elem

            for child in elem.children:
                collect_recursive(child)

        collect_recursive(element)
        return parameters

    def _collect_storyboard_elements(self, element: IElement) -> Dict[str, IElement]:
        """Collect all storyboard elements (Acts, Maneuvers, Events, etc.)"""
        storyboard_elements = {}

        def collect_recursive(elem: IElement):
            if elem.tag in ["Act", "ManeuverGroup", "Maneuver", "Event", "Action"]:
                name = elem.attrs.get("name")
                if name:
                    storyboard_elements[name] = elem

            for child in elem.children:
                collect_recursive(child)

        collect_recursive(element)
        return storyboard_elements

    def _validate_entity_references(self, element: IElement, entities: Dict[str, IElement]) -> List[str]:
        """Validate that all entity references can be resolved"""
        errors = []

        def validate_recursive(elem: IElement):
            # Check for entity reference attributes
            entity_ref_attrs = ["entityRef", "objectRef", "actorRef"]
            for attr_name in entity_ref_attrs:
                if attr_name in elem.attrs:
                    ref_value = elem.attrs[attr_name]
                    if ref_value and not ref_value.startswith('$') and ref_value not in entities:
                        errors.append(f"REFERENCE_ERROR: Entity reference '{ref_value}' in element '{elem.tag}' cannot be resolved. Available entities: {', '.join(entities.keys())}. Fix: Use one of the available entity names or define the referenced entity, the name should be directly after '$'. For example, '$Ego'.")

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def _validate_variable_references(self, element: IElement, variables: Dict[str, IElement]) -> List[str]:
        """Validate that all variable references can be resolved"""
        errors = []

        def validate_recursive(elem: IElement):
            if elem.tag == "VariableAction" and "variableRef" in elem.attrs:
                ref_value = elem.attrs["variableRef"]
                if ref_value and ref_value not in variables:
                    errors.append(f"REFERENCE_ERROR: Variable reference '{ref_value}' in VariableAction cannot be resolved. Available variables: {', '.join(variables.keys())}. Fix: Use one of the available variable names or declare the referenced variable, the name should be directly after '$'. For example, '$Speed'.")

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def _validate_parameter_references(self, element: IElement, parameters: Dict[str, IElement]) -> List[str]:
        """Validate that all parameter references can be resolved"""
        errors = []
        def validate_recursive(elem: IElement):
            for attr_name, attr_value in elem.attrs.items():
                if attr_name != "variableRef" and attr_value and attr_value.startswith('$'):
                    param_name = attr_value[1:]
                    if param_name not in parameters:
                        errors.append(f"REFERENCE_ERROR: Parameter reference '{param_name}' in element '{elem.tag}' cannot be resolved. Available parameters: {', '.join(parameters.keys())}. Fix: Use one of the available parameter names or define the referenced parameter, the name should be directly after '$'. For example, '$Speed'.")

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def _validate_storyboard_element_references(self, element: IElement, storyboard_elements: Dict[str, IElement]) -> List[str]:
        """Validate that all storyboard element references can be resolved"""
        errors = []

        def validate_recursive(elem: IElement):
            storyboard_ref_attrs = ["actRef", "maneuverRef", "eventRef", "actionRef"]
            for attr_name in storyboard_ref_attrs:
                if attr_name in elem.attrs:
                    ref_value = elem.attrs[attr_name]
                    if ref_value and not ref_value.startswith('$') and ref_value not in storyboard_elements:
                        errors.append(f"REFERENCE_ERROR: Storyboard element reference '{ref_value}' in element '{elem.tag}' cannot be resolved. Available elements: {', '.join(storyboard_elements.keys())}. Fix: Use one of the available element names or define the referenced element, the name should be directly after '$'. For example, '$Act1'.")

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def _validate_unique_element_names(self, element: IElement) -> List[str]:
        """Validate that elements have unique names on the same level"""
        errors = []

        def validate_level(elem: IElement):
            name_counts = {}
            for child in elem.children:
                if "name" in child.attrs:
                    name = child.attrs["name"]
                    if name in name_counts:
                        name_counts[name].append(child)
                    else:
                        name_counts[name] = [child]

            for name, elements in name_counts.items():
                if len(elements) > 1:
                    element_tags = [e.tag for e in elements]
                    errors.append(f"UNIQUENESS_ERROR: Duplicate name '{name}' found in {len(elements)} elements: {', '.join(element_tags)} under parent '{elem.tag}'. Fix: Ensure each element has a unique name within its parent scope.")

            for child in elem.children:
                validate_level(child)

        validate_level(element)
        return errors

    def _validate_traffic_signal_references(self, element: IElement) -> List[str]:
        """Validate traffic signal controller and signal ID references"""
        errors = []

        # Collect traffic signal controllers
        controllers = {}
        signals = {}

        def collect_traffic_elements(elem: IElement):
            if elem.tag == "TrafficSignalController":
                name = elem.attrs.get("name")
                if name:
                    controllers[name] = elem
            elif elem.tag == "TrafficSignal":
                signal_id = elem.attrs.get("id")
                if signal_id:
                    signals[signal_id] = elem

            for child in elem.children:
                collect_traffic_elements(child)

        collect_traffic_elements(element)

        def validate_traffic_refs(elem: IElement):
            if elem.tag == "TrafficSignalStateAction":
                if "trafficSignalControllerRef" in elem.attrs:
                    controller_ref = elem.attrs["trafficSignalControllerRef"]
                    if controller_ref and controller_ref not in controllers:
                        errors.append(f"REFERENCE_ERROR: Traffic signal controller reference '{controller_ref}' cannot be resolved. Available controllers: {', '.join(controllers.keys())}. Fix: Use one of the available controller names or define the referenced controller, the name should be directly after '$'. For example, '$TrafficSignalController1'.")

                if "signalId" in elem.attrs:
                    signal_id = elem.attrs["signalId"]
                    if signal_id and signal_id not in signals:
                        errors.append(f"REFERENCE_ERROR: Signal ID '{signal_id}' cannot be resolved. Available signal IDs: {', '.join(signals.keys())}. Fix: Use one of the available signal IDs or define the referenced signal, the name should be directly after '$'. For example, '$Signal1'.")

            for child in elem.children:
                validate_traffic_refs(child)

        validate_traffic_refs(element)
        return errors

    def _validate_special_data_types(self, element: IElement) -> List[str]:
        """Validate data type specific constraints"""
        errors = []

        def validate_recursive(elem: IElement):

            # Validate non-negative transition times
            if elem.tag == "LightStateAction" and "transitionTime" in elem.attrs:
                transition_time = elem.attrs["transitionTime"]
                if not transition_time.startswith('$'):
                    try:
                        time_value = float(transition_time)
                        if time_value < 0:
                            errors.append(f"DATA_TYPE_ERROR: Transition time in LightStateAction must be non-negative, got '{transition_time}'. Fix: Use a value >= 0.")
                    except ValueError:
                        pass

            # Validate positive durations
            if elem.tag == "Phase" and "duration" in elem.attrs:
                duration = elem.attrs["duration"]
                if not duration.startswith('$'):
                    try:
                        duration_value = float(duration)
                        if duration_value <= 0:
                            errors.append(f"DATA_TYPE_ERROR: Duration in Phase must be positive, got '{duration}'. Fix: Use a value > 0.")
                    except ValueError:
                        pass

            # Validate speed values are reasonable
            if "speed" in elem.attrs:
                speed = elem.attrs["speed"]
                if not speed.startswith('$'):
                    try:
                        speed_value = float(speed)
                        if speed_value < 0:
                            errors.append(f"DATA_TYPE_ERROR: Speed values should be non-negative, got '{speed}' in {elem.tag}. Fix: Use a value >= 0.")
                    except ValueError:
                        pass

            # Validate probability values are between 0 and 1
            if "probability" in elem.attrs:
                probability = elem.attrs["probability"]
                if not probability.startswith('$'):
                    try:
                        prob_value = float(probability)
                        if not (0 <= prob_value <= 1):
                            errors.append(f"DATA_TYPE_ERROR: Probability values must be between 0 and 1, got '{probability}' in {elem.tag}. Fix: Use a value between 0.0 and 1.0.")
                    except ValueError:
                        pass

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def get_name(self) -> str:
        """Get the name of this validator plugin"""
        return self.metadata.name
