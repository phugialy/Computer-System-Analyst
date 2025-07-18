#!/usr/bin/env python3
"""
Test Google OAuth Integration
Tests the Google OAuth authentication functionality.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from google_oauth import GoogleAccountDialog, GoogleSignInButton
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt


class TestWindow(QMainWindow):
    """Test window for Google OAuth functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google OAuth Test")
        self.setGeometry(100, 100, 500, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Google OAuth Test")
        title_label.setFont(QLabel().font())
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Test the Google OAuth authentication functionality")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Google Sign-in button
        self.google_btn = GoogleSignInButton()
        self.google_btn.authentication_completed.connect(self._on_auth_completed)
        self.google_btn.authentication_failed.connect(self._on_auth_failed)
        layout.addWidget(self.google_btn)
        
        # Status label
        self.status_label = QLabel("Click 'Sign in with Google' to test authentication")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)
        
        # Add spacing
        layout.addStretch()
    
    def _on_auth_completed(self, user):
        """Handle successful authentication."""
        self.status_label.setText(f"✅ Successfully authenticated as: {user.email}")
        self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        
        print(f"Authentication successful!")
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Name: {user.name}")
        print(f"Picture: {user.picture}")
    
    def _on_auth_failed(self, error):
        """Handle authentication failure."""
        self.status_label.setText(f"❌ Authentication failed: {error}")
        self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        
        print(f"Authentication failed: {error}")


def test_google_oauth():
    """Test the Google OAuth functionality."""
    app = QApplication(sys.argv)
    
    # Create test window
    window = TestWindow()
    window.show()
    
    print("Google OAuth Test")
    print("=" * 40)
    print("1. Click 'Sign in with Google' button")
    print("2. Choose your Google account")
    print("3. Grant permissions to the application")
    print("4. Check the authentication result")
    print()
    
    # Start the application
    sys.exit(app.exec())


if __name__ == "__main__":
    test_google_oauth() 