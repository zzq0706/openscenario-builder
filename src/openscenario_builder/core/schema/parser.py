"""
OpenSCENARIO Schema Parser
Parses XSD files and maintains element hierarchy and relationships
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from openscenario_builder.interfaces import IElementDefinition, IGroupDefinition, ISchemaInfo, IAttributeDefinition, IChildElementInfo


@dataclass
class AttributeDefinition(IAttributeDefinition):
    """Concrete implementation of attribute definition"""
    name: str
    type: str
    required: bool

@dataclass
class ChildElementInfo(IChildElementInfo):
    """Information about a child element including occurrence constraints"""
    name: str
    min_occur: int = 1
    max_occur: str = "1"  # Can be "unbounded" or a number


@dataclass
class ElementDefinition(IElementDefinition):
    """Complete definition of an XML element"""
    name: str
    attributes: List[AttributeDefinition]
    children: List[str]
    parent: Optional[str] = None
    description: str = ""
    is_abstract: bool = False
    is_root: bool = False
    child_occurrence_info: Dict[str, ChildElementInfo] = field(default_factory=dict)
    content_model_type: str = "sequence"  # "sequence", "choice", or "all"


@dataclass
class GroupDefinition(IGroupDefinition):
    """Definition of an XSD group"""
    name: str
    children: List[str]
    is_choice: bool = False
    is_sequence: bool = False
    is_all: bool = False
    child_occurrence_info: Dict[str, ChildElementInfo] = field(default_factory=dict)


@dataclass
class SchemaInfo(ISchemaInfo):
    """Complete schema information with hierarchy"""
    elements: Dict[str, ElementDefinition]
    groups: Dict[str, GroupDefinition]
    root_elements: List[str]
    element_hierarchy: Dict[str, List[str]]
    simple_type_definitions: Dict[str, List[str]]


class XSDParser:
    """XSD parser that maintains element relationships"""

    def __init__(self, xsd_path: str):
        self.xsd_path = Path(xsd_path)
        self.xs_ns = "{http://www.w3.org/2001/XMLSchema}"

    def parse_schema(self) -> ISchemaInfo:
        """Parse the complete XSD schema with hierarchy"""
        tree = ET.parse(self.xsd_path)
        root = tree.getroot()

        simple_type_definitions = self._parse_simple_types(root)

        groups = self._parse_groups(root)
        complex_types = self._parse_complex_types(root, groups)

        # Parse elements and build hierarchy
        elements, root_elements = self._parse_elements(
            root, complex_types, groups)
        hierarchy = self._build_hierarchy(elements)

        return SchemaInfo(
            elements=elements,
            groups=groups,
            root_elements=root_elements,
            element_hierarchy=hierarchy,
            simple_type_definitions=simple_type_definitions
        )

    def _parse_simple_types(self, root: ET.Element) -> Dict[str, List[str]]:
        """Parse all simple type definitions)"""
        simple_type_definitions = {}
        # Parse simple types with restrictions
        for simple_type in root.findall(f".//{self.xs_ns}simpleType"):
            type_name = simple_type.attrib.get("name")
            if type_name:
                simple_type_definitions[type_name] = self._parse_simple_type(
                    simple_type)
        return simple_type_definitions

    def _parse_simple_type(self, simple_type: ET.Element) -> List[str]:
        """Parse a simple type definition"""
        restrictions = []

        # Check for restrictions (enumerations, etc.)
        for restriction in simple_type.findall(f".//{self.xs_ns}restriction"):
            # Parse enumerations
            for enum in restriction.findall(f".//{self.xs_ns}enumeration"):
                enum_value = enum.attrib.get("value")
                if enum_value:
                    restrictions.append(enum_value)

        return restrictions

    def _parse_namespaces(self, root: ET.Element) -> Dict[str, str]:
        """Parse all namespaces from the schema"""
        namespaces = {}
        for prefix, uri in root.attrib.items():
            if prefix.startswith('xmlns:'):
                namespaces[prefix[6:]] = uri
            elif prefix == 'xmlns':
                namespaces['default'] = uri
        return namespaces

    def _parse_groups(self, root: ET.Element) -> Dict[str, GroupDefinition]:
        """Parse all group definitions"""
        groups = {}

        for group in root.findall(f".//{self.xs_ns}group"):
            group_name = group.attrib.get("name")
            if not group_name:
                continue

            children = []
            child_occurrence_info = {}
            is_choice = False
            is_sequence = False
            is_all = False

            # Parse group content
            for content in group.findall("*"):
                if content.tag == f"{self.xs_ns}choice":
                    is_choice = True
                    for child in content.findall(f"{self.xs_ns}element"):
                        child_name = child.attrib.get("name")
                        if child_name:
                            children.append(child_name)
                            # Capture occurrence constraints
                            min_occur = int(child.attrib.get("minOccurs", "1"))
                            max_occur = child.attrib.get("maxOccurs", "1")
                            child_occurrence_info[child_name] = ChildElementInfo(
                                name=child_name,
                                min_occur=min_occur,
                                max_occur=max_occur
                            )
                    # Also check for group references in choice
                    for child in content.findall(f"{self.xs_ns}group"):
                        ref_name = child.attrib.get("ref")
                        if ref_name:
                            children.append(f"GROUP:{ref_name}")
                            # Capture occurrence constraints for groups
                            min_occur = int(child.attrib.get("minOccurs", "1"))
                            max_occur = child.attrib.get("maxOccurs", "1")
                            child_occurrence_info[f"GROUP:{ref_name}"] = ChildElementInfo(
                                name=f"GROUP:{ref_name}",
                                min_occur=min_occur,
                                max_occur=max_occur
                            )
                elif content.tag == f"{self.xs_ns}sequence":
                    is_sequence = True
                    for child in content.findall(f"{self.xs_ns}element"):
                        child_name = child.attrib.get("name")
                        if child_name:
                            children.append(child_name)
                            # Capture occurrence constraints
                            min_occur = int(child.attrib.get("minOccurs", "1"))
                            max_occur = child.attrib.get("maxOccurs", "1")
                            child_occurrence_info[child_name] = ChildElementInfo(
                                name=child_name,
                                min_occur=min_occur,
                                max_occur=max_occur
                            )
                    # Also check for group references in sequence
                    for child in content.findall(f"{self.xs_ns}group"):
                        ref_name = child.attrib.get("ref")
                        if ref_name:
                            children.append(f"GROUP:{ref_name}")
                            # Capture occurrence constraints for groups
                            min_occur = int(child.attrib.get("minOccurs", "1"))
                            max_occur = child.attrib.get("maxOccurs", "1")
                            child_occurrence_info[f"GROUP:{ref_name}"] = ChildElementInfo(
                                name=f"GROUP:{ref_name}",
                                min_occur=min_occur,
                                max_occur=max_occur
                            )
                elif content.tag == f"{self.xs_ns}all":
                    is_all = True
                    for child in content.findall(f"{self.xs_ns}element"):
                        child_name = child.attrib.get("name")
                        if child_name:
                            children.append(child_name)
                            # Capture occurrence constraints
                            min_occur = int(child.attrib.get("minOccurs", "1"))
                            max_occur = child.attrib.get("maxOccurs", "1")
                            child_occurrence_info[child_name] = ChildElementInfo(
                                name=child_name,
                                min_occur=min_occur,
                                max_occur=max_occur
                            )
                    # Also check for group references in all
                    for child in content.findall(f"{self.xs_ns}group"):
                        ref_name = child.attrib.get("ref")
                        if ref_name:
                            children.append(f"GROUP:{ref_name}")
                            # Capture occurrence constraints for groups
                            min_occur = int(child.attrib.get("minOccurs", "1"))
                            max_occur = child.attrib.get("maxOccurs", "1")
                            child_occurrence_info[f"GROUP:{ref_name}"] = ChildElementInfo(
                                name=f"GROUP:{ref_name}",
                                min_occur=min_occur,
                                max_occur=max_occur
                            )

            groups[group_name] = GroupDefinition(
                name=group_name,
                children=children,
                is_choice=is_choice,
                is_sequence=is_sequence,
                is_all=is_all,
                child_occurrence_info=child_occurrence_info
            )

        return groups

    def _expand_group_references(self, children: List[str], groups: Dict[str, GroupDefinition]) -> List[str]:
        """Recursively expand group references to get all available elements"""
        expanded_children = []

        for child in children:
            if child.startswith("GROUP:"):
                group_name = child[6:]  # Remove "GROUP:" prefix
                if group_name in groups:
                    group = groups[group_name]
                    # For choice groups, we keep the group reference to handle choice logic
                    if group.is_choice:
                        expanded_children.append(child)
                    else:
                        # For sequence/all groups, recursively expand the group's children
                        expanded_children.extend(
                            self._expand_group_references(group.children, groups))
                else:
                    # Group not found, keep the reference
                    expanded_children.append(child)
            else:
                expanded_children.append(child)

        return expanded_children

    def _parse_complex_types(self, root: ET.Element, groups: Dict[str, GroupDefinition]) -> Dict[str, Dict]:
        """Parse all complex type definitions"""
        complex_types = {}
        for ct in root.findall(f".//{self.xs_ns}complexType"):
            type_name = ct.attrib.get("name")
            if type_name:
                complex_types[type_name] = self._parse_complex_type_content(
                    ct, groups)
        return complex_types

    def _parse_complex_type_content(self, ct_elem: ET.Element, groups: Dict[str, GroupDefinition]) -> Dict:
        """Parse the content of a complex type"""
        result = {
            "attributes": [],
            "children": [],
            "child_occurrence_info": {},
            "content_model_type": "sequence",  # Default
            "is_abstract": ct_elem.attrib.get("abstract", "false").lower() == "true"
        }

        # Parse attributes
        for attr in ct_elem.findall(f".//{self.xs_ns}attribute"):
            attr_name = attr.attrib.get("name")
            attr_type = self._extract_type(attr.attrib.get("type", "string"))

            # Determine if attribute is required based on XSD 'use' attribute
            use_attr = attr.attrib.get("use", "optional")
            is_required = use_attr == "required"

            if attr_name:
                # Create AttributeDefinition with proper structure
                attr_def: AttributeDefinition = {
                    "name": attr_name,
                    "type": attr_type,
                    "required": is_required
                }
                result["attributes"].append(attr_def)

        # Parse child elements from various content models
        for content_model in ct_elem.findall("*"):
            if content_model.tag == f"{self.xs_ns}sequence":
                result["content_model_type"] = "sequence"
                for child in content_model.findall(f"{self.xs_ns}element"):
                    child_name = child.attrib.get("name")
                    if child_name:
                        result["children"].append(child_name)
                        # Capture occurrence constraints
                        min_occur = int(child.attrib.get("minOccurs", "1"))
                        max_occur = child.attrib.get("maxOccurs", "1")
                        result["child_occurrence_info"][child_name] = ChildElementInfo(
                            name=child_name,
                            min_occur=min_occur,
                            max_occur=max_occur
                        )
                # Also check for group references
                for child in content_model.findall(f"{self.xs_ns}group"):
                    ref_name = child.attrib.get("ref")
                    if ref_name:
                        result["children"].append(f"GROUP:{ref_name}")
                        # Capture occurrence constraints for groups
                        min_occur = int(child.attrib.get("minOccurs", "1"))
                        max_occur = child.attrib.get("maxOccurs", "1")
                        result["child_occurrence_info"][f"GROUP:{ref_name}"] = ChildElementInfo(
                            name=f"GROUP:{ref_name}",
                            min_occur=min_occur,
                            max_occur=max_occur
                        )
            elif content_model.tag == f"{self.xs_ns}choice":
                result["content_model_type"] = "choice"
                for child in content_model.findall(f"{self.xs_ns}element"):
                    child_name = child.attrib.get("name")
                    if child_name:
                        result["children"].append(child_name)
                        # Capture occurrence constraints
                        min_occur = int(child.attrib.get("minOccurs", "1"))
                        max_occur = child.attrib.get("maxOccurs", "1")
                        result["child_occurrence_info"][child_name] = ChildElementInfo(
                            name=child_name,
                            min_occur=min_occur,
                            max_occur=max_occur
                        )
                # Also check for group references
                for child in content_model.findall(f"{self.xs_ns}group"):
                    ref_name = child.attrib.get("ref")
                    if ref_name:
                        result["children"].append(f"GROUP:{ref_name}")
                        # Capture occurrence constraints for groups
                        min_occur = int(child.attrib.get("minOccurs", "1"))
                        max_occur = child.attrib.get("maxOccurs", "1")
                        result["child_occurrence_info"][f"GROUP:{ref_name}"] = ChildElementInfo(
                            name=f"GROUP:{ref_name}",
                            min_occur=min_occur,
                            max_occur=max_occur
                        )
            elif content_model.tag == f"{self.xs_ns}all":
                result["content_model_type"] = "all"
                for child in content_model.findall(f"{self.xs_ns}element"):
                    child_name = child.attrib.get("name")
                    if child_name:
                        result["children"].append(child_name)
                        # Capture occurrence constraints
                        min_occur = int(child.attrib.get("minOccurs", "1"))
                        max_occur = child.attrib.get("maxOccurs", "1")
                        result["child_occurrence_info"][child_name] = ChildElementInfo(
                            name=child_name,
                            min_occur=min_occur,
                            max_occur=max_occur
                        )
                # Also check for group references
                for child in content_model.findall(f"{self.xs_ns}group"):
                    ref_name = child.attrib.get("ref")
                    if ref_name:
                        result["children"].append(f"GROUP:{ref_name}")
                        # Capture occurrence constraints for groups
                        min_occur = int(child.attrib.get("minOccurs", "1"))
                        max_occur = child.attrib.get("maxOccurs", "1")
                        result["child_occurrence_info"][f"GROUP:{ref_name}"] = ChildElementInfo(
                            name=f"GROUP:{ref_name}",
                            min_occur=min_occur,
                            max_occur=max_occur
                        )

        return result

    def _parse_elements(self, root: ET.Element, complex_types: Dict, groups: Dict[str, GroupDefinition]) -> Tuple[Dict[str, ElementDefinition], List[str]]:
        """Parse all element definitions"""
        elements = {}
        root_elements = []

        # First pass: collect all element names
        all_element_names = set()
        for elem in root.findall(f".//{self.xs_ns}element"):
            name = elem.attrib.get("name")
            if name:
                all_element_names.add(name)

        # Second pass: parse elements with proper type resolution
        for elem in root.findall(f".//{self.xs_ns}element"):
            name = elem.attrib.get("name")
            if not name:
                continue

            # Get type reference or inline type
            type_ref = elem.attrib.get("type")
            if type_ref:
                # Reference to a complex type
                ref_type = type_ref.replace("xs:", "").replace("xsd:", "")
                if ref_type in complex_types:
                    ct_info = complex_types[ref_type]
                    # Expand group references in children
                    expanded_children = self._expand_group_references(
                        ct_info["children"], groups)
                    elements[name] = ElementDefinition(
                        name=name,
                        attributes=ct_info["attributes"],
                        children=expanded_children,
                        is_abstract=ct_info["is_abstract"],
                        is_root=False,  # Will be determined later
                        child_occurrence_info=ct_info.get("child_occurrence_info", {}),
                        content_model_type=ct_info.get("content_model_type", "sequence")
                    )
                else:
                    # Handle simple types or other references
                    elements[name] = ElementDefinition(
                        name=name,
                        attributes=[
                            {"name": "value", "type": "string", "required": False}],
                        children=[],
                        is_abstract=False,
                        is_root=False,
                    )
            else:
                # Inline complex type
                ct = elem.find(
                    f".//{self.xs_ns}complexType")
                if ct is not None:
                    ct_info = self._parse_complex_type_content(ct, groups)
                    # Expand group references in children
                    expanded_children = self._expand_group_references(
                        ct_info["children"], groups)
                    elements[name] = ElementDefinition(
                        name=name,
                        attributes=ct_info["attributes"],
                        children=expanded_children,
                        is_abstract=ct_info["is_abstract"],
                        is_root=False,
                        child_occurrence_info=ct_info.get("child_occurrence_info", {}),
                        content_model_type=ct_info.get("content_model_type", "sequence")
                    )
                else:
                    # Element without complex type (simple element)
                    elements[name] = ElementDefinition(
                        name=name,
                        attributes=[
                            {"name": "value", "type": "string", "required": False}],
                        children=[],
                        is_abstract=False,
                        is_root=False
                    )

        # Determine root elements (elements that are not children of other elements)
        children_set = set()
        for element_def in elements.values():
            children_set.update(element_def.children)

        for name in elements:
            if name not in children_set:
                root_elements.append(name)
                elements[name].is_root = True

        return elements, root_elements

    def _build_hierarchy(self, elements: Dict[str, ElementDefinition]) -> Dict[str, List[str]]:
        """Build the element hierarchy based on parent-child relationships"""
        hierarchy = {}

        for element_name, element_def in elements.items():
            hierarchy[element_name] = element_def.children

        return hierarchy

    def _extract_type(self, xsd_type: str) -> str:
        """Extract Python type from XSD type"""
        if not xsd_type:
            return "string"

        # Fallback to direct type mapping
        type_mapping = {
            "String": "string",
            "UnsignedInt": "unsignedInt",
            "Int": "int",
            "Double": "double",
            "Float": "float",
            "Boolean": "boolean",
            "DateTime": "dateTime",
        }

        return type_mapping.get(xsd_type, "string")


def parse_openscenario_schema(xsd_path: str) -> ISchemaInfo:
    """Convenience function to parse OpenSCENARIO schema"""
    parser = XSDParser(xsd_path)
    return parser.parse_schema()


if __name__ == "__main__":
    # Test the parser
    import os
    from pathlib import Path

    # Find the schema file relative to the current file
    current_dir = Path(__file__).parent
    schema_path = current_dir / "OpenSCENARIO_v1_3.xsd"

    if not schema_path.exists():
        print(f"Schema file not found at: {schema_path}")
        print("Please run this from the project root directory")
        exit(1)

    schema_info: ISchemaInfo = parse_openscenario_schema(str(schema_path))

    print(f"Parsed {len(schema_info.elements)} elements")
    print(f"Root elements: {schema_info.root_elements}")
    print(f"All elements: {list(schema_info.elements.keys())}")

    # Show hierarchy for some key elements
    for root_elem in schema_info.root_elements[:3]:
        print(f"Number of root elements: {len(schema_info.root_elements)}")
        print(f"\nHierarchy for {root_elem}:")
        if root_elem in schema_info.element_hierarchy:
            for child in schema_info.element_hierarchy[root_elem]:
                print(f"  - {child}")

    # Show attribute structure for some elements
    print("\n=== Attribute Structure Examples ===")
    for elem_name, elem_def in list(schema_info.elements.items())[:3]:
        print(f"\nElement: {elem_name}")
        print(f"  Attributes: {elem_def.attributes}")
        print(f"  Children: {elem_def.children}")
        print(f"  Is Root: {elem_def.is_root}")
        print(f"  Is Abstract: {elem_def.is_abstract}")
