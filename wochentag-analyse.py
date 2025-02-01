import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import locale
import os

# Deutsche Lokalisierung für Wochentage
try:
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
except:
    locale.setlocale(locale.LC_TIME, 'German')

# Alte Heatmap löschen, falls vorhanden
if os.path.exists('verzögerungen_heatmap.png'):
    os.remove('verzögerungen_heatmap.png')

# Excel-Datei einlesen
df = pd.read_excel('Editorial_Importzeit_mgo_2025-01-31_15_43_31.xlsx')

# Daten inspizieren
print("Erste Zeilen der Daten:")
print(df.head())
print("\nSpaltennamen:")
print(df.columns.tolist())

# Vierte Spalte inspizieren
print("\nInhalt der vierten Spalte:")
print(df.iloc[:, 3].head())

# Zeitstempel aus der ersten Spalte (IPTC_DE Anweisung) bereinigen
df['Bildankunft_Zeit'] = df['IPTC_DE Anweisung'].str.extract(r'\[(\d{2}:\d{2}:\d{2})\]').iloc[:, 0]

# Zeitstempel aus der letzten Spalte (Bild Aktivierungszeitpunkt) konvertieren
df['Onlinestellung'] = pd.to_datetime(df['Bild Aktivierungszeitpunkt'])

# Bildankunft berechnen
df['Bildankunft'] = pd.to_datetime(
    df['Onlinestellung'].dt.strftime('%Y-%m-%d') + ' ' + df['Bildankunft_Zeit']
)

# Debug-Ausgabe
print("\nErste 5 Zeilen der Zeitstempel:")
for i in range(5):
    print(f"\nZeile {i+1}:")
    print(f"Bildankunft: {df['Bildankunft'].iloc[i]}")
    print(f"Onlinestellung: {df['Onlinestellung'].iloc[i]}")

# Berechnung der Verzögerung in Minuten
df['Verzögerung'] = (df['Onlinestellung'] - df['Bildankunft']).dt.total_seconds() / 60

print("\nErste 5 Verzögerungen (Minuten):")
print(df['Verzögerung'].head())

# Extrahieren von Wochentag und Stunde aus dem Bildankunft-Zeitstempel
df['Wochentag'] = df['Bildankunft'].dt.strftime('%A')  # Explizit als String
df['Stunde'] = df['Bildankunft'].dt.hour

# Debug-Ausgabe der einzigartigen Wochentage
print("\nGefundene Wochentage:")
print(df['Wochentag'].unique())

# Erstellen einer Pivot-Tabelle für die Heatmap
pivot_table = pd.pivot_table(
    df,
    values='Verzögerung',
    index='Wochentag',
    columns='Stunde',
    aggfunc='mean',
    fill_value=0  # Fülle NaN-Werte mit 0
)

# Sortieren der Wochentage in richtiger Reihenfolge
wochentage_order = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
pivot_table = pivot_table.reindex(wochentage_order)

# Debug-Ausgabe der Pivot-Tabelle
print("\nPivot-Tabelle Form:", pivot_table.shape)
print("\nPivot-Tabelle Inhalt:")
print(pivot_table)

# Matplotlib Figure schließen, falls noch offen
plt.close('all')

# Erstellen der Heatmap
plt.figure(figsize=(15, 8))
sns.heatmap(pivot_table, 
            cmap='YlOrRd',  # Farbschema: Gelb zu Orange zu Rot
            annot=True,     # Zeigt Werte in den Zellen
            fmt='.0f',      # Formatierung der Zahlen (keine Dezimalstellen)
            cbar_kws={'label': 'Durchschnittliche Verzögerung (Minuten)'},
            mask=pivot_table.isna()  # Maskiere NaN-Werte
)

plt.title('Durchschnittliche Verzögerungen nach Wochentag und Uhrzeit')
plt.xlabel('Stunde des Tages')
plt.ylabel('Wochentag')

# Speichern der Grafik
plt.savefig('verzögerungen_heatmap.png', bbox_inches='tight', dpi=300)
plt.close()

# Gesamtstatistik
print("\nGesamtstatistik:")
print(f"Anzahl der Datensätze: {len(df)}")
print(f"Durchschnittliche Verzögerung: {df['Verzögerung'].mean():.2f} Minuten")
print(f"Maximale Verzögerung: {df['Verzögerung'].max():.2f} Minuten")
print(f"Minimale Verzögerung: {df['Verzögerung'].min():.2f} Minuten")

# Statistik pro Wochentag
print("\nStatistik pro Wochentag:")
wochentag_stats = df.groupby('Wochentag').agg({
    'Verzögerung': ['count', 'mean', 'min', 'max']
}).round(2)
print(wochentag_stats)
