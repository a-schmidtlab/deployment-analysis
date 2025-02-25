# Processing Time Analysis System 📊

A Windows desktop application for analyzing image processing system delays and delivery times. Built with Python and PyQt6, featuring a modern Windows interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)

## Features

### Data Processing (Module 1)
- Import and process timestamp data from multiple CSV files
- Data cleaning and normalization
- Quality assessment and event prioritization
- Structured database storage with automatic updates
- Batch processing capabilities

### Interactive Analysis (Module 2)
- Timeline-based navigation and visualization
- Flexible drill-down from yearly to hourly views
- Smart filtering by:
  - Processing time
  - Time of day
  - Day of week
- Comparative period analysis
- Event overlay system with toggle options
- Anomaly threshold configuration
- Event annotation capabilities
- Intelligent preset configurations for quick insights

### Reporting Engine (Module 3)
- Automated PNG export functionality
- Pre-configured report templates:
  - Daily overview with peak analysis
  - Week-to-week comparison
  - Monthly analysis
  - Yearly overview
  - Anomaly reports
  - Event correlation analysis
- Batch export processing
- Optional legends and explanations

### Event Correlation (Module 4)
- Automatic correlation detection
- Event relevance weighting
- Statistical significance calculations

### User Interface
- Clean, intuitive interface
- Responsive design
- Comprehensive help system
- Multilingual support (German/English)
- High DPI optimization
- Multi-monitor support
- Drag-and-drop file handling

## Getting Started

### System Requirements

#### Minimum
- Windows 10 (20H2 or later)
- 4GB RAM
- 1GB free disk space
- 1080p display
- x64 processor

#### Recommended
- Windows 11
- 8GB RAM
- SSD with 5GB free
- 1440p display or better

### Installation

#### Standard Installation
1. Download ProcessingTimeAnalysis.exe from the releases page
2. Run the installer which will:
   - Check system requirements
   - Install all required components
   - Create desktop and Start menu shortcuts
3. Launch the application

#### Silent Installation (IT Administrators)
```batch
ProcessingTimeAnalysis.exe /S /D=C:\Program Files\ProcessingTimeAnalysis
```

## Quick Usage Guide

1. **Data Import**
   - Import single or multiple CSV files via:
     - Drag and drop
     - File menu selection
   - Data is automatically processed and stored

2. **Analysis**
   - Select time range and granularity
   - Use intelligent presets or customize views
   - Apply filters and thresholds
   - Toggle event overlays
   - Add annotations as needed

3. **Report Generation**
   - Choose from pre-configured templates
   - Customize report parameters
   - Generate PNG exports
   - Process batch exports

## Technical Details

### Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
PyQt6 = "^6.5.0"
pandas = "^2.0.0"
numpy = "^1.24.0"
matplotlib = "^3.7.0"
plotly = "^5.14.0"
sqlite3 = "*"
```

### Project Structure
```
src/
├── ui/          # User interface components
├── data/        # Data processing and storage
├── analysis/    # Analysis algorithms
├── utils/       # Utility functions
└── tests/       # Test suite
```

## Documentation

- [Installation Guide](docs/installation.md)
- [User Manual](docs/user-manual.md)
- [Technical Documentation](docs/technical.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Michael Gottschalk for the concept
- PyQt6 team for the GUI framework
