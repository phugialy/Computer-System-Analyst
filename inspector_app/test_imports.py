#!/usr/bin/env python3
"""
Test script to identify import issues.
"""

import sys
import traceback

def test_imports():
    """Test all imports step by step."""
    print("Testing imports...")
    
    # Test basic imports
    try:
        import platform
        import psutil
        import GPUtil
        import screeninfo
        print("✅ Basic system imports successful")
    except Exception as e:
        print(f"❌ Basic system imports failed: {e}")
        return False
    
    # Test PyQt6 imports
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        print("✅ PyQt6 imports successful")
    except Exception as e:
        print(f"❌ PyQt6 imports failed: {e}")
        return False
    
    # Test core module imports
    try:
        from core.system_info import system_collector
        print("✅ System info import successful")
    except Exception as e:
        print(f"❌ System info import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from core.test_launcher import test_launcher
        print("✅ Test launcher import successful")
    except Exception as e:
        print(f"❌ Test launcher import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from core.report_generator import ReportFormatter
        print("✅ Report generator import successful")
    except Exception as e:
        print(f"❌ Report generator import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from core.email_sender import EmailSender, EmailConfig, EmailStatus
        print("✅ Email sender import successful")
    except Exception as e:
        print(f"❌ Email sender import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from core.inspector_input import input_manager, ScanConfiguration, ReportConfiguration
        print("✅ Inspector input import successful")
    except Exception as e:
        print(f"❌ Inspector input import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test Gmail config imports
    try:
        from gmail_config import GmailConfigManager, setup_gmail_interactive, test_gmail_configuration
        print("✅ Gmail config import successful")
    except Exception as e:
        print(f"❌ Gmail config import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test Google OAuth imports
    try:
        from google_oauth_simple import GoogleAccountSelectionDialog, GoogleUser
        print("✅ Google OAuth import successful")
    except Exception as e:
        print(f"❌ Google OAuth import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test UI imports
    try:
        from ui.main_window import MainWindow
        print("✅ Main window import successful")
    except Exception as e:
        print(f"❌ Main window import failed: {e}")
        traceback.print_exc()
        return False
    
    print("✅ All imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 All imports passed! The application should work.")
    else:
        print("\n❌ Some imports failed. Please check the errors above.") 