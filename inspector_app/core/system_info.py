"""
System Information Module
Provides comprehensive system information gathering capabilities.
"""

import platform
import psutil
import subprocess
import GPUtil
import screeninfo
from typing import Dict, List, Optional, Tuple


class SystemInfoCollector:
    """Collects and manages system information for computer inspection."""
    
    def __init__(self):
        self._cached_info = {}
        self._last_update = None
        
    def get_system_info(self) -> Dict[str, str]:
        """
        Get comprehensive system information for inspection.
        
        Returns:
            Dict containing system information with keys:
            - brand_model: Computer brand and model
            - cpu: CPU information
            - ram: Total RAM in GB
            - storage: Total storage in GB
            - gpu: GPU information
            - os: Operating system and version
            - display: Display resolution
            - touch_support: Touch screen support
            - fingerprint_reader: Fingerprint reader availability
            - battery_health: Battery health status
        """
        try:
            return {
                'brand_model': self._get_brand_model(),
                'cpu': self._get_cpu_info(),
                'ram': self._get_ram_info(),
                'storage': self._get_storage_info(),
                'gpu': self._get_gpu_info(),
                'os': self._get_os_info(),
                'display': self._get_display_info(),
                'touch_support': self._get_touch_support(),
                'fingerprint_reader': self._get_fingerprint_reader(),
                'battery_health': self._get_battery_health()
            }
        except Exception as e:
            # Return default values if collection fails
            return {
                'brand_model': 'N/A',
                'cpu': 'N/A',
                'ram': 'N/A',
                'storage': 'N/A',
                'gpu': 'N/A',
                'os': 'N/A',
                'display': 'N/A',
                'touch_support': 'N/A',
                'fingerprint_reader': 'N/A',
                'battery_health': 'N/A'
            }
    
    def _get_brand_model(self) -> str:
        """Get computer brand and model using PowerShell."""
        try:
            # Use Get-WmiObject instead of Get-CimInstance for better compatibility
            result = subprocess.run(
                ['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe', '-NoProfile', '-NonInteractive', '-Command', 
                 'Get-WmiObject -Class Win32_ComputerSystem | Select-Object Manufacturer, Model | ConvertTo-Csv -NoTypeInformation'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Parse CSV output: "Manufacturer","Model"
                    # Handle CSV with commas in manufacturer names
                    csv_line = lines[1].strip()
                    # Find the last comma to separate manufacturer and model
                    last_comma_index = csv_line.rfind(',')
                    if last_comma_index > 0:
                        manufacturer_part = csv_line[:last_comma_index].strip('"')
                        model_part = csv_line[last_comma_index + 1:].strip('"')
                        # Simplify manufacturer name
                        simplified_brand = self._simplify_brand_name(manufacturer_part)
                        
                        if simplified_brand and model_part:
                            return f"{simplified_brand} {model_part}"
                        elif model_part:
                            return model_part
                        elif simplified_brand:
                            return simplified_brand
            
            # Fallback to wmic if PowerShell fails
            result = subprocess.run(
                ['wmic', 'csproduct', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    model = lines[1].strip()
                    if model and model != "Name":
                        return model
            
            return "N/A"
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return "N/A"
    
    def _get_cpu_info(self) -> str:
        """Get CPU information using PowerShell to get proper processor name."""
        try:
            # Try PowerShell to get the actual processor name
            result = subprocess.run(
                ['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe', '-NoProfile', '-NonInteractive', '-Command', 
                 'Get-WmiObject -Class Win32_Processor | Select-Object Name | ConvertTo-Csv -NoTypeInformation'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Parse CSV output: "Name"
                    csv_line = lines[1].strip()
                    if csv_line.startswith('"') and csv_line.endswith('"'):
                        processor_name = csv_line[1:-1].strip()  # Remove quotes and extra spaces
                        if processor_name and processor_name != "Name":
                            return processor_name
            
            # Fallback to platform.processor()
            processor = platform.processor()
            if processor and processor != "":
                return processor
            
            # Final fallback to psutil for CPU info
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                return f"{cpu_count} cores @ {cpu_freq.current:.1f} GHz"
            else:
                return f"{cpu_count} cores"
        except Exception:
            return "N/A"
    
    def _get_ram_info(self) -> str:
        """Get total RAM in GB."""
        try:
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            return f"{total_gb:.1f} GB"
        except Exception:
            return "N/A"
    
    def _get_storage_info(self) -> str:
        """Get total storage in GB."""
        try:
            total_bytes = 0
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_bytes += usage.total
                except (PermissionError, FileNotFoundError):
                    continue
            
            if total_bytes > 0:
                total_gb = total_bytes / (1024**3)
                return f"{total_gb:.1f} GB"
            else:
                return "N/A"
        except Exception:
            return "N/A"
    
    def _get_gpu_info(self) -> str:
        """Get GPU information using PowerShell to get actual GPU names."""
        try:
            # Try PowerShell to get actual GPU names
            result = subprocess.run(
                ['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe', '-NoProfile', '-NonInteractive', '-Command', 
                 'Get-WmiObject -Class Win32_VideoController | Select-Object Name | ConvertTo-Csv -NoTypeInformation'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    gpu_names = []
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            # Parse CSV output: "Name"
                            if line.startswith('"') and line.endswith('"'):
                                gpu_name = line[1:-1].strip()  # Remove quotes and spaces
                                if gpu_name and gpu_name != "Name":
                                    gpu_names.append(gpu_name)
                    
                    if gpu_names:
                        return ", ".join(gpu_names)
            
            # Fallback to GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_names = []
                for gpu in gpus:
                    if gpu.name:
                        gpu_names.append(gpu.name)
                if gpu_names:
                    return ", ".join(gpu_names)
            
            # Final fallback
            return "Integrated Graphics"
        except Exception:
            return "N/A"
    
    def _get_os_info(self) -> str:
        """Get operating system and version using PowerShell."""
        try:
            # Try PowerShell to get accurate OS information
            result = subprocess.run(
                ['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe', '-NoProfile', '-NonInteractive', '-Command', 
                 'Get-WmiObject -Class Win32_OperatingSystem | Select-Object Caption, Version | ConvertTo-Csv -NoTypeInformation'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Parse CSV output: "Caption","Version"
                    csv_line = lines[1].strip()
                    if csv_line.startswith('"') and csv_line.endswith('"'):
                        # Extract caption (OS name)
                        parts = csv_line.split('","')
                        if len(parts) >= 2:
                            caption = parts[0].strip('"')
                            version = parts[1].strip('"')
                            if caption:
                                return caption
            
            # Fallback to platform
            system = platform.system()
            version = platform.version()
            release = platform.release()
            
            if system == "Windows":
                return f"Windows {release} {version}"
            elif system == "Linux":
                return f"Linux {release} {version}"
            elif system == "Darwin":
                return f"macOS {release} {version}"
            else:
                return f"{system} {release} {version}"
        except Exception:
            return "N/A"
    
    def _get_display_info(self) -> str:
        """Get display resolution using screeninfo."""
        try:
            monitors = screeninfo.get_monitors()
            if monitors:
                # Get primary monitor
                primary = monitors[0]
                return f"{primary.width}x{primary.height}"
            else:
                return "N/A"
        except Exception:
            return "N/A"
    
    def _get_touch_support(self) -> str:
        """Check for touch screen support using PowerShell."""
        try:
            # Try PowerShell command first
            result = subprocess.run(
                ['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe', '-NoProfile', '-NonInteractive', '-Command', 
                 'Get-WmiObject -Class Win32_TouchScreen | Measure-Object | Select-Object Count'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if output and "Count" in output:
                    # Parse the count
                    lines = output.split('\n')
                    for line in lines:
                        if 'Count' in line and line.strip() != 'Count':
                            count = line.strip()
                            if count.isdigit() and int(count) > 0:
                                return "Yes"
                    return "No"
            
            # Fallback to wmic
            result = subprocess.run(
                ['wmic', 'path', 'Win32_TouchScreen', 'get'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if output and len(output.split('\n')) > 1:
                    return "Yes"
                else:
                    return "No"
            else:
                return "No"
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return "N/A"
    
    def _get_fingerprint_reader(self) -> str:
        """Check for fingerprint reader in PnP devices."""
        try:
            # Try PowerShell command first
            result = subprocess.run(
                ['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe', '-NoProfile', '-NonInteractive', '-Command', 
                 'Get-WmiObject -Class Win32_PnPEntity | Where-Object {$_.Name -like "*fingerprint*"} | Measure-Object | Select-Object Count'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if output and "Count" in output:
                    # Parse the count
                    lines = output.split('\n')
                    for line in lines:
                        if 'Count' in line and line.strip() != 'Count':
                            count = line.strip()
                            if count.isdigit() and int(count) > 0:
                                return "Yes"
                    return "No"
            
            # Fallback to wmic
            result = subprocess.run(
                ['wmic', 'path', 'Win32_PnPEntity', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                output = result.stdout.lower()
                if "fingerprint" in output:
                    return "Yes"
                else:
                    return "No"
            else:
                return "No"
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return "N/A"
    
    def _get_battery_health(self) -> str:
        """Get battery health using psutil."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                if battery.percent is not None:
                    return f"{battery.percent:.0f}%"
                else:
                    return "Connected"
            else:
                return "N/A"
        except Exception:
            return "N/A"
    
    def refresh_info(self):
        """Refresh system information cache."""
        self._cached_info = self.get_system_info()
        self._last_update = psutil.time.time()
    
    def get_cached_info(self) -> Dict[str, str]:
        """Get cached system information."""
        if not self._cached_info:
            self.refresh_info()
        return self._cached_info
    
    def _simplify_brand_name(self, manufacturer: str) -> str:
        """Simplify manufacturer names to common brand names."""
        if not manufacturer:
            return ""
        
        manufacturer_lower = manufacturer.lower()
        
        # Common brand mappings
        brand_mappings = {
            "micro-star international": "MSI",
            "micro-star": "MSI",
            "dell": "Dell",
            "hewlett-packard": "HP",
            "hp": "HP",
            "lenovo": "Lenovo",
            "asus": "ASUS",
            "acer": "Acer",
            "toshiba": "Toshiba",
            "samsung": "Samsung",
            "apple": "Apple",
            "microsoft": "Microsoft",
            "gigabyte": "Gigabyte",
            "msi": "MSI"
        }
        
        # Check for exact matches first
        for key, value in brand_mappings.items():
            if key in manufacturer_lower:
                return value
        
        # If no match found, return the original manufacturer
        return manufacturer


# Global instance for easy access
system_collector = SystemInfoCollector() 