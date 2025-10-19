"""
Unit tests for schema parser implementations
Tests schema-related classes and XSD parsing
"""

import pytest
from pathlib import Path
from openscenario_builder.core.schema.parser import (
    AttributeDefinition,
    ChildElementInfo,
    ElementDefinition,
    GroupDefinition,
    SchemaInfo,
    XSDParser,
    parse_openscenario_schema
)
from openscenario_builder.interfaces import (
    IAttributeDefinition,
    IChildElementInfo,
    IElementDefinition,
    IGroupDefinition,
    ISchemaInfo
)


class TestAttributeDefinition:
    """Test AttributeDefinition implementation"""
    
    def test_create_attribute_definition(self):
        """Should create attribute definition"""
        attr_def = AttributeDefinition("testAttr", "string", True)
        
        assert isinstance(attr_def, IAttributeDefinition)
        assert attr_def.name == "testAttr"
        assert attr_def.type == "string"
        assert attr_def.required is True
    
    def test_optional_attribute(self):
        """Should create optional attribute"""
        attr_def = AttributeDefinition("optionalAttr", "double", False)
        
        assert attr_def.required is False


class TestChildElementInfo:
    """Test ChildElementInfo implementation"""
    
    def test_create_child_element_info(self):
        """Should create child element info"""
        child_info = ChildElementInfo("ChildElement", min_occur=1, max_occur="1")
        
        assert isinstance(child_info, IChildElementInfo)
        assert child_info.name == "ChildElement"
        assert child_info.min_occur == 1
        assert child_info.max_occur == "1"
    
    def test_unbounded_child(self):
        """Should create unbounded child"""
        child_info = ChildElementInfo("ChildElement", min_occur=0, max_occur="unbounded")
        
        assert child_info.min_occur == 0
        assert child_info.max_occur == "unbounded"


class TestElementDefinition:
    """Test ElementDefinition implementation"""
    
    def test_create_element_definition(self):
        """Should create element definition"""
        attr1 = AttributeDefinition("attr1", "string", True)
        element_def = ElementDefinition(
            name="TestElement",
            attributes=[attr1],
            children=["Child1", "Child2"]
        )
        
        assert isinstance(element_def, IElementDefinition)
        assert element_def.name == "TestElement"
        assert len(element_def.attributes) == 1
        assert element_def.attributes[0] == attr1
        assert element_def.children == ["Child1", "Child2"]
        assert element_def.is_abstract is False
        assert element_def.is_root is False
    
    def test_abstract_element(self):
        """Should create abstract element"""
        element_def = ElementDefinition(
            name="AbstractElement",
            attributes=[],
            children=[],
            is_abstract=True
        )
        
        assert element_def.is_abstract is True
    
    def test_root_element(self):
        """Should create root element"""
        element_def = ElementDefinition(
            name="RootElement",
            attributes=[],
            children=[],
            is_root=True
        )
        
        assert element_def.is_root is True
    
    def test_element_with_description(self):
        """Should create element with description"""
        element_def = ElementDefinition(
            name="TestElement",
            attributes=[],
            children=[],
            description="Test description"
        )
        
        assert element_def.description == "Test description"
    
    def test_element_with_child_occurrence_info(self):
        """Should create element with child occurrence info"""
        child_info = ChildElementInfo("Child", min_occur=1, max_occur="unbounded")
        element_def = ElementDefinition(
            name="TestElement",
            attributes=[],
            children=["Child"],
            child_occurrence_info={"Child": child_info}
        )
        
        assert "Child" in element_def.child_occurrence_info
        assert element_def.child_occurrence_info["Child"] == child_info
    
    def test_element_with_content_model_type(self):
        """Should create element with content model type"""
        element_def = ElementDefinition(
            name="TestElement",
            attributes=[],
            children=[],
            content_model_type="choice"
        )
        
        assert element_def.content_model_type == "choice"
    
    def test_element_setters(self):
        """Should allow setting is_abstract and is_root"""
        element_def = ElementDefinition(
            name="TestElement",
            attributes=[],
            children=[]
        )
        
        element_def.is_abstract = True
        assert element_def.is_abstract is True
        
        element_def.is_root = True
        assert element_def.is_root is True


class TestGroupDefinition:
    """Test GroupDefinition implementation"""
    
    def test_create_group_definition(self):
        """Should create group definition"""
        group_def = GroupDefinition(
            name="TestGroup",
            children=["Element1", "Element2"]
        )
        
        assert isinstance(group_def, IGroupDefinition)
        assert group_def.name == "TestGroup"
        assert group_def.children == ["Element1", "Element2"]
        assert group_def.is_choice is False
        assert group_def.is_sequence is False
        assert group_def.is_all is False
    
    def test_choice_group(self):
        """Should create choice group"""
        group_def = GroupDefinition(
            name="ChoiceGroup",
            children=["Option1", "Option2"],
            is_choice=True
        )
        
        assert group_def.is_choice is True
    
    def test_sequence_group(self):
        """Should create sequence group"""
        group_def = GroupDefinition(
            name="SequenceGroup",
            children=["Element1", "Element2"],
            is_sequence=True
        )
        
        assert group_def.is_sequence is True
    
    def test_all_group(self):
        """Should create all group"""
        group_def = GroupDefinition(
            name="AllGroup",
            children=["Element1", "Element2"],
            is_all=True
        )
        
        assert group_def.is_all is True


class TestSchemaInfo:
    """Test SchemaInfo implementation"""
    
    def test_create_schema_info(self):
        """Should create schema info"""
        element_def = ElementDefinition("TestElement", [], [])
        group_def = GroupDefinition("TestGroup", [])
        
        schema_info = SchemaInfo(
            elements={"TestElement": element_def},
            groups={"TestGroup": group_def},
            root_elements=["RootElement"],
            element_hierarchy={"Parent": ["Child"]},
            simple_type_definitions={"Color": ["red", "green", "blue"]}
        )
        
        assert isinstance(schema_info, ISchemaInfo)
        assert "TestElement" in schema_info.elements
        assert "TestGroup" in schema_info.groups
        assert schema_info.root_elements == ["RootElement"]
        assert schema_info.element_hierarchy == {"Parent": ["Child"]}
        assert schema_info.simple_type_definitions == {"Color": ["red", "green", "blue"]}


class TestXSDParser:
    """Test XSD parser (requires actual XSD file)"""
    
    @pytest.fixture
    def schema_path(self):
        """Get path to test schema file"""
        # Use the OpenSCENARIO schema from the schemas/ directory
        # From: tests/unit/core/schema/test_parser.py
        # To: project_root/schemas/OpenSCENARIO_v1_3.xsd
        # Need 5 .parent calls: schema -> core -> unit -> tests -> project_root
        test_file = Path(__file__).resolve()
        project_root = test_file.parent.parent.parent.parent.parent
        schema_file = project_root / "schemas" / "OpenSCENARIO_v1_3.xsd"
        
        if schema_file.exists():
            return str(schema_file)
        pytest.skip(f"OpenSCENARIO schema file not found at {schema_file}")
    
    def test_parser_initialization(self, schema_path):
        """Should initialize parser with XSD path"""
        parser = XSDParser(schema_path)
        
        assert parser.xsd_path == Path(schema_path)
        assert parser.xs_ns == "{http://www.w3.org/2001/XMLSchema}"
    
    def test_parse_schema(self, schema_path):
        """Should parse complete schema"""
        parser = XSDParser(schema_path)
        
        schema_info = parser.parse_schema()
        
        assert isinstance(schema_info, ISchemaInfo)
        assert len(schema_info.elements) > 0
        assert len(schema_info.root_elements) > 0
    
    def test_parse_openscenario_schema_function(self, schema_path):
        """Should parse schema using convenience function"""
        schema_info = parse_openscenario_schema(schema_path)
        
        assert isinstance(schema_info, ISchemaInfo)
        assert "OpenSCENARIO" in schema_info.elements or "FileHeader" in schema_info.elements


class TestSchemaIntegration:
    """Integration tests for schema parsing"""
    
    @pytest.fixture
    def schema_info(self):
        """Get parsed schema info"""
        # From: tests/unit/core/schema/test_parser.py
        # To: project_root/schemas/OpenSCENARIO_v1_3.xsd
        # Need 5 .parent calls: schema -> core -> unit -> tests -> project_root
        test_file = Path(__file__).resolve()
        project_root = test_file.parent.parent.parent.parent.parent
        schema_file = project_root / "schemas" / "OpenSCENARIO_v1_3.xsd"
        
        if not schema_file.exists():
            pytest.skip(f"OpenSCENARIO schema file not found at {schema_file}")
        return parse_openscenario_schema(str(schema_file))
    
    def test_schema_has_elements(self, schema_info):
        """Parsed schema should have elements"""
        assert len(schema_info.elements) > 0
    
    def test_schema_has_root_elements(self, schema_info):
        """Parsed schema should have root elements"""
        assert len(schema_info.root_elements) > 0
    
    def test_file_header_element_exists(self, schema_info):
        """FileHeader element should exist"""
        assert "FileHeader" in schema_info.elements
    
    def test_file_header_has_attributes(self, schema_info):
        """FileHeader should have required attributes"""
        if "FileHeader" in schema_info.elements:
            file_header = schema_info.elements["FileHeader"]
            assert len(file_header.attributes) > 0
            
            # Check for known required attributes
            attr_names = [attr.name for attr in file_header.attributes]
            assert any(name in attr_names for name in ["revMajor", "revMinor", "date"])
    
    def test_element_hierarchy_populated(self, schema_info):
        """Element hierarchy should be populated"""
        assert len(schema_info.element_hierarchy) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
