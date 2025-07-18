"""
Report Generator Module
Handles generation of diagnostic reports in various formats.
"""

import os
import json
import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from .system_info import system_collector
from .inspector_input import ReportConfiguration, ReportFormat


class ReportStatus(Enum):
    """Status of report generation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ReportResult:
    """Result of report generation."""
    status: ReportStatus
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    generation_time: Optional[float] = None
    file_size: Optional[int] = None


class ReportGenerator:
    """Generates diagnostic reports in various formats."""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.output_dir = Path.home() / "InspectorReports"
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_report(
        self,
        config: ReportConfiguration,
        system_data: Optional[Dict[str, Any]] = None
    ) -> ReportResult:
        """Generate a diagnostic report based on configuration."""
        start_time = datetime.datetime.now()
        
        try:
            # Collect system data if not provided
            if system_data is None:
                system_data = system_collector.get_comprehensive_system_info()
            
            # Generate report based on format
            if config.format == ReportFormat.HTML:
                return self._generate_html_report(config, system_data, start_time)
            elif config.format == ReportFormat.PDF:
                return self._generate_pdf_report(config, system_data, start_time)
            elif config.format == ReportFormat.TXT:
                return self._generate_text_report(config, system_data, start_time)
            elif config.format == ReportFormat.JSON:
                return self._generate_json_report(config, system_data, start_time)
            else:
                return ReportResult(
                    status=ReportStatus.FAILED,
                    error_message=f"Unsupported report format: {config.format}"
                )
                
        except Exception as e:
            return ReportResult(
                status=ReportStatus.FAILED,
                error_message=f"Report generation failed: {str(e)}"
            )
    
    def _generate_html_report(
        self,
        config: ReportConfiguration,
        system_data: Dict[str, Any],
        start_time: datetime.datetime
    ) -> ReportResult:
        """Generate HTML report."""
        try:
            # Create HTML content
            html_content = self._create_html_content(config, system_data)
            
            # Generate filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_report_{timestamp}.html"
            file_path = self.output_dir / filename
            
            # Write HTML file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            generation_time = (datetime.datetime.now() - start_time).total_seconds()
            file_size = file_path.stat().st_size
            
            return ReportResult(
                status=ReportStatus.COMPLETED,
                file_path=str(file_path),
                generation_time=generation_time,
                file_size=file_size
            )
            
        except Exception as e:
            return ReportResult(
                status=ReportStatus.FAILED,
                error_message=f"HTML report generation failed: {str(e)}"
            )
    
    def _generate_pdf_report(
        self,
        config: ReportConfiguration,
        system_data: Dict[str, Any],
        start_time: datetime.datetime
    ) -> ReportResult:
        """Generate PDF report."""
        try:
            # For now, create a simple text-based PDF
            # In a real implementation, you would use a library like reportlab or weasyprint
            
            # Create text content first
            text_content = self._create_text_content(config, system_data)
            
            # Generate filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_report_{timestamp}.pdf"
            file_path = self.output_dir / filename
            
            # For now, just create a placeholder file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"PDF Report: {config.title}\n")
                f.write(f"Generated: {datetime.datetime.now()}\n")
                f.write("PDF generation not yet implemented.\n")
                f.write(text_content)
            
            generation_time = (datetime.datetime.now() - start_time).total_seconds()
            file_size = file_path.stat().st_size
            
            return ReportResult(
                status=ReportStatus.COMPLETED,
                file_path=str(file_path),
                generation_time=generation_time,
                file_size=file_size
            )
            
        except Exception as e:
            return ReportResult(
                status=ReportStatus.FAILED,
                error_message=f"PDF report generation failed: {str(e)}"
            )
    
    def _generate_text_report(
        self,
        config: ReportConfiguration,
        system_data: Dict[str, Any],
        start_time: datetime.datetime
    ) -> ReportResult:
        """Generate text report."""
        try:
            # Create text content
            text_content = self._create_text_content(config, system_data)
            
            # Generate filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_report_{timestamp}.txt"
            file_path = self.output_dir / filename
            
            # Write text file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            generation_time = (datetime.datetime.now() - start_time).total_seconds()
            file_size = file_path.stat().st_size
            
            return ReportResult(
                status=ReportStatus.COMPLETED,
                file_path=str(file_path),
                generation_time=generation_time,
                file_size=file_size
            )
            
        except Exception as e:
            return ReportResult(
                status=ReportStatus.FAILED,
                error_message=f"Text report generation failed: {str(e)}"
            )
    
    def _generate_json_report(
        self,
        config: ReportConfiguration,
        system_data: Dict[str, Any],
        start_time: datetime.datetime
    ) -> ReportResult:
        """Generate JSON report."""
        try:
            # Create JSON content
            json_data = self._create_json_content(config, system_data)
            
            # Generate filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_report_{timestamp}.json"
            file_path = self.output_dir / filename
            
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, default=str)
            
            generation_time = (datetime.datetime.now() - start_time).total_seconds()
            file_size = file_path.stat().st_size
            
            return ReportResult(
                status=ReportStatus.COMPLETED,
                file_path=str(file_path),
                generation_time=generation_time,
                file_size=file_size
            )
            
        except Exception as e:
            return ReportResult(
                status=ReportStatus.FAILED,
                error_message=f"JSON report generation failed: {str(e)}"
            )
    
    def _create_html_content(self, config: ReportConfiguration, system_data: Dict[str, Any]) -> str:
        """Create HTML content for the report."""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #1976D2; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: flex; justify-content: space-between; margin: 10px 0; }}
        .progress-bar {{ width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background-color: #4CAF50; transition: width 0.3s; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{config.title}</h1>
        <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>System Overview</h2>
        <div class="metric">
            <span>Operating System:</span>
            <span>{system_data.get('basic_info', {}).get('os_name', 'Unknown')} {system_data.get('basic_info', {}).get('os_release', '')}</span>
        </div>
        <div class="metric">
            <span>CPU:</span>
            <span>{system_data.get('basic_info', {}).get('processor', 'Unknown')}</span>
        </div>
        <div class="metric">
            <span>Architecture:</span>
            <span>{system_data.get('basic_info', {}).get('architecture', 'Unknown')}</span>
        </div>
    </div>
    
    <div class="section">
        <h2>Performance Metrics</h2>
        <div class="metric">
            <span>CPU Usage:</span>
            <span>{system_data.get('cpu_info', {}).get('cpu_usage_percent', 0):.1f}%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {system_data.get('cpu_info', {}).get('cpu_usage_percent', 0)}%"></div>
        </div>
        
        <div class="metric">
            <span>Memory Usage:</span>
            <span>{system_data.get('memory_info', {}).get('percent', 0):.1f}%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {system_data.get('memory_info', {}).get('percent', 0)}%"></div>
        </div>
    </div>
    
    <div class="section">
        <h2>System Information</h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Hostname</td><td>{system_data.get('basic_info', {}).get('hostname', 'Unknown')}</td></tr>
            <tr><td>Machine</td><td>{system_data.get('basic_info', {}).get('machine', 'Unknown')}</td></tr>
            <tr><td>Physical Cores</td><td>{system_data.get('cpu_info', {}).get('physical_cores', 'Unknown')}</td></tr>
            <tr><td>Logical Cores</td><td>{system_data.get('cpu_info', {}).get('logical_cores', 'Unknown')}</td></tr>
        </table>
    </div>
</body>
</html>
        """
        return html_template
    
    def _create_text_content(self, config: ReportConfiguration, system_data: Dict[str, Any]) -> str:
        """Create text content for the report."""
        text_content = f"""
{config.title}
{'=' * len(config.title)}

Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SYSTEM OVERVIEW
{'-' * 20}
Operating System: {system_data.get('basic_info', {}).get('os_name', 'Unknown')} {system_data.get('basic_info', {}).get('os_release', '')}
CPU: {system_data.get('basic_info', {}).get('processor', 'Unknown')}
Architecture: {system_data.get('basic_info', {}).get('architecture', 'Unknown')}
Hostname: {system_data.get('basic_info', {}).get('hostname', 'Unknown')}

PERFORMANCE METRICS
{'-' * 20}
CPU Usage: {system_data.get('cpu_info', {}).get('cpu_usage_percent', 0):.1f}%
Memory Usage: {system_data.get('memory_info', {}).get('percent', 0):.1f}%
Memory Total: {system_data.get('memory_info', {}).get('formatted_total', 'Unknown')}
Memory Used: {system_data.get('memory_info', {}).get('formatted_used', 'Unknown')}

SYSTEM DETAILS
{'-' * 20}
Physical Cores: {system_data.get('cpu_info', {}).get('physical_cores', 'Unknown')}
Logical Cores: {system_data.get('cpu_info', {}).get('logical_cores', 'Unknown')}
Machine: {system_data.get('basic_info', {}).get('machine', 'Unknown')}

DISK INFORMATION
{'-' * 20}
"""
        
        # Add disk information
        for disk in system_data.get('disk_info', []):
            if 'error' not in disk:
                text_content += f"""
Device: {disk.get('device', 'Unknown')}
Mountpoint: {disk.get('mountpoint', 'Unknown')}
Filesystem: {disk.get('filesystem', 'Unknown')}
Total: {disk.get('formatted_total', 'Unknown')}
Used: {disk.get('formatted_used', 'Unknown')}
Free: {disk.get('formatted_free', 'Unknown')}
Usage: {disk.get('percent', 0):.1f}%

"""
        
        return text_content
    
    def _create_json_content(self, config: ReportConfiguration, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create JSON content for the report."""
        return {
            'report_info': {
                'title': config.title,
                'format': config.format.value,
                'generated_at': datetime.datetime.now().isoformat(),
                'include_screenshots': config.include_screenshots,
                'include_charts': config.include_charts
            },
            'system_data': system_data
        }


# Global instance for easy access
report_generator = ReportGenerator() 