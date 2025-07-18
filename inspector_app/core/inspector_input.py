"""
Inspector Input Module
Handles user input validation and processing for diagnostic operations.
"""

import re
import os
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum


class ScanType(Enum):
    """Types of diagnostic scans available."""
    QUICK = "quick"
    FULL = "full"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    NETWORK = "network"
    HARDWARE = "hardware"


class ReportFormat(Enum):
    """Available report formats."""
    HTML = "html"
    PDF = "pdf"
    TXT = "txt"
    JSON = "json"


@dataclass
class ScanConfiguration:
    """Configuration for diagnostic scans."""
    scan_types: List[ScanType]
    include_screenshots: bool = True
    include_charts: bool = True
    max_threads: int = 4
    timeout_seconds: int = 300


@dataclass
class ReportConfiguration:
    """Configuration for report generation."""
    title: str
    format: ReportFormat
    include_screenshots: bool = True
    include_charts: bool = True
    include_processes: bool = True
    include_network: bool = True


class InputValidator:
    """Validates user input for various operations."""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email address format."""
        if not email:
            return False, "Email address is required"
        
        # Basic email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email address format"
        
        return True, "Email address is valid"
    
    @staticmethod
    def validate_file_path(file_path: str) -> Tuple[bool, str]:
        """Validate file path for saving reports."""
        if not file_path:
            return False, "File path is required"
        
        # Check if directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            return False, f"Directory does not exist: {directory}"
        
        # Check if file is writable
        if os.path.exists(file_path):
            if not os.access(file_path, os.W_OK):
                return False, f"File is not writable: {file_path}"
        
        return True, "File path is valid"
    
    @staticmethod
    def validate_scan_config(config: ScanConfiguration) -> Tuple[bool, str]:
        """Validate scan configuration."""
        if not config.scan_types:
            return False, "At least one scan type must be selected"
        
        if config.max_threads < 1 or config.max_threads > 16:
            return False, "Max threads must be between 1 and 16"
        
        if config.timeout_seconds < 30 or config.timeout_seconds > 3600:
            return False, "Timeout must be between 30 and 3600 seconds"
        
        return True, "Scan configuration is valid"
    
    @staticmethod
    def validate_report_config(config: ReportConfiguration) -> Tuple[bool, str]:
        """Validate report configuration."""
        if not config.title.strip():
            return False, "Report title is required"
        
        if len(config.title) > 100:
            return False, "Report title must be less than 100 characters"
        
        return True, "Report configuration is valid"


class InputProcessor:
    """Processes and normalizes user input."""
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email address."""
        return email.strip().lower()
    
    @staticmethod
    def normalize_file_path(file_path: str) -> str:
        """Normalize file path."""
        return os.path.normpath(file_path.strip())
    
    @staticmethod
    def parse_scan_types(scan_checkboxes: Dict[str, bool]) -> List[ScanType]:
        """Parse scan types from checkbox states."""
        scan_types = []
        
        if scan_checkboxes.get('system', False):
            scan_types.append(ScanType.SYSTEM)
        if scan_checkboxes.get('performance', False):
            scan_types.append(ScanType.PERFORMANCE)
        if scan_checkboxes.get('security', False):
            scan_types.append(ScanType.SECURITY)
        if scan_checkboxes.get('network', False):
            scan_types.append(ScanType.NETWORK)
        if scan_checkboxes.get('hardware', False):
            scan_types.append(ScanType.HARDWARE)
        
        return scan_types
    
    @staticmethod
    def create_scan_configuration(
        scan_types: List[ScanType],
        include_screenshots: bool = True,
        include_charts: bool = True,
        max_threads: int = 4,
        timeout_seconds: int = 300
    ) -> ScanConfiguration:
        """Create scan configuration from parameters."""
        return ScanConfiguration(
            scan_types=scan_types,
            include_screenshots=include_screenshots,
            include_charts=include_charts,
            max_threads=max_threads,
            timeout_seconds=timeout_seconds
        )
    
    @staticmethod
    def create_report_configuration(
        title: str,
        format_str: str,
        include_screenshots: bool = True,
        include_charts: bool = True,
        include_processes: bool = True,
        include_network: bool = True
    ) -> ReportConfiguration:
        """Create report configuration from parameters."""
        try:
            report_format = ReportFormat(format_str.lower())
        except ValueError:
            report_format = ReportFormat.HTML  # Default to HTML
        
        return ReportConfiguration(
            title=title.strip(),
            format=report_format,
            include_screenshots=include_screenshots,
            include_charts=include_charts,
            include_processes=include_processes,
            include_network=include_network
        )


class InputManager:
    """Manages input validation and processing."""
    
    def __init__(self):
        self.validator = InputValidator()
        self.processor = InputProcessor()
    
    def validate_and_process_email(self, email: str) -> Tuple[bool, str, str]:
        """Validate and process email address."""
        normalized_email = self.processor.normalize_email(email)
        is_valid, message = self.validator.validate_email(normalized_email)
        return is_valid, message, normalized_email
    
    def validate_and_process_file_path(self, file_path: str) -> Tuple[bool, str, str]:
        """Validate and process file path."""
        normalized_path = self.processor.normalize_file_path(file_path)
        is_valid, message = self.validator.validate_file_path(normalized_path)
        return is_valid, message, normalized_path
    
    def validate_and_process_scan_config(
        self,
        scan_checkboxes: Dict[str, bool],
        include_screenshots: bool = True,
        include_charts: bool = True,
        max_threads: int = 4,
        timeout_seconds: int = 300
    ) -> Tuple[bool, str, ScanConfiguration]:
        """Validate and process scan configuration."""
        scan_types = self.processor.parse_scan_types(scan_checkboxes)
        config = self.processor.create_scan_configuration(
            scan_types, include_screenshots, include_charts, max_threads, timeout_seconds
        )
        is_valid, message = self.validator.validate_scan_config(config)
        return is_valid, message, config
    
    def validate_and_process_report_config(
        self,
        title: str,
        format_str: str,
        include_screenshots: bool = True,
        include_charts: bool = True,
        include_processes: bool = True,
        include_network: bool = True
    ) -> Tuple[bool, str, ReportConfiguration]:
        """Validate and process report configuration."""
        config = self.processor.create_report_configuration(
            title, format_str, include_screenshots, include_charts, include_processes, include_network
        )
        is_valid, message = self.validator.validate_report_config(config)
        return is_valid, message, config


# Global instance for easy access
input_manager = InputManager() 