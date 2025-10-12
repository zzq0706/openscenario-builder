"""
Qt-based Main Window for OpenSCENARIO Builder
Decoupled from core business logic
"""

import sys
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QFormLayout, QLineEdit, QPushButton,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QFileDialog, QMenu,
    QSplitter, QTabWidget, QMessageBox, QStatusBar, QToolBar,
    QDockWidget, QListWidget, QListWidgetItem
)
from PySide6.QtGui import QAction, QIcon, QFont
from PySide6.QtCore import Qt, Signal, QObject, QThread

from openscenario_builder.core.model.element import Element
from openscenario_builder.core.schema.parser import SchemaInfo
from openscenario_builder.core.plugins.plugin_manager import PluginManager
from .tree_widget import ScenarioTreeWidget
from .form_widget import ElementFormWidget
from .preview_widget import XMLPreviewWidget


class ScenarioController(QObject):
    """Controller that manages scenario state and operations"""

    scenario_changed = Signal()
    element_selected = Signal(Element)
    validation_errors = Signal(list)

    def __init__(self, schema_info: SchemaInfo, plugin_manager: PluginManager):
        super().__init__()
        self.schema_info = schema_info
        self.plugin_manager = plugin_manager
        self.root_element: Optional[Element] = None
        self.selected_element: Optional[Element] = None

    def create_new_scenario(self) -> None:
        """Create a new empty scenario"""
        self.root_element = Element("OpenSCENARIO")
        self.selected_element = None
        self.scenario_changed.emit()

    def load_scenario(self, file_path: str) -> bool:
        """Load scenario from file"""
        try:
            # Use plugin manager to import
            scenario = self.plugin_manager.import_scenario(file_path)
            if scenario:
                self.root_element = scenario
                self.selected_element = None
                self.scenario_changed.emit()
                return True
            return False
        except Exception as e:
            print(f"Failed to load scenario: {e}")
            return False

    def save_scenario(self, file_path: str) -> bool:
        """Save scenario to file"""
        if not self.root_element:
            return False

        try:
            return self.plugin_manager.export_scenario(self.root_element, file_path)
        except Exception as e:
            print(f"Failed to save scenario: {e}")
            return False

    def add_element(self, element_name: str, parent_element: Optional[Element] = None) -> Optional[Element]:
        """Add a new element to the scenario"""
        if not self.root_element:
            return None

        # Get element definition
        element_def = self.schema_info.elements.get(element_name)
        if not element_def:
            return None

        # Create new element
        new_element = Element(element_name)

        # Set default attributes
        for attr_def in element_def.attributes:
            if attr_def.get("required", False):
                new_element.set_attribute(attr_def["name"], "")

        # Add to parent
        target_parent = parent_element or self.root_element
        target_parent.add_child(new_element)

        self.scenario_changed.emit()
        return new_element

    def remove_element(self, element: Element) -> bool:
        """Remove an element from the scenario"""
        if not self.root_element or element == self.root_element:
            return False

        # Find parent and remove
        parent = self._find_parent(element)
        if parent:
            parent.remove_child(element)
            if self.selected_element == element:
                self.selected_element = None
            self.scenario_changed.emit()
            return True
        return False

    def select_element(self, element: Element) -> None:
        """Select an element"""
        print(
            f"Controller.select_element called with: {element.tag if element else 'None'}")
        self.selected_element = element
        self.element_selected.emit(element)

    def update_element_attributes(self, element: Element, attributes: Dict[str, str]) -> None:
        """Update element attributes"""
        for name, value in attributes.items():
            if value:
                element.set_attribute(name, value)
            else:
                element.remove_attribute(name)

        self.scenario_changed.emit()

    def validate_scenario(self) -> list:
        """Validate the current scenario"""
        if not self.root_element:
            return []

        errors = []

        plugin_errors = self.plugin_manager.validate_scenario(
            self.root_element, self.schema_info)
        errors.extend(plugin_errors)

        self.validation_errors.emit(errors)
        return errors

    def _find_parent(self, element: Element) -> Optional[Element]:
        """Find the parent of an element"""
        if not self.root_element:
            return None

        def find_in_subtree(parent: Element, target: Element) -> Optional[Element]:
            for child in parent.children:
                if child == target:
                    return parent
                result = find_in_subtree(child, target)
                if result:
                    return result
            return None

        return find_in_subtree(self.root_element, element)

    def get_element_definitions(self) -> Dict[str, Any]:
        """Get all element definitions"""
        # Combine schema definitions with plugin definitions
        definitions = {}

        # Add schema definitions
        for element_name, element_def in self.schema_info.elements.items():
            definitions[element_name] = {
                "attrs": element_def.attributes,
                "children": element_def.children,
                "description": element_def.description,
                "category": "Schema"
            }

        # Add plugin definitions
        plugin_definitions = self.plugin_manager.get_element_definitions()
        definitions.update(plugin_definitions)

        return definitions

    def get_schema_info(self) -> SchemaInfo:
        """Get the schema information"""
        return self.schema_info


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, schema_info: SchemaInfo, plugin_manager: PluginManager):
        super().__init__()
        self.schema_info = schema_info
        self.plugin_manager = plugin_manager

        # Initialize controller
        self.controller = ScenarioController(schema_info, plugin_manager)

        # Setup UI
        self.setup_ui()
        self.setup_connections()
        self.setup_menu()
        # self.setup_toolbar()
        self.setup_statusbar()

        # Create new scenario
        self.controller.create_new_scenario()

    def setup_ui(self):
        """Setup the main UI components"""
        self.setWindowTitle("OpenSCENARIO Builder")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([400, 800])

    def create_left_panel(self) -> QWidget:
        """Create the left panel with tree and form"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Element picker
        # picker_layout = QFormLayout()
        # self.element_combo = QComboBox()
        # self.element_combo.addItems(self.get_available_elements())
        # picker_layout.addRow("Element:", self.element_combo)

        # self.add_button = QPushButton("Add Element")
        # picker_layout.addRow(self.add_button)

        # layout.addLayout(picker_layout)

        # Scenario tree
        self.tree_widget = ScenarioTreeWidget(self.controller)
        layout.addWidget(self.tree_widget)

        return panel

    def create_right_panel(self) -> QWidget:
        """Create the right panel with tabs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Element form tab
        self.form_widget = ElementFormWidget(self.controller)
        self.tab_widget.addTab(self.form_widget, "Element Properties")

        # XML preview tab
        self.preview_widget = XMLPreviewWidget(self.controller)
        self.tab_widget.addTab(self.preview_widget, "XML Preview")

        # Validation tab
        self.validation_widget = QTextEdit()
        self.validation_widget.setReadOnly(True)
        self.tab_widget.addTab(self.validation_widget, "Validation")

        return panel

    def setup_connections(self):
        """Setup signal connections"""
        # Controller signals
        self.controller.scenario_changed.connect(self.on_scenario_changed)
        self.controller.element_selected.connect(self.on_element_selected)
        self.controller.validation_errors.connect(self.on_validation_errors)

        # UI signals
        # self.add_button.clicked.connect(self.on_add_element)
        # self.element_combo.currentTextChanged.connect(
        #     self.on_element_type_changed)

        # Tree widget signals
        self.tree_widget.element_selected.connect(
            self.controller.select_element)

    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_scenario)
        file_menu.addAction(new_action)

        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open_scenario)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save_scenario)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.on_save_scenario_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Tools")

        validate_action = QAction("&Validate", self)
        validate_action.setShortcut("Ctrl+V")
        validate_action.triggered.connect(self.on_validate_scenario)
        edit_menu.addAction(validate_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add toolbar actions
        toolbar.addAction("New")
        toolbar.addAction("Open")
        toolbar.addAction("Save")
        toolbar.addSeparator()
        toolbar.addAction("Validate")

    def setup_statusbar(self):
        """Setup the status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    def get_available_elements(self) -> list:
        """Get list of available element types"""
        definitions = self.controller.get_element_definitions()
        return sorted(definitions.keys())

    def on_scenario_changed(self):
        """Handle scenario changes"""
        self.tree_widget.refresh()
        self.preview_widget.refresh()
        self.statusbar.showMessage("Scenario updated")

    def on_element_selected(self, element: Element):
        """Handle element selection"""
        print(
            f"MainWindow.on_element_selected called with: {element.tag if element else 'None'}")
        self.form_widget.set_element(element)

    def on_validation_errors(self, errors: list):
        """Handle validation errors"""
        if errors:
            self.validation_widget.setPlainText("\n".join(errors))
            self.tab_widget.setCurrentWidget(self.validation_widget)
        else:
            self.validation_widget.setPlainText("No validation errors found.")

    def on_add_element(self):
        """Add a new element"""
        element_name = self.element_combo.currentText()
        if element_name:
            new_element = self.controller.add_element(element_name)
            if new_element:
                self.statusbar.showMessage(f"Added {element_name}")

    def on_element_type_changed(self, element_type: str):
        """Handle element type change"""
        # Could update form with default values for the selected type
        pass

    def on_new_scenario(self):
        """Create new scenario"""
        if self.prompt_save():
            self.controller.create_new_scenario()
            self.statusbar.showMessage("New scenario created")

    def prompt_save(self) -> bool:
        """
        Prompt user to save current scenario if it's modified.
        Returns True if user wants to proceed, False if user cancels.
        """
        # Check if there's a current scenario and if it's modified
        if not self.controller.root_element:
            return True

        reply = QMessageBox.question(
            self,
            "",
            "The current working scenario will be lost if not saved. Do you want to save before proceeding?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.on_save_scenario()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def on_open_scenario(self):
        """Open scenario file"""
        if self.prompt_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Scenario", "",
                "OpenSCENARIO Files (*.xosc);;XML Files (*.xml);;All Files (*)"
            )
            if file_path:
                if self.controller.load_scenario(file_path):
                    self.statusbar.showMessage(f"Opened {file_path}")
                else:
                    QMessageBox.critical(
                        self, "Error", "Failed to open scenario file")

    def on_save_scenario(self) -> bool:
        """Save scenario"""
        # For now, always show save dialog
        return self.on_save_scenario_as()

    def on_save_scenario_as(self) -> bool:
        """Save scenario as"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Scenario", "",
            "OpenSCENARIO Files (*.xosc);;XML Files (*.xml)"
        )
        if file_path:
            if self.controller.save_scenario(file_path):
                self.statusbar.showMessage(f"Saved to {file_path}")
                return True
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to save scenario file")
                return False
        return False

    def on_validate_scenario(self):
        """Validate scenario"""
        errors = self.controller.validate_scenario()
        if errors:
            self.statusbar.showMessage(
                f"Validation found {len(errors)} errors")
        else:
            self.statusbar.showMessage("Validation passed")

    def on_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About OpenSCENARIO Builder",
            "OpenSCENARIO Builder\n\n"
            "A professional tool for creating and editing OpenSCENARIO files.\n\n"
            "Version: 1.0.0\n"
            "Built with extensible plugin architecture."
        )

    def closeEvent(self, event):
        """Handle application close event"""
        if self.prompt_save():
            event.accept()
        else:
            event.ignore()
