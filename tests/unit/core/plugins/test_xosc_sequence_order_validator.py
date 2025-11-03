"""
Unit tests for XOSC Sequence Order Validator
Tests XoscSequenceOrderValidator plugin
"""

from openscenario_builder.core.utils.validators import XoscSequenceOrderValidator
from openscenario_builder.core.model.element import Element
from openscenario_builder.core.schema.parser import (
    SchemaInfo,
    ElementDefinition,
    AttributeDefinition,
    GroupDefinition,
    ChildElementInfo,
)


class TestXoscSequenceOrderValidator:
    """Test Sequence Order Validator plugin"""

    def test_validate_without_schema_info(self):
        """Should return error when schema info is missing"""
        validator = XoscSequenceOrderValidator()
        element = Element("Test")

        errors = validator.validate(element, None)

        assert len(errors) == 1
        assert "CONFIGURATION_ERROR" in errors[0]
        assert "Schema information required" in errors[0]

    def test_validate_correct_sequence_order(self):
        """Should not return error when elements are in correct sequence order"""
        validator = XoscSequenceOrderValidator()

        # Create parent element with children in correct order
        parent = Element("Parent")
        child1 = Element("FirstChild")
        child2 = Element("SecondChild")
        child3 = Element("ThirdChild")

        parent.add_child(child1)
        parent.add_child(child2)
        parent.add_child(child3)

        # Define schema with sequence content model
        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["FirstChild", "SecondChild", "ThirdChild"],
            content_model_type="sequence",
        )
        child1_def = ElementDefinition(name="FirstChild", attributes=[], children=[])
        child2_def = ElementDefinition(name="SecondChild", attributes=[], children=[])
        child3_def = ElementDefinition(name="ThirdChild", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "FirstChild": child1_def,
                "SecondChild": child2_def,
                "ThirdChild": child3_def,
            },
            groups={},
            root_elements=["Parent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(parent, schema_info)

        assert len(errors) == 0

    def test_validate_incorrect_sequence_order(self):
        """Should return error when elements are out of order"""
        validator = XoscSequenceOrderValidator()

        # Create parent element with children in wrong order
        parent = Element("Parent")
        child2 = Element("SecondChild")
        child1 = Element("FirstChild")  # Out of order
        child3 = Element("ThirdChild")

        parent.add_child(child2)  # Should come after FirstChild
        parent.add_child(child1)  # Out of order
        parent.add_child(child3)

        # Define schema with sequence content model
        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["FirstChild", "SecondChild", "ThirdChild"],
            content_model_type="sequence",
        )
        child1_def = ElementDefinition(name="FirstChild", attributes=[], children=[])
        child2_def = ElementDefinition(name="SecondChild", attributes=[], children=[])
        child3_def = ElementDefinition(name="ThirdChild", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "FirstChild": child1_def,
                "SecondChild": child2_def,
                "ThirdChild": child3_def,
            },
            groups={},
            root_elements=["Parent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(parent, schema_info)

        assert len(errors) >= 1
        assert any("SEQUENCE_ORDER_ERROR" in error for error in errors)
        assert any("FirstChild" in error for error in errors)

    def test_validate_optional_elements_omitted(self):
        """Should not error when optional elements omitted but order maintained"""
        validator = XoscSequenceOrderValidator()

        # Create parent with only some children (skipping optional ones)
        parent = Element("Parent")
        child1 = Element("FirstChild")
        child3 = Element("ThirdChild")  # Skipping SecondChild (optional)

        parent.add_child(child1)
        parent.add_child(child3)

        # Define schema with sequence content model
        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["FirstChild", "SecondChild", "ThirdChild"],
            content_model_type="sequence",
            child_occurrence_info={
                "FirstChild": ChildElementInfo(
                    name="FirstChild", min_occur=1, max_occur="1"
                ),
                "SecondChild": ChildElementInfo(
                    name="SecondChild", min_occur=0, max_occur="1"
                ),
                "ThirdChild": ChildElementInfo(
                    name="ThirdChild", min_occur=1, max_occur="1"
                ),
            },
        )
        child1_def = ElementDefinition(name="FirstChild", attributes=[], children=[])
        child2_def = ElementDefinition(name="SecondChild", attributes=[], children=[])
        child3_def = ElementDefinition(name="ThirdChild", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "FirstChild": child1_def,
                "SecondChild": child2_def,
                "ThirdChild": child3_def,
            },
            groups={},
            root_elements=["Parent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(parent, schema_info)

        assert len(errors) == 0

    def test_validate_multiple_occurrences_in_order(self):
        """Should not error when elements repeat in correct order"""
        validator = XoscSequenceOrderValidator()

        # Create parent with repeating child elements in order
        parent = Element("Parent")
        child1a = Element("Child")
        child1b = Element("Child")
        child1c = Element("Child")

        parent.add_child(child1a)
        parent.add_child(child1b)
        parent.add_child(child1c)

        # Define schema allowing multiple occurrences
        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["Child"],
            content_model_type="sequence",
            child_occurrence_info={
                "Child": ChildElementInfo(
                    name="Child", min_occur=1, max_occur="unbounded"
                ),
            },
        )
        child_def = ElementDefinition(name="Child", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "Child": child_def,
            },
            groups={},
            root_elements=["Parent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(parent, schema_info)

        assert len(errors) == 0

    def test_validate_mixed_order_with_repeating_elements(self):
        """Should error when repeating elements are mixed out of order"""
        validator = XoscSequenceOrderValidator()

        # Create parent with mixed order: A, B, A (A appears again after B)
        parent = Element("Parent")
        childA1 = Element("ChildA")
        childB = Element("ChildB")
        childA2 = Element("ChildA")  # Out of order - A should come before B

        parent.add_child(childA1)
        parent.add_child(childB)
        parent.add_child(childA2)  # This is wrong order

        # Define schema with sequence: A, A, B (A can appear twice, then B)
        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["ChildA", "ChildA", "ChildB"],
            content_model_type="sequence",
        )
        childA_def = ElementDefinition(name="ChildA", attributes=[], children=[])
        childB_def = ElementDefinition(name="ChildB", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "ChildA": childA_def,
                "ChildB": childB_def,
            },
            groups={},
            root_elements=["Parent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(parent, schema_info)

        assert len(errors) >= 1
        assert any("SEQUENCE_ORDER_ERROR" in error for error in errors)

    def test_validate_choice_group_in_sequence(self):
        """Should handle choice groups within sequences correctly"""
        validator = XoscSequenceOrderValidator()

        # Create parent with choice element in sequence
        parent = Element("Parent")
        child1 = Element("FirstChild")
        choice_child = Element("ChoiceB")  # One of the choice options
        child2 = Element("LastChild")

        parent.add_child(child1)
        parent.add_child(choice_child)
        parent.add_child(child2)

        # Define schema with choice group in sequence
        choice_group = GroupDefinition(
            name="MiddleChoice",
            children=["ChoiceA", "ChoiceB", "ChoiceC"],
            is_choice=True,
            is_sequence=False,
            is_all=False,
        )

        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["FirstChild", "GROUP:MiddleChoice", "LastChild"],
            content_model_type="sequence",
        )
        child1_def = ElementDefinition(name="FirstChild", attributes=[], children=[])
        choiceA_def = ElementDefinition(name="ChoiceA", attributes=[], children=[])
        choiceB_def = ElementDefinition(name="ChoiceB", attributes=[], children=[])
        choiceC_def = ElementDefinition(name="ChoiceC", attributes=[], children=[])
        child2_def = ElementDefinition(name="LastChild", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "FirstChild": child1_def,
                "ChoiceA": choiceA_def,
                "ChoiceB": choiceB_def,
                "ChoiceC": choiceC_def,
                "LastChild": child2_def,
            },
            groups={"MiddleChoice": choice_group},
            root_elements=["Parent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(parent, schema_info)

        assert len(errors) == 0

    def test_validate_choice_content_model(self):
        """Should not validate order for choice content model"""
        validator = XoscSequenceOrderValidator()

        # Create parent with choice content model (order doesn't matter)
        parent = Element("Parent")
        child2 = Element("ChoiceB")

        parent.add_child(child2)

        # Define schema with choice content model
        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["ChoiceA", "ChoiceB"],
            content_model_type="choice",  # Choice, not sequence
        )
        choiceA_def = ElementDefinition(name="ChoiceA", attributes=[], children=[])
        choiceB_def = ElementDefinition(name="ChoiceB", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "ChoiceA": choiceA_def,
                "ChoiceB": choiceB_def,
            },
            groups={},
            root_elements=["Parent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(parent, schema_info)

        # Should not validate order for choice content model
        assert len(errors) == 0

    def test_validate_nested_sequences(self):
        """Should validate sequences recursively in nested elements"""
        validator = XoscSequenceOrderValidator()

        # Create nested structure with out of order child
        grandparent = Element("GrandParent")
        parent = Element("Parent")
        child2 = Element("SecondChild")
        child1 = Element("FirstChild")  # Out of order

        grandparent.add_child(parent)
        parent.add_child(child2)
        parent.add_child(child1)  # This is out of order

        # Define schema
        grandparent_def = ElementDefinition(
            name="GrandParent",
            attributes=[],
            children=["Parent"],
            content_model_type="sequence",
        )
        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["FirstChild", "SecondChild"],
            content_model_type="sequence",
        )
        child1_def = ElementDefinition(name="FirstChild", attributes=[], children=[])
        child2_def = ElementDefinition(name="SecondChild", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "GrandParent": grandparent_def,
                "Parent": parent_def,
                "FirstChild": child1_def,
                "SecondChild": child2_def,
            },
            groups={},
            root_elements=["GrandParent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(grandparent, schema_info)

        assert len(errors) >= 1
        assert any("SEQUENCE_ORDER_ERROR" in error for error in errors)
        assert any("FirstChild" in error for error in errors)

    def test_validate_empty_parent(self):
        """Should not error when parent has no children"""
        validator = XoscSequenceOrderValidator()

        parent = Element("Parent")

        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["Child"],
            content_model_type="sequence",
        )

        schema_info = SchemaInfo(
            elements={"Parent": parent_def},
            groups={},
            root_elements=["Parent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(parent, schema_info)

        assert len(errors) == 0

    def test_validate_sequence_group_expansion(self):
        """Should properly expand sequence groups"""
        validator = XoscSequenceOrderValidator()

        # Create parent with group reference
        parent = Element("Parent")
        group_child1 = Element("GroupChildA")
        group_child2 = Element("GroupChildB")

        parent.add_child(group_child1)
        parent.add_child(group_child2)

        # Define schema with sequence group
        sequence_group = GroupDefinition(
            name="ChildrenGroup",
            children=["GroupChildA", "GroupChildB"],
            is_choice=False,
            is_sequence=True,
            is_all=False,
        )

        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["GROUP:ChildrenGroup"],
            content_model_type="sequence",
        )
        childA_def = ElementDefinition(name="GroupChildA", attributes=[], children=[])
        childB_def = ElementDefinition(name="GroupChildB", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "GroupChildA": childA_def,
                "GroupChildB": childB_def,
            },
            groups={"ChildrenGroup": sequence_group},
            root_elements=["Parent"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(parent, schema_info)

        assert len(errors) == 0

    def test_validate_complex_act_structure(self):
        """Test realistic Act structure from OpenSCENARIO schema"""
        validator = XoscSequenceOrderValidator()

        # Create Act element with correct sequence:
        # ManeuverGroup, StartTrigger, StopTrigger
        act = Element("Act", {"name": "TestAct"})
        maneuver_group = Element(
            "ManeuverGroup", {"name": "MG1", "maximumExecutionCount": "1"}
        )
        start_trigger = Element("StartTrigger")
        stop_trigger = Element("StopTrigger")

        act.add_child(maneuver_group)
        act.add_child(start_trigger)
        act.add_child(stop_trigger)

        # Define schema
        act_def = ElementDefinition(
            name="Act",
            attributes=[AttributeDefinition(name="name", type="String", required=True)],
            children=["ManeuverGroup", "StartTrigger", "StopTrigger"],
            content_model_type="sequence",
            child_occurrence_info={
                "ManeuverGroup": ChildElementInfo(
                    name="ManeuverGroup", min_occur=1, max_occur="unbounded"
                ),
                "StartTrigger": ChildElementInfo(
                    name="StartTrigger", min_occur=0, max_occur="1"
                ),
                "StopTrigger": ChildElementInfo(
                    name="StopTrigger", min_occur=0, max_occur="1"
                ),
            },
        )
        mg_def = ElementDefinition(name="ManeuverGroup", attributes=[], children=[])
        st_def = ElementDefinition(name="StartTrigger", attributes=[], children=[])
        sp_def = ElementDefinition(name="StopTrigger", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Act": act_def,
                "ManeuverGroup": mg_def,
                "StartTrigger": st_def,
                "StopTrigger": sp_def,
            },
            groups={},
            root_elements=["Act"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(act, schema_info)

        assert len(errors) == 0

    def test_validate_complex_act_structure_wrong_order(self):
        """Test Act structure with wrong order"""
        validator = XoscSequenceOrderValidator()

        # Create Act element with WRONG sequence: StartTrigger before ManeuverGroup
        act = Element("Act", {"name": "TestAct"})
        start_trigger = Element("StartTrigger")  # Wrong position
        maneuver_group = Element(
            "ManeuverGroup", {"name": "MG1", "maximumExecutionCount": "1"}
        )
        stop_trigger = Element("StopTrigger")

        act.add_child(start_trigger)  # Should come AFTER ManeuverGroup
        act.add_child(maneuver_group)
        act.add_child(stop_trigger)

        # Define schema (same as above)
        act_def = ElementDefinition(
            name="Act",
            attributes=[AttributeDefinition(name="name", type="String", required=True)],
            children=["ManeuverGroup", "StartTrigger", "StopTrigger"],
            content_model_type="sequence",
        )
        mg_def = ElementDefinition(name="ManeuverGroup", attributes=[], children=[])
        st_def = ElementDefinition(name="StartTrigger", attributes=[], children=[])
        sp_def = ElementDefinition(name="StopTrigger", attributes=[], children=[])

        schema_info = SchemaInfo(
            elements={
                "Act": act_def,
                "ManeuverGroup": mg_def,
                "StartTrigger": st_def,
                "StopTrigger": sp_def,
            },
            groups={},
            root_elements=["Act"],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(act, schema_info)

        assert len(errors) >= 1
        assert any("SEQUENCE_ORDER_ERROR" in error for error in errors)
        assert any(
            "ManeuverGroup" in error or "StartTrigger" in error for error in errors
        )
