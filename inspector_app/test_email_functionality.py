#!/usr/bin/env python3
"""
Test Email Functionality
Demonstrates the working email sending functionality with Gmail SMTP.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gmail_config import GmailConfigManager
from core.email_sender import EmailSender, EmailConfig
from core.report_generator import ReportFormatter


class EmailTestWindow(QMainWindow):
    """Simple test window for email functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Functionality Test")
        self.setGeometry(100, 100, 500, 400)
        
        # Initialize components
        self.gmail_config = GmailConfigManager()
        self.report_formatter = ReportFormatter()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the test UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Email Functionality Test")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "This test demonstrates the email sending functionality.\n"
            "1. Setup Gmail credentials\n"
            "2. Enter recipient email\n"
            "3. Test sending a report"
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(instructions)
        
        # Gmail Setup Button
        self.setup_gmail_btn = QPushButton("🔧 Setup Gmail Credentials")
        self.setup_gmail_btn.setMinimumHeight(40)
        self.setup_gmail_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.setup_gmail_btn.clicked.connect(self.setup_gmail)
        layout.addWidget(self.setup_gmail_btn)
        
        # Recipient Email
        recipient_label = QLabel("Recipient Email:")
        recipient_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        layout.addWidget(recipient_label)
        
        self.recipient_edit = QLineEdit()
        self.recipient_edit.setPlaceholderText("Enter recipient email address")
        self.recipient_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.recipient_edit)
        
        # Test Email Button
        self.test_email_btn = QPushButton("📧 Test Send Email")
        self.test_email_btn.setMinimumHeight(40)
        self.test_email_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.test_email_btn.clicked.connect(self.test_send_email)
        layout.addWidget(self.test_email_btn)
        
        # Status Label
        self.status_label = QLabel("Ready to test email functionality")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Add some spacing
        layout.addStretch()
        
        # Check Gmail configuration status
        self.update_gmail_status()
    
    def update_gmail_status(self):
        """Update the Gmail configuration status."""
        if self.gmail_config.is_configured():
            credentials = self.gmail_config.get_credentials()
            self.status_label.setText(f"✅ Gmail configured: {credentials.email}")
            self.setup_gmail_btn.setText("🔧 Reconfigure Gmail")
        else:
            self.status_label.setText("❌ Gmail not configured")
            self.setup_gmail_btn.setText("🔧 Setup Gmail Credentials")
    
    def setup_gmail(self):
        """Setup Gmail credentials."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Gmail Setup")
        dialog.setModal(True)
        dialog.resize(450, 250)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # Instructions
        instructions = QLabel(
            "To use email functionality, you need to:\n"
            "1. Enable 2-Factor Authentication on your Gmail account\n"
            "2. Generate an App Password\n"
            "3. Enter your credentials below"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #2c3e50; font-size: 12px;")
        layout.addWidget(instructions)
        
        # Email field
        email_layout = QHBoxLayout()
        email_label = QLabel("Gmail Address:")
        email_label.setMinimumWidth(120)
        email_edit = QLineEdit()
        email_edit.setPlaceholderText("your-email@gmail.com")
        email_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        email_layout.addWidget(email_label)
        email_layout.addWidget(email_edit)
        layout.addLayout(email_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("App Password:")
        password_label.setMinimumWidth(120)
        password_edit = QLineEdit()
        password_edit.setPlaceholderText("your-app-password")
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        password_layout.addWidget(password_label)
        password_layout.addWidget(password_edit)
        layout.addLayout(password_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        setup_btn = QPushButton("Setup Gmail")
        setup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(setup_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect buttons
        def on_setup():
            email = email_edit.text().strip()
            password = password_edit.text().strip()
            
            if not email or not password:
                QMessageBox.warning(dialog, "Warning", "Please enter both email and password.")
                return
            
            # Setup Gmail
            if self.gmail_config.setup_credentials(email, password):
                QMessageBox.information(dialog, "Success", "Gmail configured successfully!")
                dialog.accept()
                self.update_gmail_status()
            else:
                QMessageBox.critical(dialog, "Error", "Failed to configure Gmail. Please check your credentials.")
        
        setup_btn.clicked.connect(on_setup)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Show dialog
        dialog.exec()
    
    def test_send_email(self):
        """Test sending an email."""
        recipient = self.recipient_edit.text().strip()
        
        if not recipient:
            QMessageBox.warning(self, "Warning", "Please enter a recipient email address.")
            return
        
        if not self.gmail_config.is_configured():
            QMessageBox.warning(self, "Warning", "Please setup Gmail credentials first.")
            return
        
        try:
            self.status_label.setText("Preparing to send test email...")
            
            # Get Gmail credentials
            credentials = self.gmail_config.get_credentials()
            
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
            
            # Generate a simple test report
            inspector_data = {
                "client_name": "Test Client",
                "order_number": "TEST-001",
                "inspection_date": "2024-01-15",
                "inspector": "Test Inspector",
                "initial_location": "Test Location",
                "sku_number": "TEST-SKU-001",
                "charger": "Yes",
                "issues": "No issues found",
                "warranty": "Yes",
                "condition": "9",
                "condition_notes": "Excellent condition",
                "findings": {
                    "hardware_condition": "Good",
                    "software_issues": "No issues found",
                    "performance_score": "95/100"
                }
            }
            
            system_data = {
                "brand_model": "Test Computer",
                "cpu": "Intel Core i7",
                "ram": "16GB DDR4",
                "storage": "512GB SSD",
                "gpu": "Integrated Graphics",
                "os": "Windows 11",
                "display": "15.6\" Full HD",
                "touch_support": "No",
                "fingerprint_reader": "No",
                "battery_health": "Good"
            }
            
            # Generate report
            report_content, report_path = self.report_formatter.generate_report(
                inspector_data=inspector_data,
                system_data=system_data,
                save_to_file=True
            )
            
            if not report_path:
                QMessageBox.critical(self, "Error", "Failed to generate test report")
                return
            
            # Create email content with detailed report in body
            subject = "Computer Inspector - Test Email"
            body = f"""
Dear {recipient},

This is a test email from the Computer Inspector application.

TEST REPORT SUMMARY:
═══════════════════════════════════════════════════════════════════════════════

INSPECTION DETAILS:
• Inspector: {inspector_data['inspector']}
• Order Number: {inspector_data['order_number']}
• Inspection Date: {inspector_data['inspection_date']}
• Location: {inspector_data['initial_location']}
• SKU: {inspector_data['sku_number']}

DEVICE CONDITION:
• Charger: {inspector_data['charger']}
• Warranty: {inspector_data['warranty']}
• Condition Rating: {inspector_data['condition']}/10
• Condition Notes: {inspector_data['condition_notes']}

ISSUES FOUND:
• {inspector_data['issues']}

SYSTEM SPECIFICATIONS:
• Brand/Model: {system_data['brand_model']}
• CPU: {system_data['cpu']}
• RAM: {system_data['ram']}
• Storage: {system_data['storage']}
• GPU: {system_data['gpu']}
• Operating System: {system_data['os']}
• Display: {system_data['display']}
• Touch Support: {system_data['touch_support']}
• Fingerprint Reader: {system_data['fingerprint_reader']}
• Battery Health: {system_data['battery_health']}

═══════════════════════════════════════════════════════════════════════════════

INSPECTION STATUS: ✅ TEST COMPLETED SUCCESSFULLY

The test inspection was completed successfully and all system components have been evaluated.
A detailed technical report is attached for your records.

Best regards,
Computer Inspector Test System
            """.strip()
            
            # Send email
            self.status_label.setText("Sending email...")
            
            result = email_sender.send_email(
                recipient=recipient,
                subject=subject,
                body=body,
                attachment_path=report_path
            )
            
            if result.status.value == "sent":
                self.status_label.setText("✅ Email sent successfully!")
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Test email sent successfully to {recipient}!\n\n"
                    f"Message ID: {result.message_id}"
                )
            else:
                self.status_label.setText(f"❌ Email failed: {result.error_message}")
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to send email:\n{result.error_message}"
                )
                
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Email sending error: {str(e)}")


def main():
    """Main function to run the email test."""
    app = QApplication(sys.argv)
    
    window = EmailTestWindow()
    window.show()
    
    print("Email Functionality Test")
    print("=" * 30)
    print("1. Click 'Setup Gmail Credentials' to configure Gmail")
    print("2. Enter a recipient email address")
    print("3. Click 'Test Send Email' to send a test email")
    print()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 