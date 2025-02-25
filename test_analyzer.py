#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the Image Distribution Analysis Tool

This script demonstrates the functionality of the tool
by importing sample data, cleaning it, analyzing it,
and generating visualizations.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import modules from the project
from src.modules.data_preparation.csv_importer import CSVImporter
from src.modules.data_preparation.data_cleaner import DataCleaner
from src.modules.data_preparation.database import Database
from src.modules.interactive_analysis.timeline_analyzer import TimelineAnalyzer
from src.modules.interactive_analysis.anomaly_detector import AnomalyDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

def test_data_import():
    """Test the CSV data import functionality."""
    logger.info("=== Testing Data Import ===")
    
    # Create a CSV importer
    importer = CSVImporter(delimiter=';', encoding='utf-8')
    
    # Get CSV files from data directory
    data_dir = 'data'
    csv_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        logger.error("No CSV files found in the data directory")
        return None
    
    # Choose the first CSV file for testing
    test_file = csv_files[0]
    logger.info(f"Testing with file: {test_file}")
    
    # Import the CSV file
    df = importer.import_file(test_file)
    
    if df is not None:
        logger.info(f"Successfully imported {len(df)} rows from {test_file}")
        # Print sample data
        logger.info("Sample data:")
        print(df.head())
        return df
    else:
        logger.error("Failed to import data")
        return None

def test_data_cleaning(df):
    """Test the data cleaning functionality."""
    logger.info("=== Testing Data Cleaning ===")
    
    if df is None:
        logger.error("No data to clean")
        return None
    
    # Create a data cleaner
    cleaner = DataCleaner()
    
    # Extract timestamps from the data
    df_with_timestamps = CSVImporter().extract_timestamps(df)
    
    # Clean the data
    cleaned_df = cleaner.clean_data(df_with_timestamps)
    
    if cleaned_df is not None:
        logger.info(f"Successfully cleaned data. {len(cleaned_df)} rows remaining")
        # Print sample cleaned data
        logger.info("Sample cleaned data:")
        print(cleaned_df.head())
        
        # Print data statistics
        logger.info("Data statistics:")
        print(cleaned_df.describe())
        
        # Assess data quality
        quality_metrics = cleaner.assess_quality(cleaned_df)
        logger.info("Data quality metrics:")
        print(quality_metrics)
        
        return cleaned_df
    else:
        logger.error("Failed to clean data")
        return None

def test_database_storage(df):
    """Test the database storage functionality."""
    logger.info("=== Testing Database Storage ===")
    
    if df is None:
        logger.error("No data to store")
        return None
    
    # Create a database connection
    db = Database(db_path='db/test_image_distribution.db')
    
    # Connect to the database
    if db.connect():
        # Store the data
        success = db.store_data(df, source_file='test_data.csv')
        
        if success:
            logger.info("Successfully stored data in the database")
            
            # Test querying the data
            query = "SELECT COUNT(*) as count FROM image_data"
            result = db.query_data(query)
            
            if result is not None:
                logger.info(f"Database query result: {result.iloc[0]['count']} rows")
            
            return db
        else:
            logger.error("Failed to store data in the database")
            return None
    else:
        logger.error("Failed to connect to the database")
        return None

def test_timeline_analysis(df, db=None):
    """Test the timeline analysis functionality."""
    logger.info("=== Testing Timeline Analysis ===")
    
    if df is None:
        logger.error("No data for timeline analysis")
        return None
    
    # Create a timeline analyzer
    analyzer = TimelineAnalyzer(db_connection=db)
    
    # Load data directly
    analyzer.load_data(data=df)
    
    # Set time granularity
    analyzer.set_time_granularity('hour')
    
    # Analyze time patterns
    time_patterns = analyzer.analyze_time_pattern()
    
    if time_patterns is not None:
        logger.info(f"Successfully analyzed time patterns. {len(time_patterns)} time groups")
        
        # Print sample time patterns
        logger.info("Sample time patterns:")
        print(time_patterns.head())
        
        # Create a timeline plot
        fig = analyzer.plot_timeline(
            metric='mean', 
            title='Mean Processing Delay by Hour',
            save_path='output/timeline_plot.png'
        )
        
        if fig is not None:
            logger.info("Successfully created timeline plot")
        
        # Create a weekday-hour heatmap
        fig = analyzer.plot_weekday_hour_heatmap(
            save_path='output/weekday_hour_heatmap.png'
        )
        
        if fig is not None:
            logger.info("Successfully created weekday-hour heatmap")
        
        return analyzer
    else:
        logger.error("Failed to analyze time patterns")
        return None

def test_anomaly_detection(df, db=None):
    """Test the anomaly detection functionality."""
    logger.info("=== Testing Anomaly Detection ===")
    
    if df is None:
        logger.error("No data for anomaly detection")
        return None
    
    # Create an anomaly detector
    detector = AnomalyDetector(db_connection=db)
    
    # Load data directly
    detector.load_data(data=df)
    
    # Set threshold method
    detector.set_threshold_method('zscore', value=2.5)
    
    # Detect anomalies
    anomalies = detector.detect_anomalies()
    
    if anomalies is not None:
        logger.info(f"Successfully detected {len(anomalies)} anomalies")
        
        # Print sample anomalies
        logger.info("Sample anomalies:")
        print(anomalies.head())
        
        # Get anomaly summary
        summary = detector.get_summary()
        logger.info("Anomaly summary:")
        print(summary)
        
        # Create an anomaly plot
        fig = detector.plot_anomalies(
            save_path='output/anomalies_plot.png'
        )
        
        if fig is not None:
            logger.info("Successfully created anomalies plot")
        
        return detector
    else:
        logger.error("Failed to detect anomalies")
        return None

def main():
    """Main test function."""
    logger.info("Starting test of Image Distribution Analysis Tool")
    
    # Test data import
    df = test_data_import()
    
    if df is not None:
        # Test data cleaning
        cleaned_df = test_data_cleaning(df)
        
        if cleaned_df is not None:
            # Test database storage
            db = test_database_storage(cleaned_df)
            
            # Test timeline analysis
            analyzer = test_timeline_analysis(cleaned_df, db)
            
            # Test anomaly detection
            detector = test_anomaly_detection(cleaned_df, db)
    
    logger.info("Test completed")

if __name__ == "__main__":
    main() 