# Inspector Diagnostic Utility

A comprehensive system inspection and diagnostic tool built with PyQt6.

## Features

- **System Information**: Collect and display detailed system information
- **Performance Monitoring**: Real-time CPU, memory, and disk usage monitoring
- **Diagnostic Scans**: Run comprehensive system diagnostics with customizable options
- **Report Generation**: Generate reports in multiple formats (HTML, PDF, TXT, JSON)
- **Email Integration**: Send diagnostic reports via email
- **Modular Architecture**: Clean, maintainable code structure ready for feature injection

## Project Structure

```
inspector_app/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── admin.manifest         # Windows UAC manifest
├── ui/
│   ├── __init__.py
│   └── main_window.py     # Main GUI window
├── core/
│   ├── __init__.py
│   ├── system_info.py     # System information collection
│   ├── inspector_input.py # Input validation and processing
│   ├── report_generator.py # Report generation
│   ├── email_sender.py    # Email functionality
│   └── test_launcher.py   # Diagnostic test execution
└── assets/
    └── test_sound.mp3     # Placeholder asset file
```

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

## Usage

### Quick Start
1. Launch the application
2. Use the "Quick System Scan" button for basic diagnostics
3. Use the "Full Diagnostic Scan" button for comprehensive analysis
4. Generate reports in your preferred format
5. Send reports via email if needed

### Features Overview

#### System Information Tab
- View basic system information (OS, CPU, RAM, Storage)
- Monitor real-time performance metrics
- Refresh system data on demand

#### Diagnostics Tab
- Select scan options (System, Performance, Security, Network, Hardware)
- Start/stop diagnostic scans
- View scan progress and results
- Customize scan parameters

#### Reporting Tab
- Configure report settings (title, format, options)
- Generate reports in multiple formats
- Save reports to custom locations
- Send reports via email

#### Settings Tab
- Configure auto-refresh intervals
- Set log levels and thread limits
- Manage application preferences

## Development

### Architecture

The application follows a modular architecture with clear separation of concerns:

- **UI Layer**: PyQt6-based user interface
- **Core Layer**: Business logic and system operations
- **Data Layer**: System information collection and processing

### Adding New Features

1. **UI Components**: Add to `ui/main_window.py`
2. **Business Logic**: Add to appropriate core module
3. **System Operations**: Extend `core/system_info.py`
4. **Input Validation**: Extend `core/inspector_input.py`

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints throughout
- Include comprehensive error handling
- Write descriptive docstrings
- Maintain modular function structure

## Dependencies

- **PyQt6**: Modern GUI framework
- **psutil**: System and process utilities
- **platform-utils**: Platform-specific utilities

## Future Enhancements

- **Real-time Monitoring**: Live system monitoring dashboard
- **Advanced Diagnostics**: Deep system analysis tools
- **Custom Reports**: User-defined report templates
- **Plugin System**: Extensible architecture for custom modules
- **Cloud Integration**: Remote monitoring and reporting
- **Automated Testing**: Comprehensive test suite

## Contributing

1. Follow the established code structure
2. Add appropriate error handling
3. Include input validation
4. Test thoroughly before submitting
5. Update documentation as needed

## License

This project is developed by DNCL for internal use and demonstration purposes.

## Support

For issues or questions, please refer to the project documentation or contact the development team. 