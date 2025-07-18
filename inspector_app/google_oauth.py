#!/usr/bin/env python3
"""
Google OAuth Authentication Module
Provides Google OAuth sign-in functionality similar to n8n.
"""

import os
import json
import webbrowser
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

from PyQt6.QtWidgets import (
    QPushButton, QVBoxLayout, QHBoxLayout, QLabel, 
    QDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon


@dataclass
class GoogleUser:
    """Google user information."""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    access_token: Optional[str] = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP server to handle OAuth callback."""
    
    def __init__(self, *args, auth_code_callback: Callable[[str], None], **kwargs):
        self.auth_code_callback = auth_code_callback
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET request for OAuth callback."""
        try:
            # Parse the authorization code from the callback URL
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                auth_code = query_params['code'][0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                success_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Successful</title>
                    <style>
                        body { 
                            font-family: Arial, sans-serif; 
                            text-align: center; 
                            padding: 50px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }
                        .container {
                            background: rgba(255,255,255,0.1);
                            padding: 30px;
                            border-radius: 10px;
                            backdrop-filter: blur(10px);
                        }
                        .success-icon {
                            font-size: 48px;
                            margin-bottom: 20px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success-icon">✅</div>
                        <h2>Authentication Successful!</h2>
                        <p>You have successfully signed in with Google.</p>
                        <p>You can close this window now.</p>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(success_html.encode())
                
                # Call the callback with the auth code
                self.auth_code_callback(auth_code)
            else:
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Error</title>
                    <style>
                        body { 
                            font-family: Arial, sans-serif; 
                            text-align: center; 
                            padding: 50px;
                            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                            color: white;
                        }
                        .container {
                            background: rgba(255,255,255,0.1);
                            padding: 30px;
                            border-radius: 10px;
                            backdrop-filter: blur(10px);
                        }
                        .error-icon {
                            font-size: 48px;
                            margin-bottom: 20px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error-icon">❌</div>
                        <h2>Authentication Error</h2>
                        <p>There was an error during authentication.</p>
                        <p>Please try again.</p>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(error_html.encode())
                
        except Exception as e:
            print(f"Error handling OAuth callback: {str(e)}")
            self.send_response(500)
            self.end_headers()


class GoogleOAuth:
    """Google OAuth authentication handler."""
    
    def __init__(self):
        # Google OAuth 2.0 configuration
        self.client_id = "YOUR_GOOGLE_CLIENT_ID"  # Replace with your Google Client ID
        self.client_secret = "YOUR_GOOGLE_CLIENT_SECRET"  # Replace with your Google Client Secret
        self.redirect_uri = "http://localhost:8080/callback"
        self.scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
        
        # OAuth endpoints
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        self.server = None
        self.auth_code = None
    
    def get_auth_url(self) -> str:
        """Generate Google OAuth authorization URL."""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def start_auth_server(self, callback: Callable[[str], None]):
        """Start local server to handle OAuth callback."""
        def handler(*args, **kwargs):
            return OAuthCallbackHandler(*args, auth_code_callback=callback, **kwargs)
        
        self.server = HTTPServer(('localhost', 8080), handler)
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
    
    def stop_auth_server(self):
        """Stop the local auth server."""
        if self.server:
            self.server.shutdown()
            self.server = None
    
    def exchange_code_for_token(self, auth_code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token."""
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': auth_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error exchanging code for token: {str(e)}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information using access token."""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            return None
    
    def authenticate(self) -> Optional[GoogleUser]:
        """Complete OAuth authentication flow."""
        try:
            # Start local server
            self.start_auth_server(self._handle_auth_code)
            
            # Open browser for authentication
            auth_url = self.get_auth_url()
            webbrowser.open(auth_url)
            
            # Wait for authorization code
            timeout = 60  # 60 seconds timeout
            start_time = time.time()
            
            while not self.auth_code and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.auth_code:
                print("Authentication timeout")
                return None
            
            # Exchange code for token
            token_data = self.exchange_code_for_token(self.auth_code)
            if not token_data:
                return None
            
            access_token = token_data.get('access_token')
            if not access_token:
                return None
            
            # Get user information
            user_info = self.get_user_info(access_token)
            if not user_info:
                return None
            
            # Create GoogleUser object
            user = GoogleUser(
                id=user_info.get('id'),
                email=user_info.get('email'),
                name=user_info.get('name'),
                picture=user_info.get('picture'),
                access_token=access_token
            )
            
            return user
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None
        finally:
            self.stop_auth_server()
    
    def _handle_auth_code(self, auth_code: str):
        """Handle the authorization code from OAuth callback."""
        self.auth_code = auth_code


class GoogleSignInButton(QPushButton):
    """Google Sign-in button with OAuth functionality."""
    
    authentication_completed = pyqtSignal(object)  # Emits GoogleUser object
    authentication_failed = pyqtSignal(str)  # Emits error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.oauth = GoogleOAuth()
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
        """Start the Google OAuth authentication process."""
        try:
            # Disable button during authentication
            self.setEnabled(False)
            self.setText("Signing in...")
            
            # Start authentication in background thread
            self.auth_thread = GoogleAuthThread(self.oauth)
            self.auth_thread.authentication_completed.connect(self._on_auth_completed)
            self.auth_thread.authentication_failed.connect(self._on_auth_failed)
            self.auth_thread.start()
            
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


class GoogleAuthThread(QThread):
    """Background thread for Google authentication."""
    
    authentication_completed = pyqtSignal(object)  # Emits GoogleUser object
    authentication_failed = pyqtSignal(str)  # Emits error message
    
    def __init__(self, oauth: GoogleOAuth):
        super().__init__()
        self.oauth = oauth
    
    def run(self):
        """Run the authentication process."""
        try:
            user = self.oauth.authenticate()
            if user:
                self.authentication_completed.emit(user)
            else:
                self.authentication_failed.emit("Authentication failed")
        except Exception as e:
            self.authentication_failed.emit(f"Authentication error: {str(e)}")


class GoogleAccountDialog(QDialog):
    """Dialog for Google account selection and authentication."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign in with Google")
        self.setModal(True)
        self.resize(400, 300)
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
        
        # Google Sign-in button
        self.google_btn = GoogleSignInButton()
        self.google_btn.authentication_completed.connect(self._on_auth_completed)
        self.google_btn.authentication_failed.connect(self._on_auth_failed)
        layout.addWidget(self.google_btn)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)
        
        # Add some spacing
        layout.addStretch()
        
        # Footer
        footer_label = QLabel("By signing in, you agree to our Terms of Service and Privacy Policy")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #999; font-size: 12px;")
        layout.addWidget(footer_label)
    
    def _on_auth_completed(self, user: GoogleUser):
        """Handle successful authentication."""
        self.status_label.setText(f"Signed in as {user.email}")
        self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        
        # Store user information
        self.user = user
        
        # Close dialog after a short delay
        QTimer.singleShot(1000, self.accept)
    
    def _on_auth_failed(self, error: str):
        """Handle authentication failure."""
        self.status_label.setText(f"Authentication failed: {error}")
        self.status_label.setStyleSheet("color: #f44336;")
        
        # Re-enable button
        self.google_btn.setEnabled(True)
        self.google_btn.setText("Sign in with Google")


def test_google_oauth():
    """Test the Google OAuth functionality."""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = GoogleAccountDialog()
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted and hasattr(dialog, 'user'):
        print(f"Successfully authenticated as: {dialog.user.email}")
        print(f"User ID: {dialog.user.id}")
        print(f"Name: {dialog.user.name}")
    else:
        print("Authentication cancelled or failed")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_google_oauth() 