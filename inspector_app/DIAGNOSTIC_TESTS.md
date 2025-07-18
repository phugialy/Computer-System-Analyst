# Diagnostic Tests Feature

## Overview

The Computer Inspector Application now includes built-in diagnostic tests that allow inspectors to quickly run hardware, audio, and input tests directly from the application interface.

## Available Tests

### 1. Audio Test
- **Button**: ▶ Play Test Sound
- **Function**: Plays the test sound file (`test_sound.mp3`) from the assets directory
- **Usage**: Click the button to verify audio output is working correctly
- **File Location**: `assets/test_sound.mp3`

### 2. Dead Pixel Test
- **Button**: 🔍 Open Dead Pixel Test
- **Function**: Opens https://lcdtech.info/en/tests/dead.pixel.htm in the default browser
- **Usage**: Click to launch an online dead pixel detection tool
- **Requirement**: Internet connection required

### 3. Keyboard Test
- **Button**: ⌨ Launch Keyboard Test
- **Function**: Opens https://en.key-test.ru/ in the default browser
- **Usage**: Click to launch an online keyboard testing tool
- **Requirement**: Internet connection required

## Implementation Details

### TestLauncher Class
The diagnostic tests are implemented in `core/test_launcher.py` with the following methods:

```python
def play_audio_test(self) -> bool:
    """Play test sound from assets directory."""
    
def launch_dead_pixel_test(self) -> bool:
    """Open dead pixel test in default browser."""
    
def launch_keyboard_test(self) -> bool:
    """Open keyboard test in default browser."""
```

### UI Integration
The tests are connected to buttons in `ui/main_window.py`:

- `_on_play_test_sound()` - Handles audio test
- `_on_open_dead_pixel_test()` - Handles dead pixel test
- `_on_launch_keyboard_test()` - Handles keyboard test

### Error Handling
All tests include comprehensive error handling:

- **Audio Test**: Checks if test sound file exists, shows appropriate error messages
- **Browser Tests**: Handles network connectivity issues, shows user-friendly error dialogs
- **General**: Graceful fallbacks and informative status messages

## PyInstaller Bundling Support

### Asset Management
The application is prepared for PyInstaller bundling with:

1. **Relative Path Handling**: Uses `sys._MEIPASS` for bundled assets
2. **Fallback Paths**: Desktop as default save location for reports
3. **Asset Inclusion**: Test sound file is included in the bundle

### Build Configuration
- **Spec File**: `inspector_app.spec` for detailed build configuration
- **Build Scripts**: 
  - `build.bat` - Windows batch script
  - `build.ps1` - PowerShell script

### Build Commands
```bash
# Basic build
pyinstaller --onefile --windowed --manifest admin.manifest main.py

# Using spec file
pyinstaller inspector_app.spec
```

## File Structure
```
inspector_app/
├── assets/
│   └── test_sound.mp3          # Audio test file
├── core/
│   └── test_launcher.py        # Test implementation
├── ui/
│   └── main_window.py          # UI integration
├── inspector_app.spec           # PyInstaller spec
├── build.bat                   # Windows build script
├── build.ps1                   # PowerShell build script
└── admin.manifest              # Windows manifest
```

## Usage Instructions

### For Inspectors
1. **Audio Test**: Click "▶ Play Test Sound" to verify speakers/headphones
2. **Display Test**: Click "🔍 Open Dead Pixel Test" to check for dead pixels
3. **Input Test**: Click "⌨ Launch Keyboard Test" to test all keyboard keys

### For Developers
1. **Testing**: Run `python main.py` to test the application
2. **Building**: Run `build.ps1` or `build.bat` to create executable
3. **Distribution**: The bundled executable includes all necessary assets

## Error Recovery

### Common Issues
1. **Audio File Missing**: Check if `assets/test_sound.mp3` exists
2. **Browser Not Opening**: Verify internet connection and default browser
3. **Build Failures**: Ensure PyInstaller is installed and all dependencies are met

### Troubleshooting
- **Audio Issues**: Verify system audio is working and file permissions
- **Network Issues**: Check firewall settings and internet connectivity
- **Build Issues**: Clean previous builds and reinstall dependencies

## Future Enhancements

### Planned Features
1. **Local Tests**: Implement offline versions of display and keyboard tests
2. **Test Results**: Store and display test results in reports
3. **Custom Tests**: Allow inspectors to add custom diagnostic procedures
4. **Batch Testing**: Run multiple tests automatically

### Technical Improvements
1. **Native Audio**: Use PyQt6 multimedia for better audio control
2. **Embedded Browser**: Consider QWebEngineView for offline tests
3. **Test Scheduling**: Add automated test scheduling capabilities
4. **Result Export**: Export test results in various formats

## Dependencies

### Required Packages
- `PyQt6` - GUI framework
- `PyInstaller` - Application bundling (for distribution)

### Optional Packages
- `pywin32` - Windows-specific features (for Windows builds)

## Security Considerations

### File Access
- Audio files are loaded from trusted assets directory
- External URLs are validated before opening
- User confirmation for file operations

### Network Access
- Browser tests require internet connectivity
- URLs are hardcoded to trusted testing sites
- No data is transmitted to external servers

## Performance Notes

### Resource Usage
- Audio test: Minimal CPU/memory usage
- Browser tests: Uses system default browser
- UI responsiveness: Tests run in background threads

### Optimization
- Lazy loading of test resources
- Efficient error handling
- Minimal file I/O operations

## Support

### Getting Help
1. Check the error messages in the application
2. Verify all required files are present
3. Test internet connectivity for browser-based tests
4. Ensure proper file permissions

### Reporting Issues
- Include error messages and system information
- Specify the test that failed
- Provide steps to reproduce the issue 