# Bild-Auslieferungsanalyse-Tool 

*[English version below](#image-deployment-analysis-tool-)*

Ein Werkzeug zur Analyse von Verzögerungen bei der Bildauslieferung, das Ihnen hilft, die Antwort auf die wichtigste Frage der Bildverarbeitung zu finden.

## Überblick

Das Bild-Auslieferungsanalyse-Tool ist eine spezialisierte Anwendung zur Analyse und Visualisierung von Verarbeitungsverzögerungen in Bildverteilungssystemen. Es bietet sowohl eine grafische Benutzeroberfläche für interaktive Analysen als auch eine Befehlszeilenschnittstelle für automatisierte Berichte - und das alles ohne dass Sie in Panik geraten müssen.

## Hauptfunktionen

- **Datenimport**: Import von Zeitstempeldaten aus Excel (.xlsx) oder CSV-Dateien
- **Datenverarbeitung**: Automatische Berechnung von Verarbeitungsverzögerungen zwischen Bildempfang und -aktivierung
- **Visualisierung**: Generierung von Heatmaps, die durchschnittliche Verzögerungen nach Wochentag und Stunde anzeigen
- **Zeitanalyse**: Detaillierte Analyse nach Jahr, Monat oder Woche
- **Statistiken**: Anzeige wichtiger Kennzahlen wie Gesamtzahl der verarbeiteten Bilder, durchschnittliche Verarbeitungsverzögerung, minimale und maximale Verzögerungen
- **Export**: Speichern von Analyseergebnissen und Visualisierungen

## Installation

1. Klonen Sie dieses Repository oder laden Sie den Quellcode herunter
2. Installieren Sie die erforderlichen Abhängigkeiten:

```bash
pip install -r requirements.txt
```

## Verwendung

### GUI-Modus

Für interaktive Analysen mit einer grafischen Benutzeroberfläche:

```bash
python deployment-analyse.py --gui
```

Um mit einer bestimmten Datei zu öffnen:

```bash
python deployment-analyse.py --gui --file ihre_daten.xlsx
```

### Befehlszeilenmodus

Für Batch-Verarbeitung oder Skriptintegration:

```bash
python deployment-analyse.py --file ihre_daten.xlsx --output heatmap.png
```

## Datenformat

Ihre Excel/CSV-Datei sollte diese Spalten enthalten:

| Spaltenname | Beschreibung | Format |
|-------------|-------------|--------|
| IPTC_DE Anweisung | Zeitanweisung | Enthält Zeitstempel im Format [HH:MM:SS] |
| IPTC_EN Anweisung | Englisches Äquivalent | Optional |
| Bild Upload Zeitpunkt | Zeitstempel des Bild-Uploads | DD.MM.YYYY HH:MM:SS |
| Bild Veröffentlicht | Veröffentlichungsstatus | "Ja" oder "Nein" |
| Bild Aktivierungszeitpunkt | Zeitstempel der Bildaktivierung | DD.MM.YYYY HH:MM:SS |

## Technische Details

Weitere technische Details finden Sie in der [design-simple.md](design-simple.md) Datei.

---

# Image Deployment Analysis Tool 

A tool for analyzing image deployment delays that helps you navigate the vast improbability of image processing timelines.

## Overview

The Image Deployment Analysis Tool is a specialized application designed to analyze and visualize processing delays in image distribution systems. It provides both a graphical user interface for interactive analysis and a command-line interface for automated reporting - essential equipment for any data analyst traveling through the galaxy of image processing metrics.

## Key Features

- **Data Import**: Import timestamp data from Excel (.xlsx) or CSV files
- **Data Processing**: Automatic calculation of processing delays between image receipt and activation
- **Visualization**: Generate heatmaps showing average delays by weekday and hour
- **Time Analysis**: Drill down to analyze data by year, month, or week
- **Statistics**: View key metrics including total number of processed images, average processing delay, minimum and maximum delays
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
2. **Process**: The application automatically extracts timestamps, calculates processing delays, and cleans data
3. **Analyze**: Choose a time period (year, month, week) to analyze
4. **Visualize**: View heatmaps showing processing delays by day and hour
5. **Export**: Save visualizations or processed data for reporting

## Technical Details

For more technical details, please refer to the [design-simple.md](design-simple.md) file.

## Directory Structure

```
├── deployment-analyse.py   # Main application (both GUI and CLI)
├── requirements.txt        # Python dependencies
├── design-simple.md        # Technical design document
├── data/                   # Place your input files here (optional)
├── output/                 # Generated visualizations are saved here
├── logs/                   # Application logs
└── db/                     # Database files (for future use)
```

## Troubleshooting

- **File Import Issues**: Ensure your Excel/CSV files follow the expected format
- **Visualization Errors**: Check that your data contains valid timestamps
- **GUI Not Responding**: For large files, the application may take some time to process data

In the grand scheme of things, time is relative. What seems like a processing delay might just be the universe's way of reminding you to appreciate the journey.

## License

This project is provided under the MIT License - see the LICENSE file for details.

## Copyright

© 2025 Axel Schmidt - All rights reserved.

After exactly forty-two iterations of development, we believe we've created something almost, but not quite, entirely unlike any other analysis tool.
