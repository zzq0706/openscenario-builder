"""
Unit tests for ElementBuilder
Tests fluent API for schema-aware element building

NOTE: These tests require ElementBuilder from the schema-aware creation branch.
      They will be skipped if the module is not available.
"""

import pytest

# Try to import, skip all tests if not available
try:
    from openscenario_builder.core.model.element_builder import ElementBuilder
    BUILDER_AVAILABLE = True
except ImportError:
    BUILDER_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="ElementBuilder not available on this branch")
from openscenario_builder.core.model.element import Element
from openscenario_builder.core.schema.parser import (
    AttributeDefinition,
    ChildElementInfo,
    ElementDefinition,
    SchemaInfo
)


class TestElementBuilder:
    """Test ElementBuilder fluent API"""
    
    @pytest.fixture
    def simple_schema(self):
        """Create a simple test schema"""
        # Define Parent element
        parent_attrs = [
            AttributeDefinition("name", "string", True),
            AttributeDefinition("version", "string", False)
        ]
        parent_def = ElementDefinition(
            name="Parent",
            attributes=parent_attrs,
            children=["Child"]
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
    
    def test_create_builder_with_schema(self, simple_schema):
        """Should create builder with schema"""
        builder = ElementBuilder(simple_schema)
        
        assert builder.factory.schema_info == simple_schema
    
    def test_build_simple_element(self, simple_schema):
        """Should build simple element"""
        builder = ElementBuilder(simple_schema)
        
        element = (builder
            .element("Parent")
            .attr("name", "TestParent")
            .build())
        
        assert element.tag == "Parent"
        assert element.get_attribute("name") == "TestParent"
    
    def test_build_element_with_multiple_attributes(self, simple_schema):
        """Should build element with multiple attributes"""
        builder = ElementBuilder(simple_schema)
        
        element = (builder
            .element("Parent")
            .attr("name", "Test")
            .attr("version", "1.0")
            .build())
        
        assert element.get_attribute("name") == "Test"
        assert element.get_attribute("version") == "1.0"
    
    def test_build_element_with_attrs_dict(self, simple_schema):
        """Should build element with attributes dictionary"""
        builder = ElementBuilder(simple_schema)
        
        element = (builder
            .element("Parent")
            .attrs({"name": "Test", "version": "1.0"})
            .build())
        
        assert element.get_attribute("name") == "Test"
        assert element.get_attribute("version") == "1.0"
    
    def test_build_element_with_child(self, simple_schema):
        """Should build element with child"""
        builder = ElementBuilder(simple_schema)
        
        child = Element("Child")
        child.set_attribute("id", "1")
        
        element = (builder
            .element("Parent")
            .attr("name", "Test")
            .child(child)
            .build())
        
        assert len(element.children) == 1
        assert element.children[0].tag == "Child"
    
    def test_build_nested_elements(self, simple_schema):
        """Should build nested elements fluently"""
        builder = ElementBuilder(simple_schema)
        
        # Build child separately
        child = (builder
            .element("Child")
            .attr("id", "1")
            .attr("value", "42.0")
            .build())
        
        # Build parent with child
        parent = (builder
            .element("Parent")
            .attr("name", "Test")
            .child(child)
            .build())
        
        assert parent.tag == "Parent"
        assert len(parent.children) == 1
        assert parent.children[0].get_attribute("id") == "1"
    
    def test_build_with_multiple_children(self, simple_schema):
        """Should build element with multiple children"""
        builder = ElementBuilder(simple_schema)
        
        child1 = Element("Child")
        child1.set_attribute("id", "1")
        
        child2 = Element("Child")
        child2.set_attribute("id", "2")
        
        element = (builder
            .element("Parent")
            .attr("name", "Test")
            .child(child1)
            .child(child2)
            .build())
        
        assert len(element.children) == 2
    
    def test_builder_reuse(self, simple_schema):
        """Should be able to reuse builder for multiple elements"""
        builder = ElementBuilder(simple_schema)
        
        element1 = (builder
            .element("Parent")
            .attr("name", "First")
            .build())
        
        element2 = (builder
            .element("Parent")
            .attr("name", "Second")
            .build())
        
        assert element1.get_attribute("name") == "First"
        assert element2.get_attribute("name") == "Second"
    
    def test_strict_mode_validation(self, simple_schema):
        """Should validate in strict mode"""
        builder = ElementBuilder(simple_schema, strict=True)
        
        with pytest.raises(ValueError, match="missing required attributes"):
            builder.element("Parent").build()
    
    def test_permissive_mode_allows_invalid(self, simple_schema):
        """Should allow invalid elements in permissive mode"""
        builder = ElementBuilder(simple_schema, strict=False)
        
        element = builder.element("Parent").build()
        
        assert element is not None
        errors = builder.factory.get_validation_errors(element)
        assert len(errors) > 0


class TestElementBuilderEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_build_without_element_call(self):
        """Should raise error when building without element()"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        builder = ElementBuilder(schema_info)
        
        with pytest.raises(ValueError, match="tag must be set"):
            builder.build()
    
    def test_attrs_overwrites_previous_attrs(self):
        """attrs() should merge with previous attributes"""
        schema_info = SchemaInfo(
            elements={"Test": ElementDefinition("Test", [], [])},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        builder = ElementBuilder(schema_info, strict=False)
        
        element = (builder
            .element("Test")
            .attr("first", "1")
            .attrs({"second": "2", "third": "3"})
            .build())
        
        assert element.get_attribute("first") == "1"
        assert element.get_attribute("second") == "2"
        assert element.get_attribute("third") == "3"
    
    def test_build_resets_builder_state(self):
        """build() should reset builder state"""
        schema_info = SchemaInfo(
            elements={"Test": ElementDefinition("Test", [], [])},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        builder = ElementBuilder(schema_info, strict=False)
        
        builder.element("Test").attr("attr1", "value1").build()
        
        # After build, state should be reset
        element2 = builder.element("Test").build()
        
        # Second element should not have attr1
        assert not element2.has_attribute("attr1")


class TestElementBuilderChaining:
    """Test method chaining behavior"""
    
    def test_element_returns_self(self):
        """element() should return self for chaining"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        builder = ElementBuilder(schema_info)
        
        result = builder.element("Test")
        
        assert result is builder
    
    def test_attr_returns_self(self):
        """attr() should return self for chaining"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        builder = ElementBuilder(schema_info)
        
        result = builder.element("Test").attr("key", "value")
        
        assert result is builder
    
    def test_attrs_returns_self(self):
        """attrs() should return self for chaining"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        builder = ElementBuilder(schema_info)
        
        result = builder.element("Test").attrs({"key": "value"})
        
        assert result is builder
    
    def test_child_returns_self(self):
        """child() should return self for chaining"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        builder = ElementBuilder(schema_info)
        child_elem = Element("Child")
        
        result = builder.element("Test").child(child_elem)
        
        assert result is builder


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
