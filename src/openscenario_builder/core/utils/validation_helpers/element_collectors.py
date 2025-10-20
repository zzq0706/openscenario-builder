"""
Element collection utilities for XOSC validators
Provides methods for collecting specific elements from the scenario tree
"""

from typing import Dict, List
from openscenario_builder.interfaces import IElement


class ElementCollector:
    """Collection methods for gathering elements from the scenario tree"""

    @staticmethod
    def collect_by_tags(root: IElement, tags: List[str]) -> Dict[str, IElement]:
        """
        Collect elements with specific tags from the element tree

        Args:
            root: Root element to start collection from
            tags: List of element tags to collect

        Returns:
            Dictionary mapping element names to elements
        """
        collected = {}

        def collect_recursive(elem: IElement):
            if elem.tag in tags:
                name = elem.attrs.get("name")
                if name:
                    collected[name] = elem

            for child in elem.children:
                collect_recursive(child)

        collect_recursive(root)
        return collected

    @staticmethod
    def collect_entities(root: IElement) -> Dict[str, IElement]:
        """Collect all entity definitions in the scenario"""
        return ElementCollector.collect_by_tags(
            root,
            ["ScenarioObject", "EntityObject", "Vehicle", "Pedestrian", "MiscObject"],
        )

    @staticmethod
    def collect_variables(root: IElement) -> Dict[str, IElement]:
        """Collect all variable declarations"""
        return ElementCollector.collect_by_tags(root, ["VariableDeclaration"])

    @staticmethod
    def collect_parameters(root: IElement) -> Dict[str, IElement]:
        """Collect all parameter declarations"""
        return ElementCollector.collect_by_tags(root, ["ParameterDeclaration"])

    @staticmethod
    def collect_storyboard_elements(root: IElement) -> Dict[str, IElement]:
        """Collect all storyboard elements (Acts, Maneuvers, Events, etc.)"""
        return ElementCollector.collect_by_tags(
            root, ["Act", "ManeuverGroup", "Maneuver", "Event", "Action"]
        )

    @staticmethod
    def collect_traffic_elements(
        root: IElement,
    ) -> tuple[Dict[str, IElement], Dict[str, IElement]]:
        """
        Collect traffic signal controllers and signals

        Returns:
            Tuple of (controllers, signals) dictionaries
        """
        controllers = {}
        signals = {}

        def collect_recursive(elem: IElement):
            if elem.tag == "TrafficSignalController":
                name = elem.attrs.get("name")
                if name:
                    controllers[name] = elem
            elif elem.tag == "TrafficSignal":
                signal_id = elem.attrs.get("id")
                if signal_id:
                    signals[signal_id] = elem

            for child in elem.children:
                collect_recursive(child)

        collect_recursive(root)
        return controllers, signals
