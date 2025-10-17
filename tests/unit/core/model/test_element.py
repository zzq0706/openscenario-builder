"""
Unit tests for core model implementations
Tests Element and ElementMetadata classes
"""

import pytest
from datetime import datetime
from openscenario_builder.core.model.element import Element, ElementMetadata
from openscenario_builder.interfaces import IElement, IElementMetadata


class TestElementMetadata:
    """Test ElementMetadata implementation"""
    
    def test_create_default_metadata(self):
        """Should create metadata with defaults"""
        metadata = ElementMetadata()
        
        assert isinstance(metadata, IElementMetadata)
        assert isinstance(metadata.created_at, datetime)
        assert isinstance(metadata.modified_at, datetime)
        assert metadata.created_by == ""
        assert metadata.description == ""
        assert metadata.tags == []
        assert metadata.validation_errors == []
    
    def test_create_metadata_with_values(self):
        """Should create metadata with custom values"""
        now = datetime.now()
        metadata = ElementMetadata(
            created_at=now,
            modified_at=now,
            created_by="test_user",
            description="Test description",
            tags=["test", "unit"],
            validation_errors=["error1"]
        )
        
        assert metadata.created_at == now
        assert metadata.modified_at == now
        assert metadata.created_by == "test_user"
        assert metadata.description == "Test description"
        assert metadata.tags == ["test", "unit"]
        assert metadata.validation_errors == ["error1"]
    
    def test_metadata_properties_are_readable(self):
        """All metadata properties should be readable"""
        metadata = ElementMetadata(
            created_by="test",
            description="desc",
            tags=["tag1"]
        )
        
        # Should not raise exceptions
        _ = metadata.created_at
        _ = metadata.modified_at
        _ = metadata.created_by
        _ = metadata.description
        _ = metadata.tags
        _ = metadata.validation_errors
    
    def test_modified_at_is_settable(self):
        """modified_at should have a setter"""
        metadata = ElementMetadata()
        new_time = datetime(2025, 1, 1)
        
        metadata.modified_at = new_time
        assert metadata.modified_at == new_time


class TestElement:
    """Test Element implementation"""
    
    def test_create_simple_element(self):
        """Should create a simple element"""
        element = Element("TestElement")
        
        assert isinstance(element, IElement)
        assert element.tag == "TestElement"
        assert element.attrs == {}
        assert element.children == []
        assert isinstance(element.metadata, IElementMetadata)
    
    def test_create_element_with_attributes(self):
        """Should create element with attributes"""
        attrs = {"attr1": "value1", "attr2": "value2"}
        element = Element("TestElement", attrs)
        
        assert element.tag == "TestElement"
        assert element.attrs == attrs
        assert element.get_attribute("attr1") == "value1"
        assert element.get_attribute("attr2") == "value2"
    
    def test_create_element_with_children(self):
        """Should create element with children"""
        child1 = Element("Child1")
        child2 = Element("Child2")
        element = Element("Parent", children=[child1, child2])
        
        assert len(element.children) == 2
        assert element.children[0].tag == "Child1"
        assert element.children[1].tag == "Child2"
    
    
    def test_add_child(self):
        """Should add child element"""
        parent = Element("Parent")
        child = Element("Child")
        
        parent.add_child(child)
        
        assert len(parent.children) == 1
        assert parent.children[0] == child
    
    def test_remove_child(self):
        """Should remove child element"""
        parent = Element("Parent")
        child = Element("Child")
        parent.add_child(child)
        
        result = parent.remove_child(child)
        
        assert result is True
        assert len(parent.children) == 0
    
    def test_remove_nonexistent_child(self):
        """Should return False when removing nonexistent child"""
        parent = Element("Parent")
        child = Element("Child")
        
        result = parent.remove_child(child)
        
        assert result is False
    
    def test_insert_child(self):
        """Should insert child at specific index"""
        parent = Element("Parent")
        child1 = Element("Child1")
        child2 = Element("Child2")
        child3 = Element("Child3")
        
        parent.add_child(child1)
        parent.add_child(child3)
        parent.insert_child(1, child2)
        
        assert len(parent.children) == 3
        assert parent.children[0] == child1
        assert parent.children[1] == child2
        assert parent.children[2] == child3
    
    def test_get_child_by_tag(self):
        """Should get first child by tag"""
        parent = Element("Parent")
        child1 = Element("Child")
        child2 = Element("Child")
        parent.add_child(child1)
        parent.add_child(child2)
        
        result = parent.get_child_by_tag("Child")
        
        assert result == child1
    
    def test_get_child_by_tag_not_found(self):
        """Should return None when child not found"""
        parent = Element("Parent")
        
        result = parent.get_child_by_tag("NonExistent")
        
        assert result is None
    
    def test_get_children_by_tag(self):
        """Should get all children by tag"""
        parent = Element("Parent")
        child1 = Element("Child")
        child2 = Element("Other")
        child3 = Element("Child")
        parent.add_child(child1)
        parent.add_child(child2)
        parent.add_child(child3)
        
        results = parent.get_children_by_tag("Child")
        
        assert len(results) == 2
        assert child1 in results
        assert child3 in results
        assert child2 not in results
    
    def test_set_attribute(self):
        """Should set attribute value"""
        element = Element("Test")
        
        element.set_attribute("name", "value")
        
        assert element.get_attribute("name") == "value"
    
    def test_get_attribute_default(self):
        """Should return default when attribute not found"""
        element = Element("Test")
        
        result = element.get_attribute("nonexistent", "default")
        
        assert result == "default"
    
    def test_remove_attribute(self):
        """Should remove attribute"""
        element = Element("Test", {"name": "value"})
        
        result = element.remove_attribute("name")
        
        assert result is True
        assert not element.has_attribute("name")
    
    def test_remove_nonexistent_attribute(self):
        """Should return False when removing nonexistent attribute"""
        element = Element("Test")
        
        result = element.remove_attribute("nonexistent")
        
        assert result is False
    
    def test_has_attribute(self):
        """Should check if attribute exists"""
        element = Element("Test", {"name": "value"})
        
        assert element.has_attribute("name") is True
        assert element.has_attribute("nonexistent") is False
    
    def test_to_dict(self):
        """Should convert to dictionary"""
        element = Element("Test", {"attr": "value"})
        
        result = element.to_dict()
        
        assert result["tag"] == "Test"
        assert result["attrs"] == {"attr": "value"}
        assert "children" in result
        assert "metadata" in result
    
    def test_from_dict(self):
        """Should create from dictionary"""
        data = {
            "tag": "Test",
            "attrs": {"attr": "value"},
            "children": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "modified_at": datetime.now().isoformat(),
                "created_by": "test",
                "description": "desc",
                "tags": ["test"]
            }
        }
        
        element = Element.from_dict(data)
        
        assert element.tag == "Test"
        assert element.attrs == {"attr": "value"}
        assert element.metadata.created_by == "test"
    
    def test_clone(self):
        """Should create deep copy"""
        original = Element("Test", {"attr": "value"})
        original.add_child(Element("Child"))
        
        cloned = original.clone()
        
        assert cloned.tag == original.tag
        assert cloned.attrs == original.attrs
        assert len(cloned.children) == len(original.children)
        assert cloned is not original
        assert cloned.children[0] is not original.children[0]
    
    def test_find_elements_by_tag(self):
        """Should find all elements by tag in subtree"""
        root = Element("Root")
        child1 = Element("Target")
        child2 = Element("Other")
        grandchild = Element("Target")
        
        root.add_child(child1)
        root.add_child(child2)
        child2.add_child(grandchild)
        
        results = root.find_elements_by_tag("Target")
        
        assert len(results) == 2
        assert child1 in results
        assert grandchild in results
    
    def test_to_xml_string(self):
        """Should convert to XML string"""
        element = Element("Test", {"attr": "value"})
        
        xml_str = element.to_xml_string()
        
        assert isinstance(xml_str, str)
        assert "Test" in xml_str
        assert "attr" in xml_str
        assert "value" in xml_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
