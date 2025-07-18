#!/usr/bin/env python3
"""
Test script for Google Account Switching functionality
Demonstrates the enhanced Google OAuth with account switching capabilities.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from google_oauth_real import GoogleSignInButton, GoogleOAuthConfig


class TestAccountSwitchingWindow(QMainWindow):
    """Test window for Google account switching functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Account Switching Test")
        self.setGeometry(100, 100, 500, 300)
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Google Account Switching Test")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "This test demonstrates the enhanced Google OAuth functionality:\n\n"
            "1. Click 'Sign in with Google' to authenticate\n"
            "2. Once signed in, click the button again to switch accounts\n"
            "3. The button will ask if you want to switch accounts\n"
            "4. Choose 'Yes' to switch or 'No' to cancel\n\n"
            "The button automatically shows your current sign-in status."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(desc)
        
        # Google Sign-in button
        self.google_btn = GoogleSignInButton()
        self.google_btn.authentication_completed.connect(self._on_auth_completed)
        self.google_btn.authentication_failed.connect(self._on_auth_failed)
        layout.addWidget(self.google_btn)
        
        # Status label
        self.status_label = QLabel("Status: Ready to test")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Clear tokens button (for testing)
        clear_btn = QPushButton("🗑️ Clear Stored Tokens (Test)")
        clear_btn.clicked.connect(self._clear_tokens)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(clear_btn)
        
        # Add some spacing
        layout.addStretch()
        
        # Instructions
        instructions = QLabel(
            "💡 Tip: The button automatically detects if you're already signed in\n"
            "and will show your current account status."
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: #27ae60; font-size: 11px; font-style: italic;")
        layout.addWidget(instructions)
    
    def _on_auth_completed(self, user):
        """Handle successful authentication."""
        self.status_label.setText(f"✅ Signed in as: {user.email}")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        QMessageBox.information(
            self,
            "Authentication Successful",
            f"Successfully signed in as {user.email}!\n\n"
            "Now try clicking the Google sign-in button again to test account switching."
        )
    
    def _on_auth_failed(self, error):
        """Handle authentication failure."""
        self.status_label.setText(f"❌ Authentication failed: {error}")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        QMessageBox.critical(
            self,
            "Authentication Failed",
            f"Failed to sign in with Google:\n{error}"
        )
    
    def _clear_tokens(self):
        """Clear stored OAuth tokens for testing."""
        try:
            GoogleOAuthConfig.clear_tokens()
            self.status_label.setText("🗑️ Tokens cleared - ready for fresh sign-in")
            self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
            
            QMessageBox.information(
                self,
                "Tokens Cleared",
                "Stored OAuth tokens have been cleared.\n\n"
                "You can now test a fresh sign-in process."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to clear tokens: {str(e)}"
            )


def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    # Check if client secrets file exists
    client_secrets_path = Path(__file__).parent / 'res' / 'client_secrets.json'
    if not client_secrets_path.exists():
        QMessageBox.critical(
            None,
            "Setup Required",
            f"Google OAuth setup required!\n\n"
            f"Please create the file: {client_secrets_path}\n\n"
            f"1. Go to Google Cloud Console\n"
            f"2. Create OAuth 2.0 credentials\n"
            f"3. Download as client_secrets.json\n"
            f"4. Place in the res/ directory"
        )
        return
    
    # Create and show test window
    window = TestAccountSwitchingWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 