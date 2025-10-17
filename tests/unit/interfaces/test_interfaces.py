"""
Unit tests for interface definitions
Tests that all interface contracts are properly defined and enforceable
"""

import pytest
from abc import ABC
from datetime import datetime
from typing import Dict, List

from openscenario_builder.interfaces import (
    IElement, 
    IElementMetadata,
    ISchemaInfo,
    IElementDefinition,
    IAttributeDefinition,
    IChildElementInfo,
    IGroupDefinition,
    IPluginMetadata,
    IElementPlugin,
    IValidatorPlugin,
    IExportPlugin,
    IImportPlugin
)
# Import IBasePlugin directly from plugins module
from openscenario_builder.interfaces.plugins import IBasePlugin


class TestInterfaceDefinitions:
    """Test that all interfaces are properly defined as ABCs"""
    
    def test_ielement_is_abc(self):
        """IElement should be an ABC"""
        assert issubclass(IElement, ABC)
    
    def test_ielement_metadata_is_abc(self):
        """IElementMetadata should be an ABC"""
        assert issubclass(IElementMetadata, ABC)
    
    def test_ischema_info_is_abc(self):
        """ISchemaInfo should be an ABC"""
        assert issubclass(ISchemaInfo, ABC)
    
    def test_ielement_definition_is_abc(self):
        """IElementDefinition should be an ABC"""
        assert issubclass(IElementDefinition, ABC)
    
    def test_iattribute_definition_is_abc(self):
        """IAttributeDefinition should be an ABC"""
        assert issubclass(IAttributeDefinition, ABC)
    
    def test_ichild_element_info_is_abc(self):
        """IChildElementInfo should be an ABC"""
        assert issubclass(IChildElementInfo, ABC)
    
    def test_igroup_definition_is_abc(self):
        """IGroupDefinition should be an ABC"""
        assert issubclass(IGroupDefinition, ABC)
    
    def test_iplugin_metadata_is_abc(self):
        """IPluginMetadata should be an ABC"""
        assert issubclass(IPluginMetadata, ABC)
    
    def test_ibase_plugin_is_abc(self):
        """IBasePlugin should be an ABC"""
        assert issubclass(IBasePlugin, ABC)
    
    def test_ielement_plugin_is_abc(self):
        """IElementPlugin should be an ABC"""
        assert issubclass(IElementPlugin, ABC)
    
    def test_ivalidator_plugin_is_abc(self):
        """IValidatorPlugin should be an ABC"""
        assert issubclass(IValidatorPlugin, ABC)
    
    def test_iexport_plugin_is_abc(self):
        """IExportPlugin should be an ABC"""
        assert issubclass(IExportPlugin, ABC)
    
    def test_iimport_plugin_is_abc(self):
        """IImportPlugin should be an ABC"""
        assert issubclass(IImportPlugin, ABC)


class TestInterfaceEnforcement:
    """Test that interfaces enforce implementation of abstract methods"""
    
    def test_ielement_metadata_requires_properties(self):
        """IElementMetadata should require all properties to be implemented"""
        
        class IncompleteMetadata(IElementMetadata):
            pass
        
        with pytest.raises(TypeError, match="abstract"):
            IncompleteMetadata()
    
    def test_ielement_requires_all_methods(self):
        """IElement should require all methods to be implemented"""
        
        class IncompleteElement(IElement):
            pass
        
        with pytest.raises(TypeError, match="abstract"):
            IncompleteElement()
    
    def test_ischema_info_requires_properties(self):
        """ISchemaInfo should require all properties to be implemented"""
        
        class IncompleteSchemaInfo(ISchemaInfo):
            pass
        
        with pytest.raises(TypeError, match="abstract"):
            IncompleteSchemaInfo()
    
    def test_ivalidator_plugin_requires_methods(self):
        """IValidatorPlugin should require all abstract methods"""
        
        class IncompleteValidator(IValidatorPlugin):
            pass
        
        with pytest.raises(TypeError, match="abstract"):
            IncompleteValidator()


class TestInterfaceImplementation:
    """Test that interfaces can be properly implemented"""
    
    def test_ielement_metadata_can_be_implemented(self):
        """IElementMetadata should be implementable"""
        
        class TestMetadata(IElementMetadata):
            @property
            def created_at(self) -> datetime:
                return datetime.now()
            
            @property
            def modified_at(self) -> datetime:
                return datetime.now()
            
            @property
            def created_by(self) -> str:
                return "test"
            
            @property
            def description(self) -> str:
                return "test description"
            
            @property
            def tags(self) -> List[str]:
                return ["test"]
            
            @property
            def validation_errors(self) -> List[str]:
                return []
        
        metadata = TestMetadata()
        assert isinstance(metadata, IElementMetadata)
        assert metadata.created_by == "test"
        assert metadata.description == "test description"
        assert metadata.tags == ["test"]
        assert metadata.validation_errors == []
    
    def test_iattribute_definition_can_be_implemented(self):
        """IAttributeDefinition should be implementable"""
        
        class TestAttributeDefinition(IAttributeDefinition):
            @property
            def name(self) -> str:
                return "testAttr"
            
            @property
            def type(self) -> str:
                return "string"
            
            @property
            def required(self) -> bool:
                return True
        
        attr_def = TestAttributeDefinition()
        assert isinstance(attr_def, IAttributeDefinition)
        assert attr_def.name == "testAttr"
        assert attr_def.type == "string"
        assert attr_def.required is True
    
    def test_ichild_element_info_can_be_implemented(self):
        """IChildElementInfo should be implementable"""
        
        class TestChildElementInfo(IChildElementInfo):
            @property
            def name(self) -> str:
                return "ChildElement"
            
            @property
            def min_occur(self) -> int:
                return 1
            
            @property
            def max_occur(self) -> str:
                return "unbounded"
        
        child_info = TestChildElementInfo()
        assert isinstance(child_info, IChildElementInfo)
        assert child_info.name == "ChildElement"
        assert child_info.min_occur == 1
        assert child_info.max_occur == "unbounded"
    
    def test_iplugin_metadata_can_be_implemented(self):
        """IPluginMetadata should be implementable"""
        
        class TestPluginMetadata(IPluginMetadata):
            @property
            def name(self) -> str:
                return "Test Plugin"
            
            @property
            def version(self) -> str:
                return "1.0.0"
            
            @property
            def description(self) -> str:
                return "Test plugin description"
            
            @property
            def author(self) -> str:
                return "Test Author"
            
            @property
            def license(self) -> str:
                return "MIT"
            
            @property
            def homepage(self) -> str:
                return "https://example.com"
            
            @property
            def dependencies(self) -> List[str]:
                return []
            
            @property
            def tags(self) -> List[str]:
                return ["test"]
        
        metadata = TestPluginMetadata()
        assert isinstance(metadata, IPluginMetadata)
        assert metadata.name == "Test Plugin"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.license == "MIT"
        assert metadata.homepage == "https://example.com"
        assert metadata.dependencies == []
        assert metadata.tags == ["test"]
    
    def test_ivalidator_plugin_can_be_implemented(self):
        """IValidatorPlugin should be implementable"""
        
        class TestPluginMeta(IPluginMetadata):
            @property
            def name(self) -> str:
                return "Test Validator"
            
            @property
            def version(self) -> str:
                return "1.0.0"
            
            @property
            def description(self) -> str:
                return "Test"
            
            @property
            def author(self) -> str:
                return "Test"
            
            @property
            def license(self) -> str:
                return "MIT"
            
            @property
            def homepage(self) -> str:
                return ""
            
            @property
            def dependencies(self) -> List[str]:
                return []
            
            @property
            def tags(self) -> List[str]:
                return []
        
        class TestValidator(IValidatorPlugin):
            def __init__(self):
                self._activated = True
                self._metadata = TestPluginMeta()
            
            @property
            def activated(self) -> bool:
                return self._activated
            
            @activated.setter
            def activated(self, value: bool) -> None:
                self._activated = value
            
            @property
            def metadata(self) -> IPluginMetadata:
                return self._metadata
            
            def validate(self, element: IElement, schema_info=None) -> List[str]:
                return []
            
            def get_name(self) -> str:
                return "Test Validator"
        
        validator = TestValidator()
        assert isinstance(validator, IValidatorPlugin)
        assert validator.activated is True
        assert validator.get_name() == "Test Validator"
        assert validator.validate(None) == []
        
        validator.activated = False
        assert validator.activated is False


class TestInterfaceInheritance:
    """Test interface inheritance relationships"""
    
    def test_ielement_plugin_inherits_from_base(self):
        """IElementPlugin should inherit from IBasePlugin"""
        assert issubclass(IElementPlugin, IBasePlugin)
    
    def test_ivalidator_plugin_inherits_from_base(self):
        """IValidatorPlugin should inherit from IBasePlugin"""
        assert issubclass(IValidatorPlugin, IBasePlugin)
    
    def test_iexport_plugin_inherits_from_base(self):
        """IExportPlugin should inherit from IBasePlugin"""
        assert issubclass(IExportPlugin, IBasePlugin)
    
    def test_iimport_plugin_inherits_from_base(self):
        """IImportPlugin should inherit from IBasePlugin"""
        assert issubclass(IImportPlugin, IBasePlugin)


class TestInterfaceMethodSignatures:
    """Test that interface method signatures are correct"""
    
    def test_ielement_has_required_methods(self):
        """IElement should define all required methods"""
        required_methods = [
            'add_child', 'remove_child', 'insert_child',
            'get_child_by_tag', 'get_children_by_tag',
            'set_attribute', 'get_attribute', 'remove_attribute', 'has_attribute',
            'to_etree_element', 'to_xml_string', 'to_dict',
            'from_dict', 'from_etree_element', 'clone', 'find_elements_by_tag'
        ]
        
        for method in required_methods:
            assert hasattr(IElement, method), f"IElement should have {method} method"
    
    def test_ielement_has_required_properties(self):
        """IElement should define all required properties"""
        required_properties = ['tag', 'attrs', 'children', 'metadata']
        
        for prop in required_properties:
            assert hasattr(IElement, prop), f"IElement should have {prop} property"
    
    def test_ivalidator_plugin_has_validate_method(self):
        """IValidatorPlugin should have validate method"""
        assert hasattr(IValidatorPlugin, 'validate')
    
    def test_ielement_plugin_has_element_methods(self):
        """IElementPlugin should have element-specific methods"""
        assert hasattr(IElementPlugin, 'get_element_name')
        assert hasattr(IElementPlugin, 'get_attributes')
        assert hasattr(IElementPlugin, 'get_allowed_children')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
