"""
Plugin System for OpenSCENARIO Builder

This package provides a plugin system for extending the OpenSCENARIO Builder
with custom elements, validators, and UI components.
"""

# Base classes
from .plugin_metadata import PluginMetadata

# Plugin implementations
from .xosc_scenario_validator_plugin import XoscScenarioValidatorPlugin
from .import_plugin import ImportPlugin
from .export_plugin import ExportPlugin
from .plugin_manager import PluginManager

__all__ = [
    # Base classes
    "PluginMetadata",
    # Plugin implementations
    "XoscScenarioValidatorPlugin",
    "ImportPlugin",
    "ExportPlugin",
    # Plugin management
    "PluginManager",
]
