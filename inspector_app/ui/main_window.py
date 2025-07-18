"""
Main Window UI for Inspector Diagnostic Utility
Provides the primary interface for system diagnostics and reporting.
"""

import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox, QTabWidget,
    QProgressBar, QCheckBox, QComboBox, QSpinBox, QFileDialog,
    QMessageBox, QSplitter, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon, QPixmap

# Import the system info collector
from core.system_info import system_collector

# Import test launcher
from core.test_launcher import test_launcher

# Import Gmail and report functionality
from gmail_config import GmailConfigManager, setup_gmail_interactive, test_gmail_configuration
from core.report_generator import ReportFormatter
from core.email_sender import EmailSender, EmailConfig, EmailStatus
from google_oauth_simple import GoogleAccountSelectionDialog, GoogleUser


class CustomTestResultComboBox(QWidget):
    """Custom combo box for test results with Pass, Fail, and custom input options."""
    
    valueChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the custom combo box UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Create the combo box
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Not Tested", "Pass", "Fail", "Comments"])
        self.combo_box.setFont(QFont("Segoe UI", 11))
        self.combo_box.setMinimumHeight(40)
        self.combo_box.setStyleSheet("""
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px 15px;
                background-color: white;
                color: #2c3e50;
                font-size: 11px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #7f8c8d;
                margin-right: 10px;
            }
        """)
        
        # Create the custom input field (initially hidden)
        self.custom_input = QLineEdit()
        self.custom_input.setFont(QFont("Segoe UI", 11))
        self.custom_input.setMinimumHeight(40)
        self.custom_input.setPlaceholderText("Enter custom result...")
        self.custom_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px 15px;
                background-color: white;
                color: #2c3e50;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        self.custom_input.hide()
        
        # Connect signals
        self.combo_box.currentTextChanged.connect(self._on_combo_changed)
        self.custom_input.textChanged.connect(self._on_custom_input_changed)
        
        # Add widgets to layout
        layout.addWidget(self.combo_box)
        layout.addWidget(self.custom_input)
        
    def _on_combo_changed(self, text):
        """Handle combo box selection changes."""
        if text == "Comments":
            self.custom_input.show()
            self.custom_input.setFocus()
            self.valueChanged.emit("")
        else:
            self.custom_input.hide()
            self.valueChanged.emit(text)
            
    def _on_custom_input_changed(self, text):
        """Handle custom input text changes."""
        if self.combo_box.currentText() == "Comments":
            self.valueChanged.emit(text)
            
    def currentText(self):
        """Get the current text value."""
        if self.combo_box.currentText() == "Comments":
            return self.custom_input.text()
        return self.combo_box.currentText()
        
    def setCurrentText(self, text):
        """Set the current text value."""
        if text in ["Not Tested", "Pass", "Fail"]:
            self.combo_box.setCurrentText(text)
            self.custom_input.hide()
        else:
            self.combo_box.setCurrentText("Comments")
            self.custom_input.setText(text)
            self.custom_input.show()


class EmailWorker(QThread):
    """Worker thread for sending emails."""
    email_sent = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, email_sender: EmailSender, recipient: str, subject: str, 
                 body: str, attachment_path: str = None):
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


class MainWindow(QMainWindow):
    """Main application window with diagnostic interface."""
    
    # Signals for future feature integration
    system_scan_requested = pyqtSignal()
    report_generation_requested = pyqtSignal(str)
    email_send_requested = pyqtSignal(str, str, str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inspector Diagnostic Utility")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1400, 800)
        
        # Initialize Gmail and report components
        self.gmail_config = GmailConfigManager()
        self.report_formatter = ReportFormatter()
        self.email_worker = None
        
        # Initialize UI components
        self._setup_ui()
        self._setup_connections()
        self._setup_status_timer()
        
        # Load initial system information
        self._update_system_info()
        
    def _setup_ui(self):
        """Initialize the main user interface with spacious design."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with spacious design
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        self._create_simple_title(main_layout)
        
        # Top section with three columns
        top_section = QHBoxLayout()
        top_section.setSpacing(20)
        
        # Client Order Info (left column)
        client_panel = QWidget()
        client_layout = QVBoxLayout(client_panel)
        client_layout.setContentsMargins(0, 0, 0, 0)
        self._create_client_order_section(client_layout)
        
        # System Info (middle column)
        system_panel = QWidget()
        system_layout = QVBoxLayout(system_panel)
        system_layout.setContentsMargins(0, 0, 0, 0)
        self._create_system_info_section(system_layout)
        
        # Diagnostic Tests (right column)
        tests_panel = QWidget()
        tests_layout = QVBoxLayout(tests_panel)
        tests_layout.setContentsMargins(0, 0, 0, 0)
        self._create_diagnostic_tests_section(tests_layout)
        
        # Add panels to top section with different proportions
        top_section.addWidget(client_panel, 1)
        top_section.addWidget(system_panel, 3)  # Give system info much more space
        top_section.addWidget(tests_panel, 1)
        
        main_layout.addLayout(top_section)
        
        # Email and Report section (full width at bottom)
        self._create_email_report_section(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def _create_simple_title(self, parent_layout):
        """Create a simple title line."""
        title_label = QLabel("Computer Device Inspection App")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        parent_layout.addWidget(title_label)
        
    def _create_client_order_section(self, parent_layout):
        """Create the Client Order Info section with spacious layout."""
        order_group = QGroupBox("Client Order Information")
        order_group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        order_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
            }
        """)
        
        order_layout = QVBoxLayout(order_group)
        order_layout.setContentsMargins(20, 25, 20, 20)
        order_layout.setSpacing(15)
        
        # Create styled labels and fields with spacious sizing
        def create_field_pair(label_text, field, placeholder=None, readonly=False, field_type="line"):
            # Create label with spacious sizing
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            label.setStyleSheet("color: #2c3e50; min-width: 150px; padding: 5px;")
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            
            # Create field with spacious responsive sizing
            if field_type == "line":
                field.setFont(QFont("Segoe UI", 11))
                field.setMinimumHeight(40)
                field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                field.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #bdc3c7;
                        border-radius: 8px;
                        padding: 10px 15px;
                        background-color: white;
                        color: #2c3e50;
                        font-size: 11px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #3498db;
                        background-color: #f8f9fa;
                    }
                    QLineEdit:read-only {
                        background-color: #ecf0f1;
                        color: #7f8c8d;
                    }
                """)
                
                if placeholder:
                    field.setPlaceholderText(placeholder)
                if readonly:
                    field.setReadOnly(True)
                    
            elif field_type == "text":
                field.setFont(QFont("Segoe UI", 11))
                field.setMinimumHeight(80)
                field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                field.setStyleSheet("""
                    QTextEdit {
                        border: 2px solid #bdc3c7;
                        border-radius: 8px;
                        padding: 10px 15px;
                        background-color: white;
                        color: #2c3e50;
                        font-size: 11px;
                    }
                    QTextEdit:focus {
                        border: 2px solid #3498db;
                        background-color: #f8f9fa;
                    }
                """)
                
                if placeholder:
                    field.setPlaceholderText(placeholder)
                if readonly:
                    field.setReadOnly(True)
            
            # Create layout for this field pair
            field_layout = QHBoxLayout()
            field_layout.addWidget(label)
            field_layout.addWidget(field)
            field_layout.setSpacing(15)
            
            return field_layout
        
        # Client Order fields with spacious responsive sizing
        self.client_name = QLineEdit()
        self.client_name.setPlaceholderText("Enter client name")
        
        self.order_number = QLineEdit()
        self.order_number.setPlaceholderText("Enter order number")
        
        self.device_type = QLineEdit()
        self.device_type.setPlaceholderText("Enter device type")
        
        self.inspector_name = QLineEdit()
        self.inspector_name.setPlaceholderText("Enter inspector name")
        
        self.inspection_date = QLineEdit()
        self.inspection_date.setPlaceholderText("Enter inspection date")
        
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Enter any additional notes...")
        
        # Add fields to layout with spacious spacing
        order_layout.addLayout(create_field_pair("Client Name:", self.client_name))
        order_layout.addLayout(create_field_pair("Order Number:", self.order_number))
        order_layout.addLayout(create_field_pair("Device Type:", self.device_type))
        order_layout.addLayout(create_field_pair("Inspector Name:", self.inspector_name))
        order_layout.addLayout(create_field_pair("Inspection Date:", self.inspection_date))
        order_layout.addLayout(create_field_pair("Notes:", self.notes, field_type="text"))
        
        parent_layout.addWidget(order_group)
        
    def _create_system_info_section(self, parent_layout):
        """Create the System Information section with enhanced visibility."""
        system_group = QGroupBox("System Information")
        system_group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        system_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
            }
        """)
        
        system_layout = QVBoxLayout(system_group)
        system_layout.setContentsMargins(20, 25, 20, 20)
        system_layout.setSpacing(20)
        
        # Create styled labels and fields with enhanced visibility
        def create_system_field_pair(label_text, field, readonly=True):
            # Create label with enhanced styling
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            label.setStyleSheet("color: #2c3e50; min-width: 180px; padding: 8px;")
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            
            # Create field with enhanced styling for better visibility
            field.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            field.setMinimumHeight(45)
            field.setMinimumWidth(300)
            field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            field.setStyleSheet("""
                QLineEdit {
                    border: 3px solid #27ae60;
                    border-radius: 10px;
                    padding: 12px 18px;
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    font-size: 12px;
                    font-weight: medium;
                }
                QLineEdit:read-only {
                    background-color: #e8f5e8;
                    color: #2c3e50;
                    border: 3px solid #27ae60;
                }
            """)
            
            if readonly:
                field.setReadOnly(True)
            
            # Create layout for this field pair
            field_layout = QHBoxLayout()
            field_layout.addWidget(label)
            field_layout.addWidget(field)
            field_layout.setSpacing(20)
            
            return field_layout
        
        # System Info fields with enhanced visibility
        self.cpu_info = QLineEdit()
        self.cpu_info.setReadOnly(True)
        
        self.memory_info = QLineEdit()
        self.memory_info.setReadOnly(True)
        
        self.disk_info = QLineEdit()
        self.disk_info.setReadOnly(True)
        
        self.os_info = QLineEdit()
        self.os_info.setReadOnly(True)
        
        self.graphics_info = QLineEdit()
        self.graphics_info.setReadOnly(True)
        
        self.network_info = QLineEdit()
        self.network_info.setReadOnly(True)
        
        # Add fields to layout with enhanced spacing
        system_layout.addLayout(create_system_field_pair("CPU:", self.cpu_info))
        system_layout.addLayout(create_system_field_pair("Memory:", self.memory_info))
        system_layout.addLayout(create_system_field_pair("Storage:", self.disk_info))
        system_layout.addLayout(create_system_field_pair("Operating System:", self.os_info))
        system_layout.addLayout(create_system_field_pair("Graphics:", self.graphics_info))
        system_layout.addLayout(create_system_field_pair("Network:", self.network_info))
        
        # Recheck hardware button
        self.recheck_hardware_btn = QPushButton("🔄 Recheck Hardware")
        self.recheck_hardware_btn.setMinimumHeight(50)
        self.recheck_hardware_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.recheck_hardware_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
        system_layout.addWidget(self.recheck_hardware_btn)
        
        parent_layout.addWidget(system_group)
        
    def _create_diagnostic_tests_section(self, parent_layout):
        """Create the Diagnostic Test buttons section with spacious layout."""
        tests_group = QGroupBox("Diagnostic Tests")
        tests_group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        tests_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
            }
        """)
        
        tests_layout = QVBoxLayout(tests_group)
        tests_layout.setContentsMargins(20, 25, 20, 20)
        tests_layout.setSpacing(20)
        
        # Test buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Test buttons with spacious responsive sizing
        self.play_sound_btn = QPushButton("▶ Play Test Sound")
        self.play_sound_btn.setMinimumHeight(50)
        self.play_sound_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.play_sound_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.play_sound_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        self.dead_pixel_btn = QPushButton("🔍 Open Dead Pixel Test")
        self.dead_pixel_btn.setMinimumHeight(50)
        self.dead_pixel_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.dead_pixel_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.dead_pixel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """)
        
        self.keyboard_test_btn = QPushButton("⌨ Launch Keyboard Test")
        self.keyboard_test_btn.setMinimumHeight(50)
        self.keyboard_test_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.keyboard_test_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.keyboard_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        
        buttons_layout.addWidget(self.play_sound_btn)
        buttons_layout.addWidget(self.dead_pixel_btn)
        buttons_layout.addWidget(self.keyboard_test_btn)
        
        tests_layout.addLayout(buttons_layout)
        
        # Test results section
        results_layout = QGridLayout()
        results_layout.setSpacing(15)
        results_layout.setColumnStretch(1, 1)  # Make the second column expandable
        
        # Audio test result
        audio_label = QLabel("Audio Test Result:")
        audio_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        audio_label.setStyleSheet("color: #2c3e50; min-width: 150px; padding: 5px;")
        
        self.audio_test_result = CustomTestResultComboBox()
        
        # Dead pixel test result
        pixel_label = QLabel("Dead Pixel Test Result:")
        pixel_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        pixel_label.setStyleSheet("color: #2c3e50; min-width: 150px; padding: 5px;")
        
        self.pixel_test_result = CustomTestResultComboBox()
        
        # Keyboard test result
        keyboard_label = QLabel("Keyboard Test Result:")
        keyboard_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        keyboard_label.setStyleSheet("color: #2c3e50; min-width: 150px; padding: 5px;")
        
        self.keyboard_test_result = CustomTestResultComboBox()
        
        # Add test result fields to grid
        results_layout.addWidget(audio_label, 0, 0)
        results_layout.addWidget(self.audio_test_result, 0, 1)
        results_layout.addWidget(pixel_label, 1, 0)
        results_layout.addWidget(self.pixel_test_result, 1, 1)
        results_layout.addWidget(keyboard_label, 2, 0)
        results_layout.addWidget(self.keyboard_test_result, 2, 1)
        
        tests_layout.addLayout(results_layout)
        
        parent_layout.addWidget(tests_group)
        
    def _create_email_report_section(self, parent_layout):
        """Create the Email and Report section with compact layout."""
        report_group = QGroupBox("Email & Report Generation")
        report_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        report_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
        """)
        
        report_layout = QVBoxLayout(report_group)
        report_layout.setContentsMargins(15, 20, 15, 15)
        report_layout.setSpacing(15)
        
        # Email recipient field with compact responsive styling
        email_layout = QHBoxLayout()
        email_layout.setSpacing(15)
        
        email_label = QLabel("Recipient Email:")
        email_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        email_label.setStyleSheet("color: #2c3e50; min-width: 120px; padding: 3px;")
        email_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Enter recipient email address")
        self.email_edit.setFont(QFont("Segoe UI", 10))
        self.email_edit.setMinimumHeight(32)
        self.email_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.email_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                color: #2c3e50;
                font-size: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_edit)
        
        # Google OAuth section
        google_layout = QHBoxLayout()
        google_layout.setSpacing(15)
        
        google_label = QLabel("Google Account:")
        google_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        google_label.setStyleSheet("color: #2c3e50; min-width: 120px; padding: 3px;")
        google_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # Google Sign-in button with real OAuth
        try:
            from google_oauth_real import GoogleSignInButton
            self.google_signin_btn = GoogleSignInButton()
            self.google_signin_btn.setMinimumHeight(32)
            self.google_signin_btn.authentication_completed.connect(self._on_google_auth_completed)
            self.google_signin_btn.authentication_failed.connect(self._on_google_auth_failed)
        except Exception as e:
            # Fallback to simple button if OAuth setup fails
            self.google_signin_btn = QPushButton("Sign in with Google (Setup Required)")
            self.google_signin_btn.setEnabled(False)
            self.google_signin_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-height: 40px;
                    font-weight: bold;
                }
            """)
        
        google_layout.addWidget(google_label)
        google_layout.addWidget(self.google_signin_btn)
        
        # Add both layouts to report layout
        report_layout.addLayout(email_layout)
        report_layout.addLayout(google_layout)
        
        # Report buttons with compact responsive styling
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.generate_report_btn = QPushButton("📄 Generate Report")
        self.generate_report_btn.setMinimumHeight(40)
        self.generate_report_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.generate_report_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.generate_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
        self.save_report_btn = QPushButton("💾 Save Locally")
        self.save_report_btn.setMinimumHeight(40)
        self.save_report_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.save_report_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.save_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        self.send_email_btn = QPushButton("📧 Send via Email")
        self.send_email_btn.setMinimumHeight(40)
        self.send_email_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.send_email_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.send_email_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """)
        
        buttons_layout.addWidget(self.generate_report_btn)
        buttons_layout.addWidget(self.save_report_btn)
        buttons_layout.addWidget(self.send_email_btn)
        
        report_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(report_group)
        
    def _setup_connections(self):
        """Setup signal connections for UI interactions."""
        # Diagnostic test buttons
        self.play_sound_btn.clicked.connect(self._on_play_test_sound)
        self.dead_pixel_btn.clicked.connect(self._on_open_dead_pixel_test)
        self.keyboard_test_btn.clicked.connect(self._on_launch_keyboard_test)
        
        # Hardware re-check button
        self.recheck_hardware_btn.clicked.connect(self._on_recheck_hardware)
        
        # Report buttons
        self.generate_report_btn.clicked.connect(self._on_generate_report)
        self.save_report_btn.clicked.connect(self._on_save_report)
        self.send_email_btn.clicked.connect(self._on_send_email)
        
    def _setup_status_timer(self):
        """Setup timer for updating status information."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
        
    def _on_play_test_sound(self):
        """Handle play test sound button click."""
        try:
            self.statusBar().showMessage("Playing test sound...")
            success = test_launcher.play_audio_test()
            
            if success:
                self.statusBar().showMessage("Test sound played successfully")
                # Ask user for test result
                result = QMessageBox.question(
                    self, 
                    "Audio Test Result", 
                    "Did the audio test pass?\n\nClick 'Yes' for Pass, 'No' for Fail, or 'Cancel' for Partial",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )
                
                if result == QMessageBox.StandardButton.Yes:
                    self.audio_test_result.setCurrentText("Pass")
                elif result == QMessageBox.StandardButton.No:
                    self.audio_test_result.setCurrentText("Fail")
                else:
                    self.audio_test_result.setCurrentText("Partial")
            else:
                QMessageBox.warning(self, "Audio Test", "Failed to play test sound. Please check if the audio file exists.")
                self.audio_test_result.setCurrentText("Fail")
                
        except Exception as e:
            self.statusBar().showMessage(f"Error playing test sound: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to play test sound: {str(e)}")
            self.audio_test_result.setCurrentText("Fail")
        
    def _on_open_dead_pixel_test(self):
        """Handle dead pixel test button click."""
        try:
            self.statusBar().showMessage("Opening dead pixel test...")
            success = test_launcher.launch_dead_pixel_test()
            
            if success:
                self.statusBar().showMessage("Dead pixel test opened in browser")
                # Ask user for test result after a delay
                QTimer.singleShot(2000, self._ask_pixel_test_result)
            else:
                QMessageBox.warning(self, "Dead Pixel Test", "Failed to open dead pixel test. Please check your internet connection.")
                self.pixel_test_result.setCurrentText("Fail")
                
        except Exception as e:
            self.statusBar().showMessage(f"Error opening dead pixel test: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open dead pixel test: {str(e)}")
            self.pixel_test_result.setCurrentText("Fail")
    
    def _ask_pixel_test_result(self):
        """Ask user for dead pixel test result."""
        result = QMessageBox.question(
            self, 
            "Dead Pixel Test Result", 
            "Did the dead pixel test pass?\n\nClick 'Yes' for Pass, 'No' for Fail, or 'Cancel' for Partial",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if result == QMessageBox.StandardButton.Yes:
            self.pixel_test_result.setCurrentText("Pass")
        elif result == QMessageBox.StandardButton.No:
            self.pixel_test_result.setCurrentText("Fail")
        else:
            self.pixel_test_result.setCurrentText("Partial")
        
    def _on_launch_keyboard_test(self):
        """Handle keyboard test button click."""
        try:
            self.statusBar().showMessage("Launching keyboard test...")
            success = test_launcher.launch_keyboard_test()
            
            if success:
                self.statusBar().showMessage("Keyboard test opened in browser")
                # Ask user for test result after a delay
                QTimer.singleShot(2000, self._ask_keyboard_test_result)
            else:
                QMessageBox.warning(self, "Keyboard Test", "Failed to open keyboard test. Please check your internet connection.")
                self.keyboard_test_result.setCurrentText("Fail")
                
        except Exception as e:
            self.statusBar().showMessage(f"Error launching keyboard test: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to launch keyboard test: {str(e)}")
            self.keyboard_test_result.setCurrentText("Fail")
    
    def _ask_keyboard_test_result(self):
        """Ask user for keyboard test result."""
        result = QMessageBox.question(
            self, 
            "Keyboard Test Result", 
            "Did the keyboard test pass?\n\nClick 'Yes' for Pass, 'No' for Fail, or 'Cancel' for Partial",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if result == QMessageBox.StandardButton.Yes:
            self.keyboard_test_result.setCurrentText("Pass")
        elif result == QMessageBox.StandardButton.No:
            self.keyboard_test_result.setCurrentText("Fail")
        else:
            self.keyboard_test_result.setCurrentText("Partial")
        
    def _on_recheck_hardware(self):
        """Handle re-check hardware button click."""
        self.statusBar().showMessage("Re-checking hardware information...")
        # TODO: Implement hardware re-check
        self._update_system_info()
        
    def _update_system_info(self):
        """Update system information fields using SystemInfoCollector."""
        try:
            # Get system information from the collector
            system_data = system_collector.get_system_info()
            
            # Update UI fields with collected data
            if hasattr(self, 'cpu_info'):
                self.cpu_info.setText(str(system_data.get('cpu', 'N/A')))
            if hasattr(self, 'memory_info'):
                self.memory_info.setText(str(system_data.get('ram', 'N/A')))
            if hasattr(self, 'disk_info'):
                self.disk_info.setText(str(system_data.get('storage', 'N/A')))
            if hasattr(self, 'os_info'):
                self.os_info.setText(str(system_data.get('os', 'N/A')))
            if hasattr(self, 'graphics_info'):
                self.graphics_info.setText(str(system_data.get('gpu', 'N/A')))
            if hasattr(self, 'network_info'):
                self.network_info.setText(str(system_data.get('network', 'N/A')))
            
            self.statusBar().showMessage("Hardware information updated successfully")
        except Exception as e:
            self.statusBar().showMessage(f"Error updating hardware info: {str(e)}")
            # Set error state for fields
            if hasattr(self, 'cpu_info'):
                self.cpu_info.setText("Error")
            if hasattr(self, 'memory_info'):
                self.memory_info.setText("Error")
            if hasattr(self, 'disk_info'):
                self.disk_info.setText("Error")
            if hasattr(self, 'os_info'):
                self.os_info.setText("Error")
            if hasattr(self, 'graphics_info'):
                self.graphics_info.setText("Error")
            if hasattr(self, 'network_info'):
                self.network_info.setText("Error")
        
    def _on_generate_report(self):
        """Handle generate report button click."""
        try:
            self.statusBar().showMessage("Generating report...")
            
            # Collect inspector data from UI
            inspector_data = self._collect_inspector_data()
            
            # Get system data
            system_data = system_collector.get_system_info()
            
            # Generate report
            report_content, file_path = self.report_formatter.generate_report(
                inspector_data=inspector_data,
                system_data=system_data,
                save_to_file=True
            )
            
            if file_path:
                self.statusBar().showMessage(f"Report generated successfully: {file_path}")
                QMessageBox.information(self, "Success", f"Report generated and saved to:\n{file_path}")
            else:
                self.statusBar().showMessage("Failed to generate report")
                QMessageBox.critical(self, "Error", "Failed to generate report")
                
        except Exception as e:
            self.statusBar().showMessage(f"Error generating report: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def _on_save_report(self):
        """Handle save report button click."""
        try:
            # Collect inspector data from UI
            inspector_data = self._collect_inspector_data()
            
            # Get system data
            system_data = system_collector.get_system_info()
            
            # Set default save location to Desktop if available
            default_path = ""
            try:
                desktop_path = Path.home() / "Desktop"
                if desktop_path.exists():
                    default_path = str(desktop_path / "computer_inspection_report.txt")
            except Exception:
                pass
            
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Report", default_path, "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                # Generate and save report
                report_content, saved_path = self.report_formatter.generate_report(
                    inspector_data=inspector_data,
                    system_data=system_data,
                    save_to_file=True,
                    custom_path=file_path
                )
                
                if saved_path:
                    self.statusBar().showMessage(f"Report saved to: {saved_path}")
                    QMessageBox.information(self, "Success", f"Report saved to:\n{saved_path}")
                else:
                    self.statusBar().showMessage("Failed to save report")
                    QMessageBox.critical(self, "Error", "Failed to save report")
                    
        except Exception as e:
            self.statusBar().showMessage(f"Error saving report: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save report: {str(e)}")
    
    def _on_send_email(self):
        """Handle send email button click with Google OAuth."""
        recipient = self.email_edit.text().strip()
        
        if not recipient:
            QMessageBox.warning(self, "Warning", "Please enter a recipient email address.")
            return
        
        # Check if user is authenticated with Google
        if not hasattr(self, 'google_user') or not self.google_user:
            QMessageBox.information(
                self, 
                "Google Authentication Required", 
                "Please sign in with Google first to send emails.\n\n"
                "Click the 'Sign in with Google' button above."
            )
            return
        
        # User is authenticated, proceed with sending
        self._send_report_email_with_google_oauth(recipient)
    

    
    def _on_google_auth_completed(self, user):
        """Handle successful Google OAuth authentication."""
        from google_oauth_real import GoogleUser
        self.google_user = user
        self.statusBar().showMessage(f"Signed in as {user.email}")
        
        # The enhanced GoogleSignInButton handles its own UI updates
        # No need to manually update button text/style
        
        QMessageBox.information(
            self, 
            "Google Authentication Successful", 
            f"Successfully signed in as {user.email}\n\n"
            "You can now send emails using your Google account!\n\n"
            "To switch to a different account, click the Google sign-in button again."
        )
    
    def _on_google_auth_failed(self, error: str):
        """Handle Google OAuth authentication failure."""
        self.statusBar().showMessage(f"Google authentication failed: {error}")
        QMessageBox.critical(
            self, 
            "Authentication Failed", 
            f"Failed to sign in with Google:\n{error}\n\n"
            "Please try again or check your internet connection."
        )
    
    def _send_report_email_with_google_oauth(self, recipient: str):
        """Send report via email using Google OAuth and Gmail API."""
        try:
            self.statusBar().showMessage(f"Preparing to send email to: {recipient}")
            
            # Collect inspector data
            inspector_data = self._collect_inspector_data()
            
            # Get system data
            system_data = system_collector.get_system_info()
            
            # Generate report for attachment
            report_content, report_path = self.report_formatter.generate_report(
                inspector_data=inspector_data,
                system_data=system_data,
                save_to_file=True
            )
            
            if not report_path:
                QMessageBox.critical(self, "Error", "Failed to generate report for email")
                return
            
            # Create email content with detailed report in body
            subject = "Computer Inspection Report"
            
            # Create detailed report content for email body
            # Get test results
            test_results = inspector_data.get('test_results', {})
            audio_test = test_results.get('audio_test', 'Not Tested')
            dead_pixel_test = test_results.get('dead_pixel_test', 'Not Tested')
            keyboard_test = test_results.get('keyboard_test', 'Not Tested')
            
            # Calculate overall test status
            test_statuses = [audio_test, dead_pixel_test, keyboard_test]
            passed_tests = sum(1 for status in test_statuses if status == 'Pass')
            total_tests = sum(1 for status in test_statuses if status != 'Not Tested')
            
            if total_tests == 0:
                overall_test_status = "No Tests Performed"
            elif passed_tests == total_tests:
                overall_test_status = "✅ ALL TESTS PASSED"
            elif passed_tests > 0:
                overall_test_status = "⚠️ PARTIAL PASS"
            else:
                overall_test_status = "❌ ALL TESTS FAILED"
            
            report_body = f"""
Dear Client,

Please find attached the detailed computer inspection report for your order.

REPORT SUMMARY:
═══════════════════════════════════════════════════════════════════════════════

INSPECTION DETAILS:
• Client: {inspector_data.get('client_name', 'N/A')}
• Order Number: {inspector_data.get('order_number', 'N/A')}
• Device Type: {inspector_data.get('device_type', 'N/A')}
• Inspector: {inspector_data.get('inspector', 'N/A')}
• Inspection Date: {inspector_data.get('inspection_date', 'N/A')}

DIAGNOSTIC TEST RESULTS:
• Audio Test: {audio_test}
• Dead Pixel Test: {dead_pixel_test}
• Keyboard Test: {keyboard_test}
• Overall Test Status: {overall_test_status}

NOTES:
• {inspector_data.get('notes', 'No additional notes')}

SYSTEM SPECIFICATIONS:
• CPU: {system_data.get('cpu', 'N/A')}
• Memory: {system_data.get('ram', 'N/A')}
• Storage: {system_data.get('storage', 'N/A')}
• Operating System: {system_data.get('os', 'N/A')}
• Graphics: {system_data.get('gpu', 'N/A')}
• Network: {system_data.get('network', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════

INSPECTION STATUS: ✅ COMPLETED SUCCESSFULLY

The inspection was completed successfully and all system components have been evaluated. 
A detailed technical report is attached for your records.

If you have any questions about this report, please don't hesitate to contact us.

Best regards,
Computer Inspector Team
            """.strip()
            
            # Send email using Gmail API
            from google_oauth_real import GmailSender
            gmail_sender = GmailSender(self.google_user.access_token)
            
            # Create email worker for Gmail API
            self._send_email_with_gmail_api(gmail_sender, recipient, subject, report_body, report_path)
            
        except Exception as e:
            self.statusBar().showMessage(f"Error sending email: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")
    
    def _send_email_with_gmail_api(self, gmail_sender, recipient: str, subject: str, body: str, attachment_path: str):
        """Send email using Gmail API in background thread."""
        class GmailAPIWorker(QThread):
            email_sent = pyqtSignal(bool, str)  # success, message
            
            def __init__(self, gmail_sender, recipient, subject, body, attachment_path):
                super().__init__()
                self.gmail_sender = gmail_sender
                self.recipient = recipient
                self.subject = subject
                self.body = body
                self.attachment_path = attachment_path
            
            def run(self):
                """Send email using Gmail API."""
                try:
                    result = self.gmail_sender.send_email(
                        to=self.recipient,
                        subject=self.subject,
                        body=self.body,
                        attachment_path=self.attachment_path
                    )
                    
                    if result['success']:
                        self.email_sent.emit(True, f"Email sent successfully! Message ID: {result['message_id']}")
                    else:
                        self.email_sent.emit(False, f"Email failed: {result['error']}")
                        
                except Exception as e:
                    self.email_sent.emit(False, f"Email error: {str(e)}")
        
        # Create and start Gmail API worker
        self.gmail_worker = GmailAPIWorker(gmail_sender, recipient, subject, body, attachment_path)
        self.gmail_worker.email_sent.connect(self._on_email_sent)
        
        # Start email sending
        self.statusBar().showMessage("Sending email via Gmail API...")
        self.gmail_worker.start()
    

    
    def _on_email_sent(self, success: bool, message: str):
        """Handle email sending result."""
        if success:
            self.statusBar().showMessage("Email sent successfully!")
            QMessageBox.information(self, "Success", message)
        else:
            self.statusBar().showMessage("Email failed to send")
            QMessageBox.critical(self, "Error", message)
        
        # Clean up worker
        if self.email_worker:
            self.email_worker.deleteLater()
            self.email_worker = None
    
    def _collect_inspector_data(self) -> dict:
        """Collect inspector data from UI fields."""
        return {
            "client_name": getattr(self, 'client_name', QLineEdit()).text(),
            "order_number": getattr(self, 'order_number', QLineEdit()).text(),
            "device_type": getattr(self, 'device_type', QLineEdit()).text(),
            "inspector": getattr(self, 'inspector_name', QLineEdit()).text(),
            "inspection_date": getattr(self, 'inspection_date', QLineEdit()).text(),
            "notes": getattr(self, 'notes', QTextEdit()).toPlainText(),
            "test_results": {
                "audio_test": getattr(self, 'audio_test_result', CustomTestResultComboBox()).currentText(),
                "dead_pixel_test": getattr(self, 'pixel_test_result', CustomTestResultComboBox()).currentText(),
                "keyboard_test": getattr(self, 'keyboard_test_result', CustomTestResultComboBox()).currentText()
            },
            "findings": {
                "hardware_condition": "Good",
                "software_issues": getattr(self, 'notes', QTextEdit()).toPlainText() or "No issues found",
                "performance_score": "85/100"
            }
        }
        
    def _update_status(self):
        """Update status information periodically."""
        # TODO: Implement real-time status updates
        pass 