# Image Deployment Analysis Tool 📊

A simple, easy-to-use application for analyzing image deployment delays. This tool allows you to import Excel/CSV files containing timestamp data and visualize processing times with customizable heatmaps.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2FLinux%2FMacOS-lightgrey.svg)

## Features

- **Data Import**: Import timestamp data from Excel (.xlsx) or CSV files
- **Data Processing**: Automatic calculation of processing delays between image receipt and activation
- **Visualization**: Generate heatmaps showing average delays by weekday and hour
- **Time Analysis**: Drill down to analyze data by:
  - Year
  - Month
  - Week
- **Statistics**: View key metrics including:
  - Total number of processed images
  - Average processing delay
  - Minimum and maximum delays
- **Export**: Save analysis results and visualizations

## Installation

1. Clone this repository or download the source code
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode

For interactive analysis with a graphical interface:

```bash
python deployment-analyse.py --gui
```

To open with a specific file:

```bash
python deployment-analyse.py --gui --file your_data.xlsx
```

### Command-Line Mode

For batch processing or script integration:

```bash
python deployment-analyse.py --file your_data.xlsx --output heatmap.png
```

## Data Format

Your Excel/CSV file should include these columns:

| Column Name | Description | Format |
|-------------|-------------|--------|
| IPTC_DE Anweisung | Time instruction | Contains timestamp in [HH:MM:SS] format |
| IPTC_EN Anweisung | English equivalent | Optional |
| Bild Upload Zeitpunkt | Image upload timestamp | DD.MM.YYYY HH:MM:SS |
| Bild Veröffentlicht | Publication status | "Ja" or "Nein" |
| Bild Aktivierungszeitpunkt | Image activation timestamp | DD.MM.YYYY HH:MM:SS |

## Application Workflow

1. **Import**: Select an Excel or CSV file containing your image processing data
2. **Process**: The application automatically:
   - Extracts timestamps
   - Calculates processing delays
   - Cleans and normalizes data
3. **Analyze**: Choose a time period (year, month, week) to analyze
4. **Visualize**: View heatmaps showing processing delays by day and hour
5. **Export**: Save visualizations or processed data for reporting

## Directory Structure

```
├── deployment-analyse.py   # Main application (both GUI and CLI)
├── requirements.txt        # Python dependencies
├── data/                   # Place your input files here (optional)
├── output/                 # Generated visualizations are saved here
├── logs/                   # Application logs
└── db/                     # Database files (for future use)
```

## Troubleshooting

- **File Import Issues**: Ensure your Excel/CSV files follow the expected format
- **Visualization Errors**: Check that your data contains valid timestamps and date information
- **GUI Not Responding**: For large files, the application may take some time to process data

## License

This project is provided under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the pandas, matplotlib, and seaborn teams for the excellent data processing and visualization libraries
- Special thanks to all contributors who have provided feedback and suggestions
