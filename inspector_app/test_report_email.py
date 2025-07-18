#!/usr/bin/env python3
"""
Test script for ReportFormatter and EmailSender functionality.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.report_generator import ReportFormatter
from core.email_sender import EmailSender, EmailConfig
from core.system_info import SystemInfoCollector
from core.email_sender import EmailStatus


def test_report_generation():
    """Test the ReportFormatter functionality."""
    print("Testing ReportFormatter...")
    
    # Create sample data
    inspector_data = {
        "client_name": "John Doe",
        "order_number": "ORD-2024-001",
        "inspection_date": "2024-01-15",
        "inspector": "Tech Support Team",
        "findings": {
            "hardware_condition": "Good",
            "software_issues": "Minor updates needed",
            "performance_score": "85/100"
        }
    }
    
    # Get real system data
    system_collector = SystemInfoCollector()
    system_data = system_collector.get_system_info()
    
    # Create report formatter
    formatter = ReportFormatter()
    
    # Generate report (string only, no file save)
    report_content, file_path = formatter.generate_report(
        inspector_data=inspector_data,
        system_data=system_data,
        save_to_file=False
    )
    
    print("Report generated successfully!")
    print("Report content preview:")
    print("-" * 50)
    print(report_content[:500] + "..." if len(report_content) > 500 else report_content)
    print("-" * 50)
    
    # Generate report with file save
    report_content, file_path = formatter.generate_report(
        inspector_data=inspector_data,
        system_data=system_data,
        save_to_file=True
    )
    
    if file_path:
        print(f"Report saved to: {file_path}")
        return file_path
    else:
        print("Failed to save report file")
        return None


def test_email_sending(report_file_path: str = None):
    """Test the EmailSender functionality."""
    print("\nTesting EmailSender...")
    
    # Create email configuration
    # Note: You need to replace these with actual Gmail credentials
    email_config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="your-email@gmail.com",  # Replace with your Gmail
        password="your-app-password",     # Replace with Gmail App Password
        use_tls=True
    )
    
    # Create email sender
    email_sender = EmailSender(email_config)
    
    # Test email content
    recipient = "recipient@example.com"  # Replace with actual recipient
    subject = "Computer Inspection Report"
    body = """
Dear Client,

Please find attached the computer inspection report for your order.

The inspection was completed successfully and all system components have been evaluated.

If you have any questions about the report, please don't hesitate to contact us.

Best regards,
Computer Inspector Team
    """.strip()
    
    # Send email
    result = email_sender.send_email(
        recipient=recipient,
        subject=subject,
        body=body,
        attachment_path=report_file_path
    )
    
    if result.status == EmailStatus.SENT:
        print("Email sent successfully!")
        print(f"Message ID: {result.message_id}")
    else:
        print(f"Email sending failed: {result.error_message}")
        print("\nNote: To test email functionality, you need to:")
        print("1. Replace 'your-email@gmail.com' with your actual Gmail address")
        print("2. Replace 'your-app-password' with a Gmail App Password")
        print("3. Replace 'recipient@example.com' with the actual recipient email")
        print("4. Enable 2-factor authentication on your Gmail account")
        print("5. Generate an App Password in Gmail settings")


def main():
    """Main test function."""
    print("Computer Inspector - Report and Email Test")
    print("=" * 50)
    
    # Test report generation
    report_file_path = test_report_generation()
    
    # Test email sending
    test_email_sending(report_file_path)
    
    print("\nTest completed!")
    print("\nTo use this functionality in your application:")
    print("1. Import ReportFormatter and EmailSender from core modules")
    print("2. Configure email settings with your Gmail credentials")
    print("3. Use the generate_report() and send_email() methods")


if __name__ == "__main__":
    main() 