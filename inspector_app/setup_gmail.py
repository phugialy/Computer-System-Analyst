#!/usr/bin/env python3
"""
Gmail Setup Script
Simple script to configure Gmail for the Computer Inspector application.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gmail_config import setup_gmail_interactive, test_gmail_configuration, GmailConfigManager


def main():
    """Main setup function."""
    print("Computer Inspector - Gmail Setup")
    print("=" * 40)
    print()
    
    # Check if already configured
    config_manager = GmailConfigManager()
    if config_manager.is_configured():
        print("✅ Gmail is already configured!")
        credentials = config_manager.get_credentials()
        print(f"Email: {credentials.email}")
        
        response = input("Would you like to test the configuration? (y/n): ").strip().lower()
        if response == 'y':
            if test_gmail_configuration():
                print("✅ Gmail configuration test successful!")
            else:
                print("❌ Gmail test failed. You may need to update your credentials.")
        
        response = input("Would you like to reconfigure Gmail? (y/n): ").strip().lower()
        if response == 'y':
            config_manager.clear_credentials()
            print("Configuration cleared. Setting up new configuration...")
        else:
            print("Keeping existing configuration.")
            return
    else:
        print("Gmail is not configured. Let's set it up!")
    
    # Setup Gmail
    print("\nSetting up Gmail configuration...")
    if setup_gmail_interactive():
        print("\n✅ Gmail configured successfully!")
        
        # Test the configuration
        print("\nTesting configuration...")
        if test_gmail_configuration():
            print("✅ Gmail configuration test successful!")
            print("\n🎉 Gmail is ready to use with Computer Inspector!")
        else:
            print("❌ Gmail test failed. Please check your credentials and try again.")
    else:
        print("❌ Gmail setup failed. Please try again.")
    
    print("\nSetup complete!")


if __name__ == "__main__":
    main() 