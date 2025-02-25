# Analyse der Auslieferungsverzögerungen für Bilddistibutionssystem - Anforderungsdokument

## Ausgangssituation
Unser Bilddistributionssystem verarbeitet täglich eine große Anzahl von Bildern. Die Verarbeitungszeiten und potenzielle Verzögerungen sollen systematisch analysiert werden. 
## Projektziel
Entwicklung eines Analysesystems, das Verarbeitungszeiten visualisiert. Das System soll sowohl für interaktive Analysen als auch für automatisierte Berichterstellung geeignet sein.

## Funktionale Anforderungen

### Modul 1: Datenaufbereitung
- Import von CSV-Dateien mit Zeitstempeln
- Bereinigung und Normalisierung der Daten. Zusammenfügen mehrerer csv Dateien zu einem Datensatz.
- Qualitätsbewertung der Datenquellen danach priorisierung der Ereignisse
- Speicherung in einer strukturierten Datenbank. Bei neuem Analyseauftrag aktualisierung der Datenbank.

### Modul 2: Interaktive Analyse
- Webbasiertes Dashboard mit folgenden Hauptfunktionen:
  * Zeitleisten-Navigation
  * Drill-Down-Funktionalität von Jahr bis Stunde
  * Filter nach Verarbeitungszeit, Tageszeit, Wochentag
  * Vergleichsansicht verschiedener Zeiträume
  * Ereignis-Overlay mit flexibler Ein-/Ausblendung
  * Schwellenwert-Definition für Anomalien
  * Annotationsmöglichkeit für identifizierte Ereignisse
  * Es gibt einen intelligenten Preset für alle Einstellungen der direkt gute Übersichten erzeugt

### Modul 3: Reporting-Engine
- Automatische Generierung von PNG-Exporten
- Vordefinierte Report-Templates:
  * Tagesübersicht mit Peaks
  * Wochenvergleich
  * Monatsanalyse
  * Jahresübersicht
  * Anomalie-Report
  * Ereigniskorrelations-Bericht

- Batch-Verarbeitung für Massenexport
- Integration von Legenden und Erklärungen optional

### Modul 4: Ereigniskorrelation
- Automatische Erkennung von Korrelationen
- Gewichtung von Ereignissen nach Relevanz
- Berechnung statistischer Signifikanz

### Benutzerfreundlichkeit
- Intuitive Benutzeroberfläche
- Responsive Design
- Hilfesystem und Dokumentation
- Mehrsprachenfähigkeit (DE/EN)

## Lieferumfang
1. Vollständiges Analysesystem als eigenständige Windows-Anwendung:
   - Einzelne .exe Datei (keine Python-Installation erforderlich)
   - Automatische Installation aller benötigten Komponenten
   - Desktop-Verknüpfung und Startmenü-Integration
   
2. Installer für Windows:
   - Einfacher Installations-Wizard
   - Automatische Überprüfung der Systemanforderungen
   - Deinstallations-Option

3. Dokumentation:
   - Installations-Anleitung
   - Benutzerhandbuch
   - Technische Dokumentation

## Datenanalyse-Ergebnisse

### CSV-Dateistruktur
- Dateiformat: CSV mit Semikolon-Trennung
- Zeichenkodierung: vermutlich UTF-8
- Spalten:
  * IPTC_DE Anweisung (Zeitstempel + Rights Management)
  * IPTC_EN Anweisung (English equivalent)
  * Bild Upload Zeitpunkt (Timestamp format: DD.MM.YYYY HH:mm:ss)
  * Bild Veröffentlicht (Boolean: Ja/Nein)
  * Bild Aktivierungszeitpunkt (Timestamp format: DD.MM.YYYY HH:mm:ss)

### Erkenntnisse
1. **Zeitstempel-Formate**
   - IPTC Anweisungen enthalten Zeitstempel in [HH:mm:ss] Format
   - Upload und Aktivierung verwenden DD.MM.YYYY HH:mm:ss Format
   - Standardisierung der Zeitstempel wird für die Analyse benötigt

2. **Verarbeitungszeit-Berechnung**
   - Verzögerung kann berechnet werden aus:
     * Delta zwischen IPTC Zeitstempel und Upload-Zeit
     * Delta zwischen Upload und Aktivierung
   - Mehrere Ereignisse können in der gleichen Sekunde auftreten

3. **Datenkonsistenz**
   - Zweisprachige IPTC-Anweisungen (DE/EN)
   - Rights Management Info ist in Anweisungen integriert
   - Aktivierungs- und Upload-Zeitpunkte scheinen oft identisch

### Empfehlungen für die Implementierung

1. **Datenverarbeitung**
   - Parser muss robust gegen verschiedene Zeitstempel-Formate sein
   - Extraktion der Rights-Information aus IPTC-Anweisungen
   - Deduplizierung bei identischen Zeitstempeln
   - Normalisierung aller Zeitstempel auf einheitliches Format

2. **Analyse-Funktionen**
   - Gruppierung nach Minuten/Stunden für bessere Übersicht
   - Berechnung von:
     * Durchschnittliche Verarbeitungszeit
     * Verzögerungen zwischen Anweisung und Upload
     * Verzögerungen zwischen Upload und Aktivierung
   - Erkennung von Verarbeitungsspitzen

3. **Visualisierung**
   - Zeitreihen mit verschiedenen Granularitäten
   - Farbkodierung für verschiedene Verarbeitungszeiten
   - Separate Ansichten für:
     * Upload-Verzögerungen
     * Aktivierungs-Verzögerungen
     * Gesamtverarbeitungszeit

4. **Datenbankschema**
   - Normalisierte Speicherung der Zeitstempel
   - Separate Tabellen für:
     * IPTC-Anweisungen
     * Verarbeitungsereignisse
     * Rights Management
   - Indizierung für schnelle Zeitbereichsabfragen
