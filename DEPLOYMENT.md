# Deployment Guide

This document provides detailed instructions for building and deploying the Deployment Analyzer application.

## Building the Application

### Prerequisites

- Python 3.9 or higher
- PyInstaller 6.0 or higher
- Required Python packages (install with `pip install -r requirements.txt`)

### Step 1: Clean Previous Builds

```powershell
# In PowerShell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue -Path build, dist, *.spec
```

or in Command Prompt:

```cmd
rmdir /s /q build dist
del *.spec
```

### Step 2: Build the Application

```powershell
# For directory-based build (recommended for testing)
pyinstaller --noconfirm --onedir --windowed --add-data "data;data" --add-data "logs;logs" --add-data "output;output" --add-data "deployment-analyse.py;." --name "DeploymentAnalyzer" launcher.py

# For single executable (final distribution)
pyinstaller --noconfirm --onefile --windowed --add-data "data;data" --add-data "logs;logs" --add-data "output;output" --add-data "deployment-analyse.py;." --name "DeploymentAnalyzer" launcher.py
```

### Step 3: Create a Clean Distribution (Recommended)

For a cleaner, more user-friendly distribution with minimal visible files, use the provided script:

```cmd
# Creates a clean distribution with only two visible files
.\create_final_release.bat
```

This creates a distribution in `dist\DeploymentAnalyzer-Release` with the following features:
- Only two visible files: `DeploymentAnalyzer.bat` (launcher) and `README.txt`
- All application files hidden in the `.app` folder
- Proper configuration and directory structure

### Step 4: Optimizing Build Size (Important)

The build scripts now automatically exclude large CSV data files and test directories to minimize distribution size:

- Large sample CSV files (like `Editorial_Importzeit*.csv`) are excluded
- Test directories and files are excluded
- Sample data directories are excluded

If you need to add more exclusions, edit one of these files:
- `enhanced_build.bat`: Contains exclusion patterns for PyInstaller command line
- `DeploymentAnalyzer.spec`: Contains exclusion patterns for spec-based builds

To further optimize size after building, you can run the executable update script:

```cmd
# Updates an existing release to clean up unnecessary files
.\update_release_with_exe.bat
```

## Running the Application

### Method 1: Run the Clean Distribution (Recommended)

1. Navigate to the `dist\DeploymentAnalyzer-Release` directory
2. Double-click `DeploymentAnalyzer.bat` to start the application

### Method 2: Run the Standard Distribution

Navigate to the `dist\DeploymentAnalyzer` directory and run `DeploymentAnalyzer.exe`.

### Method 3: Use the Debug Launcher

Run `debug_DeploymentAnalyzer.bat` from the project root directory to launch with debug output.

## Distribution Structures

### Clean Distribution Structure (DeploymentAnalyzer-Release)

```
DeploymentAnalyzer-Release/
├── DeploymentAnalyzer.bat       # Visible launcher
├── README.txt                   # Visible documentation
└── .app/                        # Hidden application folder
    ├── lib/                     # Application executables and libraries
    │   ├── DeploymentAnalyzer.exe
    │   ├── app_config.ini
    │   └── ...
    └── support/                 # User data folders
        ├── data/
        ├── logs/
        └── output/
```

### Standard Distribution Structure (DeploymentAnalyzer)

```
DeploymentAnalyzer/
├── DeploymentAnalyzer.exe       # Main executable
├── README.txt                   # Documentation
├── data/                        # Data directory
├── logs/                        # Logs directory
├── output/                      # Output directory
└── ...                          # Other application files
```

## Troubleshooting

### If the Application Won't Start

1. **Check log files**:
   - For clean distribution: Check for log files in `.app\support\logs`
   - Look for `app_output.log` and `app_error.log` in the project root
   - Check for `launcher.log` and `launcher_error.log` in the logs directory

2. **Verify file structure**:
   - For clean distribution: Make sure the `.app` folder exists alongside the launcher
   - Make sure required directories exist (data, logs, output)
   - Ensure all necessary files are included in the build

3. **System-specific issues**:
   - Install Microsoft Visual C++ Redistributable if you see "Missing DLL" errors
   - Temporarily disable antivirus software which may block execution

4. **Manual debugging**:
   - For clean distribution, run the VBS script directly to see error messages:
     ```
     cscript //nologo DeploymentAnalyzer.vbs
     ```
   - For standard distribution, run the executable from Command Prompt:
     ```
     cd dist\DeploymentAnalyzer
     DeploymentAnalyzer.exe
     ```

### Known Issues and Solutions

1. **File Not Found Errors**:
   - Check if data files are properly bundled with the executable
   - Make sure all required directories exist

2. **Module Import Errors**:
   - If you get missing module errors, add them to the build command:
     ```
     pyinstaller --hidden-import=missing_module ...
     ```

3. **Permission Errors**:
   - Run as administrator if the application needs elevated permissions
   - Check if the application has write permissions to its directories

4. **Missing DLLs**:
   - If Python DLLs are missing, use the enhanced build script:
     ```
     .\enhanced_build.bat
     ```
   - This explicitly includes Python and Visual C++ runtime DLLs

5. **Large Distribution Size**:
   - The build now automatically excludes large CSV files and test directories
   - If the distribution is still too large, consider removing more files using the patterns in `enhanced_build.bat`
   - You can run a post-build cleanup using PowerShell:
     ```powershell
     Get-ChildItem -Path "dist\DeploymentAnalyzer-Release" -Recurse -Force -Include *.csv | Remove-Item -Force
     ```

## Distributing the Application

1. **Clean Distribution (Recommended)**:
   - Copy the entire `dist\DeploymentAnalyzer-Release` directory
   - Users will only see two files (DeploymentAnalyzer.bat and README.txt)
   - Provides a clean, professional appearance

2. **Standard Directory Distribution**:
   - Copy the entire `dist\DeploymentAnalyzer` directory
   - Include README.md with usage instructions

3. **Single-file Distribution**:
   - Distribute the single .exe file from the `dist` directory
   - Create a zip file with the .exe and any required documentation

4. **Creating an Installer**:
   - Consider using InnoSetup or NSIS to create a proper installer
   - Include Visual C++ redistributables if needed

## Building Distribution Variants

The project includes several scripts to create different distribution variants:

- `build.bat` - Standard PyInstaller build
- `enhanced_build.bat` - Enhanced build with explicit DLL inclusion and CSV exclusion
- `create_final_release.bat` - Creates the clean distribution
- `reorganize_dist.bat` - Reorganizes standard distribution with lib/support folders
- `create_minimal_distribution.bat` - Creates a minimal distribution variant
- `update_release_with_exe.bat` - Updates an existing release with an EXE launcher and cleans up unnecessary files

## Optimizing Distribution Size

The distribution size has been optimized by:

1. **Excluding test files and directories**:
   - All test directories from libraries are excluded
   - This saves approximately 21 MB

2. **Excluding large sample data CSV files**:
   - Files like `Editorial_Importzeit*.csv` are excluded
   - This can save hundreds of MB depending on the size of your data files

3. **Excluding other unnecessary components**:
   - Sample data directories from libraries
   - Documentation files that aren't needed for runtime
   - Debug symbols and compile artifacts

To verify the exclusion worked, check the final distribution size - it should be approximately 330-350 MB (down from 600+ MB).

## Testing Deployment

Always test the application on a clean system (or virtual machine) that resembles the target environment before distributing to end users. 