#!/usr/bin/env python3
"""
Integration Example for Report Generation and Email Functionality
Shows how to integrate ReportFormatter and EmailSender into the main application.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.report_generator import ReportFormatter
from core.email_sender import EmailSender, EmailConfig, EmailStatus
from core.system_info import SystemInfoCollector
from gmail_config import GmailConfigManager, setup_gmail_interactive, test_gmail_configuration


class ReportEmailManager:
    """Manages report generation and email sending functionality."""
    
    def __init__(self):
        self.report_formatter = ReportFormatter()
        self.system_collector = SystemInfoCollector()
        self.email_sender = None
        self.gmail_config = GmailConfigManager()
    
    def setup_gmail(self) -> bool:
        """Setup Gmail using the configuration manager."""
        if self.gmail_config.is_configured():
            print("Gmail is already configured!")
            return True
        
        print("Gmail is not configured. Setting up now...")
        return setup_gmail_interactive()
    
    def test_gmail(self) -> bool:
        """Test Gmail configuration."""
        return test_gmail_configuration()
    
    def generate_inspection_report(self, inspector_data: dict, save_to_file: bool = True) -> tuple[str, str]:
        """
        Generate a complete inspection report.
        
        Args:
            inspector_data: Dictionary containing inspection results
            save_to_file: Whether to save the report to disk
            
        Returns:
            Tuple of (report_content, file_path)
        """
        try:
            # Get system information
            system_data = self.system_collector.get_system_info()
            
            # Generate report
            report_content, file_path = self.report_formatter.generate_report(
                inspector_data=inspector_data,
                system_data=system_data,
                save_to_file=save_to_file
            )
            
            return report_content, file_path
            
        except Exception as e:
            print(f"Failed to generate report: {str(e)}")
            return str(e), None
    
    def send_report_email(self, recipient: str, subject: str, body: str, 
                         report_file_path: str = None) -> bool:
        """
        Send a report via email.
        
        Args:
            recipient: Email address of recipient
            subject: Email subject
            body: Email body text
            report_file_path: Path to report file to attach
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # Get Gmail credentials
        credentials = self.gmail_config.get_credentials()
        if not credentials:
            print("Gmail not configured. Please run setup_gmail() first.")
            return False
        
        try:
            # Create email configuration
            email_config = EmailConfig(
                smtp_server=credentials.smtp_server,
                smtp_port=credentials.smtp_port,
                username=credentials.email,
                password=credentials.app_password,
                use_tls=credentials.use_tls
            )
            
            # Create email sender
            email_sender = EmailSender(email_config)
            
            # Send email
            result = email_sender.send_email(
                recipient=recipient,
                subject=subject,
                body=body,
                attachment_path=report_file_path
            )
            
            if result.status == EmailStatus.SENT:
                print(f"Email sent successfully! Message ID: {result.message_id}")
                return True
            else:
                print(f"Email failed: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"Email error: {str(e)}")
            return False
    
    def generate_and_send_report(self, inspector_data: dict, recipient: str, 
                                subject: str = "Computer Inspection Report") -> bool:
        """
        Generate a report and send it via email in one operation.
        
        Args:
            inspector_data: Dictionary containing inspection results
            recipient: Email address of recipient
            subject: Email subject
            
        Returns:
            True if both report generation and email sending succeeded
        """
        try:
            # Generate report
            report_content, report_file_path = self.generate_inspection_report(
                inspector_data=inspector_data,
                save_to_file=True
            )
            
            if not report_file_path:
                print("Failed to generate report file")
                return False
            
            # Create email body
            body = f"""
Dear Client,

Please find attached the computer inspection report for your order.

Report Summary:
- Client: {inspector_data.get('client_name', 'N/A')}
- Order Number: {inspector_data.get('order_number', 'N/A')}
- Inspection Date: {inspector_data.get('inspection_date', 'N/A')}

The inspection was completed successfully and all system components have been evaluated.

If you have any questions about the report, please don't hesitate to contact us.

Best regards,
Computer Inspector Team
            """.strip()
            
            # Send email
            return self.send_report_email(
                recipient=recipient,
                subject=subject,
                body=body,
                report_file_path=report_file_path
            )
            
        except Exception as e:
            print(f"Failed to generate and send report: {str(e)}")
            return False


def main():
    """Main example function."""
    print("Computer Inspector - Report and Email Integration Example")
    print("=" * 60)
    
    # Create manager
    manager = ReportEmailManager()
    
    # Sample inspection data (in real app, this would come from the inspection process)
    sample_inspector_data = {
        "client_name": "Jane Smith",
        "order_number": "ORD-2024-002",
        "inspection_date": "2024-01-16",
        "inspector": "Tech Support Team",
        "findings": {
            "hardware_condition": "Excellent",
            "software_issues": "No issues found",
            "performance_score": "92/100",
            "recommendations": "System is in good condition"
        }
    }
    
    # Example 1: Generate report only
    print("\n1. Generating report...")
    report_content, file_path = manager.generate_inspection_report(
        inspector_data=sample_inspector_data,
        save_to_file=True
    )
    
    if file_path:
        print(f"✅ Report generated and saved to: {file_path}")
    else:
        print("❌ Failed to generate report")
    
    # Example 2: Setup Gmail and send report
    print("\n2. Gmail setup and email functionality...")
    
    # Check if Gmail is configured
    if not manager.gmail_config.is_configured():
        print("Gmail is not configured. Would you like to set it up now? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            if manager.setup_gmail():
                print("✅ Gmail configured successfully!")
            else:
                print("❌ Gmail setup failed.")
                return
        else:
            print("Skipping Gmail setup.")
            return
    else:
        print("✅ Gmail is already configured!")
    
    # Test Gmail configuration
    print("\nTesting Gmail configuration...")
    if manager.test_gmail():
        print("✅ Gmail test successful!")
        
        # Send test email
        print("\nSending test email...")
        success = manager.generate_and_send_report(
            inspector_data=sample_inspector_data,
            recipient=manager.gmail_config.get_credentials().email  # Send to yourself
        )
        
        if success:
            print("✅ Report generated and sent successfully!")
        else:
            print("❌ Failed to send report via email")
    else:
        print("❌ Gmail test failed. Please check your configuration.")
    
    print("\nIntegration example completed!")
    print("\nTo use in your application:")
    print("1. Create a ReportEmailManager instance")
    print("2. Call setup_gmail() to configure Gmail")
    print("3. Use generate_inspection_report() to create reports")
    print("4. Use send_report_email() or generate_and_send_report() to send emails")


if __name__ == "__main__":
    main() 