"""
System Information Module
Provides comprehensive system information gathering capabilities.
"""

import platform
import psutil
from typing import Dict, List, Optional, Tuple


class SystemInfoCollector:
    """Collects and manages system information."""
    
    def __init__(self):
        self._cached_info = {}
        self._last_update = None
        
    def get_basic_system_info(self) -> Dict[str, str]:
        """Get basic system information."""
        try:
            return {
                'os_name': platform.system(),
                'os_version': platform.version(),
                'os_release': platform.release(),
                'architecture': platform.architecture()[0],
                'machine': platform.machine(),
                'processor': platform.processor(),
                'hostname': platform.node()
            }
        except Exception as e:
            return {
                'error': f"Failed to collect basic system info: {str(e)}"
            }
    
    def get_cpu_info(self) -> Dict[str, any]:
        """Get detailed CPU information."""
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'cpu_usage_percent': psutil.cpu_percent(interval=1),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                'cpu_stats': psutil.cpu_stats()._asdict()
            }
            return cpu_info
        except Exception as e:
            return {
                'error': f"Failed to collect CPU info: {str(e)}"
            }
    
    def get_memory_info(self) -> Dict[str, any]:
        """Get memory information."""
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'formatted_total': self._format_bytes(memory.total),
                'formatted_available': self._format_bytes(memory.available),
                'formatted_used': self._format_bytes(memory.used)
            }
        except Exception as e:
            return {
                'error': f"Failed to collect memory info: {str(e)}"
            }
    
    def get_disk_info(self) -> List[Dict[str, any]]:
        """Get disk information for all partitions."""
        try:
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent,
                        'formatted_total': self._format_bytes(usage.total),
                        'formatted_used': self._format_bytes(usage.used),
                        'formatted_free': self._format_bytes(usage.free)
                    })
                except PermissionError:
                    continue
            return disk_info
        except Exception as e:
            return [{'error': f"Failed to collect disk info: {str(e)}"}]
    
    def get_network_info(self) -> Dict[str, any]:
        """Get network interface information."""
        try:
            network_info = {
                'interfaces': {},
                'connections': []
            }
            
            # Network interfaces
            for interface, addresses in psutil.net_if_addrs().items():
                network_info['interfaces'][interface] = []
                for addr in addresses:
                    network_info['interfaces'][interface].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
            
            # Network connections
            for conn in psutil.net_connections():
                network_info['connections'].append({
                    'family': str(conn.family),
                    'type': str(conn.type),
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status
                })
            
            return network_info
        except Exception as e:
            return {
                'error': f"Failed to collect network info: {str(e)}"
            }
    
    def get_process_info(self) -> List[Dict[str, any]]:
        """Get information about running processes."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:20]  # Return top 20 processes
        except Exception as e:
            return [{'error': f"Failed to collect process info: {str(e)}"}]
    
    def get_system_uptime(self) -> Dict[str, any]:
        """Get system uptime information."""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = psutil.time.time() - boot_time
            return {
                'boot_time': boot_time,
                'uptime_seconds': uptime_seconds,
                'uptime_formatted': self._format_uptime(uptime_seconds)
            }
        except Exception as e:
            return {
                'error': f"Failed to collect uptime info: {str(e)}"
            }
    
    def get_comprehensive_system_info(self) -> Dict[str, any]:
        """Get all system information in one call."""
        return {
            'basic_info': self.get_basic_system_info(),
            'cpu_info': self.get_cpu_info(),
            'memory_info': self.get_memory_info(),
            'disk_info': self.get_disk_info(),
            'network_info': self.get_network_info(),
            'uptime_info': self.get_system_uptime(),
            'timestamp': psutil.time.time()
        }
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def refresh_cache(self):
        """Refresh cached system information."""
        self._cached_info = self.get_comprehensive_system_info()
        self._last_update = psutil.time.time()
    
    def get_cached_info(self) -> Dict[str, any]:
        """Get cached system information."""
        if not self._cached_info or not self._last_update:
            self.refresh_cache()
        return self._cached_info


# Global instance for easy access
system_collector = SystemInfoCollector() 