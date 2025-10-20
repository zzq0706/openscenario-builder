"""
Unit tests for XOSC Structure Validator
Tests XoscStructureValidator plugin
"""

import pytest
from openscenario_builder.core.utils.validators import XoscStructureValidator
from openscenario_builder.core.model.element import Element


class TestXoscStructureValidator:
    """Test Basic Structure Validator plugin"""

    def test_validate_openscenario_without_fileheader(self):
        """Should error when FileHeader is missing"""
        validator = XoscStructureValidator()
        root = Element("OpenSCENARIO")
        
        errors = validator.validate(root)
        
        assert len(errors) == 1
        assert "STRUCTURE_ERROR" in errors[0]
        assert "FileHeader" in errors[0]

    def test_validate_openscenario_with_fileheader(self):
        """Should not error when FileHeader is present with all required attributes"""
        validator = XoscStructureValidator()
        root = Element("OpenSCENARIO")
        fileheader = Element("FileHeader", {
            "revMajor": "1",
            "revMinor": "3",
            "date": "2023-12-01T10:00:00",
            "description": "Test scenario"
        })
        root.add_child(fileheader)
        
        errors = validator.validate(root)
        
        assert len(errors) == 0

    def test_validate_fileheader_missing_required_attributes(self):
        """Should error when FileHeader missing required attributes"""
        validator = XoscStructureValidator()
        root = Element("OpenSCENARIO")
        fileheader = Element("FileHeader", {
            "revMajor": "1"
            # Missing revMinor, date, description
        })
        root.add_child(fileheader)
        
        errors = validator.validate(root)
        
        assert len(errors) == 3
        for error in errors:
            assert "STRUCTURE_ERROR" in error
            assert "FileHeader" in error

    def test_validate_openscenario_lowercase(self):
        """Should validate OpenScenario with lowercase 's'"""
        validator = XoscStructureValidator()
        root = Element("OpenScenario")
        fileheader = Element("FileHeader", {
            "revMajor": "1",
            "revMinor": "3",
            "date": "2023-12-01T10:00:00",
            "description": "Test"
        })
        root.add_child(fileheader)
        
        errors = validator.validate(root)
        
        assert len(errors) == 0

    def test_validate_non_root_element(self):
        """Should not validate non-root elements"""
        validator = XoscStructureValidator()
        element = Element("SomeOtherElement")
        
        errors = validator.validate(element)
        
        assert len(errors) == 0

    def test_validate_nested_structure(self):
        """Should validate nested structure correctly"""
        validator = XoscStructureValidator()
        root = Element("OpenSCENARIO")
        fileheader = Element("FileHeader", {
            "revMajor": "1",
            "revMinor": "3",
            "date": "2023-12-01T10:00:00",
            "description": "Test"
        })
        catalog = Element("CatalogLocations")
        entities = Element("Entities")
        root.add_child(fileheader)
        root.add_child(catalog)
        root.add_child(entities)
        
        errors = validator.validate(root)
        
        assert len(errors) == 0

    def test_validate_fileheader_with_empty_attributes(self):
        """Should error when FileHeader attributes are empty"""
        validator = XoscStructureValidator()
        root = Element("OpenSCENARIO")
        fileheader = Element("FileHeader", {
            "revMajor": "",
            "revMinor": "3",
            "date": "2023-12-01T10:00:00",
            "description": "Test"
        })
        root.add_child(fileheader)
        
        errors = validator.validate(root)
        
        assert len(errors) == 1
        assert "revMajor" in errors[0]

    def test_validate_fileheader_partial_attributes(self):
        """Should error for each missing required attribute"""
        validator = XoscStructureValidator()
        root = Element("OpenSCENARIO")
        fileheader = Element("FileHeader", {
            "revMajor": "1",
            "revMinor": "3"
            # Missing date and description
        })
        root.add_child(fileheader)
        
        errors = validator.validate(root)
        
        assert len(errors) == 2
        assert any("date" in error for error in errors)
        assert any("description" in error for error in errors)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
