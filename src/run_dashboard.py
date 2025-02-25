#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dashboard Runner

This script initializes and runs the simplified interactive dashboard for the
image distribution analysis system.
"""

import os
import sys
import logging
import argparse
from modules.data_preparation.database import Database
from modules.interactive_analysis.timeline_analyzer import TimelineAnalyzer
from modules.interactive_analysis.anomaly_detector import AnomalyDetector
from modules.interactive_analysis.dashboard import Dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Run the interactive dashboard for image distribution analysis")
    
    parser.add_argument(
        "--db-path",
        type=str,
        default="db/image_distribution.db",
        help="Path to the SQLite database file (default: db/image_distribution.db)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Port to run the dashboard on (default: 8050)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run the dashboard in debug mode"
    )
    
    return parser.parse_args()

def main():
    """
    Main function to run the dashboard.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Check if database file exists
    if not os.path.exists(args.db_path):
        logger.error(f"Database file not found: {args.db_path}")
        logger.info("Please import your data first using the following command:")
        logger.info(f"python src/cli.py import --file yourfile.csv --db-path {args.db_path} --store")
        logger.info("For more information on importing data, run: python src/cli.py import --help")
        return
    
    try:
        # Initialize database connection
        logger.info(f"Connecting to database: {args.db_path}")
        db = Database(args.db_path)
        
        # Initialize analyzers
        logger.info("Initializing timeline analyzer")
        timeline_analyzer = TimelineAnalyzer(db_connection=db)
        
        logger.info("Initializing anomaly detector")
        anomaly_detector = AnomalyDetector(db_connection=db)
        
        # Initialize dashboard
        logger.info("Initializing dashboard")
        dashboard = Dashboard(
            db_connection=db,
            timeline_analyzer=timeline_analyzer,
            anomaly_detector=anomaly_detector
        )
        
        # Run the dashboard
        logger.info(f"Starting dashboard on port {args.port}")
        app = dashboard.initialize_app()
        
        # Display access instructions
        url = f"http://127.0.0.1:{args.port}"
        logger.info("=" * 60)
        logger.info(f"Dashboard is running at: {url}")
        logger.info("Open the above URL in your web browser to access the dashboard")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("=" * 60)
        
        # Start the server
        dashboard.run_server(debug=args.debug, port=args.port)
        
    except Exception as e:
        logger.error(f"Error running dashboard: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return

if __name__ == "__main__":
    main() 