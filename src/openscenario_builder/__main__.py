"""
Main application entry point for OpenSCENARIO Builder
"""

from openscenario_builder.core.schema.parser import parse_openscenario_schema
from openscenario_builder.core.plugins.plugin_manager import PluginManager
from openscenario_builder.ui.qt.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import logging
import sys
import os
from pathlib import Path


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("openscenario_builder.log"),
        ],
    )


def find_schema_file() -> str:
    """Find the OpenSCENARIO schema file"""
    # Look in various locations
    possible_paths = [
        "schemas/OpenSCENARIO_v1_3.xsd",  # Recommended location
        "src/openscenario_builder/core/schema/OpenSCENARIO_v1_3.xsd",  # Legacy location
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError("Could not find OpenSCENARIO schema file")


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Find and parse schema
        logger.info("Loading OpenSCENARIO schema...")
        schema_path = find_schema_file()
        schema_info = parse_openscenario_schema(schema_path)
        logger.info(f"Loaded schema with {len(schema_info.elements)} elements")

        # Initialize plugin manager
        logger.info("Initializing plugin manager...")
        plugin_manager = PluginManager()

        # Add plugin paths - use absolute paths based on script location
        script_dir = Path(__file__).parent

        plugin_paths = [
            script_dir / "core" / "plugins",  # Built-in plugins
            Path.cwd() / "plugins",  # External plugins directory
        ]

        for path in plugin_paths:
            if path.exists():
                plugin_manager.add_plugin_path(str(path))
                logger.info(f"Added plugin path: {path}")
            else:
                logger.debug(f"Plugin path does not exist: {path}")

        # Load plugins
        loaded_counts = plugin_manager.load_plugins()
        logger.info(f"Loaded plugins: {loaded_counts}")

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("OpenSCENARIO Builder")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("OpenSCENARIO Builder Team")

        # Create and show main window
        window = MainWindow(schema_info, plugin_manager)
        window.show()

        # Run application
        logger.info("Starting OpenSCENARIO Builder...")
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
