"""
Unit tests for ElementFactory
Tests schema-aware element creation and validation

NOTE: These tests require ElementFactory from the schema-aware creation branch.
      They will be skipped if the module is not available.
"""

import pytest

# Try to import, skip all tests if not available
try:
    from openscenario_builder.core.model.element_factory import ElementFactory
    FACTORY_AVAILABLE = True
except ImportError:
    FACTORY_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="ElementFactory not available on this branch")
from openscenario_builder.core.model.element import Element
from openscenario_builder.core.schema.parser import (
    AttributeDefinition,
    ChildElementInfo,
    ElementDefinition,
    SchemaInfo
)


class TestElementFactory:
    """Test ElementFactory schema-aware creation"""
    
    @pytest.fixture
    def simple_schema(self):
        """Create a simple test schema"""
        # Define Parent element with required attributes
        parent_attrs = [
            AttributeDefinition("name", "string", True),
            AttributeDefinition("version", "string", False)
        ]
        parent_def = ElementDefinition(
            name="Parent",
            attributes=parent_attrs,
            children=["Child"],
            child_occurrence_info={
                "Child": ChildElementInfo("Child", min_occur=1, max_occur="unbounded")
            }
        )
        
        # Define Child element
        child_attrs = [
            AttributeDefinition("id", "string", True),
            AttributeDefinition("value", "double", False)
        ]
        child_def = ElementDefinition(
            name="Child",
            attributes=child_attrs,
            children=[]
        )
        
        schema_info = SchemaInfo(
            elements={"Parent": parent_def, "Child": child_def},
            groups={},
            root_elements=["Parent"],
            element_hierarchy={"Parent": ["Child"]},
            simple_type_definitions={}
        )
        
        return schema_info
    
    def test_create_factory_with_schema(self, simple_schema):
        """Should create factory with schema"""
        factory = ElementFactory(simple_schema)
        
        assert factory.schema_info == simple_schema
    
    def test_create_element_with_required_attributes(self, simple_schema):
        """Should create element with required attributes"""
        factory = ElementFactory(simple_schema)
        
        element = factory.create("Parent", {"name": "TestParent"})
        
        assert element.name == "Parent"
        assert element.get_attribute("name") == "TestParent"
    
    def test_strict_mode_raises_on_missing_required_attribute(self, simple_schema):
        """Should raise error in strict mode when required attribute missing"""
        factory = ElementFactory(simple_schema, strict=True)
        
        with pytest.raises(ValueError, match="Missing required attribute.*name"):
            factory.create("Parent", {})
    
    def test_permissive_mode_allows_missing_required_attribute(self, simple_schema):
        """Should allow missing required attribute in permissive mode"""
        factory = ElementFactory(simple_schema, strict=False)
        
        element = factory.create("Parent", {})
        
        assert element is not None
        assert len(factory.validation_errors) > 0
        assert any("required attribute" in err.lower() for err in factory.validation_errors)
    
    def test_strict_mode_raises_on_unknown_attribute(self, simple_schema):
        """Should raise error in strict mode for unknown attribute"""
        factory = ElementFactory(simple_schema, strict=True)
        
        with pytest.raises(ValueError, match="Unknown attribute.*unknown"):
            factory.create("Parent", {"name": "Test", "unknown": "value"})
    
    def test_permissive_mode_allows_unknown_attribute(self, simple_schema):
        """Should allow unknown attribute in permissive mode"""
        factory = ElementFactory(simple_schema, strict=False)
        
        element = factory.create("Parent", {"name": "Test", "unknown": "value"})
        
        assert element is not None
        assert len(factory.validation_errors) > 0
    
    def test_create_element_with_optional_attributes(self, simple_schema):
        """Should create element with optional attributes"""
        factory = ElementFactory(simple_schema)
        
        element = factory.create("Parent", {"name": "Test", "version": "1.0"})
        
        assert element.get_attribute("version") == "1.0"
    
    def test_create_unknown_element_in_strict_mode(self, simple_schema):
        """Should raise error for unknown element in strict mode"""
        factory = ElementFactory(simple_schema, strict=True)
        
        with pytest.raises(ValueError, match="Unknown element type.*Unknown"):
            factory.create("Unknown", {})
    
    def test_create_unknown_element_in_permissive_mode(self, simple_schema):
        """Should create unknown element in permissive mode"""
        factory = ElementFactory(simple_schema, strict=False)
        
        element = factory.create("Unknown", {"attr": "value"})
        
        assert element.name == "Unknown"
        assert len(factory.validation_errors) > 0
    
    def test_get_element_definition(self, simple_schema):
        """Should retrieve element definition"""
        factory = ElementFactory(simple_schema)
        
        definition = factory.get_element_definition("Parent")
        
        assert definition is not None
        assert definition.name == "Parent"
    
    def test_get_required_attributes(self, simple_schema):
        """Should get required attributes for element"""
        factory = ElementFactory(simple_schema)
        
        required = factory.get_required_attributes("Parent")
        
        assert "name" in required
        assert "version" not in required
    
    def test_get_allowed_children(self, simple_schema):
        """Should get allowed children for element"""
        factory = ElementFactory(simple_schema)
        
        allowed = factory.get_allowed_children("Parent")
        
        assert "Child" in allowed
    
    def test_validate_child_addition_valid(self, simple_schema):
        """Should validate valid child addition"""
        factory = ElementFactory(simple_schema)
        parent = factory.create("Parent", {"name": "Test"})
        
        is_valid = factory.validate_child_addition(parent, "Child")
        
        assert is_valid is True
    
    def test_validate_child_addition_invalid(self, simple_schema):
        """Should reject invalid child"""
        factory = ElementFactory(simple_schema)
        child = factory.create("Child", {"id": "1"})
        
        is_valid = factory.validate_child_addition(child, "Parent")
        
        assert is_valid is False
    
    def test_get_child_occurrence_info(self, simple_schema):
        """Should get child occurrence info"""
        factory = ElementFactory(simple_schema)
        
        info = factory.get_child_occurrence_info("Parent", "Child")
        
        assert info is not None
        assert info.min_occur == 1
        assert info.max_occur == "unbounded"
    
    def test_clear_validation_errors(self, simple_schema):
        """Should clear validation errors"""
        factory = ElementFactory(simple_schema, strict=False)
        
        # Create invalid element to generate errors
        factory.create("Unknown", {})
        assert len(factory.validation_errors) > 0
        
        factory.clear_validation_errors()
        assert len(factory.validation_errors) == 0


class TestElementFactoryEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_create_factory_without_schema(self):
        """Should create factory without schema (permissive mode)"""
        factory = ElementFactory(None, strict=False)
        
        element = factory.create("AnyElement", {"attr": "value"})
        
        assert element.name == "AnyElement"
    
    def test_create_element_with_empty_attributes(self):
        """Should create element with no attributes"""
        schema_info = SchemaInfo(
            elements={"Simple": ElementDefinition("Simple", [], [])},
            groups={},
            root_elements=["Simple"],
            element_hierarchy={},
            simple_type_definitions={}
        )
        factory = ElementFactory(schema_info)
        
        element = factory.create("Simple", {})
        
        assert element.name == "Simple"
    
    def test_get_definition_for_unknown_element(self):
        """Should return None for unknown element definition"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        factory = ElementFactory(schema_info)
        
        definition = factory.get_element_definition("Unknown")
        
        assert definition is None
    
    def test_get_required_attributes_for_unknown_element(self):
        """Should return empty list for unknown element"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        factory = ElementFactory(schema_info)
        
        required = factory.get_required_attributes("Unknown")
        
        assert required == []
    
    def test_get_allowed_children_for_unknown_element(self):
        """Should return empty list for unknown element"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        factory = ElementFactory(schema_info)
        
        allowed = factory.get_allowed_children("Unknown")
        
        assert allowed == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
