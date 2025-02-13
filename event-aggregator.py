import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import _ from 'lodash';

// Quellen-Gewichtungen und Qualitätsfaktoren
const SOURCE_WEIGHTS = {
  wikipedia: 0.4,
  news: {
    'oeffentlich-rechtlich': 0.35,
    'etablierte-zeitung': 0.3,
    'online-portal': 0.25,
    'sonstige': 0.2
  },
  trends: 0.25
};

// Verweildauer-Faktoren
const TIME_ON_PAGE_FACTORS = {
  short: 0.8,    // < 30s
  medium: 1.0,   // 30s - 2min
  long: 1.2      // > 2min
};

const EventAggregator = () => {
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Berechnung des Verweildauer-Faktors
  const calculateTimeOnPageFactor = (timeOnPage) => {
    if (!timeOnPage) return TIME_ON_PAGE_FACTORS.medium;
    if (timeOnPage < 30) return TIME_ON_PAGE_FACTORS.short;
    if (timeOnPage > 120) return TIME_ON_PAGE_FACTORS.long;
    return TIME_ON_PAGE_FACTORS.medium;
  };

  // Erweitertes Wikipedia-Daten-Abrufen mit Verweildauer
  const fetchWikipediaData = async (date) => {
    try {
      // Pageviews abrufen
      const pageviewResponse = await fetch(
        `https://wikimedia.org/api/rest_v1/metrics/pageviews/top/de.wikipedia/all-access/${date}`
      );
      const pageviewData = await pageviewResponse.json();

      // Verweildauer für jeden Artikel abrufen (simuliert)
      const articlesWithMetrics = await Promise.all(
        pageviewData.items[0].articles.map(async (article) => {
          // Hier würde normalerweise die echte Verweildauer-API aufgerufen werden
          const timeOnPage = Math.random() * 180; // Simulierte Verweildauer 0-180s
          
          return {
            source: 'wikipedia',
            title: article.article,
            views: article.views,
            date: date,
            timeOnPage,
            relevance: 0,
            sourceQuality: SOURCE_WEIGHTS.wikipedia
          };
        })
      );

      return articlesWithMetrics;
    } catch (error) {
      console.error('Wikipedia API Error:', error);
      return [];
    }
  };

  // Erweitertes News-API-Abrufen mit Quellenqualität
  const fetchNewsData = async (date) => {
    const API_KEY = 'YOUR_NEWS_API_KEY';
    try {
      const response = await fetch(
        `https://newsapi.org/v2/everything?q=*&from=${date}&to=${date}&language=de&sortBy=popularity&apiKey=${API_KEY}`
      );
      const data = await response.json();

      return data.articles.map(article => {
        // Bestimme Quellenqualität basierend auf Domain
        const sourceQuality = determineSourceQuality(article.source.name);
        
        return {
          source: 'news',
          title: article.title,
          date: date,
          relevance: 0,
          url: article.url,
          sourceQuality,
          source_name: article.source.name
        };
      });
    } catch (error) {
      console.error('News API Error:', error);
      return [];
    }
  };

  // Bestimmung der Quellenqualität
  const determineSourceQuality = (sourceName) => {
    const oeffentlichRechtlich = ['ard', 'zdf', 'deutschlandfunk'];
    const etablierteZeitungen = ['faz', 'sueddeutsche', 'zeit', 'spiegel'];
    const onlinePortale = ['t-online', 'web.de', 'gmx'];

    const domain = sourceName.toLowerCase();

    if (oeffentlichRechtlich.some(source => domain.includes(source))) {
      return SOURCE_WEIGHTS.news['oeffentlich-rechtlich'];
    }
    if (etablierteZeitungen.some(source => domain.includes(source))) {
      return SOURCE_WEIGHTS.news['etablierte-zeitung'];
    }
    if (onlinePortale.some(source => domain.includes(source))) {
      return SOURCE_WEIGHTS.news['online-portal'];
    }
    return SOURCE_WEIGHTS.news['sonstige'];
  };

  // Erweiterte Normalisierung mit Gewichtung
  const normalizeRelevance = (events) => {
    const maxValues = {
      wikipedia: Math.max(...events.filter(e => e.source === 'wikipedia').map(e => e.views)),
      news: Math.max(...events.filter(e => e.source === 'news').map(e => e.relevance)),
      trends: Math.max(...events.filter(e => e.source === 'trends').map(e => e.relevance))
    };

    return events.map(event => {
      let normalizedRelevance;
      
      if (event.source === 'wikipedia') {
        const baseRelevance = event.views / maxValues.wikipedia;
        const timeOnPageFactor = calculateTimeOnPageFactor(event.timeOnPage);
        normalizedRelevance = baseRelevance * timeOnPageFactor;
      } else {
        normalizedRelevance = event.relevance / maxValues[event.source];
      }

      return {
        ...event,
        normalizedRelevance: normalizedRelevance * event.sourceQuality
      };
    });
  };

  // Erweitertes Clustering mit gewichteter Relevanz
  const clusterEvents = (events) => {
    const clustered = {};
    
    events.forEach(event => {
      const date = event.date;
      if (!clustered[date]) {
        clustered[date] = [];
      }
      
      const similarEvent = clustered[date].find(e => 
        stringSimilarity(e.title, event.title) > 0.7
      );
      
      if (similarEvent) {
        // Gewichtete Kombination der Relevanzwerte
        const combinedSources = [...new Set([...similarEvent.sources, event.source])];
        const avgSourceQuality = (similarEvent.sourceQuality + event.sourceQuality) / 2;
        
        similarEvent.normalizedRelevance = Math.max(
          similarEvent.normalizedRelevance,
          event.normalizedRelevance
        );
        similarEvent.sources = combinedSources;
        similarEvent.sourceQuality = avgSourceQuality;
        
        // Speichere die höchste Verweildauer
        if (event.timeOnPage > similarEvent.timeOnPage) {
          similarEvent.timeOnPage = event.timeOnPage;
        }
      } else {
        clustered[date].push({
          ...event,
          sources: [event.source]
        });
      }
    });

    return Object.entries(clustered).flatMap(([date, events]) => 
      events.map(event => ({
        ...event,
        date,
        // Erweiterte Relevanzberechnung
        finalRelevance: event.normalizedRelevance * 
          Math.sqrt(event.sources.length) * 
          calculateTimeOnPageFactor(event.timeOnPage)
      }))
    );
  };

  // Rest des Codes bleibt größtenteils gleich, nur Anzeige wird erweitert

  return (
    <div className="w-full space-y-8">
      <div className="h-96">
        <h2 className="text-xl font-bold mb-4">Aggregierte Ereignisrelevanz</h2>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart>
            <CartesianGrid />
            <XAxis dataKey="date" />
            <YAxis dataKey="finalRelevance" />
            <ZAxis dataKey="sources.length" range={[20, 60]} />
            <Tooltip 
              content={({ payload }) => {
                if (!payload?.[0]) return null;
                const event = payload[0].payload;
                return (
                  <div className="bg-white p-2 border rounded shadow">
                    <p className="font-bold">{event.title}</p>
                    <p>Datum: {event.date}</p>
                    <p>Relevanz: {(event.finalRelevance * 100).toFixed(1)}%</p>
                    <p>Quellen: {event.sources.join(', ')}</p>
                    <p>Quellenqualität: {(event.sourceQuality * 100).toFixed(1)}%</p>
                    {event.timeOnPage && (
                      <p>Durchschn. Verweildauer: {event.timeOnPage.toFixed(1)}s</p>
                    )}
                  </div>
                );
              }}
            />
            <Scatter 
              data={events} 
              fill="#