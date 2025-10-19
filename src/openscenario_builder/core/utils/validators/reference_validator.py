"""
XOSC Reference Validator
Validates all reference-related checks (entities, parameters, variables, storyboard, traffic signals)
"""

from typing import Dict, List, Optional

from openscenario_builder.core.utils.validation_helpers import ElementCollector

from openscenario_builder.interfaces import IElement, ISchemaInfo


class XoscReferenceValidator:
    """Validates that all references can be resolved to their declarations"""

    def validate(self, element: IElement, schema_info: Optional[ISchemaInfo] = None) -> List[str]:
        """
        Validate all references in the scenario
        
        Args:
            element: Root element to validate
            schema_info: Optional schema information (not used by this validator)
            
        Returns:
            List of validation error messages
        """
        errors = []

        # Collect all declarations
        entities = ElementCollector.collect_entities(element)
        variables = ElementCollector.collect_variables(element)
        parameters = ElementCollector.collect_parameters(element)
        storyboard_elements = ElementCollector.collect_storyboard_elements(element)

        # Validate references
        errors.extend(self._validate_entity_references(element, entities))
        errors.extend(self._validate_variable_references(element, variables))
        errors.extend(self._validate_parameter_references(element, parameters))
        errors.extend(self._validate_storyboard_element_references(element, storyboard_elements))
        errors.extend(self._validate_traffic_signal_references(element))

        return errors

    def _validate_entity_references(
        self,
        element: IElement,
        entities: Dict[str, IElement]
    ) -> List[str]:
        """
        Validate that all entity references can be resolved
        
        Args:
            element: Root element
            entities: Dictionary of declared entities
            
        Returns:
            List of validation errors
        """
        errors = []

        def validate_recursive(elem: IElement):
            # Check for entity reference attributes
            entity_ref_attrs = ["entityRef", "objectRef", "actorRef"]
            for attr_name in entity_ref_attrs:
                if attr_name in elem.attrs:
                    ref_value = elem.attrs[attr_name]
                    # Skip parameter references and check if entity exists
                    if ref_value and not ref_value.startswith('$') and ref_value not in entities:
                        available = ', '.join(entities.keys()) if entities else "None"
                        error_msg = (
                            f"REFERENCE_ERROR: Entity reference '{ref_value}' in element '{elem.tag}' "
                            f"cannot be resolved. Available entities: {available}. "
                            f"Fix: Use one of the available entity names or define the referenced entity."
                        )
                        errors.append(error_msg)

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def _validate_variable_references(
        self,
        element: IElement,
        variables: Dict[str, IElement]
    ) -> List[str]:
        """
        Validate that all variable references can be resolved
        
        Args:
            element: Root element
            variables: Dictionary of declared variables
            
        Returns:
            List of validation errors
        """
        errors = []

        def validate_recursive(elem: IElement):
            if elem.tag == "VariableAction" and "variableRef" in elem.attrs:
                ref_value = elem.attrs["variableRef"]
                if ref_value and ref_value not in variables:
                    available = ', '.join(variables.keys()) if variables else "None"
                    error_msg = (
                        f"REFERENCE_ERROR: Variable reference '{ref_value}' in VariableAction "
                        f"cannot be resolved. Available variables: {available}. "
                        f"Fix: Use one of the available variable names or declare the referenced variable."
                    )
                    errors.append(error_msg)

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def _validate_parameter_references(
        self,
        element: IElement,
        parameters: Dict[str, IElement]
    ) -> List[str]:
        """
        Validate that all parameter references can be resolved
        
        Args:
            element: Root element
            parameters: Dictionary of declared parameters
            
        Returns:
            List of validation errors
        """
        errors = []

        def validate_recursive(elem: IElement):
            for attr_name, attr_value in elem.attrs.items():
                # Skip reference attributes as they're validated separately and can be parameters or entity names
                reference_attrs = ["variableRef", "entityRef", "objectRef", "actorRef", 
                                   "actRef", "maneuverRef", "eventRef", "actionRef"]
                if attr_name not in reference_attrs and attr_value and attr_value.startswith('$'):
                    param_name = attr_value[1:]  # Remove $ prefix
                    if param_name not in parameters:
                        available = ', '.join(parameters.keys()) if parameters else "None"
                        error_msg = (
                            f"REFERENCE_ERROR: Parameter reference '{param_name}' in element '{elem.tag}' "
                            f"attribute '{attr_name}' cannot be resolved. "
                            f"Available parameters: {available}. "
                            f"Fix: Use one of the available parameter names or define the referenced parameter."
                        )
                        errors.append(error_msg)

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def _validate_storyboard_element_references(
        self,
        element: IElement,
        storyboard_elements: Dict[str, IElement]
    ) -> List[str]:
        """
        Validate that all storyboard element references can be resolved
        
        Args:
            element: Root element
            storyboard_elements: Dictionary of declared storyboard elements
            
        Returns:
            List of validation errors
        """
        errors = []

        def validate_recursive(elem: IElement):
            storyboard_ref_attrs = ["actRef", "maneuverRef", "eventRef", "actionRef"]
            for attr_name in storyboard_ref_attrs:
                if attr_name in elem.attrs:
                    ref_value = elem.attrs[attr_name]
                    # Skip parameter references and check if element exists
                    if ref_value and not ref_value.startswith('$') and ref_value not in storyboard_elements:
                        available = ', '.join(storyboard_elements.keys()) if storyboard_elements else "None"
                        error_msg = (
                            f"REFERENCE_ERROR: Storyboard element reference '{ref_value}' "
                            f"in element '{elem.tag}' cannot be resolved. "
                            f"Available elements: {available}. "
                            f"Fix: Use one of the available element names or define the referenced element."
                        )
                        errors.append(error_msg)

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def _validate_traffic_signal_references(self, element: IElement) -> List[str]:
        """
        Validate traffic signal controller and signal ID references
        
        Args:
            element: Root element
            
        Returns:
            List of validation errors
        """
        errors = []

        # Collect traffic signal controllers and signals
        controllers, signals = ElementCollector.collect_traffic_elements(element)

        def validate_traffic_refs(elem: IElement):
            if elem.tag == "TrafficSignalStateAction":
                if "trafficSignalControllerRef" in elem.attrs:
                    controller_ref = elem.attrs["trafficSignalControllerRef"]
                    if controller_ref and controller_ref not in controllers:
                        available = ', '.join(controllers.keys()) if controllers else "None"
                        error_msg = (
                            f"REFERENCE_ERROR: Traffic signal controller reference '{controller_ref}' "
                            f"cannot be resolved. Available controllers: {available}. "
                            f"Fix: Use one of the available controller names or define the referenced controller."
                        )
                        errors.append(error_msg)

                if "signalId" in elem.attrs:
                    signal_id = elem.attrs["signalId"]
                    if signal_id and signal_id not in signals:
                        available = ', '.join(signals.keys()) if signals else "None"
                        error_msg = (
                            f"REFERENCE_ERROR: Signal ID '{signal_id}' cannot be resolved. "
                            f"Available signal IDs: {available}. "
                            f"Fix: Use one of the available signal IDs or define the referenced signal."
                        )
                        errors.append(error_msg)

            for child in elem.children:
                validate_traffic_refs(child)

        validate_traffic_refs(element)
        return errors
