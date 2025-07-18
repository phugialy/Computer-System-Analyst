#!/usr/bin/env python3
"""
Real Google OAuth Integration
Provides actual Google OAuth authentication and Gmail API integration.
"""

import os
import json
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import urlencode, parse_qs

from PyQt6.QtWidgets import (
    QPushButton, QVBoxLayout, QHBoxLayout, QLabel, 
    QDialog, QMessageBox, QProgressBar, QLineEdit,
    QApplication, QMainWindow, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QFont, QDesktopServices

# Google OAuth imports
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


@dataclass
class GoogleUser:
    """Google user information from OAuth."""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class GoogleOAuthConfig:
    """Google OAuth configuration."""
    
    # Gmail API scopes
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.send",
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    
    # Token file path
    TOKEN_FILE = Path.home() / ".inspector_google_token.json"
    
    @classmethod
    def clear_tokens(cls):
        """Clear stored OAuth tokens."""
        try:
            if cls.TOKEN_FILE.exists():
                cls.TOKEN_FILE.unlink()
                print(f"Cleared tokens from {cls.TOKEN_FILE}")
        except Exception as e:
            print(f"Error clearing tokens: {e}")


class GoogleOAuthAuthenticator(QThread):
    """Handles Google OAuth authentication flow with local server."""
    
    authentication_completed = pyqtSignal(object)  # Emits GoogleUser object
    authentication_failed = pyqtSignal(str)  # Emits error message
    
    def __init__(self, parent=None, force_new_auth=False):
        super().__init__(parent)
        self.credentials = None
        self.force_new_auth = force_new_auth
        
    def run(self):
        """Run the OAuth authentication flow."""
        try:
            # Load existing credentials if available and not forcing new auth
            if not self.force_new_auth and GoogleOAuthConfig.TOKEN_FILE.exists():
                self.credentials = Credentials.from_authorized_user_file(
                    str(GoogleOAuthConfig.TOKEN_FILE), 
                    GoogleOAuthConfig.SCOPES
                )
            
            # If no valid credentials available, let the user log in
            if not self.credentials or not self.credentials.valid or self.force_new_auth:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token and not self.force_new_auth:
                    self.credentials.refresh(Request())
                else:
                    # Clear old tokens if forcing new auth
                    if self.force_new_auth:
                        GoogleOAuthConfig.clear_tokens()
                    
                    # Create the flow using the client secrets
                    client_secrets_path = Path(__file__).parent / 'res' / 'client_secrets.json'
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(client_secrets_path),  # Look in res directory
                        GoogleOAuthConfig.SCOPES
                    )
                    
                    # This line starts a local server on port 8080 for the redirect
                    self.credentials = flow.run_local_server(port=8080)
                
                # Save the credentials for the next run
                with open(GoogleOAuthConfig.TOKEN_FILE, 'w') as token:
                    token.write(self.credentials.to_json())
            
            # Get user information
            user_info = self._get_user_info()
            
            # Create GoogleUser object
            user = GoogleUser(
                id=user_info.get('id', ''),
                email=user_info.get('email', ''),
                name=user_info.get('name', ''),
                picture=user_info.get('picture'),
                access_token=self.credentials.token,
                refresh_token=self.credentials.refresh_token
            )
            
            self.authentication_completed.emit(user)
            
        except FileNotFoundError:
            self.authentication_failed.emit(
                "client_secrets.json not found in res/ directory. Please create this file with your Google OAuth credentials."
            )
        except Exception as e:
            self.authentication_failed.emit(f"Authentication error: {str(e)}")
    
    def _get_user_info(self) -> Dict[str, Any]:
        """Get user information from Google."""
        try:
            headers = {
                'Authorization': f'Bearer {self.credentials.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'email': 'unknown@gmail.com', 'name': 'Unknown User'}
                
        except Exception as e:
            print(f"Error getting user info: {e}")
            return {'email': 'unknown@gmail.com', 'name': 'Unknown User'}


class GoogleSignInButton(QPushButton):
    """Google Sign-in button with real OAuth integration and account switching."""
    
    authentication_completed = pyqtSignal(object)  # Emits GoogleUser object
    authentication_failed = pyqtSignal(str)  # Emits error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.authenticator = None
        self.current_user = None
        self.setup_ui()
        self.setup_connections()
        self._check_existing_auth()
    
    def setup_ui(self):
        """Setup the Google Sign-in button UI."""
        # Create layout for button content
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # Google logo
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
        
        # Button text (will be updated based on auth state)
        self.text_label = QLabel("Sign in with Google")
        self.text_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(logo_label)
        layout.addWidget(self.text_label)
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
    
    def _check_existing_auth(self):
        """Check if user is already authenticated and update UI."""
        try:
            if GoogleOAuthConfig.TOKEN_FILE.exists():
                # Try to load existing credentials
                credentials = Credentials.from_authorized_user_file(
                    str(GoogleOAuthConfig.TOKEN_FILE), 
                    GoogleOAuthConfig.SCOPES
                )
                
                if credentials and credentials.valid:
                    # Get user info
                    headers = {
                        'Authorization': f'Bearer {credentials.token}',
                        'Content-Type': 'application/json'
                    }
                    
                    response = requests.get(
                        'https://www.googleapis.com/oauth2/v2/userinfo',
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        user_info = response.json()
                        self.current_user = GoogleUser(
                            id=user_info.get('id', ''),
                            email=user_info.get('email', ''),
                            name=user_info.get('name', ''),
                            picture=user_info.get('picture'),
                            access_token=credentials.token,
                            refresh_token=credentials.refresh_token
                        )
                        self._update_ui_for_signed_in()
                        return
                        
        except Exception as e:
            print(f"Error checking existing auth: {e}")
        
        # If we get here, no valid auth found
        self._update_ui_for_signed_out()
    
    def _update_ui_for_signed_in(self):
        """Update UI to show signed-in state."""
        if self.current_user:
            self.text_label.setText(f"Signed in as {self.current_user.email}")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
                QPushButton:disabled {
                    background-color: #bdbdbd;
                }
            """)
    
    def _update_ui_for_signed_out(self):
        """Update UI to show signed-out state."""
        self.text_label.setText("Sign in with Google")
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
    
    def start_authentication(self):
        """Start the Google OAuth authentication process."""
        try:
            # If already signed in, ask if user wants to switch accounts
            if self.current_user:
                reply = QMessageBox.question(
                    self,
                    "Switch Google Account",
                    f"You are currently signed in as {self.current_user.email}.\n\n"
                    "Would you like to sign in with a different account?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return
                
                # User wants to switch accounts
                self._switch_account()
            else:
                # First time sign in
                self._perform_authentication()
                
        except Exception as e:
            self._on_auth_failed(f"Authentication error: {str(e)}")
    
    def _switch_account(self):
        """Switch to a different Google account."""
        try:
            # Disable button during authentication
            self.setEnabled(False)
            self.text_label.setText("Switching accounts...")
            
            # Start authentication with force_new_auth=True
            self.authenticator = GoogleOAuthAuthenticator(self, force_new_auth=True)
            self.authenticator.authentication_completed.connect(self._on_auth_completed)
            self.authenticator.authentication_failed.connect(self._on_auth_failed)
            self.authenticator.start()
            
        except Exception as e:
            self._on_auth_failed(f"Account switching error: {str(e)}")
    
    def _perform_authentication(self):
        """Perform the authentication flow."""
        try:
            # Disable button during authentication
            self.setEnabled(False)
            self.text_label.setText("Signing in...")
            
            # Start authentication
            self.authenticator = GoogleOAuthAuthenticator(self)
            self.authenticator.authentication_completed.connect(self._on_auth_completed)
            self.authenticator.authentication_failed.connect(self._on_auth_failed)
            self.authenticator.start()
            
        except Exception as e:
            self._on_auth_failed(f"Authentication error: {str(e)}")
    
    def _on_auth_completed(self, user: GoogleUser):
        """Handle successful authentication."""
        self.current_user = user
        self.setEnabled(True)
        self._update_ui_for_signed_in()
        self.authentication_completed.emit(user)
    
    def _on_auth_failed(self, error: str):
        """Handle authentication failure."""
        self.setEnabled(True)
        self._update_ui_for_signed_out()
        self.authentication_failed.emit(error)
    
    def get_current_user(self) -> Optional[GoogleUser]:
        """Get the currently signed-in user."""
        return self.current_user
    
    def sign_out(self):
        """Sign out the current user."""
        try:
            GoogleOAuthConfig.clear_tokens()
            self.current_user = None
            self._update_ui_for_signed_out()
        except Exception as e:
            print(f"Error signing out: {e}")


class GmailSender:
    """Handles sending emails via Gmail API."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.api_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    
    def send_email(self, to: str, subject: str, body: str, attachment_path: str = None) -> Dict[str, Any]:
        """Send email via Gmail API."""
        try:
            # Create email message
            message = self._create_message(to, subject, body, attachment_path)
            
            # Send via Gmail API
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json={'raw': message}
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response.json().get('id'),
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'message_id': None,
                    'error': f"Gmail API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message_id': None,
                'error': f"Email sending error: {str(e)}"
            }
    
    def _create_message(self, to: str, subject: str, body: str, attachment_path: str = None) -> str:
        """Create email message in Gmail API format."""
        import email
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
        
        # Create message
        msg = MIMEMultipart()
        msg['To'] = to
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment_path and Path(attachment_path).exists():
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            filename = Path(attachment_path).name
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
        
        # Encode for Gmail API
        return base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')


def create_client_secrets_template():
    """Create a template for client_secrets.json file."""
    template = {
        "installed": {
            "client_id": "your-client-id.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "your-client-secret",
            "redirect_uris": ["http://localhost:8080"]
        }
    }
    
    # Create res directory if it doesn't exist
    res_dir = Path(__file__).parent / 'res'
    res_dir.mkdir(exist_ok=True)
    
    template_path = res_dir / 'client_secrets_template.json'
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Created {template_path}")
    print("Please:")
    print("1. Copy this file to res/client_secrets.json")
    print("2. Replace the placeholder values with your actual Google OAuth credentials")


def test_real_google_oauth():
    """Test the real Google OAuth functionality."""
    import sys
    
    app = QApplication(sys.argv)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("Real Google OAuth Test")
    window.setGeometry(100, 100, 500, 300)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # Title
    title = QLabel("Real Google OAuth Integration")
    title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # Instructions
    instructions = QLabel(
        "This will open your browser for Google OAuth authentication.\n"
        "A local server will be started on port 8080 to handle the redirect.\n"
        "Make sure you have client_secrets.json file in the res/ directory."
    )
    instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
    instructions.setStyleSheet("color: #666; font-size: 12px;")
    layout.addWidget(instructions)
    
    # Google Sign-in button
    google_btn = GoogleSignInButton()
    layout.addWidget(google_btn)
    
    # Status label
    status_label = QLabel("Ready to authenticate")
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status_label.setStyleSheet("color: #666; font-size: 12px;")
    layout.addWidget(status_label)
    
    # Connect signals
    def on_auth_completed(user: GoogleUser):
        status_label.setText(f"✅ Signed in as {user.email}")
        QMessageBox.information(
            window,
            "Authentication Successful",
            f"Successfully signed in as {user.email}\n\n"
            "You can now send emails using Gmail API!"
        )
    
    def on_auth_failed(error: str):
        status_label.setText(f"❌ Authentication failed")
        QMessageBox.critical(
            window,
            "Authentication Failed",
            f"Failed to sign in with Google:\n{error}"
        )
    
    google_btn.authentication_completed.connect(on_auth_completed)
    google_btn.authentication_failed.connect(on_auth_failed)
    
    window.show()
    
    print("Real Google OAuth Test")
    print("=" * 30)
    print("1. Make sure you have client_secrets.json file in res/ directory")
    print("2. Click 'Sign in with Google'")
    print("3. Complete authentication in browser")
    print("4. Return to application")
    print()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    # Check if client_secrets.json exists in res directory
    client_secrets_path = Path(__file__).parent / 'res' / 'client_secrets.json'
    if not client_secrets_path.exists():
        print("client_secrets.json not found in res/ directory!")
        print("Creating template file...")
        create_client_secrets_template()
        print("\nPlease set up your Google OAuth credentials first.")
    else:
        test_real_google_oauth() 