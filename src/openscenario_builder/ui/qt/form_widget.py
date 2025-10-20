"""
Element Form Widget for OpenSCENARIO Builder
Provides form interface for editing element properties
"""

from typing import Optional, Dict
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QHBoxLayout,
)
from PySide6.QtCore import Qt

from openscenario_builder.core.model.element import Element


class ElementFormWidget(QWidget):
    """Form widget for editing element properties"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.current_element: Optional[Element] = None
        self.attribute_widgets: Dict[str, QLineEdit] = {}

        self.setup_ui()

    def setup_ui(self):
        """Setup the form widget UI"""
        layout = QVBoxLayout(self)

        # Scroll area for form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Form container
        self.form_container = QWidget()
        self.form_layout = QFormLayout(self.form_container)

        scroll_area.setWidget(self.form_container)
        layout.addWidget(scroll_area)

        # Update button
        self.update_button = QPushButton("Update Attributes")
        self.update_button.clicked.connect(self.on_update_attributes)
        layout.addWidget(self.update_button)

        # Initially hide the update button
        self.update_button.setVisible(False)

    def set_element(self, element: Element):
        """Set the element to edit"""
        print(
            f"FormWidget.set_element called with element: {element.tag if element else 'None'}"
        )
        self.current_element = element
        self.build_form()

    def build_form(self):
        """Build the form for the current element"""
        print(
            f"FormWidget.build_form called for element: {self.current_element.tag if self.current_element else 'None'}"
        )
        # Clear existing form
        self.clear_form()

        if not self.current_element:
            return

        # Get element definition
        definitions = self.controller.get_element_definitions()
        element_def = definitions.get(self.current_element.tag, {})

        # Add element name (read-only)
        name_label = QLabel(self.current_element.tag)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.form_layout.addRow("Element:", name_label)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.form_layout.addRow(separator)

        # Add attribute fields
        attributes = element_def.get("attrs", [])
        for attr_def in attributes:
            if isinstance(attr_def, dict):
                attr_name = attr_def["name"]
                attr_type = attr_def.get("type", "string")
            else:
                attr_name = attr_def
                attr_type = "string"

            # Create label with type info
            label = QLabel(f"{attr_name} ({attr_type})")

            # Create input field
            input_field = QLineEdit()
            current_value = self.current_element.get_attribute(attr_name, "")
            input_field.setText(current_value)

            # Store reference to widget
            self.attribute_widgets[attr_name] = input_field

            # Add to form
            self.form_layout.addRow(label, input_field)

        # Show update button if there are attributes
        self.update_button.setVisible(len(attributes) > 0)

    def clear_form(self):
        """Clear the form"""
        # Remove all rows except the first one (which is the element name)
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)

        self.attribute_widgets.clear()
        self.update_button.setVisible(False)

    def on_update_attributes(self):
        """Handle update button click"""
        if not self.current_element:
            return

        # Collect attribute values
        attributes = {}
        for attr_name, widget in self.attribute_widgets.items():
            value = widget.text().strip()
            if value:
                attributes[attr_name] = value

        # Update element
        self.controller.update_element_attributes(self.current_element, attributes)
