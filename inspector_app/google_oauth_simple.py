#!/usr/bin/env python3
"""
Simplified Google OAuth Authentication Module
Provides a simulated Google OAuth sign-in functionality for testing.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QPushButton, QVBoxLayout, QHBoxLayout, QLabel, 
    QDialog, QMessageBox, QProgressBar, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont


@dataclass
class GoogleUser:
    """Google user information."""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    access_token: Optional[str] = None


class GoogleSignInButton(QPushButton):
    """Google Sign-in button with simulated OAuth functionality."""
    
    authentication_completed = pyqtSignal(object)  # Emits GoogleUser object
    authentication_failed = pyqtSignal(str)  # Emits error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the Google Sign-in button UI."""
        # Create layout for button content
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # Google logo (you can replace this with an actual Google logo image)
        logo_label = QLabel("G")
        logo_label.setStyleSheet("""
            QLabel {
                background-color: white;
                color: #4285f4;
                font-weight: bold;
                font-size: 16px;
                border-radius: 4px;
                padding: 4px;
                min-width: 20px;
                min-height: 20px;
                text-align: center;
            }
        """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Button text
        text_label = QLabel("Sign in with Google")
        text_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(logo_label)
        layout.addWidget(text_label)
        layout.addStretch()
        
        # Style the button
        self.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
            QPushButton:pressed {
                background-color: #2a56c6;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
            }
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setup_connections(self):
        """Setup button click connection."""
        self.clicked.connect(self.start_authentication)
    
    def start_authentication(self):
        """Start the simulated Google OAuth authentication process."""
        try:
            # Disable button during authentication
            self.setEnabled(False)
            self.setText("Signing in...")
            
            # Show account selection dialog
            dialog = GoogleAccountSelectionDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted and hasattr(dialog, 'selected_user'):
                self._on_auth_completed(dialog.selected_user)
            else:
                self._on_auth_failed("Authentication cancelled")
                
        except Exception as e:
            self._on_auth_failed(f"Authentication error: {str(e)}")
    
    def _on_auth_completed(self, user: GoogleUser):
        """Handle successful authentication."""
        self.setEnabled(True)
        self.setText("Sign in with Google")
        self.authentication_completed.emit(user)
    
    def _on_auth_failed(self, error: str):
        """Handle authentication failure."""
        self.setEnabled(True)
        self.setText("Sign in with Google")
        self.authentication_failed.emit(error)


class GoogleAccountSelectionDialog(QDialog):
    """Dialog for Google account selection (simulated)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign in with Google")
        self.setModal(True)
        self.resize(400, 500)
        self.selected_user = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Sign in with Google")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Choose an account to continue to Computer Inspector")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #666;")
        layout.addWidget(desc_label)
        
        # App icon
        app_icon = QLabel("🔍")
        app_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_icon.setStyleSheet("""
            QLabel {
                font-size: 48px;
                padding: 20px;
            }
        """)
        layout.addWidget(app_icon)
        
        # Account list
        self.create_account_list(layout)
        
        # Add spacing
        layout.addStretch()
        
        # Footer
        footer_label = QLabel("By signing in, you agree to our Terms of Service and Privacy Policy")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #999; font-size: 12px;")
        layout.addWidget(footer_label)
    
    def create_account_list(self, parent_layout):
        """Create the account selection list."""
        # Sample Google accounts (you can modify these)
        accounts = [
            {"name": "Pilo Kami_Team", "email": "bigpstudio@gmail.com", "icon": "P"},
            {"name": "Phu Ly", "email": "phu.lyg@gmail.com", "icon": "P"},
            {"name": "Pilo", "email": "phug.ly96@gmail.com", "icon": "P"},
            {"name": "minh ly", "email": "minhly2507@gmail.com", "icon": "M"},
            {"name": "Jony", "email": "jonybounce@gmail.com", "icon": "J"},
            {"name": "Blue Friends Paw", "email": "bluefriendspaw@gmail.com", "icon": "B"},
            {"name": "phu ly", "email": "phuly.dncl@gmail.com", "icon": "P"},
        ]
        
        for account in accounts:
            account_widget = self.create_account_widget(account)
            parent_layout.addWidget(account_widget)
        
        # Add another account option
        add_account_widget = self.create_add_account_widget()
        parent_layout.addWidget(add_account_widget)
    
    def create_account_widget(self, account):
        """Create an account selection widget."""
        widget = QPushButton()
        widget.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #4285f4;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Account icon
        icon_label = QLabel(account["icon"])
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: #{hash(account["email"]) % 0xFFFFFF:06x};
                color: white;
                font-weight: bold;
                border-radius: 20px;
                padding: 8px;
                min-width: 40px;
                min-height: 40px;
                text-align: center;
            }}
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Account info
        info_layout = QVBoxLayout()
        name_label = QLabel(account["name"])
        name_label.setStyleSheet("font-weight: bold; color: #333;")
        email_label = QLabel(account["email"])
        email_label.setStyleSheet("color: #666; font-size: 12px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(email_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Connect click event
        widget.clicked.connect(lambda: self.select_account(account))
        
        return widget
    
    def create_add_account_widget(self):
        """Create the 'Add another account' widget."""
        widget = QPushButton()
        widget.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #4285f4;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Generic person icon
        icon_label = QLabel("👤")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                padding: 8px;
                min-width: 40px;
                min-height: 40px;
                text-align: center;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Text
        text_label = QLabel("Use another account")
        text_label.setStyleSheet("color: #4285f4; font-weight: bold;")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        
        # Connect click event
        widget.clicked.connect(self.add_another_account)
        
        return widget
    
    def select_account(self, account):
        """Handle account selection."""
        # Create GoogleUser object
        user = GoogleUser(
            id=str(hash(account["email"])),
            email=account["email"],
            name=account["name"],
            picture=None,
            access_token="simulated_access_token"
        )
        
        self.selected_user = user
        self.accept()
    
    def add_another_account(self):
        """Handle adding another account."""
        QMessageBox.information(
            self,
            "Add Another Account",
            "This would open Google's account addition page in a browser.\n\n"
            "For this demo, you can select one of the existing accounts above."
        )


def test_simple_google_oauth():
    """Test the simplified Google OAuth functionality."""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create test window
    from test_google_oauth import TestWindow
    window = TestWindow()
    window.show()
    
    print("Simplified Google OAuth Test")
    print("=" * 40)
    print("1. Click 'Sign in with Google' button")
    print("2. Choose from the simulated Google accounts")
    print("3. See the authentication result")
    print()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_simple_google_oauth() 