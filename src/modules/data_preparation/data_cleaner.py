"""
Data Cleaner

This module handles data cleaning, normalization, and quality assessment
for the image distribution analysis system.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Class for cleaning, normalizing, and assessing data quality.
    """
    
    def __init__(self):
        """Initialize the DataCleaner."""
        self.quality_scores = {}
    
    def clean_data(self, df):
        """
        Clean the data by removing invalid entries and normalizing formats.
        
        Args:
            df (DataFrame): Raw DataFrame to clean.
            
        Returns:
            DataFrame: Cleaned DataFrame.
        """
        logger.info("Starting data cleaning process")
        
        # Make a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Remove rows with missing critical data
        critical_columns = ['IPTC_Timestamp', 'Bild Upload Zeitpunkt', 'Bild Aktivierungszeitpunkt']
        initial_count = len(cleaned_df)
        cleaned_df.dropna(subset=critical_columns, inplace=True)
        dropped_count = initial_count - len(cleaned_df)
        
        if dropped_count > 0:
            logger.info(f"Removed {dropped_count} rows with missing critical data")
        
        # Process Bildankunft timestamp with day consideration
        cleaned_df['Bildankunft'] = cleaned_df.apply(self._combine_date_time, axis=1)
        
        # Calculate delay in minutes
        cleaned_df['Verzögerung_Minuten'] = (
            cleaned_df['Bild Aktivierungszeitpunkt'] - cleaned_df['Bildankunft']
        ).dt.total_seconds() / 60
        
        # Remove rows with negative delays (likely timestamp errors)
        negative_delays = cleaned_df['Verzögerung_Minuten'] < 0
        if negative_delays.sum() > 0:
            logger.warning(f"Removed {negative_delays.sum()} rows with negative processing delays")
            cleaned_df = cleaned_df[~negative_delays]
        
        # Remove extreme outliers (delays > 24 hours)
        extreme_outliers = cleaned_df['Verzögerung_Minuten'] > 24 * 60
        if extreme_outliers.sum() > 0:
            logger.warning(f"Removed {extreme_outliers.sum()} rows with delays > 24 hours")
            cleaned_df = cleaned_df[~extreme_outliers]
        
        # Add additional time-based features
        cleaned_df['Wochentag'] = cleaned_df['Bildankunft'].dt.strftime('%A')
        cleaned_df['Stunde'] = cleaned_df['Bildankunft'].dt.hour
        cleaned_df['Datum'] = cleaned_df['Bildankunft'].dt.date
        
        logger.info(f"Data cleaning complete. {len(cleaned_df)} rows remaining")
        return cleaned_df
    
    def _combine_date_time(self, row):
        """
        Combine date from activation timestamp with time from IPTC timestamp.
        Adjusts for day boundaries when needed.
        
        Args:
            row: DataFrame row with IPTC_Timestamp and Bild Aktivierungszeitpunkt.
            
        Returns:
            datetime: Combined datetime object.
        """
        try:
            # Get the base date from the activation timestamp
            base_date = row['Bild Aktivierungszeitpunkt'].date()
            
            # Parse the IPTC timestamp
            iptc_time = datetime.strptime(row['IPTC_Timestamp'], '%H:%M:%S').time()
            
            # Combine date and time
            bildankunft = datetime.combine(base_date, iptc_time)
            
            # If the result is later than the activation timestamp, it's likely from the previous day
            if bildankunft > row['Bild Aktivierungszeitpunkt']:
                bildankunft = bildankunft - timedelta(days=1)
                
            return bildankunft
            
        except (ValueError, AttributeError, TypeError) as e:
            logger.debug(f"Error combining date and time: {str(e)}")
            return pd.NaT
    
    def assess_quality(self, df):
        """
        Assess the quality of the data source.
        
        Args:
            df (DataFrame): DataFrame to assess.
            
        Returns:
            dict: Quality metrics.
        """
        logger.info("Assessing data quality")
        
        quality_metrics = {
            'total_rows': len(df),
            'missing_data_percentage': df.isnull().mean().to_dict(),
            'completeness': 1 - df.isnull().mean().mean(),
            'delay_statistics': {
                'mean': df['Verzögerung_Minuten'].mean(),
                'median': df['Verzögerung_Minuten'].median(),
                'std': df['Verzögerung_Minuten'].std(),
                'min': df['Verzögerung_Minuten'].min(),
                'max': df['Verzögerung_Minuten'].max()
            }
        }
        
        # Store quality metrics
        file_hash = hash(tuple(sorted(df.columns)))
        self.quality_scores[file_hash] = quality_metrics
        
        logger.info(f"Data quality assessment complete. Completeness score: {quality_metrics['completeness']:.2f}")
        return quality_metrics
    
    def normalize_rights_info(self, df):
        """
        Extract and normalize rights management information from IPTC instructions.
        
        Args:
            df (DataFrame): DataFrame with IPTC instructions.
            
        Returns:
            DataFrame: DataFrame with normalized rights information.
        """
        logger.info("Normalizing rights management information")
        
        # Extract rights info using regex patterns
        rights_patterns = {
            'rights_holder': r'©\s*([^,\[\]]+)',
            'usage_rights': r'nur\s+([^,\[\]]+)',
            'expiry_date': r'bis\s+(\d{2}\.\d{2}\.\d{4})'
        }
        
        normalized_df = df.copy()
        
        for right_type, pattern in rights_patterns.items():
            normalized_df[right_type] = normalized_df['IPTC_DE Anweisung'].str.extract(pattern, expand=False)
        
        # Count extracted rights information
        extraction_counts = {
            right_type: (~normalized_df[right_type].isna()).sum()
            for right_type in rights_patterns.keys()
        }
        
        logger.info(f"Rights information extraction complete: {extraction_counts}")
        return normalized_df 