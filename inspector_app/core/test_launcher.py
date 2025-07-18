"""
Test Launcher Module
Handles running diagnostic tests and system validations.
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from .system_info import system_collector


class TestStatus(Enum):
    """Status of diagnostic tests."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestCategory(Enum):
    """Categories of diagnostic tests."""
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    NETWORK = "network"
    HARDWARE = "hardware"


@dataclass
class TestResult:
    """Result of a diagnostic test."""
    test_name: str
    category: TestCategory
    status: TestStatus
    duration: float
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DiagnosticTest:
    """Base class for diagnostic tests."""
    
    def __init__(self, name: str, category: TestCategory):
        self.name = name
        self.category = category
        self.description = ""
        self.timeout = 30  # seconds
    
    def run(self) -> TestResult:
        """Run the diagnostic test."""
        start_time = time.time()
        
        try:
            result = self._execute()
            duration = time.time() - start_time
            
            return TestResult(
                test_name=self.name,
                category=self.category,
                status=TestStatus.PASSED,
                duration=duration,
                message=result.get('message', 'Test completed successfully'),
                details=result.get('details')
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return TestResult(
                test_name=self.name,
                category=self.category,
                status=TestStatus.FAILED,
                duration=duration,
                message=f"Test failed: {str(e)}",
                error=str(e)
            )
    
    def _execute(self) -> Dict[str, Any]:
        """Execute the test logic. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _execute")


class SystemInfoTest(DiagnosticTest):
    """Test for basic system information collection."""
    
    def __init__(self):
        super().__init__("System Information", TestCategory.SYSTEM)
        self.description = "Collects basic system information"
    
    def _execute(self) -> Dict[str, Any]:
        system_info = system_collector.get_basic_system_info()
        
        if 'error' in system_info:
            raise Exception(system_info['error'])
        
        return {
            'message': f"System info collected: {system_info.get('os_name', 'Unknown')}",
            'details': system_info
        }


class CPUPerformanceTest(DiagnosticTest):
    """Test for CPU performance metrics."""
    
    def __init__(self):
        super().__init__("CPU Performance", TestCategory.PERFORMANCE)
        self.description = "Measures CPU usage and performance"
    
    def _execute(self) -> Dict[str, Any]:
        cpu_info = system_collector.get_cpu_info()
        
        if 'error' in cpu_info:
            raise Exception(cpu_info['error'])
        
        usage = cpu_info.get('cpu_usage_percent', 0)
        cores = cpu_info.get('logical_cores', 0)
        
        return {
            'message': f"CPU usage: {usage:.1f}%, Cores: {cores}",
            'details': cpu_info
        }


class MemoryTest(DiagnosticTest):
    """Test for memory usage and health."""
    
    def __init__(self):
        super().__init__("Memory Health", TestCategory.PERFORMANCE)
        self.description = "Checks memory usage and health"
    
    def _execute(self) -> Dict[str, Any]:
        memory_info = system_collector.get_memory_info()
        
        if 'error' in memory_info:
            raise Exception(memory_info['error'])
        
        usage = memory_info.get('percent', 0)
        total = memory_info.get('formatted_total', 'Unknown')
        
        return {
            'message': f"Memory usage: {usage:.1f}%, Total: {total}",
            'details': memory_info
        }


class DiskHealthTest(DiagnosticTest):
    """Test for disk health and usage."""
    
    def __init__(self):
        super().__init__("Disk Health", TestCategory.HARDWARE)
        self.description = "Checks disk health and usage"
    
    def _execute(self) -> Dict[str, Any]:
        disk_info = system_collector.get_disk_info()
        
        if not disk_info or 'error' in disk_info[0]:
            raise Exception(disk_info[0].get('error', 'Failed to get disk info'))
        
        total_disks = len(disk_info)
        high_usage_disks = [d for d in disk_info if d.get('percent', 0) > 90]
        
        return {
            'message': f"Found {total_disks} disk(s), {len(high_usage_disks)} with high usage",
            'details': disk_info
        }


class NetworkConnectivityTest(DiagnosticTest):
    """Test for network connectivity."""
    
    def __init__(self):
        super().__init__("Network Connectivity", TestCategory.NETWORK)
        self.description = "Tests network connectivity and interfaces"
    
    def _execute(self) -> Dict[str, Any]:
        network_info = system_collector.get_network_info()
        
        if 'error' in network_info:
            raise Exception(network_info['error'])
        
        interfaces = len(network_info.get('interfaces', {}))
        connections = len(network_info.get('connections', []))
        
        return {
            'message': f"Network interfaces: {interfaces}, Active connections: {connections}",
            'details': network_info
        }


class TestLauncher:
    """Launches and manages diagnostic tests."""
    
    def __init__(self):
        self.tests = self._initialize_tests()
        self.results = []
        self.is_running = False
        self.progress_callback = None
    
    def _initialize_tests(self) -> List[DiagnosticTest]:
        """Initialize available diagnostic tests."""
        return [
            SystemInfoTest(),
            CPUPerformanceTest(),
            MemoryTest(),
            DiskHealthTest(),
            NetworkConnectivityTest()
        ]
    
    def run_all_tests(self, progress_callback: Optional[Callable] = None) -> List[TestResult]:
        """Run all available diagnostic tests."""
        self.is_running = True
        self.results = []
        self.progress_callback = progress_callback
        
        try:
            total_tests = len(self.tests)
            
            for i, test in enumerate(self.tests):
                if not self.is_running:
                    break
                
                # Update progress
                if self.progress_callback:
                    progress = (i / total_tests) * 100
                    self.progress_callback(progress, f"Running {test.name}...")
                
                # Run test
                result = test.run()
                self.results.append(result)
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.1)
            
            # Final progress update
            if self.progress_callback:
                self.progress_callback(100, "All tests completed")
            
            return self.results
            
        finally:
            self.is_running = False
    
    def run_tests_by_category(self, categories: List[TestCategory]) -> List[TestResult]:
        """Run tests for specific categories."""
        filtered_tests = [test for test in self.tests if test.category in categories]
        
        results = []
        for test in filtered_tests:
            result = test.run()
            results.append(result)
        
        return results
    
    def run_single_test(self, test_name: str) -> Optional[TestResult]:
        """Run a single test by name."""
        for test in self.tests:
            if test.name == test_name:
                return test.run()
        return None
    
    def stop_tests(self):
        """Stop running tests."""
        self.is_running = False
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test results."""
        if not self.results:
            return {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'success_rate': 0.0
            }
        
        total = len(self.results)
        passed = len([r for r in self.results if r.status == TestStatus.PASSED])
        failed = len([r for r in self.results if r.status == TestStatus.FAILED])
        skipped = len([r for r in self.results if r.status == TestStatus.SKIPPED])
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'success_rate': (passed / total) * 100 if total > 0 else 0.0
        }
    
    def get_failed_tests(self) -> List[TestResult]:
        """Get list of failed tests."""
        return [result for result in self.results if result.status == TestStatus.FAILED]
    
    def get_tests_by_category(self, category: TestCategory) -> List[TestResult]:
        """Get test results for a specific category."""
        return [result for result in self.results if result.category == category]


class AsyncTestRunner:
    """Runs tests asynchronously with progress updates."""
    
    def __init__(self, test_launcher: TestLauncher):
        self.test_launcher = test_launcher
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.futures = []
    
    def run_tests_async(self, progress_callback: Callable) -> List[TestResult]:
        """Run tests asynchronously with progress updates."""
        total_tests = len(self.test_launcher.tests)
        completed = 0
        results = []
        
        # Submit all tests
        for test in self.test_launcher.tests:
            future = self.executor.submit(test.run)
            self.futures.append(future)
        
        # Collect results as they complete
        for future in as_completed(self.futures):
            result = future.result()
            results.append(result)
            completed += 1
            
            # Update progress
            progress = (completed / total_tests) * 100
            progress_callback(progress, f"Completed {completed}/{total_tests} tests")
        
        return results
    
    def cancel_all(self):
        """Cancel all running tests."""
        for future in self.futures:
            future.cancel()
        self.executor.shutdown(wait=False)


# Global instance for easy access
test_launcher = TestLauncher() 