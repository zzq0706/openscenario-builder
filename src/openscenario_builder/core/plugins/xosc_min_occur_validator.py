"""
XOSC Minimum Occurrence Validator Plugin for OpenSCENARIO Builder
Validates minimum occurrence constraints for elements in the scenario
"""

from typing import List, Optional
try:
    from .plugin_metadata import PluginMetadata
except ImportError:
    # Fallback for when loaded directly by plugin manager
    from openscenario_builder.core.plugins.plugin_metadata import PluginMetadata
from openscenario_builder.interfaces import IValidatorPlugin, IElement, ISchemaInfo


class XoscMinOccurValidatorPlugin(IValidatorPlugin):
    """XOSC Minimum Occurrence Validator Plugin - Validates minimum occurrence constraints"""

    def __init__(self):
        self._activated = True  # Default to activated
        self._min_occur_map = {}

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
            name="XOSC Minimum Occurrence Validator",
            version="1.0.0",
            description="Validates minimum occurrence constraints for elements in OpenSCENARIO files",
            author="Ziqi Zhou",
            tags=["validation", "occurrence", "xosc"]
        )

    def get_name(self) -> str:
        """Get the validator name"""
        return "XOSC Minimum Occurrence Validator"

    def validate(self, element: IElement, schema_info: Optional[ISchemaInfo] = None) -> List[str]:
        """Validate minimum occurrence constraints for the element and its children

        Args:
            element: The root element to validate
            schema_info: Schema information for validation rules

        Returns:
            List of error messages found during validation
        """
        errors = []

        if not schema_info:
            return errors

        self._validate_element_recursive(element, schema_info, errors, "")

        return errors

    def _validate_element_recursive(self, element: IElement, schema_info: ISchemaInfo,
                                  errors: List[str], path: str) -> None:
        """Recursively validate element and its children for minimum occurrence constraints"""

        current_path = f"{path}/{element.tag}" if path else element.tag

        element_def = schema_info.elements.get(element.tag)
        if not element_def:
            return

        self._validate_children_occurrence(element, element_def, schema_info, errors, current_path)

        for child in element.children:
            self._validate_element_recursive(child, schema_info, errors, current_path)

    def _validate_children_occurrence(self, element: IElement, element_def,
                                    schema_info: ISchemaInfo, errors: List[str], path: str) -> None:
        """Validate that all required children are present based on minOccurs constraints"""

        # Count occurrences of each child element type
        child_counts = {}
        for child in element.children:
            child_counts[child.tag] = child_counts.get(child.tag, 0) + 1

        # Get content model type (default to sequence if not specified)
        content_model_type = getattr(element_def, 'content_model_type', 'sequence')

        if content_model_type == "choice":
            self._validate_choice_content(element_def, child_counts, schema_info, errors, path)
        elif content_model_type in ["sequence", "all"]:
            self._validate_sequence_or_all_content(element_def, child_counts, schema_info, errors, path)

    def _validate_choice_content(self, element_def, child_counts: dict,
                                schema_info: ISchemaInfo, errors: List[str], path: str) -> None:
        """Validate choice content model - check if exactly one choice group is satisfied"""

        def expand_group_recursively(group_name: str) -> List[str]:
            """Recursively expand group references to get actual element names"""
            elements = []
            group_def = schema_info.groups.get(group_name)
            if group_def:
                for child in group_def.children:
                    if child.startswith("GROUP:"):
                        # Recursively expand nested group references
                        nested_group_name = child[6:]
                        elements.extend(expand_group_recursively(nested_group_name))
                    else:
                        elements.append(child)
            return elements

        choice_groups_satisfied = []

        # For each choice option (which could be elements or group references)
        for expected_child_name in element_def.children:
            if expected_child_name.startswith("GROUP:"):
                group_name = expected_child_name[6:]
                # Get all actual elements from this group (recursively)
                group_elements = expand_group_recursively(group_name)

                # Check if any elements from this choice group are present
                present_elements = [elem for elem in group_elements if child_counts.get(elem, 0) > 0]
                if present_elements:
                    choice_groups_satisfied.append(group_name)
            else:
                # Direct element choice
                if child_counts.get(expected_child_name, 0) > 0:
                    choice_groups_satisfied.append(expected_child_name)

        # Validate choice constraint: exactly one choice should be satisfied
        if len(choice_groups_satisfied) == 0:
            # Get choice group names for error message
            choice_names = []
            for child_name in element_def.children:
                if child_name.startswith("GROUP:"):
                    choice_names.append(child_name[6:])
                else:
                    choice_names.append(child_name)

            error_msg = (f"OCCURRENCE_ERROR: Missing required choice from group '{element_def.name}' at path '{path}'. "
                        f"Must select one of: {', '.join(choice_names)}. "
                        f"Fix: Add one of the required choice elements to satisfy the constraint.")
            errors.append(error_msg)
        elif len(choice_groups_satisfied) > 1:
            error_msg = (f"OCCURRENCE_ERROR: Invalid choice selection at path '{path}'. "
                        f"Found multiple choice groups satisfied: {', '.join(choice_groups_satisfied)}. "
                        f"Only one choice group should be satisfied. "
                        f"Fix: Remove extra elements to leave only one choice satisfied.")
            errors.append(error_msg)

    def _validate_sequence_or_all_content(self, element_def, child_counts: dict,
                                         schema_info: ISchemaInfo, errors: List[str], path: str) -> None:
        """Validate sequence or all content model - all required children must be present"""

        # Check each expected child against minOccurs requirements
        for expected_child_name in element_def.children:
            # Handle group references
            if expected_child_name.startswith("GROUP:"):
                group_name = expected_child_name[6:]  # Remove "GROUP:" prefix
                group_def = schema_info.groups.get(group_name)
                if group_def:
                    # Get the group's occurrence constraints from the parent element
                    group_occurrence_info = element_def.child_occurrence_info.get(expected_child_name)
                    group_min_occur = group_occurrence_info.min_occur if group_occurrence_info else 1

                    # For groups, we need to check the group's content model type
                    if group_def.is_choice:
                        self._validate_group_choice(group_def, child_counts, schema_info, errors, path, group_min_occur)
                    else:
                        # For sequence/all groups, validate group children normally if group is required
                        if group_min_occur > 0:
                            for group_child in group_def.children:
                                if not group_child.startswith("GROUP:"):
                                    self._check_min_occurrence(
                                        group_child, child_counts, schema_info, errors, path, element_def)
            else:
                self._check_min_occurrence(
                    expected_child_name, child_counts, schema_info, errors, path, element_def)

    def _validate_group_choice(self, group_def, child_counts: dict,
                              schema_info: ISchemaInfo, errors: List[str], path: str, group_min_occur: int = 1) -> None:
        """Validate a choice group - only one choice from the group should be present"""

        def expand_group_recursively(group_name: str) -> List[str]:
            """Recursively expand group references to get actual element names"""
            elements = []
            inner_group_def = schema_info.groups.get(group_name)
            if inner_group_def:
                for child in inner_group_def.children:
                    if child.startswith("GROUP:"):
                        nested_group_name = child[6:]
                        elements.extend(expand_group_recursively(nested_group_name))
                    else:
                        elements.append(child)
            return elements

        choice_groups_satisfied = []

        # For each choice option in the group
        for expected_child_name in group_def.children:
            if expected_child_name.startswith("GROUP:"):
                choice_group_name = expected_child_name[6:]
                # Get all actual elements from this choice group (recursively)
                choice_elements = expand_group_recursively(choice_group_name)

                # Check if any elements from this choice are present
                present_elements = [elem for elem in choice_elements if child_counts.get(elem, 0) > 0]
                if present_elements:
                    choice_groups_satisfied.append(choice_group_name)
            else:
                # Direct element choice
                if child_counts.get(expected_child_name, 0) > 0:
                    choice_groups_satisfied.append(expected_child_name)

        # Validate choice constraint
        if len(choice_groups_satisfied) == 0 and group_min_occur > 0:
            # Get choice group names for error message
            choice_names = []
            for child_name in group_def.children:
                if child_name.startswith("GROUP:"):
                    choice_names.append(child_name[6:])
                else:
                    choice_names.append(child_name)

            error_msg = (f"OCCURRENCE_ERROR: Missing required choice from group '{group_def.name}' at path '{path}'. "
                        f"Must select one of: {', '.join(choice_names)}. "
                        f"Fix: Add one of the required choice elements to satisfy the group constraint.")
            errors.append(error_msg)
        elif len(choice_groups_satisfied) > 1:
            error_msg = (f"OCCURRENCE_ERROR: Invalid group choice selection at path '{path}'. "
                        f"Found multiple choice groups satisfied: {', '.join(choice_groups_satisfied)} "
                        f"from group '{group_def.name}'. Only one choice is allowed. "
                        f"Fix: Remove extra elements to leave only one choice satisfied.")
            errors.append(error_msg)

    def _check_min_occurrence(self, child_name: str, child_counts: dict,
                             schema_info: ISchemaInfo, errors: List[str], path: str,
                             parent_element_def=None) -> None:
        """Check if a child element meets minimum occurrence requirements"""

        actual_count = child_counts.get(child_name, 0)

        # Check if parent has child occurrence info for this child
        required_count = 1  # Default when no info available
        if parent_element_def and hasattr(parent_element_def, 'child_occurrence_info'):
            child_info = parent_element_def.child_occurrence_info.get(child_name)
            if child_info:
                required_count = child_info.min_occur

        if actual_count < required_count:
            error_msg = self._generate_min_occur_error(
                child_name, actual_count, required_count, path)
            errors.append(error_msg)

    def _generate_min_occur_error(self, element_name: str, actual_count: int,
                                 required_count: int, path: str) -> str:
        """Generate AI-oriented error message for minimum occurrence violations"""

        if required_count == 1:
            return (f"OCCURRENCE_ERROR: Missing required element '{element_name}' at path '{path}'. "
                    f"This element is mandatory and must be present exactly once. "
                    f"Fix: Add the '{element_name}' element to satisfy the requirement.")
        elif required_count > 1:
            return (f"OCCURRENCE_ERROR: Insufficient occurrences of element '{element_name}' at path '{path}'. "
                    f"Found {actual_count} instances but {required_count} are required. "
                    f"Fix: Add {required_count - actual_count} more instance(s) of '{element_name}' to meet the requirement.")
