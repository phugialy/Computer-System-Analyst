#!/usr/bin/env python3
"""
Test script for CustomTestResultComboBox functionality.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

# Import the custom combo box
from ui.main_window import CustomTestResultComboBox


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Combo Box Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add label
        label = QLabel("Test the custom combo box:")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Create custom combo box
        self.custom_combo = CustomTestResultComboBox()
        self.custom_combo.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.custom_combo)
        
        # Add result label
        self.result_label = QLabel("Selected value: Not Tested")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_label)
        
    def _on_value_changed(self, value):
        """Handle value changes from the custom combo box."""
        self.result_label.setText(f"Selected value: {value}")


def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 