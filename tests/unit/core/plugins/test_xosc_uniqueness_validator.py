"""
Unit tests for XOSC Uniqueness Validator
Tests XoscUniquenessValidator plugin
"""

import pytest
from openscenario_builder.core.utils.validators import XoscUniquenessValidator
from openscenario_builder.core.model.element import Element


class TestXoscUniquenessValidator:
    """Test Uniqueness Validator plugin"""

    def test_validate_unique_names_no_duplicates(self):
        """Should not error when all names are unique"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        child1 = Element("Child", {"name": "unique1"})
        child2 = Element("Child", {"name": "unique2"})
        child3 = Element("Child", {"name": "unique3"})
        root.add_child(child1)
        root.add_child(child2)
        root.add_child(child3)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_duplicate_names_same_level(self):
        """Should error when names are duplicated at same level"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        child1 = Element("Child", {"name": "duplicate"})
        child2 = Element("Child", {"name": "duplicate"})
        root.add_child(child1)
        root.add_child(child2)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "UNIQUENESS_ERROR" in errors[0]
        assert "duplicate" in errors[0]
        assert "2 elements" in errors[0]

    def test_validate_duplicate_names_different_levels(self):
        """Should allow same names at different levels"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        child1 = Element("Child", {"name": "samename"})
        child2 = Element("Child", {"name": "other"})
        grandchild = Element("GrandChild", {"name": "samename"})
        root.add_child(child1)
        root.add_child(child2)
        child2.add_child(grandchild)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_multiple_duplicates_same_level(self):
        """Should error for multiple sets of duplicates"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        child1 = Element("TypeA", {"name": "dup1"})
        child2 = Element("TypeA", {"name": "dup1"})
        child3 = Element("TypeB", {"name": "dup2"})
        child4 = Element("TypeB", {"name": "dup2"})
        root.add_child(child1)
        root.add_child(child2)
        root.add_child(child3)
        root.add_child(child4)

        errors = validator.validate(root)

        assert len(errors) == 2
        assert all("UNIQUENESS_ERROR" in error for error in errors)

    def test_validate_triple_duplicates(self):
        """Should report correct count for triple duplicates"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        child1 = Element("Child", {"name": "triple"})
        child2 = Element("Child", {"name": "triple"})
        child3 = Element("Child", {"name": "triple"})
        root.add_child(child1)
        root.add_child(child2)
        root.add_child(child3)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "3 elements" in errors[0]

    def test_validate_elements_without_names(self):
        """Should not error for elements without name attributes"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        child1 = Element("Child")  # No name
        child2 = Element("Child")  # No name
        root.add_child(child1)
        root.add_child(child2)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_mixed_named_and_unnamed(self):
        """Should only check named elements"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        child1 = Element("Child", {"name": "named"})
        child2 = Element("Child")  # No name
        child3 = Element("Child", {"name": "named"})
        root.add_child(child1)
        root.add_child(child2)
        root.add_child(child3)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "named" in errors[0]

    def test_validate_nested_structures(self):
        """Should validate nested element structures independently"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        parent1 = Element("Parent", {"name": "p1"})
        parent2 = Element("Parent", {"name": "p2"})

        # Same name in different parent scopes - should be allowed
        child1 = Element("Child", {"name": "child"})
        child2 = Element("Child", {"name": "child"})

        root.add_child(parent1)
        root.add_child(parent2)
        parent1.add_child(child1)
        parent2.add_child(child2)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_deeply_nested_duplicates(self):
        """Should detect duplicates in deeply nested structures"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        level1 = Element("Level1")
        level2 = Element("Level2")
        child1 = Element("Child", {"name": "dup"})
        child2 = Element("Child", {"name": "dup"})

        root.add_child(level1)
        level1.add_child(level2)
        level2.add_child(child1)
        level2.add_child(child2)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "UNIQUENESS_ERROR" in errors[0]

    def test_validate_different_types_same_name(self):
        """Should error even for different element types with same name"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        child1 = Element("TypeA", {"name": "samename"})
        child2 = Element("TypeB", {"name": "samename"})
        root.add_child(child1)
        root.add_child(child2)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "TypeA" in errors[0] and "TypeB" in errors[0]

    def test_validate_empty_tree(self):
        """Should not error on empty element tree"""
        validator = XoscUniquenessValidator()
        root = Element("Root")

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_single_element(self):
        """Should not error on single named element"""
        validator = XoscUniquenessValidator()
        root = Element("Root")
        child = Element("Child", {"name": "single"})
        root.add_child(child)

        errors = validator.validate(root)

        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
