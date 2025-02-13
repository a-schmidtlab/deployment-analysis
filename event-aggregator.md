# Event Aggregator Dokumentation

## Übersicht
Der Event Aggregator ist ein System zur Zusammenführung und Analyse von Ereignisdaten aus verschiedenen Quellen. Er kombiniert Daten aus Wikipedia, NewsAPI und Google Trends, um eine gewichtete Liste relevanter Ereignisse zu erstellen.

## Kernfunktionen

### 1. Datenquellen und Gewichtung

#### Wikipedia Pageviews
- Primärquelle für Ereignisrelevanz
- Zusätzliche Metriken:
  - Verweildauer pro Artikel (durchschnittliche Sessiondauer)
  - Bounce-Rate
  - Wiederkehrende Besucher
- Gewichtungsfaktor: 0.4 (höchste Verlässlichkeit)

#### NewsAPI
- Nachrichtenquelle mit Qualitätsrating
- Gewichtungsfaktoren basierend auf Nachrichtenquelle:
  - Öffentlich-rechtliche Medien: 0.35
  - Etablierte Zeitungen: 0.3
  - Online-Nachrichtenportale: 0.25
  - Sonstige Quellen: 0.2

#### Google Trends
- Indikator für öffentliches Interesse
- Gewichtungsfaktor: 0.25 (niedrigste Verlässlichkeit)
- Normalisierung der relativen Trends-Werte

### 2. Relevanzberechnung

Die finale Relevanz eines Ereignisses wird wie folgt berechnet:

```javascript
finalRelevance = (
  (wikipediaScore * 0.4) +
  (newsScore * sourceQualityFactor) +
  (trendScore * 0.25)
) * timeOnPageFactor
```

Dabei ist:
- wikipediaScore: Normalisierte Pageviews
- newsScore: Normalisierte Nachrichtenpräsenz
- sourceQualityFactor: Gewichtung basierend auf Quellenqualität
- trendScore: Normalisierter Google Trends Wert
- timeOnPageFactor: Multiplikator basierend auf Verweildauer

### 3. Verweildauer-Analyse

Die Wikipedia-Verweildauer wird wie folgt einbezogen:
- Kurze Verweildauer (<30s): Faktor 0.8
- Mittlere Verweildauer (30s-2min): Faktor 1.0
- Lange Verweildauer (>2min): Faktor 1.2

Diese Faktoren werden auf die Gesamtrelevanz angewendet, um Artikel mit höherer Leserinteraktion stärker zu gewichten.

### 4. Quellenqualität

Die Quellenqualität wird anhand folgender Kriterien bewertet:
- Etablierte Reputation
- Faktenchecking-Prozesse
- Redaktionelle Standards
- Transparenz
- Unabhängigkeit

### 5. Ereignis-Clustering

#### Ähnlichkeitserkennung
- Levenshtein-Distanz für Textvergeleich
- Threshold: 0.7 (70% Ähnlichkeit)
- Berücksichtigung von Mehrsprachigkeit

#### Clustering-Prozess
1. Gruppierung nach Datum
2. Ähnlichkeitsvergleich innerhalb Datumsgruppen
3. Zusammenführung ähnlicher Ereignisse
4. Neuberechnung der Relevanz

## Implementierungsdetails

### Datenstruktur eines Ereignisses
```javascript
{
  title: string,
  date: string,
  sources: string[],
  originalRelevance: number,
  normalizedRelevance: number,
  finalRelevance: number,
  timeOnPage: number,
  sourceQuality: number,
  clusterId: string
}
```

### Hauptkomponenten
1. Datenabruf (DataFetcher)
2. Normalisierung (Normalizer)
3. Clustering (EventClusterer)
4. Relevanzberechnung (RelevanceCalculator)
5. Visualisierung (EventVisualizer)

## Performance-Optimierung

### Caching
- Zwischenspeicherung der API-Responses
- Caching der Clustering-Ergebnisse
- Speicherung der Quellenqualitätsbewertungen

### Batch-Verarbeitung
- Gruppierung von API-Anfragen
- Parallele Verarbeitung von Datenquellen
- Inkrementelle Updates

## Fehlerbehebung

### Häufige Probleme
1. API-Ratenlimits
2. Inkonsistente Datumsformate
3. Fehlende Metriken

### Lösungsstrategien
1. Exponentielles Backoff
2. Datumsnormalisierung
3. Fallback-Werte für fehlende Daten

## Ausblick und Verbesserungsmöglichkeiten

1. Machine Learning für Clustering
2. Sentiment-Analyse
3. Automatische Quellenqualitätsbewertung
4. Echtzeit-Updates
5. Verbesserte Mehrsprachenerkennung