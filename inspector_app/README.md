# Computer Device Inspection App

A comprehensive desktop application for inspecting and documenting computer hardware specifications and condition.

## Features

### System Information Collection
- **Brand/Model**: Automatically detects computer brand and model using WMIC
- **CPU**: Processor information with core count and frequency
- **RAM**: Total system memory in GB
- **Storage**: Total storage capacity in GB
- **GPU**: Graphics card information using GPUtil
- **OS**: Operating system and version details
- **Display**: Screen resolution detection
- **Touch Support**: Detects touch screen capability
- **Fingerprint Reader**: Checks for fingerprint reader hardware
- **Battery Health**: Battery percentage and status

### User Interface
- **Real-time System Info**: All hardware information is automatically populated on startup
- **Refresh Capability**: "Re-check Hardware Info" button updates all system information
- **Read-only Fields**: System information fields are read-only for data integrity
- **Error Handling**: Graceful fallback to "N/A" for unavailable hardware features

### Diagnostic Tools
- **Test Sound**: Audio testing functionality
- **Dead Pixel Test**: Screen quality assessment
- **Keyboard Test**: Input device verification

### Report Generation
- **Client Information**: Order details, inspector info, and device condition
- **Email Integration**: Send reports directly via email
- **Local Saving**: Save reports in multiple formats

## Technical Implementation

### SystemInfoCollector Class
The core system information collection is handled by the `SystemInfoCollector` class in `core/system_info.py`:

```python
from core.system_info import system_collector

# Get comprehensive system information
info = system_collector.get_system_info()
```

**Key Methods:**
- `get_system_info()`: Returns complete hardware information dictionary
- `refresh_info()`: Updates cached system information
- `get_cached_info()`: Retrieves cached information

**Hardware Detection Methods:**
- `_get_brand_model()`: Uses WMIC to detect computer model
- `_get_cpu_info()`: CPU information via platform and psutil
- `_get_ram_info()`: Total memory calculation
- `_get_storage_info()`: Storage capacity across all partitions
- `_get_gpu_info()`: GPU detection using GPUtil
- `_get_os_info()`: Operating system details
- `_get_display_info()`: Screen resolution via screeninfo
- `_get_touch_support()`: Touch screen detection via WMIC
- `_get_fingerprint_reader()`: Fingerprint hardware detection
- `_get_battery_health()`: Battery status via psutil

### Error Handling
All hardware detection methods include comprehensive error handling:
- Subprocess timeouts (10 seconds)
- File not found errors
- Permission errors
- Graceful fallback to "N/A" for unavailable features

### UI Integration
The main window (`ui/main_window.py`) automatically:
- Loads system information on startup
- Updates fields when "Re-check Hardware Info" is clicked
- Displays all information in read-only QLabel fields
- Provides real-time status updates

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Dependencies

- **PyQt6**: Modern GUI framework
- **psutil**: System and process utilities
- **GPUtil**: GPU information detection
- **screeninfo**: Display resolution detection

## Usage

1. **Start the Application**: Launch `main.py`
2. **System Information**: Hardware details are automatically populated
3. **Client Information**: Fill in order details and inspection information
4. **Diagnostic Tests**: Use the test buttons to verify hardware functionality
5. **Generate Reports**: Create and send inspection reports

## System Requirements

- Windows 10/11 (primary target)
- Python 3.8+
- Administrator privileges for some hardware detection features

## Development

The application follows modular architecture:
- `core/`: Business logic and system information collection
- `ui/`: User interface components
- `assets/`: Application resources

All code follows clean architecture principles with proper separation of concerns and comprehensive error handling. 