# Processing Time Analysis System 📊

A modern Windows desktop application for analyzing processing time data from image processing systems. Built with Python and PyQt6, featuring a clean Windows 11 Fluent Design interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)

## Features

### Core Functionality
- Process and analyze timestamp data from CSV files
- Real-time data preview and analysis
- Interactive visualizations and reports
- Event correlation with external data sources
- Anomaly detection and peak analysis

### Modern UI
- Windows 11 Fluent Design interface
- Dark/Light theme support
- High DPI and touch optimization
- Multi-monitor support
- Drag-and-drop file handling

### Analysis & Visualization
- Interactive time series plots
- Heat maps with zoom capability
- Distribution analysis
- Correlation matrices
- Custom chart themes
- Export to PNG/PDF

### Smart Event Analysis
- Automatic pattern detection
- Statistical analysis
- Peak detection
- Event correlation with:
  - Wikipedia events
  - News articles
  - Google Trends data

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
- GPU with DirectX 12 support

### Installation

1. Download the latest installer from the releases page
2. Run the installer and follow the setup wizard
3. Launch the application from the Start menu
4. Optional: Enable automatic updates in settings

## Quick Usage Guide

1. **Data Import**
   - Drag and drop CSV files onto the main window
   - Select files through the file menu
   - Import multiple files for batch processing

2. **Analysis**
   - Select time range for analysis
   - Choose visualization type
   - Apply filters and parameters
   - Export results as needed

3. **Report Generation**
   - Select report template
   - Customize charts and data
   - Generate PDF/PNG outputs
   - Share via email integration

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

### Key Components
- PyQt6 for modern UI
- SQLite for local data storage
- Matplotlib/Plotly for visualizations
- NumPy/Pandas for data analysis

## 🔧 Development

### Setup Development Environment
1. Clone the repository
```bash
git clone https://github.com/yourusername/processing-time-analysis.git
```

2. Install dependencies
```bash
poetry install
```

3. Run tests
```bash
poetry run pytest
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

- [User Guide](docs/user-guide.md)
- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [FAQ](docs/faq.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Michael Gottschalk for the idea 
- PyQt6 team for the GUI framework
- Python data science community
- Windows design team for Fluent Design guidelines
