#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Image Deployment Analysis Tool

A simplified GUI application for analyzing image deployment delays.
This tool allows importing Excel/CSV files and visualizing processing delays
with options to customize the analysis and dive deeper when needed.
.
(c) 2025 by Axel Schmidt
"""

import os
import sys
import traceback
import configparser
import logging
from logging.handlers import RotatingFileHandler
import time
import tempfile

# Set up robust error logging before anything else
def setup_logging():
    """Set up logging with rotation and proper formatting"""
    log_dir = get_writable_dir("logs")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Configure formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler for all logs
    log_file = os.path.join(log_dir, 'application.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Error log for critical errors
    error_file = os.path.join(log_dir, 'error.log')
    error_handler = RotatingFileHandler(error_file, maxBytes=2*1024*1024, backupCount=3)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Console handler for basic output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger

# Define global logger
logger = None
app_config = None

def load_config():
    """Load configuration from app_config.ini if it exists"""
    global app_config
    
    app_config = configparser.ConfigParser()
    
    # First check standard locations
    config_paths = [
        # Current directory
        os.path.join(os.getcwd(), 'app_config.ini'),
        # Application directory if frozen
        os.path.join(os.path.dirname(sys.executable), 'app_config.ini') if getattr(sys, 'frozen', False) else None,
        # _MEIPASS if using PyInstaller onefile mode
        os.path.join(getattr(sys, '_MEIPASS', ''), 'app_config.ini') if hasattr(sys, '_MEIPASS') else None,
    ]
    
    # Filter out None values
    config_paths = [p for p in config_paths if p]
    
    # Try to load from any of the possible locations
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                print(f"Loading configuration from: {config_path}")
                app_config.read(config_path)
                return True
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
    
    # If no config file found, create a default one
    try:
        app_config['Paths'] = {
            'DataDir': 'data',
            'LogsDir': 'logs',
            'OutputDir': 'output'
        }
        app_config['Options'] = {
            'DefaultGUIMode': 'True'
        }
        
        # If we're in a frozen application, try to save the default config
        if getattr(sys, 'frozen', False):
            default_config_path = os.path.join(os.path.dirname(sys.executable), 'app_config.ini')
            try:
                with open(default_config_path, 'w') as configfile:
                    app_config.write(configfile)
                print(f"Created default configuration at: {default_config_path}")
            except Exception as e:
                print(f"Could not save default config: {e}")
    except Exception as e:
        print(f"Error creating default config: {e}")
    
    return False

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    global app_config
    
    # Get the directory name from relative_path
    dir_name = os.path.dirname(relative_path)
    
    try:
        # Check if we have a configuration entry for this path
        if app_config and 'Paths' in app_config:
            # Extract the top-level directory from the relative path
            top_dir = relative_path.split(os.sep)[0] if os.sep in relative_path else relative_path
            
            # Check if we have a config entry for this directory
            config_dir_key = f"{top_dir.capitalize()}Dir"
            if config_dir_key in app_config['Paths']:
                config_path = app_config['Paths'][config_dir_key]
                print(f"Using configured path for {top_dir}: {config_path}")
                
                # Replace the top directory with the configured path
                if os.sep in relative_path:
                    new_path = os.path.join(config_path, *relative_path.split(os.sep)[1:])
                else:
                    new_path = config_path
                    
                # Figure out the base path depending on whether we're frozen
                if getattr(sys, 'frozen', False):
                    if hasattr(sys, '_MEIPASS'):
                        base_path = sys._MEIPASS
                    else:
                        base_path = os.path.dirname(sys.executable)
                else:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                
                # Combine base path with the new path
                abs_path = os.path.join(base_path, new_path)
                print(f"Resolved path: {abs_path}")
                return abs_path
    except Exception as e:
        print(f"Error processing resource path from config: {e}")

    # Default behavior if no config entry found
    try:
        # Check if the application is frozen (PyInstaller)
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # Running as onefile
                print(f"Using _MEIPASS path: {sys._MEIPASS}")
                base_path = sys._MEIPASS
            else:
                # Running as onedir
                print(f"Using frozen path: {os.path.dirname(sys.executable)}")
                base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            print(f"Using script path: {os.path.dirname(os.path.abspath(__file__))}")
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        # Return the absolute path to the resource
        abs_path = os.path.join(base_path, relative_path)
        print(f"Resolved path: {abs_path}")
        return abs_path
    except Exception as e:
        print(f"Error processing resource path: {e}")
        return relative_path

def get_writable_dir(dirname):
    """Get a writable directory for logs, data, or output files"""
    global app_config
    
    try:
        # Check if there's a configuration override
        if app_config and 'Paths' in app_config:
            config_dir_key = f"{dirname.capitalize()}Dir"
            if config_dir_key in app_config['Paths']:
                config_path = app_config['Paths'][config_dir_key]
                print(f"Using configured directory for {dirname}: {config_path}")
                
                # Determine base path based on execution environment
                if getattr(sys, 'frozen', False):
                    # We are running in a PyInstaller bundle
                    if hasattr(sys, '_MEIPASS'):
                        base_path = sys._MEIPASS
                    else:
                        base_path = os.path.dirname(sys.executable)
                else:
                    # We are running in a normal Python environment
                    base_path = os.path.dirname(os.path.abspath(__file__))
                
                # Create full path
                dir_path = os.path.join(base_path, config_path)
                
                # Ensure directory exists
                if not os.path.exists(dir_path):
                    try:
                        os.makedirs(dir_path)
                        print(f"Created directory: {dir_path}")
                    except Exception as e:
                        print(f"Error creating directory {dir_path}: {e}")
                        # Fall back to temporary directory if we can't create the configured directory
                        return os.path.join(tempfile.gettempdir(), 'DeploymentAnalyzer', dirname)
                
                return dir_path
    except Exception as e:
        print(f"Error processing directory from config: {e}")
    
    # Default behavior if no config entry found or configuration failed
    try:
        # Determine base path for storing data
        if getattr(sys, 'frozen', False):
            # We are running in a PyInstaller bundle
            base_path = os.path.dirname(sys.executable)
        else:
            # We are running in a normal Python environment
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        # Create the directory path
        dir_path = os.path.join(base_path, dirname)
        
        # Make sure the directory exists
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                print(f"Created directory: {dir_path}")
            except Exception as e:
                print(f"Error creating directory {dir_path}: {e}")
                # Fall back to temporary directory
                temp_path = os.path.join(tempfile.gettempdir(), 'DeploymentAnalyzer', dirname)
                if not os.path.exists(temp_path):
                    os.makedirs(temp_path)
                return temp_path
                
        return dir_path
    except Exception as e:
        print(f"Error getting writable directory: {e}")
        # As a last resort, use a directory in the temp folder
        temp_path = os.path.join(tempfile.gettempdir(), 'DeploymentAnalyzer', dirname)
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        return temp_path

# Try to import all required packages with detailed error handling
try:
    print("Importing required packages...")
    import pandas as pd
    print("✓ pandas")
    import numpy as np
    print("✓ numpy")
    import matplotlib
    print("✓ matplotlib")
    matplotlib.use('TkAgg')  # Force TkAgg backend
    import matplotlib.pyplot as plt
    print("✓ matplotlib.pyplot")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    print("✓ matplotlib.backends.backend_tkagg")
    import seaborn as sns
    print("✓ seaborn")
    from datetime import datetime, timedelta
    print("✓ datetime")
    import locale
    print("✓ locale")
    import argparse
    print("✓ argparse")
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    print("✓ tkinter")
    import threading
    print("✓ threading")
    import csv
    print("✓ csv")
    from PIL import Image
    print("✓ PIL")
    print("All packages imported successfully")
except ImportError as e:
    print(f"ERROR: Failed to import required package: {e}")
    print(f"Exception details: {traceback.format_exc()}")
    if hasattr(sys, 'frozen'):
        print("Running as frozen application - this should not happen!")
        print("Please check if the application was built with all dependencies.")
        input("Press Enter to exit...")
    sys.exit(1)

# Define your DeploymentAnalyzer class here (copy from original)
class DeploymentAnalyzer:
    """Main analyzer class that handles data processing and visualization"""
    
    def __init__(self):
        """Initialize the analyzer with empty data"""
        # ... Copy from original file ...
        # For now, just a placeholder to make the script run
        self.data = None
        self.files_loaded = []
        
    def import_file(self, file_path):
        """Import data from a file"""
        logger.info(f"Importing file: {file_path}")
        # Placeholder - would contain actual implementation
        return True
    
    def add_file(self, file_path):
        """Add a file to the analysis"""
        logger.info(f"Adding file: {file_path}")
        # Placeholder - would contain actual implementation
        return True
    
    def process_data(self):
        """Process the loaded data"""
        logger.info("Processing data")
        # Placeholder - would contain actual implementation
        return True
    
    def create_pivot_table(self, max_delay=None, granularity="daily"):
        """Create a pivot table of the data"""
        logger.info(f"Creating pivot table with granularity: {granularity}")
        # Placeholder - would contain actual implementation
        return {}
    
    def create_heatmap(self, cmap='YlOrRd', figsize=(10, 6), granularity=None):
        """Create a heatmap visualization"""
        logger.info(f"Creating heatmap with granularity: {granularity}")
        # Placeholder - would contain actual implementation
        return plt.figure()
    
    def get_loaded_files_summary(self):
        """Get a summary of loaded files"""
        logger.info("Getting loaded files summary")
        # Placeholder - would contain actual implementation
        return "No files loaded"
    
    def get_statistics(self):
        """Get statistics from the loaded data"""
        logger.info("Getting statistics")
        # Placeholder - would contain actual implementation
        return {"Total Records": 0}
    
    def save_heatmap(self, fig, output_path):
        """Save a heatmap figure to a file"""
        logger.info(f"Saving heatmap to: {output_path}")
        # Placeholder - would contain actual implementation
        return True
    
    def export_data(self, output_path):
        """Export the processed data to a file"""
        logger.info(f"Exporting data to: {output_path}")
        # Placeholder - would contain actual implementation
        return True

# Define your SimpleAnalysisGUI class here (copy from original)
class SimpleAnalysisGUI:
    """GUI for the Deployment Analyzer"""
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("Deployment Analyzer")
        self.root.geometry("1200x700")
        
        # Initialize the analyzer
        self.analyzer = DeploymentAnalyzer()
        
        # Set up the GUI layout
        self.create_main_frames()
        logger.info("GUI initialized")

    def create_main_frames(self):
        """Create the main frames for the GUI"""
        logger.info("Creating main frames")
        # Placeholder - would contain actual implementation
        label = tk.Label(self.root, text="Deployment Analyzer GUI (Placeholder)")
        label.pack(pady=20)
        
        # Add a simple test button
        test_button = tk.Button(self.root, text="Test Button", command=self.test_function)
        test_button.pack(pady=10)
        
    def test_function(self):
        """Test function for the GUI"""
        logger.info("Test button clicked")
        messagebox.showinfo("Test", "GUI is functioning correctly!")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Deployment Analysis Tool')
    parser.add_argument('--file', help='Input file path')
    parser.add_argument('--output', help='Output directory')
    parser.add_argument('--gui', action='store_true', help='Start in GUI mode')
    parser.add_argument('--max-delay', type=int, help='Maximum delay to consider (in days)')
    
    args = parser.parse_args()
    
    # Default to GUI mode if no arguments provided
    if len(sys.argv) <= 1:
        print("No command-line arguments provided. Starting in GUI mode.")
        args.gui = True
    
    # Check config for default GUI mode setting
    try:
        if app_config and 'Options' in app_config and 'DefaultGUIMode' in app_config['Options']:
            if app_config['Options']['DefaultGUIMode'].lower() == 'true' and args.file is None:
                print("Using DefaultGUIMode=True from config.")
                args.gui = True
    except Exception as e:
        print(f"Error checking DefaultGUIMode config: {e}")
    
    return args

def run_command_line(args):
    """Run the analyzer in command-line mode"""
    print("Starting command-line mode")
    
    if args.file is None:
        print("Error: --file argument is required in command-line mode.")
        return 1
    
    try:
        analyzer = DeploymentAnalyzer()
        
        print(f"Importing file: {args.file}")
        if not analyzer.import_file(args.file):
            print(f"Error importing file: {args.file}")
            return 1
        
        print("Processing data...")
        analyzer.process_data()
        
        # Generate and save the heatmap
        output_dir = args.output if args.output else get_writable_dir("output")
        output_file = os.path.join(output_dir, f"heatmap_{int(time.time())}.png")
        
        print(f"Creating heatmap with max_delay={args.max_delay}")
        fig = analyzer.create_heatmap(max_delay=args.max_delay)
        
        print(f"Saving heatmap to: {output_file}")
        analyzer.save_heatmap(fig, output_file)
        
        print(f"Analysis complete. Output saved to: {output_file}")
        return 0
    except Exception as e:
        print(f"Error in command-line mode: {e}")
        logger.error(f"Command-line error: {e}", exc_info=True)
        return 1

def main():
    """Main entry point for the application"""
    global logger, app_config
    
    try:
        # Load configuration first
        load_config()
        
        # Set up logging
        logger = setup_logging()
        logger.info("Application starting")
        
        # Log system information
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Running in {'frozen' if getattr(sys, 'frozen', False) else 'script'} mode")
        logger.info(f"Current directory: {os.getcwd()}")
        if hasattr(sys, '_MEIPASS'):
            logger.info(f"PyInstaller _MEIPASS: {sys._MEIPASS}")
        
        # Parse command line arguments
        args = parse_arguments()
        logger.info(f"Command-line arguments: {args}")
        
        # Set up global exception handler
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # Let the default handler take care of KeyboardInterrupt
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # Log the exception
            logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
            
            # If in GUI mode, show error dialog
            if 'root' in globals() and root and root.winfo_exists():
                messagebox.showerror("Error", f"An unhandled error occurred:\n{exc_value}")
        
        # Set the exception handler
        sys.excepthook = handle_exception
        
        # Run in GUI or command-line mode based on arguments
        if args.gui:
            logger.info("Starting GUI mode")
            print("Starting GUI mode")
            root = tk.Tk()
            app = SimpleAnalysisGUI(root)
            print("Starting Tkinter main loop")
            root.mainloop()
            return 0
        else:
            return run_command_line(args)
            
    except Exception as e:
        print(f"Fatal error: {e}")
        if logger:
            logger.critical(f"Fatal error: {e}", exc_info=True)
        else:
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Uncaught exception in __main__: {e}")
        traceback.print_exc()
        if getattr(sys, 'frozen', False):
            print("\nPress Enter to exit...")
            input()
        sys.exit(1) 