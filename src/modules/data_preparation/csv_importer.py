"""
CSV Importer

This module provides functionality to import CSV files containing
image distribution data with timestamp information.
"""

import os
import pandas as pd
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class CSVImporter:
    """
    Class for importing and validating CSV files with image distribution data.
    """
    
    def __init__(self, delimiter=';', encoding='utf-8'):
        """
        Initialize the CSVImporter with specified parameters.
        
        Args:
            delimiter (str): The delimiter used in the CSV files.
            encoding (str): The encoding of the CSV files.
        """
        self.delimiter = delimiter
        self.encoding = encoding
        self.imported_files = []
        
    def import_file(self, file_path):
        """
        Import a single CSV file and perform basic validation.
        
        Args:
            file_path (str): Path to the CSV file to import.
            
        Returns:
            DataFrame: Pandas DataFrame containing the imported data,
                      or None if import failed.
        """
        logger.info(f"Importing file: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
                
            # Read CSV file
            df = pd.read_csv(file_path, delimiter=self.delimiter, encoding=self.encoding)
            
            # Basic validation of expected columns
            expected_columns = [
                'IPTC_DE Anweisung',
                'IPTC_EN Anweisung',
                'Bild Upload Zeitpunkt',
                'Bild Veröffentlicht',
                'Bild Aktivierungszeitpunkt'
            ]
            
            missing_columns = [col for col in expected_columns if col not in df.columns]
            if missing_columns:
                logger.warning(f"Missing columns in {file_path}: {missing_columns}")
            
            # Log import success
            self.imported_files.append(file_path)
            logger.info(f"Successfully imported {file_path} with {len(df)} rows")
            
            return df
            
        except Exception as e:
            logger.error(f"Error importing {file_path}: {str(e)}")
            return None
    
    def import_multiple_files(self, file_paths):
        """
        Import multiple CSV files and combine them into a single DataFrame.
        
        Args:
            file_paths (list): List of paths to CSV files.
            
        Returns:
            DataFrame: Combined DataFrame from all successfully imported files.
        """
        dataframes = []
        
        for file_path in file_paths:
            df = self.import_file(file_path)
            if df is not None:
                dataframes.append(df)
        
        if not dataframes:
            logger.error("No files were successfully imported")
            return None
            
        # Combine all dataframes
        combined_df = pd.concat(dataframes, ignore_index=True)
        
        # Remove duplicates if any
        initial_count = len(combined_df)
        combined_df.drop_duplicates(inplace=True)
        
        if initial_count > len(combined_df):
            logger.info(f"Removed {initial_count - len(combined_df)} duplicate rows")
        
        return combined_df
    
    def extract_timestamps(self, df):
        """
        Extract and normalize timestamps from the DataFrame.
        
        Args:
            df (DataFrame): DataFrame containing the raw data.
            
        Returns:
            DataFrame: DataFrame with normalized timestamps.
        """
        # Make a copy to avoid modifying the original
        processed_df = df.copy()
        
        # Extract timestamp from IPTC_DE Anweisung using regex
        processed_df['IPTC_Timestamp'] = processed_df['IPTC_DE Anweisung'].str.extract(r'\[(\d{2}:\d{2}:\d{2})\]').iloc[:, 0]
        
        # Convert upload and activation timestamps to datetime
        for col in ['Bild Upload Zeitpunkt', 'Bild Aktivierungszeitpunkt']:
            if col in processed_df.columns:
                processed_df[col] = pd.to_datetime(processed_df[col], format='%d.%m.%Y %H:%M:%S', errors='coerce')
        
        # Report on conversion success
        for col in ['IPTC_Timestamp', 'Bild Upload Zeitpunkt', 'Bild Aktivierungszeitpunkt']:
            if col in processed_df.columns:
                null_count = processed_df[col].isna().sum()
                if null_count > 0:
                    logger.warning(f"Column {col} has {null_count} null values after timestamp extraction")
        
        return processed_df 