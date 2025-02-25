"""
Database Module

This module provides functionality for storing and retrieving
image distribution data from a structured database.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class Database:
    """
    Class for handling database operations for image distribution data.
    """
    
    def __init__(self, db_path='db/image_distribution.db'):
        """
        Initialize the database connection.
        
        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self._ensure_db_dir_exists()
        self.conn = None
        self.cursor = None
    
    def _ensure_db_dir_exists(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
    
    def connect(self):
        """
        Connect to the database.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {str(e)}")
            return False
    
    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Database connection closed")
    
    def create_tables(self):
        """
        Create tables for storing image distribution data.
        """
        try:
            if not self.conn:
                logger.error("Database connection not established")
                return False
            
            # Create the main data table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS image_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    iptc_de_instruction TEXT,
                    iptc_en_instruction TEXT,
                    iptc_timestamp TEXT,
                    upload_timestamp TEXT,
                    activation_timestamp TEXT,
                    bildankunft_timestamp TEXT,
                    processing_delay_minutes REAL,
                    is_published INTEGER,
                    rights_holder TEXT,
                    usage_rights TEXT,
                    expiry_date TEXT,
                    weekday TEXT,
                    hour INTEGER,
                    date TEXT,
                    source_file TEXT,
                    import_timestamp TEXT
                )
            ''')
            
            # Create table for analysis results
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_type TEXT,
                    analysis_params TEXT,
                    result_data TEXT,
                    created_at TEXT
                )
            ''')
            
            # Create table for data quality metrics
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT,
                    metrics TEXT,
                    timestamp TEXT
                )
            ''')
            
            self.conn.commit()
            logger.info("Database tables created successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {str(e)}")
            return False
    
    def store_data(self, df, source_file=None):
        """
        Store processed DataFrame in the database.
        
        Args:
            df (DataFrame): Processed DataFrame to store.
            source_file (str): Name of the source file.
            
        Returns:
            bool: Success status of the operation.
        """
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            # Create tables if they don't exist
            self.create_tables()
            
            # Prepare data for insertion
            import_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Map DataFrame columns to database columns
            df_for_db = df.copy()
            
            # Ensure all expected columns exist
            required_columns = {
                'IPTC_DE Anweisung': 'iptc_de_instruction',
                'IPTC_EN Anweisung': 'iptc_en_instruction',
                'IPTC_Timestamp': 'iptc_timestamp',
                'Bild Upload Zeitpunkt': 'upload_timestamp',
                'Bild Aktivierungszeitpunkt': 'activation_timestamp',
                'Bildankunft': 'bildankunft_timestamp',
                'Verzögerung_Minuten': 'processing_delay_minutes',
                'Bild Veröffentlicht': 'is_published',
                'rights_holder': 'rights_holder',
                'usage_rights': 'usage_rights',
                'expiry_date': 'expiry_date',
                'Wochentag': 'weekday',
                'Stunde': 'hour',
                'Datum': 'date'
            }
            
            # Create missing columns with NaN values
            for col, db_col in required_columns.items():
                if col not in df_for_db.columns:
                    df_for_db[col] = pd.NA
            
            # Convert boolean to integer for SQLite
            if 'Bild Veröffentlicht' in df_for_db.columns:
                df_for_db['Bild Veröffentlicht'] = df_for_db['Bild Veröffentlicht'].map(
                    {'Ja': 1, 'Nein': 0}
                ).fillna(0).astype(int)
            
            # Convert datetime columns to strings for SQLite
            for col in ['Bild Upload Zeitpunkt', 'Bild Aktivierungszeitpunkt', 'Bildankunft', 'Datum']:
                if col in df_for_db.columns and pd.api.types.is_datetime64_any_dtype(df_for_db[col]):
                    df_for_db[col] = df_for_db[col].astype(str)
            
            # Add source file and import timestamp
            df_for_db['source_file'] = source_file
            df_for_db['import_timestamp'] = import_timestamp
            
            # Handle NA values by replacing them with None
            df_for_db = df_for_db.replace({pd.NA: None})
            
            # Insert data row by row (less efficient but safer)
            for _, row in df_for_db.iterrows():
                self.cursor.execute('''
                    INSERT INTO image_data (
                        iptc_de_instruction, iptc_en_instruction, iptc_timestamp,
                        upload_timestamp, activation_timestamp, bildankunft_timestamp,
                        processing_delay_minutes, is_published, rights_holder,
                        usage_rights, expiry_date, weekday, hour, date,
                        source_file, import_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('IPTC_DE Anweisung'),
                    row.get('IPTC_EN Anweisung'),
                    row.get('IPTC_Timestamp'),
                    row.get('Bild Upload Zeitpunkt'),
                    row.get('Bild Aktivierungszeitpunkt'),
                    row.get('Bildankunft'),
                    row.get('Verzögerung_Minuten'),
                    row.get('Bild Veröffentlicht'),
                    row.get('rights_holder'),
                    row.get('usage_rights'),
                    row.get('expiry_date'),
                    row.get('Wochentag'),
                    row.get('Stunde'),
                    row.get('Datum'),
                    source_file,
                    import_timestamp
                ))
            
            self.conn.commit()
            logger.info(f"Successfully stored {len(df)} rows in the database")
            return True
            
        except Exception as e:
            logger.error(f"Error storing data in database: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False
            
        finally:
            self.close()
    
    def store_quality_metrics(self, metrics, source_file):
        """
        Store data quality metrics in the database.
        
        Args:
            metrics (dict): Quality metrics to store.
            source_file (str): Name of the source file.
            
        Returns:
            bool: Success status of the operation.
        """
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            # Create tables if they don't exist
            self.create_tables()
            
            # Convert metrics to JSON
            metrics_json = json.dumps(metrics)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert metrics
            self.cursor.execute('''
                INSERT INTO quality_metrics (source_file, metrics, timestamp)
                VALUES (?, ?, ?)
            ''', (source_file, metrics_json, timestamp))
            
            self.conn.commit()
            logger.info(f"Stored quality metrics for {source_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing quality metrics: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False
            
        finally:
            self.close()
    
    def query_data(self, query, params=None):
        """
        Execute a query against the database.
        
        Args:
            query (str): SQL query to execute.
            params (tuple): Parameters for the query.
            
        Returns:
            DataFrame: Results as a pandas DataFrame.
        """
        if not self.conn:
            if not self.connect():
                return None
        
        try:
            if params:
                result = pd.read_sql_query(query, self.conn, params=params)
            else:
                result = pd.read_sql_query(query, self.conn)
                
            logger.info(f"Query returned {len(result)} rows")
            return result
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return None
            
        finally:
            self.close()
    
    def get_distinct_dates(self):
        """
        Get distinct dates available in the database.
        
        Returns:
            list: List of distinct dates.
        """
        query = "SELECT DISTINCT date FROM image_data ORDER BY date"
        result = self.query_data(query)
        
        if result is not None and not result.empty:
            return result['date'].tolist()
        return [] 