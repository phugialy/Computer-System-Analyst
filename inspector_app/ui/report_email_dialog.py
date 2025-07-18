"""
Report and Email Dialog
Provides UI for generating reports and sending emails.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QGroupBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from core.report_generator import ReportFormatter
from core.email_sender import EmailSender, EmailConfig, EmailStatus
from core.system_info import SystemInfoCollector


class EmailWorker(QThread):
    """Worker thread for sending emails."""
    email_sent = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, email_sender: EmailSender, recipient: str, subject: str, 
                 body: str, attachment_path: Optional[str]):
        super().__init__()
        self.email_sender = email_sender
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.attachment_path = attachment_path
    
    def run(self):
        """Send email in background thread."""
        try:
            result = self.email_sender.send_email(
                recipient=self.recipient,
                subject=self.subject,
                body=self.body,
                attachment_path=self.attachment_path
            )
            
            if result.status == EmailStatus.SENT:
                self.email_sent.emit(True, f"Email sent successfully! Message ID: {result.message_id}")
            else:
                self.email_sent.emit(False, f"Email failed: {result.error_message}")
                
        except Exception as e:
            self.email_sent.emit(False, f"Email error: {str(e)}")


class ReportEmailDialog(QDialog):
    """Dialog for generating reports and sending emails."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Report & Send Email")
        self.setModal(True)
        self.resize(600, 500)
        
        # Initialize components
        self.report_formatter = ReportFormatter()
        self.system_collector = SystemInfoCollector()
        self.email_worker = None
        
        # Sample inspector data (in real app, this would come from the main inspection)
        self.inspector_data = {
            "client_name": "Sample Client",
            "order_number": "ORD-2024-001",
            "inspection_date": "2024-01-15",
            "inspector": "Tech Support Team",
            "findings": {
                "hardware_condition": "Good",
                "software_issues": "Minor updates needed",
                "performance_score": "85/100"
            }
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Report Generation Section
        report_group = QGroupBox("Report Generation")
        report_layout = QVBoxLayout()
        
        # Report content preview
        self.report_preview = QTextEdit()
        self.report_preview.setMaximumHeight(150)
        self.report_preview.setReadOnly(True)
        self.report_preview.setPlaceholderText("Report preview will appear here...")
        report_layout.addWidget(QLabel("Report Preview:"))
        report_layout.addWidget(self.report_preview)
        
        # Generate report button
        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.clicked.connect(self.generate_report)
        report_layout.addWidget(self.generate_btn)
        
        # Save report button
        self.save_btn = QPushButton("Save Report to File")
        self.save_btn.clicked.connect(self.save_report)
        self.save_btn.setEnabled(False)
        report_layout.addWidget(self.save_btn)
        
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)
        
        # Email Section
        email_group = QGroupBox("Email Configuration")
        email_layout = QVBoxLayout()
        
        # Email settings
        settings_layout = QHBoxLayout()
        
        # Gmail settings
        gmail_layout = QVBoxLayout()
        gmail_layout.addWidget(QLabel("Gmail Settings:"))
        
        self.gmail_email = QLineEdit()
        self.gmail_email.setPlaceholderText("your-email@gmail.com")
        gmail_layout.addWidget(QLabel("Gmail Address:"))
        gmail_layout.addWidget(self.gmail_email)
        
        self.gmail_password = QLineEdit()
        self.gmail_password.setPlaceholderText("your-app-password")
        self.gmail_password.setEchoMode(QLineEdit.Password)
        gmail_layout.addWidget(QLabel("App Password:"))
        gmail_layout.addWidget(self.gmail_password)
        
        settings_layout.addLayout(gmail_layout)
        
        # Recipient settings
        recipient_layout = QVBoxLayout()
        recipient_layout.addWidget(QLabel("Recipient:"))
        
        self.recipient_email = QLineEdit()
        self.recipient_email.setPlaceholderText("recipient@example.com")
        recipient_layout.addWidget(self.recipient_email)
        
        self.email_subject = QLineEdit()
        self.email_subject.setText("Computer Inspection Report")
        recipient_layout.addWidget(QLabel("Subject:"))
        recipient_layout.addWidget(self.email_subject)
        
        settings_layout.addLayout(recipient_layout)
        email_layout.addLayout(settings_layout)
        
        # Email body
        email_layout.addWidget(QLabel("Email Body:"))
        self.email_body = QTextEdit()
        self.email_body.setMaximumHeight(100)
        self.email_body.setText("""Dear Client,

Please find attached the computer inspection report for your order.

The inspection was completed successfully and all system components have been evaluated.

If you have any questions about the report, please don't hesitate to contact us.

Best regards,
Computer Inspector Team""")
        email_layout.addWidget(self.email_body)
        
        # Send email button
        self.send_email_btn = QPushButton("Send Email")
        self.send_email_btn.clicked.connect(self.send_email)
        self.send_email_btn.setEnabled(False)
        email_layout.addWidget(self.send_email_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        email_layout.addWidget(self.progress_bar)
        
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def generate_report(self):
        """Generate a preview of the report."""
        try:
            # Get system data
            system_data = self.system_collector.get_system_info()
            
            # Generate report content
            report_content, _ = self.report_formatter.generate_report(
                inspector_data=self.inspector_data,
                system_data=system_data,
                save_to_file=False
            )
            
            # Show preview
            self.report_preview.setText(report_content)
            self.save_btn.setEnabled(True)
            self.send_email_btn.setEnabled(True)
            
            QMessageBox.information(self, "Success", "Report generated successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def save_report(self):
        """Save the report to a file."""
        try:
            # Get system data
            system_data = self.system_collector.get_system_info()
            
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Report",
                str(Path.home() / "Desktop" / "inspection_report.txt"),
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                # Generate and save report
                report_content, saved_path = self.report_formatter.generate_report(
                    inspector_data=self.inspector_data,
                    system_data=system_data,
                    save_to_file=True,
                    custom_path=file_path
                )
                
                if saved_path:
                    QMessageBox.information(self, "Success", f"Report saved to:\n{saved_path}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save report")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save report: {str(e)}")
    
    def send_email(self):
        """Send email with report attachment."""
        try:
            # Validate email settings
            if not self.gmail_email.text().strip():
                QMessageBox.warning(self, "Warning", "Please enter your Gmail address")
                return
            
            if not self.gmail_password.text().strip():
                QMessageBox.warning(self, "Warning", "Please enter your Gmail App Password")
                return
            
            if not self.recipient_email.text().strip():
                QMessageBox.warning(self, "Warning", "Please enter recipient email address")
                return
            
            # Create email configuration
            email_config = EmailConfig(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                username=self.gmail_email.text().strip(),
                password=self.gmail_password.text().strip(),
                use_tls=True
            )
            
            # Create email sender
            email_sender = EmailSender(email_config)
            
            # Generate report for attachment
            system_data = self.system_collector.get_system_info()
            report_content, report_path = self.report_formatter.generate_report(
                inspector_data=self.inspector_data,
                system_data=system_data,
                save_to_file=True
            )
            
            if not report_path:
                QMessageBox.critical(self, "Error", "Failed to generate report for email")
                return
            
            # Create email worker
            self.email_worker = EmailWorker(
                email_sender=email_sender,
                recipient=self.recipient_email.text().strip(),
                subject=self.email_subject.text().strip(),
                body=self.email_body.toPlainText(),
                attachment_path=report_path
            )
            
            # Connect signals
            self.email_worker.email_sent.connect(self.on_email_sent)
            
            # Show progress and disable button
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.send_email_btn.setEnabled(False)
            
            # Start email sending
            self.email_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")
    
    def on_email_sent(self, success: bool, message: str):
        """Handle email sending result."""
        # Hide progress bar
        self.progress_bar.setVisible(False)
        self.send_email_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
        
        # Clean up worker
        if self.email_worker:
            self.email_worker.deleteLater()
            self.email_worker = None


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = ReportEmailDialog()
    dialog.show()
    sys.exit(app.exec_()) 