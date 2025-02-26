# Deployment Analyzer

A tool for analyzing deployment data with visualization capabilities.

## Introduction

The Deployment Analyzer is a tool designed to help analyze deployment data, generate heatmaps, and export visualizations. It provides both a command-line interface and a graphical user interface for interactive analysis.

## Installation

### Using the Standalone Executable

1. Navigate to the `dist/DeploymentAnalyzer` directory
2. You have several options to run the application:
   - Double-click on `Deployment Analyzer.bat` (recommended for most users)
   - Use the Windows shortcut `Deployment Analyzer.lnk`
   - Run `DeploymentAnalyzer.exe` directly (now defaults to GUI mode)

No additional installation steps are required as all dependencies are bundled within the executable.

## Features

- Import deployment data from CSV files
- Generate heatmaps and visualizations
- Export data and visualizations
- Customize analysis parameters
- Both GUI and command-line modes

## Usage

### GUI Mode

1. Launch the application using one of the methods described in the Installation section
2. Use the interface to load data, configure settings, and analyze your deployment data
3. Export results using the export functions in the application

### Command Line Mode

Launch the application with parameters:

```
DeploymentAnalyzer.exe --input path/to/input.csv --output path/to/output
```

## Troubleshooting

If you encounter any issues:

1. Check the log files in the `logs` directory
2. Make sure all required data directories exist (`data`, `logs`, `output`)
3. Ensure your input data is properly formatted

## Directory Structure

- `data/`: Contains reference data
- `logs/`: Application logs
- `output/`: Default location for exported files

## License

This software is proprietary and confidential.

## Contact

For support or questions, please contact the author.
