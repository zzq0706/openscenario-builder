"""
Plugin Manager for OpenSCENARIO Builder
Handles plugin discovery, loading, and management
"""

import importlib.util
import inspect
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from openscenario_builder.interfaces import (
    IElementPlugin,
    IValidatorPlugin,
    IUIPlugin,
    IExportPlugin,
    IImportPlugin,
    IElement,
    ISchemaInfo,
)

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages loading and registration of plugins"""

    def __init__(
        self,
    ):
        self.element_plugins: Dict[str, IElementPlugin] = {}
        self.validator_plugins: Dict[str, IValidatorPlugin] = {}
        self.ui_plugins: Dict[str, IUIPlugin] = {}
        self.export_plugins: Dict[str, IExportPlugin] = {}
        self.import_plugins: Dict[str, IImportPlugin] = {}

        self.plugin_paths: List[Path] = []
        self.loaded_modules: Dict[str, Any] = {}

    def add_plugin_path(self, path: str) -> None:
        """Add a directory to search for plugins"""
        plugin_path = Path(path)
        if plugin_path.exists() and plugin_path.is_dir():
            self.plugin_paths.append(plugin_path)
            logger.info(f"Added plugin path: {plugin_path}")
        else:
            logger.warning(f"Plugin path does not exist: {plugin_path}")

    def discover_plugins(self) -> Dict[str, List[str]]:
        """Discover all available plugins without loading them"""
        discovered = {
            "element": [],
            "validator": [],
            "ui": [],
            "export": [],
            "import": [],
        }

        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                continue

            for file_path in plugin_path.rglob("*.py"):
                if file_path.name.startswith("_"):
                    continue

                try:
                    # Try to load the module to inspect it
                    spec = importlib.util.spec_from_file_location(
                        file_path.stem, file_path
                    )
                    if spec is None or spec.loader is None:
                        continue

                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Look for plugin classes
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj):
                            if (
                                issubclass(obj, IElementPlugin)
                                and obj != IElementPlugin
                            ):
                                discovered["element"].append(f"{file_path.stem}.{name}")
                            elif (
                                issubclass(obj, IValidatorPlugin)
                                and obj != IValidatorPlugin
                            ):
                                discovered["validator"].append(
                                    f"{file_path.stem}.{name}"
                                )
                            elif issubclass(obj, IUIPlugin) and obj != IUIPlugin:
                                discovered["ui"].append(f"{file_path.stem}.{name}")
                            elif (
                                issubclass(obj, IExportPlugin) and obj != IExportPlugin
                            ):
                                discovered["export"].append(f"{file_path.stem}.{name}")
                            elif (
                                issubclass(obj, IImportPlugin) and obj != IImportPlugin
                            ):
                                discovered["import"].append(f"{file_path.stem}.{name}")

                except Exception as e:
                    logger.warning(f"Failed to inspect {file_path}: {e}")

        return discovered

    def load_plugins(self) -> Dict[str, int]:
        """Load all discovered plugins"""
        loaded_counts = {
            "element": 0,
            "validator": 0,
            "ui": 0,
            "export": 0,
            "import": 0,
        }

        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                continue

            for file_path in plugin_path.rglob("*.py"):
                if file_path.name.startswith("_"):
                    continue

                try:
                    self._load_plugin_from_file(file_path, loaded_counts)
                except Exception as e:
                    logger.error(f"Failed to load plugin {file_path}: {e}")

        logger.info(f"Loaded plugins: {loaded_counts}")
        return loaded_counts

    def _load_plugin_from_file(
        self, file_path: Path, loaded_counts: Dict[str, int]
    ) -> None:
        """Load plugins from a single file"""
        module_name = file_path.stem

        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            logger.warning(f"Could not load spec for {module_name}")
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.loaded_modules[module_name] = module

        # Look for plugin classes
        for name, obj in inspect.getmembers(module):
            if not inspect.isclass(obj):
                continue

            try:
                if issubclass(obj, IElementPlugin) and obj != IElementPlugin:
                    plugin = obj()
                    # Only load if plugin is activated
                    if plugin.activated:
                        self.register_element_plugin(plugin)
                        loaded_counts["element"] += 1
                        logger.info(f"Loaded element plugin: {plugin.metadata.name}")
                    else:
                        logger.info(
                            f"Skipped deactivated element plugin: "
                            f"{plugin.metadata.name}"
                        )

                elif issubclass(obj, IValidatorPlugin) and obj != IValidatorPlugin:
                    plugin = obj()
                    # Only load if plugin is activated
                    if plugin.activated:
                        self.register_validator_plugin(plugin)
                        loaded_counts["validator"] += 1
                        logger.info(f"Loaded validator plugin: {plugin.metadata.name}")
                    else:
                        logger.info(
                            f"Skipped deactivated validator plugin: "
                            f"{plugin.metadata.name}"
                        )

                elif issubclass(obj, IUIPlugin) and obj != IUIPlugin:
                    plugin = obj()
                    # Only load if plugin is activated
                    if plugin.activated:
                        self.register_ui_plugin(plugin)
                        loaded_counts["ui"] += 1
                        logger.info(f"Loaded UI plugin: {plugin.metadata.name}")
                    else:
                        logger.info(
                            f"Skipped deactivated UI plugin: {plugin.metadata.name}"
                        )

                elif issubclass(obj, IExportPlugin) and obj != IExportPlugin:
                    plugin = obj()
                    # Only load if plugin is activated
                    if plugin.activated:
                        self.register_export_plugin(plugin)
                        loaded_counts["export"] += 1
                        logger.info(f"Loaded export plugin: {plugin.metadata.name}")
                    else:
                        logger.info(
                            f"Skipped deactivated export plugin: {plugin.metadata.name}"
                        )

                elif issubclass(obj, IImportPlugin) and obj != IImportPlugin:
                    plugin = obj()
                    # Only load if plugin is activated
                    if plugin.activated:
                        self.register_import_plugin(plugin)
                        loaded_counts["import"] += 1
                        logger.info(f"Loaded import plugin: {plugin.metadata.name}")
                    else:
                        logger.info(
                            f"Skipped deactivated import plugin: {plugin.metadata.name}"
                        )

            except Exception as e:
                logger.error(
                    f"Failed to instantiate plugin {name} from {file_path}: {e}"
                )

    def register_element_plugin(self, plugin: IElementPlugin) -> None:
        """Register an element plugin"""
        element_name = plugin.get_element_name()
        self.element_plugins[element_name] = plugin

    def register_validator_plugin(self, plugin: IValidatorPlugin) -> None:
        """Register a validator plugin"""
        validator_name = plugin.get_name()
        self.validator_plugins[validator_name] = plugin

    def register_ui_plugin(self, plugin: IUIPlugin) -> None:
        """Register a UI plugin"""
        ui_name = plugin.get_widget_name()
        self.ui_plugins[ui_name] = plugin

    def register_export_plugin(self, plugin: IExportPlugin) -> None:
        """Register an export plugin"""
        for format_ext in plugin.get_supported_formats():
            self.export_plugins[format_ext] = plugin

    def register_import_plugin(self, plugin: IImportPlugin) -> None:
        """Register an import plugin"""
        for format_ext in plugin.get_supported_formats():
            self.import_plugins[format_ext] = plugin

    def get_element_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get element definitions from all element plugins"""
        definitions = {}

        for element_name, plugin in self.element_plugins.items():
            definitions[element_name] = {
                "attrs": plugin.get_attributes(),
                "children": plugin.get_allowed_children(),
                "description": plugin.get_description(),
                "plugin": plugin,
            }

        return definitions

    def validate_element(self, element: IElement) -> List[str]:
        """Validate an element using its plugin"""
        plugin = self.element_plugins.get(element.tag)
        if plugin:
            return plugin.validate(element)
        return []

    def validate_scenario(
        self, root_element: IElement, schema_info: ISchemaInfo
    ) -> List[str]:
        """Validate a scenario using all validator plugins"""
        errors = []
        for validator in self.validator_plugins.values():
            try:
                validator_errors = validator.validate(root_element, schema_info)
                errors.extend(validator_errors)
                # print(f"validator: {validator.get_name()}")
                # print(f"validator_errors: {validator_errors}")

            except Exception as e:
                logger.error(f"Validator {validator.get_name()} failed: {e}")
                errors.append(f"Validation error in {validator.get_name()}: {e}")

        return errors

    def get_export_formats(self) -> Dict[str, str]:
        """Get available export formats and their descriptions"""
        formats = {}
        for format_ext, plugin in self.export_plugins.items():
            formats[format_ext] = plugin.get_format_description(format_ext)
        return formats

    def get_import_formats(self) -> Dict[str, str]:
        """Get available import formats and their descriptions"""
        formats = {}
        for format_ext, plugin in self.import_plugins.items():
            formats[format_ext] = plugin.get_format_description(format_ext)
        return formats

    def export_scenario(self, scenario: IElement, output_path: str) -> bool:
        """Export scenario using appropriate plugin"""
        format_ext = Path(output_path).suffix.lower()
        plugin = self.export_plugins.get(format_ext)

        if plugin:
            try:
                return plugin.export_scenario(scenario, output_path)
            except Exception as e:
                logger.error(f"Export failed: {e}")
                return False
        else:
            logger.error(f"No export plugin found for format: {format_ext}")
            return False

    def import_scenario(self, file_path: str) -> Optional[IElement]:
        """Import scenario using appropriate plugin"""
        format_ext = Path(file_path).suffix.lower()
        plugin = self.import_plugins.get(format_ext)

        if plugin:
            try:
                return plugin.import_scenario(file_path)
            except Exception as e:
                logger.error(f"Import failed: {e}")
                return None
        else:
            logger.error(f"No import plugin found for format: {format_ext}")
            return None

    def get_plugin_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get information about all loaded plugins"""
        info = {"element": [], "validator": [], "ui": [], "export": [], "import": []}

        for plugin in self.element_plugins.values():
            info["element"].append(
                {
                    "name": plugin.metadata.name,
                    "version": plugin.metadata.version,
                    "description": plugin.metadata.description,
                    "author": plugin.metadata.author,
                    "element_name": plugin.get_element_name(),
                    "category": plugin.get_category(),
                }
            )

        for plugin in self.validator_plugins.values():
            info["validator"].append(
                {
                    "name": plugin.metadata.name,
                    "version": plugin.metadata.version,
                    "description": plugin.metadata.description,
                    "author": plugin.metadata.author,
                }
            )

        for plugin in self.ui_plugins.values():
            info["ui"].append(
                {
                    "name": plugin.metadata.name,
                    "version": plugin.metadata.version,
                    "description": plugin.metadata.description,
                    "author": plugin.metadata.author,
                }
            )

        for format_ext, plugin in self.export_plugins.items():
            info["export"].append(
                {
                    "name": plugin.metadata.name,
                    "version": plugin.metadata.version,
                    "description": plugin.metadata.description,
                    "author": plugin.metadata.author,
                    "format": format_ext,
                }
            )

        for format_ext, plugin in self.import_plugins.items():
            info["import"].append(
                {
                    "name": plugin.metadata.name,
                    "version": plugin.metadata.version,
                    "description": plugin.metadata.description,
                    "author": plugin.metadata.author,
                    "format": format_ext,
                }
            )

        return info

    def set_plugin_activation(self, plugin_name: str, activated: bool) -> bool:
        """Set the activation status of a plugin"""
        try:
            # Attempt to find the plugin by its name
            # This is a simplified approach; a more robust solution might involve
            # a more specific interface or a dedicated method for activation.
            # For now, we'll iterate through all loaded plugins to find it.
            for plugin in self.element_plugins.values():
                if plugin.metadata.name == plugin_name:
                    plugin.activated = activated
                    logger.info(f"Activated element plugin: {plugin_name}")
                    return True
            for plugin in self.validator_plugins.values():
                if plugin.metadata.name == plugin_name:
                    plugin.activated = activated
                    logger.info(f"Activated validator plugin: {plugin_name}")
                    return True
            for plugin in self.ui_plugins.values():
                if plugin.metadata.name == plugin_name:
                    plugin.activated = activated
                    logger.info(f"Activated UI plugin: {plugin_name}")
                    return True
            for plugin in self.export_plugins.values():
                if plugin.metadata.name == plugin_name:
                    plugin.activated = activated
                    logger.info(f"Activated export plugin: {plugin_name}")
                    return True
            for plugin in self.import_plugins.values():
                if plugin.metadata.name == plugin_name:
                    plugin.activated = activated
                    logger.info(f"Activated import plugin: {plugin_name}")
                    return True
            logger.warning(f"Plugin {plugin_name} not found.")
            return False
        except Exception as e:
            logger.error(f"Failed to set plugin activation: {e}")
            return False

    def get_plugin_activation_status(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get activation status of all discovered plugins"""
        status = {"element": [], "validator": [], "ui": [], "export": [], "import": []}

        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                continue

            for file_path in plugin_path.rglob("*.py"):
                if file_path.name.startswith("_"):
                    continue

                try:
                    # Try to load the module to inspect it
                    spec = importlib.util.spec_from_file_location(
                        file_path.stem, file_path
                    )
                    if spec is None or spec.loader is None:
                        continue

                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Look for plugin classes
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj):
                            try:
                                if (
                                    issubclass(obj, IElementPlugin)
                                    and obj != IElementPlugin
                                ):
                                    plugin = obj()
                                    status["element"].append(
                                        {
                                            "name": plugin.metadata.name,
                                            "activated": plugin.activated,
                                            "file": str(file_path),
                                            "class": name,
                                        }
                                    )
                                elif (
                                    issubclass(obj, IValidatorPlugin)
                                    and obj != IValidatorPlugin
                                ):
                                    plugin = obj()
                                    status["validator"].append(
                                        {
                                            "name": plugin.metadata.name,
                                            "activated": plugin.activated,
                                            "file": str(file_path),
                                            "class": name,
                                        }
                                    )
                                elif issubclass(obj, IUIPlugin) and obj != IUIPlugin:
                                    plugin = obj()
                                    status["ui"].append(
                                        {
                                            "name": plugin.metadata.name,
                                            "activated": plugin.activated,
                                            "file": str(file_path),
                                            "class": name,
                                        }
                                    )
                                elif (
                                    issubclass(obj, IExportPlugin)
                                    and obj != IExportPlugin
                                ):
                                    plugin = obj()
                                    status["export"].append(
                                        {
                                            "name": plugin.metadata.name,
                                            "activated": plugin.activated,
                                            "file": str(file_path),
                                            "class": name,
                                        }
                                    )
                                elif (
                                    issubclass(obj, IImportPlugin)
                                    and obj != IImportPlugin
                                ):
                                    plugin = obj()
                                    status["import"].append(
                                        {
                                            "name": plugin.metadata.name,
                                            "activated": plugin.activated,
                                            "file": str(file_path),
                                            "class": name,
                                        }
                                    )
                            except Exception as e:
                                logger.warning(
                                    f"Failed to inspect plugin {name} "
                                    f"from {file_path}: {e}"
                                )

                except Exception as e:
                    logger.warning(f"Failed to inspect {file_path}: {e}")

        return status

    def reload_plugins(self) -> Dict[str, int]:
        """Reload all plugins, respecting activation status"""
        # Clear existing plugins
        self.element_plugins.clear()
        self.validator_plugins.clear()
        self.ui_plugins.clear()
        self.export_plugins.clear()
        self.import_plugins.clear()

        # Reload
        return self.load_plugins()
