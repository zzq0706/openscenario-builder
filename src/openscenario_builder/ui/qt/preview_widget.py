"""
XML Preview Widget for OpenSCENARIO Builder
Displays the generated XML with syntax highlighting
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat, QSyntaxHighlighter, QColor


class XMLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for XML"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setup_formats()

    def setup_formats(self):
        """Setup highlighting formats"""
        # Tag format
        self.tag_format = QTextCharFormat()
        self.tag_format.setForeground(QColor("#0000FF"))
        self.tag_format.setFontWeight(QFont.Weight.Bold)

        # Attribute format
        self.attr_format = QTextCharFormat()
        self.attr_format.setForeground(QColor("#FF0000"))

        # Value format
        self.value_format = QTextCharFormat()
        self.value_format.setForeground(QColor("#008000"))

    def highlightBlock(self, text):
        """Highlight a block of text"""
        import re

        # Highlight tags
        tag_pattern = r'<[^>]+>'
        for match in re.finditer(tag_pattern, text):
            start = match.start()
            end = match.end()
            self.setFormat(start, end - start, self.tag_format)

        # Highlight attributes
        attr_pattern = r'\s+(\w+)="([^"]*)"'
        for match in re.finditer(attr_pattern, text):
            attr_start = match.start(1)
            attr_end = match.end(1)
            value_start = match.start(2)
            value_end = match.end(2)

            self.setFormat(attr_start, attr_end - attr_start, self.attr_format)
            self.setFormat(value_start, value_end -
                           value_start, self.value_format)


class XMLPreviewWidget(QWidget):
    """Widget for previewing XML output"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        """Setup the preview widget UI"""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)
        toolbar_layout.addWidget(self.refresh_button)

        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        toolbar_layout.addWidget(self.copy_button)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier", 10))

        # Setup syntax highlighting
        self.highlighter = XMLHighlighter(self.text_edit.document())

        layout.addWidget(self.text_edit)

    def refresh(self):
        """Refresh the XML preview"""
        if self.controller.root_element:
            xml_content = self.controller.root_element.to_xml_string(
                pretty=True)
            self.text_edit.setPlainText(xml_content)
        else:
            self.text_edit.setPlainText("No scenario loaded.")

    def copy_to_clipboard(self):
        """Copy XML content to clipboard"""
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            # Copy selected text
            self.text_edit.copy()
        else:
            # Copy all text
            self.text_edit.selectAll()
            self.text_edit.copy()
            # Deselect
            cursor.clearSelection()
            self.text_edit.setTextCursor(cursor)
