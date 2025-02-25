#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command-Line Interface for the Image Distribution Analysis Tool

This module provides a command-line interface to interact with
the image distribution analysis tool.
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
import pandas as pd

# Import modules from the project
from modules.data_preparation.csv_importer import CSVImporter
from modules.data_preparation.data_cleaner import DataCleaner
from modules.data_preparation.database import Database
from modules.interactive_analysis.timeline_analyzer import TimelineAnalyzer
from modules.interactive_analysis.anomaly_detector import AnomalyDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def import_data(args):
    """Import data from CSV files."""
    logger.info(f"Importing data from {args.file}")
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Create a CSV importer
    importer = CSVImporter(delimiter=args.delimiter, encoding=args.encoding)
    
    # Import the CSV file
    if args.file == 'all':
        # Import all CSV files in the data directory
        data_dir = args.data_dir
        csv_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
        if not csv_files:
            logger.error(f"No CSV files found in {data_dir}")
            return
        
        logger.info(f"Importing {len(csv_files)} CSV files")
        df = importer.import_multiple_files(csv_files)
    else:
        # Import a single CSV file
        file_path = os.path.join(args.data_dir, args.file)
        df = importer.import_file(file_path)
    
    if df is None:
        logger.error("Failed to import data")
        return
    
    logger.info(f"Successfully imported {len(df)} rows")
    
    # Extract timestamps
    df = importer.extract_timestamps(df)
    
    # Clean the data
    cleaner = DataCleaner()
    cleaned_df = cleaner.clean_data(df)
    
    if cleaned_df is None:
        logger.error("Failed to clean data")
        return
    
    logger.info(f"Successfully cleaned data. {len(cleaned_df)} rows remaining")
    
    # Save processed data to CSV if requested
    if args.output:
        output_path = os.path.join('output', args.output)
        cleaned_df.to_csv(output_path, index=False)
        logger.info(f"Saved processed data to {output_path}")
    
    # Store in database if requested
    if args.store:
        db = Database(db_path=args.db_path)
        if db.connect():
            source_file = args.file if args.file != 'all' else 'multiple_files'
            success = db.store_data(cleaned_df, source_file=source_file)
            if success:
                logger.info(f"Successfully stored data in database: {args.db_path}")
            else:
                logger.error("Failed to store data in database")
        else:
            logger.error("Failed to connect to database")

def analyze_timeline(args):
    """Analyze time patterns in the data."""
    logger.info("Analyzing time patterns")
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Connect to the database
    db = Database(db_path=args.db_path)
    
    # Create timeline analyzer
    analyzer = TimelineAnalyzer(db_connection=db)
    
    # Set time range if provided
    date_range = None
    if args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        date_range = (start_date, end_date)
    
    # Load data
    success = analyzer.load_data(date_range=date_range)
    if not success:
        logger.error("Failed to load data for analysis")
        return
    
    # Set time granularity
    analyzer.set_time_granularity(args.granularity)
    
    # Create plots
    if args.plot_type == 'timeline' or args.plot_type == 'all':
        # Create timeline plot
        fig = analyzer.plot_timeline(
            metric=args.metric,
            title=f"{args.metric.capitalize()} Processing Delay by {args.granularity.capitalize()}",
            save_path=os.path.join('output', f"timeline_{args.granularity}_{args.metric}.png")
        )
        if fig:
            logger.info(f"Created timeline plot for {args.granularity} {args.metric}")
    
    if args.plot_type == 'heatmap' or args.plot_type == 'all':
        # Create weekday-hour heatmap
        fig = analyzer.plot_weekday_hour_heatmap(
            save_path=os.path.join('output', "weekday_hour_heatmap.png")
        )
        if fig:
            logger.info("Created weekday-hour heatmap")
    
    # Compare time periods if requested
    if args.compare_with:
        try:
            # Parse comparison period
            period1_start = datetime.strptime(args.start_date, '%Y-%m-%d')
            period1_end = datetime.strptime(args.end_date, '%Y-%m-%d')
            
            # Calculate period2 based on comparison type
            if args.compare_with == 'prev_day':
                period2_start = period1_start - timedelta(days=1)
                period2_end = period1_end - timedelta(days=1)
            elif args.compare_with == 'prev_week':
                period2_start = period1_start - timedelta(weeks=1)
                period2_end = period1_end - timedelta(weeks=1)
            elif args.compare_with == 'prev_month':
                # Approximate month as 30 days
                period2_start = period1_start - timedelta(days=30)
                period2_end = period1_end - timedelta(days=30)
            else:
                logger.error(f"Invalid comparison type: {args.compare_with}")
                return
            
            # Compare periods
            comparison = analyzer.compare_time_periods(
                period1=(period1_start, period1_end),
                period2=(period2_start, period2_end),
                metric=args.metric
            )
            
            if comparison:
                logger.info("Time period comparison results:")
                print(f"Period 1 ({period1_start.date()} to {period1_end.date()}): {comparison['period1']['value']:.2f}")
                print(f"Period 2 ({period2_start.date()} to {period2_end.date()}): {comparison['period2']['value']:.2f}")
                print(f"Difference: {comparison['difference']:.2f}")
                print(f"Percent change: {comparison['percent_change']:.2f}%")
            
        except ValueError as e:
            logger.error(f"Error comparing time periods: {str(e)}")

def detect_anomalies(args):
    """Detect anomalies in the data."""
    logger.info("Detecting anomalies")
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Connect to the database
    db = Database(db_path=args.db_path)
    
    # Create anomaly detector
    detector = AnomalyDetector(db_connection=db)
    
    # Set time range if provided
    date_range = None
    if args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        date_range = (start_date, end_date)
    
    # Load data
    success = detector.load_data(date_range=date_range)
    if not success:
        logger.error("Failed to load data for anomaly detection")
        return
    
    # Set threshold method
    detector.set_threshold_method(args.method, value=args.threshold)
    
    # Detect anomalies
    anomalies = detector.detect_anomalies()
    
    if anomalies is None or len(anomalies) == 0:
        logger.info("No anomalies detected")
        return
    
    # Print anomaly summary
    summary = detector.get_summary()
    logger.info("Anomaly detection summary:")
    print(f"Total anomalies: {summary['count']} ({summary['percentage']:.2f}% of data)")
    print(f"Average anomaly score: {summary['avg_score']:.2f}")
    print(f"Min delay: {summary['min_delay']:.2f} minutes")
    print(f"Max delay: {summary['max_delay']:.2f} minutes")
    print(f"Average delay: {summary['avg_delay']:.2f} minutes")
    
    # Create anomaly plot
    fig = detector.plot_anomalies(
        save_path=os.path.join('output', f"anomalies_{args.method}.png")
    )
    if fig:
        logger.info(f"Created anomaly plot using {args.method} method")
    
    # Save anomalies to CSV if requested
    if args.output:
        output_path = os.path.join('output', args.output)
        anomalies.to_csv(output_path, index=False)
        logger.info(f"Saved anomalies to {output_path}")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='Image Distribution Analysis Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import data from CSV files')
    import_parser.add_argument('--file', default='all', help='CSV file to import (or "all" for all files)')
    import_parser.add_argument('--data-dir', default='data', help='Directory containing CSV files')
    import_parser.add_argument('--delimiter', default=';', help='CSV delimiter')
    import_parser.add_argument('--encoding', default='utf-8', help='CSV encoding')
    import_parser.add_argument('--output', help='Output CSV file name')
    import_parser.add_argument('--store', action='store_true', help='Store data in database')
    import_parser.add_argument('--db-path', default='db/image_distribution.db', help='Database path')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze time patterns')
    analyze_parser.add_argument('--granularity', default='hour', choices=['minute', 'hour', 'day', 'week', 'month', 'year'], help='Time granularity')
    analyze_parser.add_argument('--metric', default='mean', choices=['count', 'mean', 'median', 'min', 'max'], help='Metric to analyze')
    analyze_parser.add_argument('--plot-type', default='all', choices=['timeline', 'heatmap', 'all'], help='Type of plot to create')
    analyze_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    analyze_parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    analyze_parser.add_argument('--compare-with', choices=['prev_day', 'prev_week', 'prev_month'], help='Compare with previous period')
    analyze_parser.add_argument('--db-path', default='db/image_distribution.db', help='Database path')
    
    # Anomaly command
    anomaly_parser = subparsers.add_parser('anomaly', help='Detect anomalies')
    anomaly_parser.add_argument('--method', default='zscore', choices=['zscore', 'iqr', 'percentile', 'absolute'], help='Anomaly detection method')
    anomaly_parser.add_argument('--threshold', type=float, default=3.0, help='Anomaly threshold value')
    anomaly_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    anomaly_parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    anomaly_parser.add_argument('--output', help='Output CSV file name')
    anomaly_parser.add_argument('--db-path', default='db/image_distribution.db', help='Database path')
    
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == 'import':
        import_data(args)
    elif args.command == 'analyze':
        analyze_timeline(args)
    elif args.command == 'anomaly':
        detect_anomalies(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 