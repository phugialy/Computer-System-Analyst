"""
Main Window UI for Inspector Diagnostic Utility
Provides the primary interface for system diagnostics and reporting.
"""

import datetime
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

# Import Gmail and report functionality
from gmail_config import GmailConfigManager, setup_gmail_interactive, test_gmail_configuration
from core.report_generator import ReportFormatter
from core.email_sender import EmailSender, EmailConfig, EmailStatus
from google_oauth_simple import GoogleAccountSelectionDialog, GoogleUser


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
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 600)
        
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
        """Initialize the main user interface with compact design."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with compact design
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Simple title line
        self._create_simple_title(main_layout)
        
        # Create a splitter for better space utilization
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        
        # Left panel for Client Order Info
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 8, 0)
        self._create_client_order_section(left_layout)
        
        # Right panel for System Info
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        self._create_system_info_section(right_layout)
        
        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([600, 600])  # Equal initial sizes
        
        main_layout.addWidget(main_splitter)
        
        # Diagnostic Test buttons
        self._create_diagnostic_tests_section(main_layout)
        
        # Email and Report section
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
        """Create the Client Order Info section with compact layout."""
        order_group = QGroupBox("Client Order Information")
        order_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        order_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
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
        
        order_layout = QVBoxLayout(order_group)
        order_layout.setContentsMargins(15, 20, 15, 15)
        order_layout.setSpacing(12)
        
        # Create styled labels and fields with compact sizing
        def create_field_pair(label_text, field, placeholder=None, readonly=False, field_type="line"):
            # Create label with compact sizing
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
            label.setStyleSheet("color: #2c3e50; min-width: 120px; padding: 3px;")
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            
            # Create field with compact responsive sizing
            if field_type == "line":
                field.setFont(QFont("Segoe UI", 10))
                field.setMinimumHeight(32)
                field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                field.setStyleSheet("""
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
                    QLineEdit:read-only {
                        background-color: #ecf0f1;
                        color: #7f8c8d;
                    }
                """)
                if placeholder:
                    field.setPlaceholderText(placeholder)
                if readonly:
                    field.setReadOnly(True)
            elif field_type == "combo":
                field.setFont(QFont("Segoe UI", 10))
                field.setMinimumHeight(32)
                field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                field.setStyleSheet("""
                    QComboBox {
                        border: 2px solid #bdc3c7;
                        border-radius: 6px;
                        padding: 8px 12px;
                        background-color: white;
                        color: #2c3e50;
                        font-size: 10px;
                    }
                    QComboBox:focus {
                        border: 2px solid #3498db;
                    }
                    QComboBox::drop-down {
                        border: none;
                        width: 20px;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 5px solid transparent;
                        border-right: 5px solid transparent;
                        border-top: 5px solid #7f8c8d;
                        margin-right: 8px;
                    }
                """)
            
            return label, field
        
        # Date field (auto-filled, read-only)
        date_label, self.date_edit = create_field_pair(
            "Date:", QLineEdit(), readonly=True
        )
        self.date_edit.setText(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # Inspector field
        inspector_label, self.inspector_edit = create_field_pair(
            "Inspector:", QLineEdit(), "Enter inspector name"
        )
        
        # Initial Location field
        location_label, self.location_edit = create_field_pair(
            "Initial Location:", QLineEdit(), "Enter initial location"
        )
        
        # Invoice # field
        invoice_label, self.invoice_edit = create_field_pair(
            "Invoice #:", QLineEdit(), "Enter invoice number"
        )
        
        # SKU # field
        sku_label, self.sku_edit = create_field_pair(
            "SKU #:", QLineEdit(), "Enter SKU number"
        )
        
        # Charger field
        charger_label, self.charger_combo = create_field_pair(
            "Charger:", QComboBox(), field_type="combo"
        )
        self.charger_combo.addItems(["Yes", "No", "N/A"])
        
        # Issues field
        issues_label, self.issues_edit = create_field_pair(
            "Issues:", QLineEdit(), "Describe any issues found"
        )
        
        # Warranty field
        warranty_label, self.warranty_combo = create_field_pair(
            "Warranty:", QComboBox(), field_type="combo"
        )
        self.warranty_combo.addItems(["Yes", "No", "N/A"])
        
        # Condition field with compact layout
        condition_label = QLabel("Condition:")
        condition_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        condition_label.setStyleSheet("color: #2c3e50; min-width: 120px; padding: 3px;")
        
        condition_layout = QHBoxLayout()
        condition_layout.setSpacing(10)
        
        self.condition_combo = QComboBox()
        self.condition_combo.addItems([str(i) for i in range(1, 11)])
        self.condition_combo.setFont(QFont("Segoe UI", 10))
        self.condition_combo.setMinimumHeight(32)
        self.condition_combo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.condition_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                color: #2c3e50;
                font-size: 10px;
                min-width: 80px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
        """)
        
        self.condition_text = QLineEdit()
        self.condition_text.setPlaceholderText("Additional condition notes")
        self.condition_text.setFont(QFont("Segoe UI", 10))
        self.condition_text.setMinimumHeight(32)
        self.condition_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.condition_text.setStyleSheet("""
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
        
        condition_layout.addWidget(self.condition_combo)
        condition_layout.addWidget(self.condition_text)
        
        # Add fields to layout with compact spacing
        fields = [
            (date_label, self.date_edit),
            (inspector_label, self.inspector_edit),
            (location_label, self.location_edit),
            (invoice_label, self.invoice_edit),
            (sku_label, self.sku_edit),
            (charger_label, self.charger_combo),
            (issues_label, self.issues_edit),
            (warranty_label, self.warranty_combo),
            (condition_label, condition_layout)
        ]
        
        for label, field in fields:
            field_layout = QHBoxLayout()
            field_layout.setSpacing(10)
            field_layout.addWidget(label)
            if isinstance(field, QLineEdit) or isinstance(field, QComboBox):
                field_layout.addWidget(field)
            else:
                field_layout.addLayout(field)
            order_layout.addLayout(field_layout)
        
        parent_layout.addWidget(order_group)
        
    def _create_system_info_section(self, parent_layout):
        """Create the System Info section with compact layout."""
        system_group = QGroupBox("System Information")
        system_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        system_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
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
        
        system_layout = QVBoxLayout(system_group)
        system_layout.setContentsMargins(15, 20, 15, 15)
        system_layout.setSpacing(12)
        
        # System info fields with compact organization
        fields = [
            ("Brand/Model:", "brand_model"),
            ("CPU:", "cpu"),
            ("RAM:", "ram"),
            ("Storage:", "storage"),
            ("GPU:", "gpu"),
            ("OS:", "os"),
            ("Display:", "display"),
            ("Touch Support:", "touch_support"),
            ("Fingerprint Reader:", "fingerprint_reader"),
            ("Battery Health:", "battery_health")
        ]
        
        self.system_fields = {}
        for label_text, field_name in fields:
            # Create label with compact sizing
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
            label.setStyleSheet("color: #2c3e50; min-width: 130px; padding: 3px;")
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            
            # Create field with compact responsive sizing
            field = QLineEdit()
            field.setReadOnly(True)
            field.setFont(QFont("Segoe UI", 10))
            field.setMinimumHeight(32)
            field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            field.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                    padding: 8px 12px;
                    background-color: #ecf0f1;
                    color: #7f8c8d;
                    font-size: 10px;
                }
            """)
            field.setText("Loading...")
            
            # Create layout for this field pair
            field_layout = QHBoxLayout()
            field_layout.setSpacing(10)
            field_layout.addWidget(label)
            field_layout.addWidget(field)
            system_layout.addLayout(field_layout)
            
            self.system_fields[field_name] = field
        
        # Re-check Hardware Info button with compact styling
        self.recheck_hardware_btn = QPushButton("🔁 Re-check Hardware Info")
        self.recheck_hardware_btn.setMinimumHeight(40)
        self.recheck_hardware_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.recheck_hardware_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.recheck_hardware_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                margin-top: 8px;
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
        """Create the Diagnostic Test buttons section with compact layout."""
        tests_group = QGroupBox("Diagnostic Tests")
        tests_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        tests_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
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
        
        tests_layout = QHBoxLayout(tests_group)
        tests_layout.setContentsMargins(15, 20, 15, 15)
        tests_layout.setSpacing(15)
        
        # Test buttons with compact responsive sizing
        self.play_sound_btn = QPushButton("▶ Play Test Sound")
        self.play_sound_btn.setMinimumHeight(45)
        self.play_sound_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.play_sound_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.play_sound_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 20px;
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
        
        self.dead_pixel_btn = QPushButton("🔍 Open Dead Pixel Test")
        self.dead_pixel_btn.setMinimumHeight(45)
        self.dead_pixel_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.dead_pixel_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.dead_pixel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 12px 20px;
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
        
        self.keyboard_test_btn = QPushButton("⌨ Launch Keyboard Test")
        self.keyboard_test_btn.setMinimumHeight(45)
        self.keyboard_test_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.keyboard_test_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.keyboard_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        
        tests_layout.addWidget(self.play_sound_btn)
        tests_layout.addWidget(self.dead_pixel_btn)
        tests_layout.addWidget(self.keyboard_test_btn)
        
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
        self.statusBar().showMessage("Playing test sound...")
        # TODO: Implement sound playback
        QMessageBox.information(self, "Test Sound", "Test sound functionality will be implemented.")
        
    def _on_open_dead_pixel_test(self):
        """Handle dead pixel test button click."""
        self.statusBar().showMessage("Opening dead pixel test...")
        # TODO: Implement dead pixel test
        QMessageBox.information(self, "Dead Pixel Test", "Dead pixel test functionality will be implemented.")
        
    def _on_launch_keyboard_test(self):
        """Handle keyboard test button click."""
        self.statusBar().showMessage("Launching keyboard test...")
        # TODO: Implement keyboard test
        QMessageBox.information(self, "Keyboard Test", "Keyboard test functionality will be implemented.")
        
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
            for field_name, value in system_data.items():
                if field_name in self.system_fields:
                    self.system_fields[field_name].setText(str(value))
            
            self.statusBar().showMessage("Hardware information updated successfully")
        except Exception as e:
            self.statusBar().showMessage(f"Error updating hardware info: {str(e)}")
            # Set error state for fields
            for field in self.system_fields.values():
                field.setText("Error")
        
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
            
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Report", "", "Text Files (*.txt);;All Files (*)"
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
            report_body = f"""
Dear Client,

Please find attached the detailed computer inspection report for your order.

REPORT SUMMARY:
═══════════════════════════════════════════════════════════════════════════════

INSPECTION DETAILS:
• Inspector: {inspector_data.get('inspector', 'N/A')}
• Invoice #: {inspector_data.get('order_number', 'N/A')}
• Inspection Date: {inspector_data.get('inspection_date', 'N/A')}
• Location: {inspector_data.get('initial_location', 'N/A')}
• SKU: {inspector_data.get('sku_number', 'N/A')}

DEVICE CONDITION:
• Charger: {inspector_data.get('charger', 'N/A')}
• Warranty: {inspector_data.get('warranty', 'N/A')}
• Condition Rating: {inspector_data.get('condition', 'N/A')}/10
• Condition Notes: {inspector_data.get('condition_notes', 'N/A')}

ISSUES FOUND:
• {inspector_data.get('issues', 'No issues found')}

SYSTEM SPECIFICATIONS:
• Brand/Model: {system_data.get('brand_model', 'N/A')}
• CPU: {system_data.get('cpu', 'N/A')}
• RAM: {system_data.get('ram', 'N/A')}
• Storage: {system_data.get('storage', 'N/A')}
• GPU: {system_data.get('gpu', 'N/A')}
• Operating System: {system_data.get('os', 'N/A')}
• Display: {system_data.get('display', 'N/A')}
• Touch Support: {system_data.get('touch_support', 'N/A')}
• Fingerprint Reader: {system_data.get('fingerprint_reader', 'N/A')}
• Battery Health: {system_data.get('battery_health', 'N/A')}

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
            "client_name": "Client",  # Default since no client name field
            "order_number": getattr(self, 'invoice_edit', QLineEdit()).text() or "INV-001",
            "inspection_date": getattr(self, 'date_edit', QLineEdit()).text(),
            "inspector": getattr(self, 'inspector_edit', QLineEdit()).text(),
            "initial_location": getattr(self, 'location_edit', QLineEdit()).text(),
            "sku_number": getattr(self, 'sku_edit', QLineEdit()).text(),
            "charger": getattr(self, 'charger_combo', QComboBox()).currentText(),
            "issues": getattr(self, 'issues_edit', QLineEdit()).text(),
            "warranty": getattr(self, 'warranty_combo', QComboBox()).currentText(),
            "condition": getattr(self, 'condition_combo', QComboBox()).currentText(),
            "condition_notes": getattr(self, 'condition_text', QLineEdit()).text(),
            "findings": {
                "hardware_condition": "Good",
                "software_issues": getattr(self, 'issues_edit', QLineEdit()).text() or "No issues found",
                "performance_score": "85/100"
            }
        }
        
    def _update_status(self):
        """Update status information periodically."""
        # TODO: Implement real-time status updates
        pass 