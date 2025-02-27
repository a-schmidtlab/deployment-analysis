# Deployment Analyzer

A tool for analyzing deployment data with visualization capabilities.
(c) 2025 by Axel Schmidt



## Introduction

The Deployment Analyzer is a tool designed to help analyze and visualize deployment data. It provides both a command-line interface and a graphical user interface for importing data, performing analysis, and generating reports.

## Installation

### Pre-built Binary (Recommended)

1. Download the latest release package
2. Extract the ZIP file to a directory of your choice
3. Run `DeploymentAnalyzer.exe` to start the application

### From Source

1. Ensure Python 3.9 or higher is installed
2. Clone this repository
3. Install required packages: `pip install -r requirements.txt`
4. Run `python launcher.py` to start the application

## Building and Deploying

To build the application for distribution:

1. Follow the quick guide in `BUILD_GUIDE.txt`
2. Or see `DEPLOYMENT.md` for detailed instructions

### Quick Build Reference

```powershell
# Clean previous builds
Remove-Item -Recurse -Force -Path build, dist, *.spec

# Run the comprehensive build
.\ultimate_build.bat

# Create a user-friendly distribution
.\create_final_release.bat
# (Select 'Y' when prompted for EXE launcher)

# Create a distribution package
Compress-Archive -Path .\dist\DeploymentAnalyzer-Release -DestinationPath .\dist\DeploymentAnalyzer-Release.zip -Force
```

The final distribution will be located in `dist\DeploymentAnalyzer-Release` and will contain:
- `DeploymentAnalyzer.exe` - Main executable that users can double-click
- `README.txt` - User documentation
- `.app/` - Hidden folder containing application files

### Testing the Build

Always test the final distribution on a clean system before distributing to users to ensure all dependencies are included and the application starts properly.

## Features

- Data import from CSV, Excel, and multiple other formats
- Advanced data filtering and transformation
- Interactive data visualization
- Export results to various formats (CSV, Excel, PDF)
- Comprehensive reporting capabilities
- Batch processing for multiple data sets

## Usage

### GUI Mode

1. Start the application by running `DeploymentAnalyzer.bat`
2. Use the file menu to import your data
3. Select analysis options from the toolbar
4. Generate visualizations using the chart buttons
5. Export results using the export menu

### Command-line Mode

For batch processing or automation, use the command-line interface:

```
python deployment-analyse.py --input data/input.csv --output output/results.xlsx
```

Use `--help` to see all available command-line options.

## Disk Space Requirements

The application requires approximately 350 MB of disk space when installed. This optimized size was achieved by:

- Excluding large sample CSV files
- Removing test directories from libraries
- Eliminating unnecessary sample data and documentation

If you're building from source, the build scripts automatically handle these optimizations.

## Troubleshooting

If the application doesn't start:

1. Check the log files in the `logs` directory
2. Ensure all required dependencies are installed
3. Verify that you have the necessary permissions to access the data directory

If you encounter specific errors, please check the `DEPLOYMENT.md` file for detailed troubleshooting steps.

## Directory Structure

```
DeploymentAnalyzer/
├── data/           # Data files and templates
├── logs/           # Log files
├── output/         # Generated reports and output files
└── .app/           # Application files (hidden)
```

## License

This software is licensed under the MIT License. See the LICENSE file for details.

## Support

For support, please open an issue on our issue tracker or contact Axel Schmidt.
