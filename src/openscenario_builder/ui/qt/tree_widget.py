"""
Scenario Tree Widget for OpenSCENARIO Builder
Displays the scenario hierarchy in a tree view
"""

from typing import Optional
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from openscenario_builder.core.model.element import Element


class ScenarioTreeWidget(QTreeWidget):
    """Tree widget for displaying scenario hierarchy"""

    element_selected = Signal(Element)
    element_deleted = Signal(Element)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the tree widget UI"""
        self.setHeaderLabels(["Element", "Attributes"])
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setAlternatingRowColors(True)
        self.setExpandsOnDoubleClick(True)

    def setup_connections(self):
        """Setup signal connections"""
        self.itemClicked.connect(self.on_item_clicked)
        self.customContextMenuRequested.connect(self.on_context_menu)

    def refresh(self):
        """Refresh the tree display"""
        self.clear()
        if self.controller.root_element:
            self.populate_tree(self.controller.root_element, None)
        self.expandAll()

    def populate_tree(self, element: Element, parent_item: Optional[QTreeWidgetItem]):
        """Populate the tree with element hierarchy"""
        # Create item text
        attrs_text = " ".join([f'{k}="{v}"' for k, v in element.attrs.items()])
        item_text = f"{element.tag}"

        # Create tree item
        if parent_item:
            item = QTreeWidgetItem(parent_item)
        else:
            item = QTreeWidgetItem(self)

        item.setText(0, item_text)
        item.setText(1, attrs_text)
        item.setData(0, Qt.ItemDataRole.UserRole, element)

        # Add children recursively
        for child in element.children:
            self.populate_tree(child, item)

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        element = item.data(0, Qt.ItemDataRole.UserRole)
        if element:
            print(
                f"TreeWidget: Item clicked, emitting element_selected for: {element.tag}")
            self.element_selected.emit(element)

    def on_context_menu(self, position):
        """Handle context menu request"""
        item = self.itemAt(position)
        if not item:
            return

        element = item.data(0, Qt.ItemDataRole.UserRole)
        if not element:
            return

        menu = QMenu(self)

        # Add child element actions
        add_menu = menu.addMenu("Add Child")
        definitions = self.controller.get_element_definitions()
        element_def = definitions.get(element.tag, {})

        # Get schema info for groups
        schema_info = self.controller.get_schema_info()
        groups = schema_info.groups if schema_info else {}

        for child_name in element_def.get("children", []):
            if child_name.startswith("GROUP:"):
                # This is a group reference, create a submenu
                group_name = child_name[6:]  # Remove "GROUP:" prefix
                if group_name in groups:
                    group = groups[group_name]
                    group_menu = add_menu.addMenu(f"📁 {group_name}")
                    self._add_group_children(
                        group_menu, group, groups, element)
                else:
                    # Group not found, add as regular item
                    action = QAction(f"❓ {group_name} (not found)", self)
                    action.setEnabled(False)
                    group_menu.addAction(action)
            else:
                # Regular element
                action = QAction(child_name, self)
                action.triggered.connect(
                    lambda checked, name=child_name: self.add_child_element(element, name))
                add_menu.addAction(action)

        menu.addSeparator()

        # Delete action
        if element != self.controller.root_element:
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(
                lambda: self.delete_element(element))
            menu.addAction(delete_action)

        menu.exec(self.viewport().mapToGlobal(position))

    def _add_group_children(self, parent_menu: QMenu, group, groups: dict, parent_element: Element):
        """Recursively add group children to menu"""
        for child_name in group.children:
            if child_name.startswith("GROUP:"):
                # Nested group reference
                nested_group_name = child_name[6:]
                if nested_group_name in groups:
                    nested_group = groups[nested_group_name]
                    nested_menu = parent_menu.addMenu(f"📁 {nested_group_name}")
                    self._add_group_children(
                        nested_menu, nested_group, groups, parent_element)
                else:
                    # Group not found
                    action = QAction(
                        f"❓ {nested_group_name} (not found)", self)
                    action.setEnabled(False)
                    parent_menu.addAction(action)
            else:
                # Regular element
                action = QAction(child_name, self)
                action.triggered.connect(
                    lambda checked, name=child_name: self.add_child_element(parent_element, name))
                parent_menu.addAction(action)

    def add_child_element(self, parent_element: Element, child_name: str):
        """Add a child element"""
        new_element = self.controller.add_element(child_name, parent_element)
        if new_element:
            self.refresh()

    def delete_element(self, element: Element):
        """Delete an element"""
        if self.controller.remove_element(element):
            self.refresh()
