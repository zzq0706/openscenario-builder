"""
Unit tests for XOSC Data Type Validator
Tests XoscDataTypeValidator plugin
"""

import pytest
from openscenario_builder.core.utils.validators import XoscDataTypeValidator
from openscenario_builder.core.model.element import Element


class TestXoscDataTypeValidator:
    """Test Data Type Validator plugin"""

    def test_validate_negative_transition_time(self):
        """Should error on negative transition time"""
        validator = XoscDataTypeValidator()
        element = Element("LightStateAction", {"transitionTime": "-1.0"})
        
        errors = validator.validate(element)
        
        assert len(errors) == 1
        assert "DATA_TYPE_ERROR" in errors[0]
        assert "non-negative" in errors[0]

    def test_validate_positive_transition_time(self):
        """Should accept non-negative transition time"""
        validator = XoscDataTypeValidator()
        root = Element("Root")
        element1 = Element("LightStateAction", {"transitionTime": "0.0"})
        element2 = Element("LightStateAction", {"transitionTime": "5.5"})
        root.add_child(element1)
        root.add_child(element2)
        
        errors = validator.validate(root)
        
        assert len(errors) == 0

    def test_validate_transition_time_with_parameter(self):
        """Should skip validation for parameter references"""
        validator = XoscDataTypeValidator()
        element = Element("LightStateAction", {"transitionTime": "$Duration"})
        
        errors = validator.validate(element)
        
        assert len(errors) == 0

    def test_validate_non_positive_duration(self):
        """Should error on non-positive duration"""
        validator = XoscDataTypeValidator()
        root = Element("Root")
        element1 = Element("Phase", {"duration": "0"})
        element2 = Element("Phase", {"duration": "-1"})
        root.add_child(element1)
        root.add_child(element2)
        
        errors = validator.validate(root)
        
        assert len(errors) == 2
        for error in errors:
            assert "DATA_TYPE_ERROR" in error
            assert "positive" in error

    def test_validate_positive_duration(self):
        """Should accept positive duration"""
        validator = XoscDataTypeValidator()
        element = Element("Phase", {"duration": "10.5"})
        
        errors = validator.validate(element)
        
        assert len(errors) == 0

    def test_validate_negative_speed(self):
        """Should error on negative speed"""
        validator = XoscDataTypeValidator()
        element = Element("Action", {"speed": "-10"})
        
        errors = validator.validate(element)
        
        assert len(errors) == 1
        assert "DATA_TYPE_ERROR" in errors[0]
        assert "non-negative" in errors[0]

    def test_validate_positive_speed(self):
        """Should accept non-negative speed"""
        validator = XoscDataTypeValidator()
        root = Element("Root")
        element1 = Element("Action", {"speed": "0"})
        element2 = Element("Action", {"speed": "50.5"})
        root.add_child(element1)
        root.add_child(element2)
        
        errors = validator.validate(root)
        
        assert len(errors) == 0

    def test_validate_probability_out_of_range(self):
        """Should error on probability outside [0, 1]"""
        validator = XoscDataTypeValidator()
        root = Element("Root")
        element1 = Element("Action", {"probability": "-0.1"})
        element2 = Element("Action", {"probability": "1.1"})
        root.add_child(element1)
        root.add_child(element2)
        
        errors = validator.validate(root)
        
        assert len(errors) == 2
        for error in errors:
            assert "DATA_TYPE_ERROR" in error
            assert "between 0 and 1" in error

    def test_validate_probability_valid(self):
        """Should accept probability in [0, 1]"""
        validator = XoscDataTypeValidator()
        root = Element("Root")
        element1 = Element("Action", {"probability": "0"})
        element2 = Element("Action", {"probability": "0.5"})
        element3 = Element("Action", {"probability": "1"})
        root.add_child(element1)
        root.add_child(element2)
        root.add_child(element3)
        
        errors = validator.validate(root)
        
        assert len(errors) == 0

    def test_validate_negative_distance(self):
        """Should error on negative distance"""
        validator = XoscDataTypeValidator()
        element = Element("Action", {"distance": "-5.0"})
        
        errors = validator.validate(element)
        
        assert len(errors) == 1
        assert "DATA_TYPE_ERROR" in errors[0]
        assert "non-negative" in errors[0]

    def test_validate_positive_distance(self):
        """Should accept non-negative distance"""
        validator = XoscDataTypeValidator()
        element = Element("Action", {"distance": "100.5"})
        
        errors = validator.validate(element)
        
        assert len(errors) == 0

    def test_validate_negative_time(self):
        """Should error on negative time (excluding AbsoluteTime)"""
        validator = XoscDataTypeValidator()
        element = Element("Action", {"time": "-1.0"})
        
        errors = validator.validate(element)
        
        assert len(errors) == 1
        assert "DATA_TYPE_ERROR" in errors[0]

    def test_validate_absolute_time_negative(self):
        """Should not validate time attribute for AbsoluteTime element"""
        validator = XoscDataTypeValidator()
        element = Element("AbsoluteTime", {"time": "-1.0"})
        
        errors = validator.validate(element)
        
        # AbsoluteTime is excluded from time validation
        assert len(errors) == 0

    def test_validate_acceleration_positive_and_negative(self):
        """Should accept both positive and negative acceleration"""
        validator = XoscDataTypeValidator()
        root = Element("Root")
        element1 = Element("Action", {"acceleration": "-2.5"})
        element2 = Element("Action", {"acceleration": "3.0"})
        root.add_child(element1)
        root.add_child(element2)
        
        errors = validator.validate(root)
        
        assert len(errors) == 0

    def test_validate_nested_elements(self):
        """Should validate nested element structures"""
        validator = XoscDataTypeValidator()
        root = Element("Root")
        parent = Element("Parent")
        child = Element("LightStateAction", {"transitionTime": "-1.0"})
        root.add_child(parent)
        parent.add_child(child)
        
        errors = validator.validate(root)
        
        assert len(errors) == 1
        assert "DATA_TYPE_ERROR" in errors[0]

    def test_validate_multiple_errors(self):
        """Should return all data type errors"""
        validator = XoscDataTypeValidator()
        root = Element("Root")
        element1 = Element("Action", {"speed": "-10"})
        element2 = Element("Action", {"probability": "1.5"})
        element3 = Element("Phase", {"duration": "0"})
        root.add_child(element1)
        root.add_child(element2)
        root.add_child(element3)
        
        errors = validator.validate(root)
        
        assert len(errors) == 3

    def test_validate_invalid_numeric_format(self):
        """Should not error on invalid format (handled by schema validator)"""
        validator = XoscDataTypeValidator()
        element = Element("Action", {"speed": "not_a_number"})
        
        errors = validator.validate(element)
        
        # Type format validation is handled by schema structure validator
        assert len(errors) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
