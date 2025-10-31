"""
XOSC Sequence Order Validator
Validates that child elements in sequence content models appear in the correct order
"""

from typing import List, Optional, Dict, Set
from openscenario_builder.interfaces import IElement, ISchemaInfo, IElementDefinition


class XoscSequenceOrderValidator:
    """Validates element order for sequence content models"""

    def validate(
        self, element: IElement, schema_info: Optional[ISchemaInfo] = None
    ) -> List[str]:
        """
        Validate sequence order for elements with sequence content model

        Args:
            element: Root element to validate
            schema_info: Schema information for validation

        Returns:
            List of validation error messages
        """
        if schema_info is None:
            return [
                "CONFIGURATION_ERROR: Schema information required for sequence order validation. "
                "Fix: Ensure OpenSCENARIO schema is properly loaded before validation."
            ]

        errors = []
        self._validate_element_recursively(element, schema_info, errors)
        return errors

    def _validate_element_recursively(
        self, element: IElement, schema_info: ISchemaInfo, errors: List[str]
    ) -> None:
        """Recursively validate element and children for sequence order"""

        # Validate current element's children order
        element_def = schema_info.elements.get(element.tag)
        if element_def and element_def.content_model_type == "sequence":
            self._validate_sequence_order(element, element_def, schema_info, errors)

        # Recursively validate children
        for child in element.children:
            self._validate_element_recursively(child, schema_info, errors)

    def _validate_sequence_order(
        self,
        element: IElement,
        element_def: IElementDefinition,
        schema_info: ISchemaInfo,
        errors: List[str],
    ) -> None:
        """Validate that children appear in the order defined by the sequence"""

        if not element.children:
            return

        # Get the expected sequence order from schema
        expected_sequence = self._expand_sequence_with_groups(
            element_def.children, schema_info
        )

        if not expected_sequence:
            return

        # Build position map: element_name -> list of positions in expected sequence
        expected_positions = self._build_position_map(expected_sequence)

        last_position = -1

        for idx, child in enumerate(element.children):
            child_tag = child.tag

            # Get expected positions for this element type
            valid_positions = expected_positions.get(child_tag, [])

            if not valid_positions:
                # Element not in sequence (handled by structure validator)
                continue

            # Find the earliest valid position that's at or after last_position
            # Using >= allows elements to repeat at the same position
            next_valid_position = None
            for pos in valid_positions:
                if pos >= last_position:
                    next_valid_position = pos
                    break

            if next_valid_position is None:
                # This element appears out of order
                error_msg = self._generate_order_error(
                    element, child, expected_sequence, idx, last_position
                )
                errors.append(error_msg)
            else:
                last_position = next_valid_position

    def _expand_sequence_with_groups(
        self, children: List[str], schema_info: ISchemaInfo
    ) -> List[str]:
        """
        Expand group references to get flat sequence of element names
        Preserves order and allows for multiple occurrences
        """
        expanded = []

        for child in children:
            if child.startswith("GROUP:"):
                group_name = child[6:]
                group_def = schema_info.groups.get(group_name)

                if group_def:
                    if group_def.is_choice:
                        # For choice groups, all options can appear at this position
                        expanded.extend(
                            self._expand_choice_group(group_def, schema_info)
                        )
                    else:
                        # For sequence/all groups, expand recursively
                        expanded.extend(
                            self._expand_sequence_with_groups(
                                group_def.children, schema_info
                            )
                        )
                else:
                    # Group not found, keep reference for error handling
                    expanded.append(child)
            else:
                expanded.append(child)

        return expanded

    def _expand_choice_group(
        self, group_def, schema_info: ISchemaInfo
    ) -> List[str]:
        """
        Expand a choice group - all choices can appear at same position
        Returns all possible element names from the choice group
        """
        choices = []

        for child in group_def.children:
            if child.startswith("GROUP:"):
                nested_group_name = child[6:]
                nested_group = schema_info.groups.get(nested_group_name)
                if nested_group:
                    if nested_group.is_choice:
                        # Recursively expand nested choice groups
                        choices.extend(
                            self._expand_choice_group(nested_group, schema_info)
                        )
                    else:
                        # For non-choice nested groups, get all elements
                        choices.extend(
                            self._expand_sequence_with_groups(
                                nested_group.children, schema_info
                            )
                        )
            else:
                choices.append(child)

        return choices

    def _build_position_map(self, sequence: List[str]) -> Dict[str, List[int]]:
        """
        Build a map of element name to list of positions where it can appear
        Handles elements that can appear multiple times in the sequence
        """
        position_map: Dict[str, List[int]] = {}

        for pos, elem_name in enumerate(sequence):
            if elem_name not in position_map:
                position_map[elem_name] = []
            position_map[elem_name].append(pos)

        return position_map

    def _generate_order_error(
        self,
        parent: IElement,
        child: IElement,
        expected_sequence: List[str],
        child_index: int,
        last_position: int,
    ) -> str:
        """Generate detailed error message for sequence order violation"""

        # Find what elements should come at or after this position
        expected_at_position = []
        seen_elements = set()

        for pos, elem in enumerate(expected_sequence):
            if pos > last_position:
                if elem not in seen_elements:
                    expected_at_position.append(elem)
                    seen_elements.add(elem)
                if len(expected_at_position) >= 5:  # Limit suggestions
                    break

        # Get the position of the child element in the expected sequence
        child_expected_pos = expected_sequence.index(child.tag) if child.tag in expected_sequence else -1

        # Build a helpful error message
        if expected_at_position:
            expected_str = ", ".join(expected_at_position)
        else:
            expected_str = "elements that haven't appeared yet"

        return (
            f"SEQUENCE_ORDER_ERROR: Element '{child.tag}' appears out of sequence order "
            f"in parent element '{parent.tag}'. "
            f"This element should appear earlier in the sequence. "
            f"Expected sequence: {' → '.join(list(dict.fromkeys(expected_sequence)))}. "
            f"At current position, expected one of: {expected_str}. "
            f"Fix: Reorder the elements in '{parent.tag}' to match the required sequence."
        )
