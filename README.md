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

# Image Distribution Analysis Tool

A comprehensive tool for analyzing image distribution workflows, detecting anomalies, and identifying patterns in processing delays.

## Overview

This tool helps analyze the distribution of images from receipt to publication, providing insights into:

- Processing delays across different time periods
- Anomaly detection for identifying unusual processing patterns
- Timeline analysis for understanding peak times and bottlenecks
- Distribution patterns by weekday and hour

## Project Structure

```
├── data/
│   ├── raw/             # Raw CSV data files
│   └── processed/       # Processed data and database files
├── src/
│   ├── modules/
│   │   ├── data_preparation/
│   │   │   ├── csv_importer.py
│   │   │   ├── data_cleaner.py
│   │   │   └── database.py
│   │   ├── interactive_analysis/
│   │   │   ├── timeline_analyzer.py
│   │   │   ├── anomaly_detector.py
│   │   │   └── dashboard.py
│   │   └── reporting_engine/
│   │       └── report_generator.py
│   ├── cli.py           # Command-line interface
│   └── run_dashboard.py # Dashboard runner
└── requirements.txt     # Project dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/image-distribution-analysis.git
cd image-distribution-analysis
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command-line Interface

The tool provides a command-line interface for various operations:

#### Import Data

Import and process CSV data:
```bash
python src/cli.py import --file data/raw/deployments.csv
```

#### Analyze Timeline

Analyze time patterns in the data:
```bash
python src/cli.py analyze --data-dir data/processed --granularity hour
```

#### Detect Anomalies

Detect anomalies in processing delays:
```bash
python src/cli.py anomaly --data-dir data/processed --method zscore
```

### Interactive Dashboard

The tool includes an interactive web dashboard for data exploration and analysis:

1. Start the dashboard:
```bash
python src/run_dashboard.py --db-path data/processed/deployments.db
```

2. Open your web browser and navigate to `http://127.0.0.1:8050`

3. Use the dashboard to:
   - Select date ranges for analysis
   - Visualize time patterns through line charts
   - Explore weekday-hour heatmaps for pattern identification
   - Detect and visualize anomalies with various methods

Dashboard options:
- `--port`: Specify the port to run the dashboard (default: 8050)
- `--debug`: Run in debug mode with auto-reloading
- `--db-path`: Specify the path to the database file (default: data/processed/deployments.db)

## Dependencies

- pandas: Data manipulation and analysis
- numpy: Numerical computing
- matplotlib: Plotting library
- plotly: Interactive visualizations
- dash: Web application framework for dashboard
- dash-bootstrap-components: Bootstrap components for Dash
- scikit-learn: Machine learning algorithms for anomaly detection
- sqlite3: Database storage (built-in with Python)

## License

[MIT License](LICENSE)
