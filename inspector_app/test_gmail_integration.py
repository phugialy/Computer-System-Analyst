#!/usr/bin/env python3
"""
Test Gmail Integration
Tests the Gmail integration functionality.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gmail_config import GmailConfigManager, setup_gmail_interactive, test_gmail_configuration
from core.report_generator import ReportFormatter
from core.system_info import SystemInfoCollector


def test_gmail_integration():
    """Test the Gmail integration functionality."""
    print("Testing Gmail Integration")
    print("=" * 40)
    
    # Create components
    gmail_config = GmailConfigManager()
    report_formatter = ReportFormatter()
    system_collector = SystemInfoCollector()
    
    # Check if Gmail is configured
    if gmail_config.is_configured():
        print("✅ Gmail is configured!")
        credentials = gmail_config.get_credentials()
        print(f"Email: {credentials.email}")
        
        # Test Gmail configuration
        print("\nTesting Gmail configuration...")
        if test_gmail_configuration():
            print("✅ Gmail configuration test successful!")
        else:
            print("❌ Gmail test failed. You may need to update your credentials.")
    else:
        print("❌ Gmail is not configured.")
        print("\nTo set up Gmail:")
        print("1. Run: python setup_gmail.py")
        print("2. Or run: python gmail_config.py")
        print("3. Follow the prompts to enter your Gmail credentials")
    
    # Test report generation
    print("\nTesting report generation...")
    try:
        # Sample inspector data
        inspector_data = {
            "client_name": "Test Client",
            "order_number": "TEST-001",
            "inspection_date": "2024-01-17",
            "inspector": "Test Inspector",
            "initial_location": "Test Location",
            "sku_number": "SKU-001",
            "charger": "Yes",
            "issues": "No issues found",
            "warranty": "Yes",
            "condition": "8",
            "condition_notes": "Good condition",
            "findings": {
                "hardware_condition": "Good",
                "software_issues": "No issues found",
                "performance_score": "85/100"
            }
        }
        
        # Get system data
        system_data = system_collector.get_system_info()
        
        # Generate report
        report_content, file_path = report_formatter.generate_report(
            inspector_data=inspector_data,
            system_data=system_data,
            save_to_file=True
        )
        
        if file_path:
            print(f"✅ Report generated successfully: {file_path}")
        else:
            print("❌ Failed to generate report")
            
    except Exception as e:
        print(f"❌ Report generation error: {str(e)}")
    
    print("\nTest completed!")


if __name__ == "__main__":
    test_gmail_integration() 