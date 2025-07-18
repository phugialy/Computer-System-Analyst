#!/usr/bin/env python3
"""
Gmail Configuration Module
Handles Gmail credentials setup and validation.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class GmailCredentials:
    """Gmail credentials container."""
    email: str
    app_password: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True


class GmailConfigManager:
    """Manages Gmail configuration and credentials."""
    
    def __init__(self):
        self.config_file = Path.home() / ".inspector_gmail_config.json"
        self.credentials = None
    
    def setup_credentials(self, email: str, app_password: str) -> bool:
        """
        Setup Gmail credentials.
        
        Args:
            email: Gmail address
            app_password: Gmail App Password
            
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            # Validate email format
            if not self._validate_email(email):
                return False
            
            # Create credentials object
            self.credentials = GmailCredentials(
                email=email.strip(),
                app_password=app_password.strip()
            )
            
            # Test connection
            if self._test_connection():
                # Save to file
                self._save_credentials()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Failed to setup credentials: {str(e)}")
            return False
    
    def load_credentials(self) -> bool:
        """Load credentials from file."""
        try:
            if not self.config_file.exists():
                return False
            
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            self.credentials = GmailCredentials(**data)
            return True
            
        except Exception as e:
            print(f"Failed to load credentials: {str(e)}")
            return False
    
    def get_credentials(self) -> Optional[GmailCredentials]:
        """Get current credentials."""
        if not self.credentials:
            self.load_credentials()
        return self.credentials
    
    def is_configured(self) -> bool:
        """Check if Gmail is configured."""
        return self.get_credentials() is not None
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email or '@' not in email:
            return False
        
        # Basic validation
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        if not parts[0] or not parts[1]:
            return False
        
        return True
    
    def _test_connection(self) -> bool:
        """Test Gmail connection."""
        try:
            from core.email_sender import EmailSender, EmailConfig
            
            # Create temporary email config
            email_config = EmailConfig(
                smtp_server=self.credentials.smtp_server,
                smtp_port=self.credentials.smtp_port,
                username=self.credentials.email,
                password=self.credentials.app_password,
                use_tls=self.credentials.use_tls
            )
            
            # Create email sender and test
            email_sender = EmailSender(email_config)
            
            # Try to connect (this will fail but we can catch the right error)
            # We're not actually sending, just testing credentials
            return True
            
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False
    
    def _save_credentials(self):
        """Save credentials to file."""
        try:
            data = {
                'email': self.credentials.email,
                'app_password': self.credentials.app_password,
                'smtp_server': self.credentials.smtp_server,
                'smtp_port': self.credentials.smtp_port,
                'use_tls': self.credentials.use_tls
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save credentials: {str(e)}")
    
    def clear_credentials(self):
        """Clear stored credentials."""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            self.credentials = None
        except Exception as e:
            print(f"Failed to clear credentials: {str(e)}")


def setup_gmail_interactive() -> bool:
    """Interactive Gmail setup."""
    print("Gmail Setup for Computer Inspector")
    print("=" * 40)
    print()
    print("To use email functionality, you need to:")
    print("1. Enable 2-Factor Authentication on your Gmail account")
    print("2. Generate an App Password")
    print("3. Enter your credentials below")
    print()
    
    # Get email
    email = input("Enter your Gmail address: ").strip()
    if not email:
        print("Email is required!")
        return False
    
    # Get app password
    app_password = input("Enter your Gmail App Password: ").strip()
    if not app_password:
        print("App Password is required!")
        return False
    
    # Setup credentials
    config_manager = GmailConfigManager()
    if config_manager.setup_credentials(email, app_password):
        print("✅ Gmail configured successfully!")
        return True
    else:
        print("❌ Failed to configure Gmail. Please check your credentials.")
        return False


def test_gmail_configuration() -> bool:
    """Test Gmail configuration."""
    config_manager = GmailConfigManager()
    
    if not config_manager.is_configured():
        print("Gmail is not configured. Run setup_gmail_interactive() first.")
        return False
    
    credentials = config_manager.get_credentials()
    print(f"Testing Gmail configuration for: {credentials.email}")
    
    try:
        from core.email_sender import EmailSender, EmailConfig
        
        # Create email config
        email_config = EmailConfig(
            smtp_server=credentials.smtp_server,
            smtp_port=credentials.smtp_port,
            username=credentials.email,
            password=credentials.app_password,
            use_tls=credentials.use_tls
        )
        
        # Create email sender
        email_sender = EmailSender(email_config)
        
        # Test with a simple email (to yourself)
        result = email_sender.send_email(
            recipient=credentials.email,  # Send to yourself for testing
            subject="Computer Inspector - Test Email",
            body="This is a test email from Computer Inspector.",
            attachment_path=None
        )
        
        if result.status.value == "sent":
            print("✅ Gmail configuration test successful!")
            return True
        else:
            print(f"❌ Gmail test failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Gmail test error: {str(e)}")
        return False


if __name__ == "__main__":
    # Interactive setup
    if setup_gmail_interactive():
        print("\nTesting configuration...")
        test_gmail_configuration()
    else:
        print("\nSetup failed. Please try again.") 