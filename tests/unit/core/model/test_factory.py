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
    SchemaInfo,
)


class TestElementFactory:
    """Test ElementFactory schema-aware creation"""

    @pytest.fixture
    def simple_schema(self):
        """Create a simple test schema"""
        # Define Parent element with required attributes
        parent_attrs = [
            AttributeDefinition("name", "string", True),
            AttributeDefinition("version", "string", False),
        ]
        parent_def = ElementDefinition(
            name="Parent",
            attributes=parent_attrs,
            children=["Child"],
            child_occurrence_info={
                "Child": ChildElementInfo("Child", min_occur=1, max_occur="unbounded")
            },
        )

        # Define Child element
        child_attrs = [
            AttributeDefinition("id", "string", True),
            AttributeDefinition("value", "double", False),
        ]
        child_def = ElementDefinition(name="Child", attributes=child_attrs, children=[])

        schema_info = SchemaInfo(
            elements={"Parent": parent_def, "Child": child_def},
            groups={},
            root_elements=["Parent"],
            element_hierarchy={"Parent": ["Child"]},
            simple_type_definitions={},
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

        assert element.tag == "Parent"
        assert element.get_attribute("name") == "TestParent"

    def test_strict_mode_raises_on_missing_required_attribute(self, simple_schema):
        """Should raise error in strict mode when required attribute missing"""
        factory = ElementFactory(simple_schema, strict=True)

        with pytest.raises(ValueError, match="REQUIRED_ATTRIBUTE_ERROR.*name"):
            factory.create("Parent", {})

    def test_permissive_mode_allows_missing_required_attribute(self, simple_schema):
        """Should allow missing required attribute in permissive mode"""
        factory = ElementFactory(simple_schema, strict=False)

        element = factory.create("Parent", {})

        assert element is not None
        errors = factory.get_validation_errors(element)
        assert len(errors) > 0
        assert any("required attribute" in err.lower() for err in errors)

    def test_strict_mode_raises_on_unknown_attribute(self, simple_schema):
        """Should raise error in strict mode for unknown attribute"""
        factory = ElementFactory(simple_schema, strict=True)

        with pytest.raises(ValueError, match="ATTRIBUTE_ERROR.*unknown"):
            factory.create("Parent", {"name": "Test", "unknown": "value"})

    def test_permissive_mode_allows_unknown_attribute(self, simple_schema):
        """Should allow unknown attribute in permissive mode"""
        factory = ElementFactory(simple_schema, strict=False)

        element = factory.create("Parent", {"name": "Test", "unknown": "value"})

        assert element is not None
        errors = factory.get_validation_errors(element)
        assert len(errors) > 0

    def test_create_element_with_optional_attributes(self, simple_schema):
        """Should create element with optional attributes"""
        factory = ElementFactory(simple_schema)

        element = factory.create("Parent", {"name": "Test", "version": "1.0"})

        assert element.get_attribute("version") == "1.0"

    def test_create_unknown_element_in_strict_mode(self, simple_schema):
        """Should raise error for unknown element in strict mode"""
        factory = ElementFactory(simple_schema, strict=True)

        with pytest.raises(ValueError, match="SCHEMA_ERROR.*Unknown"):
            factory.create("Unknown", {})

    def test_create_unknown_element_in_permissive_mode(self, simple_schema):
        """Should create unknown element in permissive mode"""
        factory = ElementFactory(simple_schema, strict=False)

        element = factory.create("Unknown", {"attr": "value"})

        assert element.tag == "Unknown"
        errors = factory.get_validation_errors(element)
        assert len(errors) > 0

    def test_get_element_definition(self, simple_schema):
        """Should retrieve element definition"""
        factory = ElementFactory(simple_schema)

        info = factory.get_element_info("Parent")

        assert info is not None
        assert info["name"] == "Parent"

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

        errors = factory.validate_child_addition("Parent", "Child")

        assert len(errors) == 0

    def test_validate_child_addition_invalid(self, simple_schema):
        """Should reject invalid child"""
        factory = ElementFactory(simple_schema)

        errors = factory.validate_child_addition("Child", "Parent")

        assert len(errors) > 0

    def test_get_allowed_children_list(self, simple_schema):
        """Should get allowed children for element"""
        factory = ElementFactory(simple_schema)

        children = factory.get_allowed_children("Parent")

        assert "Child" in children

    def test_get_validation_errors(self, simple_schema):
        """Should get validation errors for specific element"""
        factory = ElementFactory(simple_schema, strict=False)

        # Create invalid element to generate errors
        element = factory.create("Unknown", {})
        errors = factory.get_validation_errors(element)
        assert len(errors) > 0


class TestElementFactoryEdgeCases:
    """Test edge cases and error conditions"""

    def test_create_factory_without_schema(self):
        """Should create factory without schema (permissive mode)"""
        # Note: Actual implementation requires schema_info, this test verifies the error
        # In real usage, always provide a valid schema
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )
        factory = ElementFactory(schema_info, strict=False)

        element = factory.create("AnyElement", {"attr": "value"})

        assert element.tag == "AnyElement"

    def test_create_element_with_empty_attributes(self):
        """Should create element with no attributes"""
        schema_info = SchemaInfo(
            elements={"Simple": ElementDefinition("Simple", [], [])},
            groups={},
            root_elements=["Simple"],
            element_hierarchy={},
            simple_type_definitions={},
        )
        factory = ElementFactory(schema_info)

        element = factory.create("Simple", {})

        assert element.tag == "Simple"

    def test_get_definition_for_unknown_element(self):
        """Should return None for unknown element definition"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )
        factory = ElementFactory(schema_info)

        info = factory.get_element_info("Unknown")

        assert info is None

    def test_get_required_attributes_for_unknown_element(self):
        """Should return empty list for unknown element"""
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
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
            simple_type_definitions={},
        )
        factory = ElementFactory(schema_info)

        allowed = factory.get_allowed_children("Unknown")

        assert allowed == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
