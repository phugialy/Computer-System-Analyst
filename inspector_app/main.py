#!/usr/bin/env python3
"""
Inspector Diagnostic Utility - Main Entry Point
A comprehensive system inspection and diagnostic tool.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create the Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Inspector Diagnostic Utility")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DNCL")
    
    # Set application-wide stylesheet for consistent theming
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
        }
        QLineEdit, QTextEdit, QPlainTextEdit {
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            padding: 4px;
            background-color: white;
        }
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border: 2px solid #2196F3;
        }
        QLabel {
            color: #424242;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;
        }
    """)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 