# Computer Device Inspector - Complete Application

A comprehensive desktop application for inspecting and documenting computer hardware specifications and condition. Built with PyQt6 for Windows environments.

## 🚀 Quick Start

### Option 1: Run the Complete Build Script (Recommended)
```bash
# Navigate to the inspector_app directory
cd inspector_app

# Run the complete build script
build_complete.bat
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test the application
python test_imports.py

# 3. Run the application
python main.py
```

## 📋 Features

### 🔧 System Information Collection
- **Automatic Hardware Detection**: Brand, model, CPU, RAM, storage, GPU
- **Operating System Details**: Windows version and build information
- **Display Information**: Resolution and multi-monitor support
- **Hardware Features**: Touch screen, fingerprint reader, battery health
- **Real-time Updates**: Refresh hardware information on demand

### 🧪 Diagnostic Tools
- **Audio Testing**: Play test sound to verify speakers
- **Dead Pixel Test**: Open browser-based screen quality assessment
- **Keyboard Test**: Verify input device functionality
- **Hardware Validation**: Comprehensive system health checks

### 📊 Report Generation
- **Multiple Formats**: Text, HTML, PDF, JSON reports
- **Client Information**: Order details, inspector info, device condition
- **System Specifications**: Complete hardware inventory
- **Test Results**: Diagnostic test outcomes and findings
- **Issue Tracking**: Document problems and recommendations

### 📧 Email Integration
- **Gmail Support**: Send reports directly via Gmail
- **Google OAuth**: Secure authentication with multiple accounts
- **Attachment Support**: Include reports and screenshots
- **Template System**: Professional email templates

### 🎨 User Interface
- **Modern Design**: Clean, professional interface
- **Responsive Layout**: Adapts to different screen sizes
- **Real-time Feedback**: Status updates and progress indicators
- **Error Handling**: Graceful fallbacks for unavailable features

## 🛠️ Technical Architecture

### Core Modules
```
core/
├── system_info.py      # Hardware detection and system information
├── test_launcher.py    # Diagnostic test execution
├── report_generator.py # Report creation and formatting
├── email_sender.py     # Email functionality
└── inspector_input.py  # Input validation and processing
```

### UI Components
```
ui/
├── main_window.py      # Main application interface
└── report_email_dialog.py # Report and email dialog
```

### Configuration
```
gmail_config.py         # Gmail credentials management
google_oauth_simple.py  # Google OAuth authentication
```

## 📦 Dependencies

### Required Packages
- **PyQt6**: Modern GUI framework
- **psutil**: System and process utilities
- **GPUtil**: GPU information detection
- **screeninfo**: Display resolution detection

### Optional Packages
- **PyInstaller**: For creating standalone executables

## 🔧 Installation

### Prerequisites
- Windows 10/11 (primary target)
- Python 3.8 or higher
- Administrator privileges (for some hardware detection)

### Step-by-Step Setup

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd DNCL-Computer-Inspector/inspector_app
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the Installation**
   ```bash
   python test_imports.py
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

## 🚀 Building Executable

### Using the Build Script
```bash
# Run the complete build process
build_complete.bat
```

### Manual Build
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name "ComputerInspector" main.py
```

The executable will be created in the `dist/` directory.

## 📖 Usage Guide

### 1. Starting the Application
- Run `python main.py` or double-click the executable
- The application will automatically detect and display system information

### 2. Client Information
- Fill in order details (invoice number, inspector name)
- Enter device condition and warranty information
- Add condition notes and issues found

### 3. Diagnostic Tests
- **Audio Test**: Click "Test Sound" to verify speakers
- **Dead Pixel Test**: Opens browser-based screen test
- **Keyboard Test**: Opens keyboard testing utility

### 4. Report Generation
- Click "Generate Report" to create inspection report
- Choose save location for the report file
- Reports include all system information and test results

### 5. Email Integration
- Configure Gmail credentials (requires App Password)
- Select recipient and customize email content
- Send reports with attachments

## 🔐 Gmail Setup

### 1. Enable 2-Factor Authentication
- Go to your Google Account settings
- Enable 2-Factor Authentication

### 2. Generate App Password
- Go to Security settings
- Generate an App Password for "Mail"
- Use this password in the application

### 3. Configure in Application
- Enter your Gmail address
- Enter the App Password (not your regular password)
- Test the configuration

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Run the import test
python test_imports.py
```

**2. Hardware Detection Fails**
- Run as Administrator for better hardware access
- Check Windows permissions for system information

**3. Gmail Authentication Fails**
- Verify 2-Factor Authentication is enabled
- Use App Password, not regular password
- Check firewall/antivirus settings

**4. PyQt6 Installation Issues**
```bash
# Try upgrading pip
python -m pip install --upgrade pip

# Install PyQt6 with specific version
pip install PyQt6==6.4.0
```

### Error Messages

**"Python is not installed"**
- Install Python 3.8+ from python.org
- Add Python to PATH during installation

**"Dependencies failed to install"**
- Check internet connection
- Try running as Administrator
- Use `pip install --user -r requirements.txt`

**"Application won't start"**
- Check Python version: `python --version`
- Verify PyQt6 installation: `python -c "import PyQt6"`

## 📁 File Structure

```
inspector_app/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── build_complete.bat        # Complete build script
├── test_imports.py           # Import testing script
├── README_COMPLETE.md        # This documentation
├── core/                     # Core business logic
│   ├── system_info.py       # Hardware detection
│   ├── test_launcher.py     # Diagnostic tests
│   ├── report_generator.py  # Report creation
│   ├── email_sender.py      # Email functionality
│   └── inspector_input.py   # Input validation
├── ui/                      # User interface
│   ├── main_window.py       # Main application window
│   └── report_email_dialog.py # Report dialog
├── assets/                  # Application resources
│   └── test_sound.mp3      # Audio test file
├── gmail_config.py          # Gmail configuration
└── google_oauth_simple.py  # Google OAuth
```

## 🔄 Development

### Code Structure
- **Modular Design**: Separated concerns with clear interfaces
- **Error Handling**: Comprehensive try-catch blocks
- **Type Hints**: Full type annotations for better IDE support
- **Documentation**: Detailed docstrings and comments

### Adding Features
1. Create new modules in `core/` for business logic
2. Add UI components in `ui/` for user interface
3. Update `test_imports.py` to test new imports
4. Document changes in README

### Testing
```bash
# Test imports
python test_imports.py

# Test application startup
python -c "from ui.main_window import MainWindow"

# Run full application
python main.py
```

## 📄 License

This project is developed for DNCL Computer Inspector utility.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Run `python test_imports.py` to identify import issues
3. Verify all dependencies are installed correctly
4. Check Windows permissions and firewall settings

## 🎯 System Requirements

- **OS**: Windows 10/11 (primary), Linux/macOS (experimental)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space
- **Permissions**: Administrator for full hardware access

---

**🎉 Your Computer Inspector application is now complete and ready to use!** 