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

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import locale
import os
import sys  # Added missing sys import
import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import numpy as np
import matplotlib
import csv
import logging
from logging.handlers import RotatingFileHandler
import traceback
import configparser  # Added for config file reading

# Check for configuration file
def load_config():
    """Load application configuration from app_config.ini if available"""
    config = configparser.ConfigParser()
    config_paths = []
    
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        app_dir = os.path.dirname(sys.executable)
        config_paths.append(os.path.join(app_dir, 'app_config.ini'))
    else:
        # Running in development
        app_dir = os.path.dirname(os.path.abspath(__file__))
        config_paths.append(os.path.join(app_dir, 'app_config.ini'))
    
    # Try to load config from possible locations
    config_loaded = False
    config_file_used = None
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                config.read(config_path)
                config_loaded = True
                config_file_used = config_path
                print(f"Loaded configuration from: {config_path}")
                break
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
    
    if not config_loaded:
        print("No configuration file found, using defaults")
        
    return config, config_loaded, config_file_used

# Load configuration
app_config, config_loaded, config_file_used = load_config()

# Print initial startup status - helpful for debugging
print("Application starting...")
print(f"Current working directory: {os.getcwd()}")
print(f"Is frozen (PyInstaller): {'_MEIPASS' in dir(sys)}")

# Helper function for PyInstaller bundled resources
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            print(f"Using PyInstaller base path: {base_path}")
        else:
            # Running in normal Python environment
            base_path = os.path.dirname(os.path.abspath(__file__))
            print(f"Using script directory as base path: {base_path}")
        
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Error in resource_path for {relative_path}: {str(e)}")
        traceback.print_exc()
        return relative_path

# Define log directories based on environment
def get_writable_dir(dirname):
    """Returns a writable directory path that works both in development and when frozen"""
    # Check if we have a path override in the config
    if config_loaded and 'Paths' in app_config and f"{dirname}Dir" in app_config['Paths']:
        # If running as exe, use the directory specified in the config
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
            config_path = app_config['Paths'][f"{dirname}Dir"]
            # If path is relative, make it relative to the executable
            if not os.path.isabs(config_path):
                target_dir = os.path.join(app_dir, config_path)
            else:
                target_dir = config_path
            print(f"Using configured {dirname} directory: {target_dir}")
            return target_dir
    
    # Default behavior if no config or not frozen
    if getattr(sys, 'frozen', False):
        # If running as exe, use a directory next to the executable
        app_dir = os.path.dirname(sys.executable)
        target_dir = os.path.join(app_dir, dirname)
    else:
        # In development, use local directory
        target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname)
    
    print(f"Using default {dirname} directory: {target_dir}")
    return target_dir

# Create necessary directories 
try:
    logs_dir = get_writable_dir('logs')
    data_dir = get_writable_dir('data')
    output_dir = get_writable_dir('output')
    
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Created directories: logs, data, output")
except Exception as e:
    print(f"Error creating directories: {str(e)}")
    traceback.print_exc()

# Set up logging
try:
    log_file = os.path.join(logs_dir, 'deployment_analysis.log')
    print(f"Log file path: {log_file}")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
except Exception as e:
    print(f"Error setting up logging: {str(e)}")
    traceback.print_exc()

try:
    # Set backend to TkAgg for GUI applications
    matplotlib.use('TkAgg')
    logger.info(f"Using {matplotlib.get_backend()} backend for matplotlib")
except Exception as e:
    print(f"Error setting matplotlib backend: {str(e)}")
    traceback.print_exc()

# Configure locale for German weekday names
try:
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'German')
    except:
        logger.warning("Could not set German locale. Using system default.")

class DeploymentAnalyzer:
    """
    Class for analyzing deployment data from Excel/CSV files.
    """
    
    def __init__(self):
        """Initialize the analyzer with empty data structures."""
        self.df = None
        self.cleaned_data = None
        self.pivot_table = None
        self.loaded_files = []
        
    def import_file(self, file_path):
        """
        Import data from Excel or CSV file.
        
        Args:
            file_path: Path to the Excel or CSV file
            
        Returns:
            DataFrame: The imported data
        """
        try:
            # Check if file is CSV
            if file_path.lower().endswith('.csv'):
                # Read the first line to detect delimiter
                with open(file_path, 'r') as f:
                    first_line = f.readline()
                    
                # Check for delimiter by counting occurrences
                semicolons = first_line.count(';')
                commas = first_line.count(',')
                
                # Determine the likely delimiter
                delimiter = ';' if semicolons > commas else ','
                
                # Read with the detected delimiter
                self.df = pd.read_csv(file_path, delimiter=delimiter, parse_dates=True)
            else:
                # Assume Excel file
                self.df = pd.read_excel(file_path, parse_dates=True)
                
            self.loaded_files = [file_path]
            return self.df
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing file: {str(e)}")
            return None
            
    def add_file(self, file_path):
        """
        Add data from another file to the existing dataset.
        
        Args:
            file_path: Path to the Excel or CSV file
            
        Returns:
            DataFrame: The combined data
        """
        try:
            # Import the new file
            if file_path.lower().endswith('.csv'):
                # Read the first line to detect delimiter
                with open(file_path, 'r') as f:
                    first_line = f.readline()
                    
                # Check for delimiter by counting occurrences
                semicolons = first_line.count(';')
                commas = first_line.count(',')
                
                # Determine the likely delimiter
                delimiter = ';' if semicolons > commas else ','
                
                # Read with the detected delimiter
                new_df = pd.read_csv(file_path, delimiter=delimiter, parse_dates=True)
            else:
                # Assume Excel file
                new_df = pd.read_excel(file_path, parse_dates=True)
                
            # Combine with existing data if any
            if self.df is not None:
                self.df = pd.concat([self.df, new_df], ignore_index=True)
            else:
                self.df = new_df
                
            # Add to loaded files list
            self.loaded_files.append(file_path)
            
            return self.df
        except Exception as e:
            messagebox.showerror("Import Error", f"Error adding file: {str(e)}")
            return None
    
    def process_data(self):
        """
        Clean and process the raw data.
        
        Returns:
            DataFrame: The cleaned data
        """
        if self.df is None:
            return None
            
        try:
            # Make a copy to avoid modifying the original
            df = self.df.copy()
            
            # Check if we have the expected columns
            expected_cols = ['IPTC_DE Anweisung', 'IPTC_EN Anweisung', 
                            'Bild Upload Zeitpunkt', 'Bild Veröffentlicht', 
                            'Bild Aktivierungszeitpunkt']
            
            # Check if we have at least some of the expected columns
            if not any(col in df.columns for col in expected_cols):
                # Try alternative column names
                alt_cols = ['Bildankunft', 'Onlinestellung']
                if not any(col in df.columns for col in alt_cols):
                    raise ValueError("Could not identify required columns in the data")
            
            # Extract time from IPTC_DE Anweisung if available
            if 'IPTC_DE Anweisung' in df.columns:
                df['IPTC_Timestamp'] = df['IPTC_DE Anweisung'].str.extract(r'\[(\d{2}:\d{2}:\d{2})\]').iloc[:, 0]
            
            # Convert date columns to datetime
            date_cols = ['Bild Upload Zeitpunkt', 'Bild Aktivierungszeitpunkt', 'Bildankunft', 'Onlinestellung']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
            
            # Combine date and time for Bildankunft if needed
            if 'IPTC_Timestamp' in df.columns and 'Bild Aktivierungszeitpunkt' in df.columns:
                df['Bildankunft'] = df.apply(self._combine_date_time, axis=1)
            
            # Calculate delay in minutes
            if 'Bildankunft' in df.columns and 'Bild Aktivierungszeitpunkt' in df.columns:
                df['Verzögerung_Minuten'] = (df['Bild Aktivierungszeitpunkt'] - df['Bildankunft']).dt.total_seconds() / 60
            elif 'Bildankunft' in df.columns and 'Onlinestellung' in df.columns:
                df['Verzögerung_Minuten'] = (df['Onlinestellung'] - df['Bildankunft']).dt.total_seconds() / 60
                
            # Filter out negative delays and extreme outliers
            if 'Verzögerung_Minuten' in df.columns:
                df = df[df['Verzögerung_Minuten'] >= 0]
                df = df[df['Verzögerung_Minuten'] < 24 * 60]  # Less than 24 hours
                
            # Extract day of week and hour
            if 'Bildankunft' in df.columns:
                df['Wochentag'] = df['Bildankunft'].dt.day_name()
                df['Tag'] = df['Bildankunft'].dt.day
                df['Stunde'] = df['Bildankunft'].dt.hour
                df['Monat'] = df['Bildankunft'].dt.month
                df['Jahr'] = df['Bildankunft'].dt.year
                
            self.cleaned_data = df
            return df
            
        except Exception as e:
            messagebox.showerror("Processing Error", f"Error processing data: {str(e)}")
            return None
                
    def _combine_date_time(self, row):
        """
        Combine date from activation timestamp with time from IPTC timestamp.
        
        Args:
            row: DataFrame row with IPTC_Timestamp and Bild Aktivierungszeitpunkt.
            
        Returns:
            datetime: Combined datetime object.
        """
        try:
            if pd.isna(row['IPTC_Timestamp']) or pd.isna(row['Bild Aktivierungszeitpunkt']):
                return pd.NaT
                
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
        except:
            return pd.NaT
    
    def create_pivot_table(self, max_delay=None, granularity="daily"):
        """
        Create a pivot table of processing delays.
        
        Args:
            max_delay: Maximum delay to include (in minutes)
            granularity: Time granularity ('daily', 'weekly', 'monthly', 'yearly', 'hourly')
            
        Returns:
            DataFrame: Pivot table
        """
        if self.cleaned_data is None:
            return None
            
        # Make a copy to avoid modifying the original
        data = self.cleaned_data.copy()
        
        # Apply max delay filter if specified
        if max_delay is not None:
            data = data[data['Verzögerung_Minuten'] <= max_delay]
        
        # Ensure all hours are represented (0-23)
        all_hours = list(range(24))
        
        # Create pivot table based on granularity
        if granularity == "daily":
            # Pivot by day of month and hour
            data['Day'] = data['Bildankunft'].dt.day
            data['Hour'] = data['Bildankunft'].dt.hour
            
            pivot = pd.pivot_table(
                data,
                values='Verzögerung_Minuten',
                index='Day',
                columns='Hour',
                aggfunc='mean',
                fill_value=0
            )
            
            # Ensure all hours are included
            pivot = pivot.reindex(columns=all_hours, fill_value=0)
            
        elif granularity == "weekly":
            try:
                # Pivot by day of week and hour
                try:
                    # Try with different pandas versions
                    try:
                        # Using day_name() method for newer pandas
                        data['Weekday'] = data['Bildankunft'].dt.day_name().str[:3]
                    except:
                        # For older pandas versions
                        data['Weekday'] = data['Bildankunft'].dt.strftime('%a')
                except:
                    # Last resort fallback
                    data['Weekday'] = data['Bildankunft'].dt.weekday
                    weekday_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
                    data['Weekday'] = data['Weekday'].map(weekday_map)
                
                data['Hour'] = data['Bildankunft'].dt.hour
                
                # Define weekday order
                weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                
                # Create pivot table
                pivot = pd.pivot_table(
                    data,
                    values='Verzögerung_Minuten',
                    index='Weekday',
                    columns='Hour',
                    aggfunc='mean'
                )
                
                # Ensure all weekdays and hours are included by reindexing
                pivot = pivot.reindex(index=weekday_order, columns=all_hours)
                
                # Fill NaN values with 0 for values and use None (a different color) for missing data points
                pivot = pivot.fillna(value=float('nan'))
            
            except Exception as e:
                print(f"Error creating weekly pivot table: {str(e)}")
                # Fallback to a simpler weekly view
                try:
                    data['Day'] = data['Bildankunft'].dt.day
                    data['Hour'] = data['Bildankunft'].dt.hour
                    
                    pivot = pd.pivot_table(
                        data,
                        values='Verzögerung_Minuten',
                        index='Day',
                        columns='Hour',
                        aggfunc='mean'
                    )
                    
                    # Ensure all hours are included
                    pivot = pivot.reindex(columns=all_hours)
                    pivot = pivot.fillna(value=float('nan'))
                except Exception as e2:
                    print(f"Failed to create fallback pivot: {str(e2)}")
                    return None
            
        elif granularity == "monthly":
            # Pivot by month and hour
            data['Month'] = data['Bildankunft'].dt.month
            data['Hour'] = data['Bildankunft'].dt.hour
            
            pivot = pd.pivot_table(
                data,
                values='Verzögerung_Minuten',
                index='Month',
                columns='Hour',
                aggfunc='mean'
            )
            
            # Ensure all months (1-12) and hours are included
            all_months = list(range(1, 13))
            pivot = pivot.reindex(index=all_months, columns=all_hours)
            
            # Fill missing values with NaN to render as white/empty cells
            pivot = pivot.fillna(value=float('nan'))
            
            # Map month numbers to month names
            month_names = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            }
            pivot.index = [month_names.get(m, m) for m in pivot.index]
            
            # Calculate global min and max for monthly averages
            self.global_min = pivot.min().min()
            self.global_max = pivot.max().max()
        
        elif granularity == "yearly":
            # Create a date column combining year, month, and day for each entry
            data['Date'] = pd.to_datetime(data['Bildankunft'].dt.date)
            data['Hour'] = data['Bildankunft'].dt.hour
            
            # Sort the data by date for a chronological view
            data = data.sort_values('Date')
            
            # Create pivot table with date as index and hour as columns
            pivot = pd.pivot_table(
                data,
                values='Verzögerung_Minuten',
                index='Date',
                columns='Hour',
                aggfunc='mean'
            )
            
            # Ensure all hours are included
            pivot = pivot.reindex(columns=all_hours)
            pivot = pivot.fillna(value=float('nan'))
            
            # Format the date index to be more readable
            pivot.index = [d.strftime('%b %d') for d in pivot.index]
        
        else:  # "hourly" (combined view)
            # Pivot by hour only, combining all dates
            data['Hour'] = data['Bildankunft'].dt.hour
            
            # Use a dummy index to get a 1-row heatmap
            data['All Data'] = 'All Data'
            
            pivot = pd.pivot_table(
                data,
                values='Verzögerung_Minuten',
                index='All Data',
                columns='Hour',
                aggfunc='mean'
            )
            
            # Ensure all hours are included
            pivot = pivot.reindex(columns=all_hours)
            pivot = pivot.fillna(value=float('nan'))
        
        self.pivot_table = pivot
        return pivot
    
    def create_heatmap(self, cmap='YlOrRd', figsize=(10, 6), granularity=None):
        """
        Create a heatmap visualization of the pivot table.
        
        Args:
            cmap: Colormap for the heatmap
            figsize: Figure size tuple (width, height)
            granularity: Time granularity ('daily', 'weekly', 'monthly', 'yearly')
            
        Returns:
            Figure: Matplotlib figure object
        """
        if self.pivot_table is None:
            print("No pivot table available. Please run create_pivot_table first.")
            return None
        
        try:
            # Use non-interactive backend to avoid main thread issues
            import matplotlib
            default_backend = matplotlib.get_backend()
            matplotlib.use('Agg')
            
            # Close any existing figures to prevent thread issues
            plt.close('all')

            # Get dimensions of the pivot table
            rows = len(self.pivot_table.index)
            cols = len(self.pivot_table.columns)
            
            # Define standard dimensions for complete datasets to ensure consistent square sizes
            standard_rows = {"monthly": 12, "weekly": 7, "yearly": rows, "daily": rows}
            standard_cols = 24  # Hours in a day
            
            # Adjust figure size based on standard dimensions for consistent square sizes
            if granularity in ['weekly', 'monthly']:
                std_rows = standard_rows.get(granularity, rows)
                # Calculate figure size based on standard dimensions rather than actual data size
                adjusted_height = max(8, min(std_rows * 0.4, 16))
                adjusted_width = max(10, min(standard_cols * 0.8, 20))
                figsize = (adjusted_width, adjusted_height)
            elif granularity == 'yearly':
                # For yearly view, use a more balanced approach to sizing
                # Aim for rectangles with 2:1 ratio (twice as wide as tall)
                row_to_col_ratio = rows / cols
                # Calculate width based on number of columns (hours) - increased for better screen usage
                adjusted_width = max(16, min(cols * 0.8, 24))  # Increased width for wider rectangles
                # Calculate height based on width and row-to-column ratio, but half as tall for 2:1 ratio
                adjusted_height = max(6, min(adjusted_width * row_to_col_ratio * 0.35, 18))  # Adjusted ratio for 2:1 rectangles
                
                # Limit height for very large datasets to prevent excessive stretching
                if rows > 40:
                    adjusted_height = min(adjusted_height, 20)
                    
                figsize = (adjusted_width, adjusted_height)

            # Create new figure
            fig, ax = plt.subplots(figsize=figsize)
            
            # Set aspect ratio - for yearly view, use 2:1 rectangles instead of squares
            if granularity in ['weekly', 'monthly']:
                # Use square cells for weekly and monthly views
                ax.set_aspect('equal', adjustable='box', anchor='C')
            elif granularity == 'yearly':
                # For yearly view, use rectangles twice as wide as tall (2:1 ratio)
                # We set aspect to 0.5 to make cells twice as wide as tall
                ax.set_aspect(0.5, adjustable='box', anchor='C')
            
            # Create a masked array to handle NaN values properly
            mask = np.isnan(self.pivot_table.values)  # Using .values to avoid Series truth value ambiguity
            
            # Custom colormap with white for NaN/missing values - using updated method to avoid deprecation warning
            try:
                # Modern matplotlib approach (3.7+)
                cmap_with_white = matplotlib.colormaps[cmap].copy()
            except (AttributeError, KeyError):
                # Fallback for older versions
                try:
                    cmap_with_white = plt.get_cmap(cmap).copy()  # Use plt.get_cmap instead of plt.cm.get_cmap
                except:
                    # Last resort fallback
                    cmap_with_white = plt.cm.get_cmap(cmap).copy()
                    
            cmap_with_white.set_bad('white', 1.0)  # Set NaN cells to white
            
            # Determine appropriate linewidth based on view type
            if granularity == 'yearly':
                linewidth = 0  # No lines for yearly view to remove spacing between rectangles
            elif granularity == 'yearly' and rows > 20:
                linewidth = 0.2  # Thinner lines for yearly view with many rows
            else:
                linewidth = 0.5
            
            # Compute vmin and vmax for adaptive color scaling
            # If it's yearly view, we want to adapt the color scale to show more variation
            vmin, vmax = None, None  # Default values
            if granularity == 'yearly':
                # Calculate quartile-based bounds to emphasize the variation in the middle of the data
                # Get the data as numpy array to avoid Series truth value ambiguity
                data_values = self.pivot_table.values
                if not np.all(mask):  # Using numpy's all instead of mask.all()
                    data_flat = data_values.flatten()
                    data_flat = data_flat[~np.isnan(data_flat)]  # Filter out NaN values
                    
                    if len(data_flat) > 0:
                        # For very low variation data, use percentiles closer to median
                        data_std = np.std(data_flat)
                        data_range = np.max(data_flat) - np.min(data_flat)
                        
                        # If data has low variation, use tighter percentiles to enhance contrast
                        if data_range < 5 or data_std < 2:
                            vmin = np.percentile(data_flat, 30)  # 30th percentile
                            vmax = np.percentile(data_flat, 90)  # 90th percentile
                        else:
                            vmin = np.percentile(data_flat, 10)  # 10th percentile
                            vmax = np.percentile(data_flat, 95)  # 95th percentile
                            
                        # Ensure vmin and vmax are not the same to prevent colormap issues
                        if vmin == vmax:
                            vmin = 0 if vmin == 0 else vmin * 0.9
                            vmax = vmax * 1.1
            
            # Create heatmap with masked data - without annotations
            heatmap = sns.heatmap(
                self.pivot_table,
                cmap=cmap_with_white,
                annot=False,  # No annotations as requested by user
                linewidths=linewidth,
                ax=ax,
                cbar_kws={'label': 'Average Delay (minutes)'},
                mask=mask,  # Mask NaN values
                vmin=vmin,  # Custom range for color scaling
                vmax=vmax,
                robust=True  # Use robust quantile-based scaling for color range
            )
            
            # Optimize tick labels display based on the view type
            if granularity == "yearly":
                # Special handling for yearly view to make it more compact and readable
                # Reduce font size for tick labels
                plt.setp(ax.get_xticklabels(), fontsize=6, rotation=45, ha='right')
                
                # For yearly view with many rows, show fewer y-tick labels
                if rows > 25:
                    # Show approximately 20 tick labels (one every N rows)
                    tick_step = max(1, rows // 20)
                    
                    # Create indices that are guaranteed to be within bounds
                    # This ensures we don't try to access indices beyond the size of the array
                    visible_ticks = list(range(0, rows, tick_step))
                    
                    # Always include the first and last tick if not already included
                    if len(visible_ticks) > 0 and visible_ticks[-1] != rows - 1:
                        if rows - 1 not in visible_ticks:  # Only append if not already there
                            visible_ticks.append(rows - 1)
                    
                    # Safety check - ensure all indices are within bounds
                    visible_ticks = [i for i in visible_ticks if 0 <= i < rows]
                    
                    if len(visible_ticks) > 0:  # Only proceed if we have valid ticks
                        # Get current ticks
                        y_ticks = ax.get_yticks()
                        
                        # Extra safety check to ensure we don't have an index error
                        valid_indices = [i for i in visible_ticks if i < len(y_ticks)]
                        
                        if valid_indices:  # Only proceed if we have valid indices
                            # Set visible y-ticks and format them
                            ax.set_yticks([y_ticks[i] for i in valid_indices])
                            ax.set_yticklabels([self.pivot_table.index[i] for i in valid_indices], 
                                             fontsize=6, rotation=0)
                else:
                    # For smaller datasets, just set the font size
                    plt.setp(ax.get_yticklabels(), fontsize=6, rotation=0)
            
            # Adjust layout based on view type
            if granularity == 'yearly' and rows > 25:
                # More compact layout for large yearly views
                plt.tight_layout(pad=1.2, h_pad=0.8, w_pad=0.8, rect=[0.03, 0.03, 0.97, 0.97])
            else:
                plt.tight_layout()
            
            # Switch back to the original backend
            matplotlib.use(default_backend)
            
            return fig
        except Exception as e:
            print(f"Error creating heatmap: {str(e)}")
            return None
    
    def get_loaded_files_summary(self):
        """
        Get a summary of loaded files.
        
        Returns:
            str: Summary of loaded files
        """
        if not self.loaded_files:
            return "No files loaded"
            
        file_names = [os.path.basename(f) for f in self.loaded_files]
        return f"{len(file_names)} file(s): " + ", ".join(file_names)
    
    def get_statistics(self):
        """
        Calculate basic statistics of the cleaned data.
        
        Returns:
            dict: Statistics dictionary
        """
        if self.cleaned_data is None or 'Verzögerung_Minuten' not in self.cleaned_data.columns:
            return {
                'total_records': 0,
                'avg_delay': 0,
                'min_delay': 0,
                'max_delay': 0
            }
            
        stats = {
            'total_records': len(self.cleaned_data),
            'avg_delay': self.cleaned_data['Verzögerung_Minuten'].mean(),
            'min_delay': self.cleaned_data['Verzögerung_Minuten'].min(),
            'max_delay': self.cleaned_data['Verzögerung_Minuten'].max()
        }
        
        # Get available months and years
        if 'Monat' in self.cleaned_data.columns and 'Jahr' in self.cleaned_data.columns:
            # Get unique month-year combinations
            month_year_df = self.cleaned_data[['Monat', 'Jahr']].drop_duplicates()
            
            # Convert month numbers to names
            month_names = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }
            
            # Create list of available month-year combinations
            available_months = []
            for _, row in month_year_df.iterrows():
                month_name = month_names.get(row['Monat'], str(row['Monat']))
                available_months.append((row['Monat'], row['Jahr'], f"{month_name} {row['Jahr']}"))
            
            stats['available_months'] = sorted(available_months)
            stats['available_years'] = sorted(self.cleaned_data['Jahr'].unique().tolist())
        
        return stats
    
    def save_heatmap(self, fig, output_path):
        """
        Save the heatmap figure to a file.
        
        Args:
            fig: Matplotlib figure to save
            output_path: Path to save the figure
            
        Returns:
            bool: Success status
        """
        try:
            fig.savefig(output_path, bbox_inches='tight', dpi=300)
            return True
        except Exception as e:
            print(f"Error saving heatmap: {str(e)}")
            return False
    
    def export_data(self, output_path):
        """
        Export the cleaned data to a CSV or Excel file.
        
        Args:
            output_path: Path to save the data
            
        Returns:
            bool: Success status
        """
        try:
            if self.cleaned_data is None:
                return False
                
            if output_path.lower().endswith('.csv'):
                self.cleaned_data.to_csv(output_path, index=False)
            else:
                self.cleaned_data.to_excel(output_path, index=False)
                
            return True
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
            return False

class SimpleAnalysisGUI:
    """
    A simple GUI for analyzing image deployment delays with optimized layout
    focusing on the heatmap visualization.
    """
    
    def __init__(self, root):
        """Initialize the GUI with screen-fitting size."""
        self.root = root
        self.root.title("deployment-analyse ver. 1.0.0")
        
        # Set window to fit screen with some margin
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(800, 600)
        
        self.analyzer = DeploymentAnalyzer()
        self.file_path = None
        self.current_figure = None
        self.selected_granularity = tk.StringVar(value="yearly")
        self.canvas = None
        self.selected_month = None
        self.selected_year = None
        self.selected_week = None
        self.running_threads = []
        
        # Track application state
        self.is_running = True
        
        # Set up a protocol for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main frames with weight distribution to make heatmap dominant
        self.create_main_frames()
        self._create_widgets()
        self._setup_layout()
        
    def on_closing(self):
        """Handle window close event properly."""
        # Set flag to indicate application is closing
        self.is_running = False
        
        # Close any matplotlib figures to prevent memory leaks
        plt.close('all')
        
        # Wait for threads to finish (with timeout)
        for thread in self.running_threads[:]:
            if thread.is_alive():
                thread.join(0.1)  # Wait for 100ms max
        
        # Destroy the window
        self.root.destroy()
        
    def create_main_frames(self):
        """Create main frames with proper weight distribution."""
        # Configure root grid to give heatmap more space
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=3)  # Give more weight to visualization row
        
        # Create top control panel frame (for file selection, quick stats)
        self.control_panel = ttk.Frame(self.root)
        self.control_panel.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Create center visualization frame (for heatmap and navigation)
        self.visualization_frame = ttk.Frame(self.root)
        self.visualization_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.visualization_frame.grid_rowconfigure(0, weight=1)  # Canvas row
        self.visualization_frame.grid_rowconfigure(1, weight=0)  # Navigation row
        self.visualization_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas frame for the visualization
        self.canvas_frame = ttk.Frame(self.visualization_frame)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create navigation frame (for time period buttons) inside visualization frame
        self.navigation_frame = ttk.Frame(self.visualization_frame)
        self.navigation_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Create bottom navigation frame (for time period buttons)
        self.navigation_frame = ttk.Frame(self.root)
        self.navigation_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
    def _create_widgets(self):
        """Create all widgets for the GUI with optimized space usage."""
        padding = {"padx": 3, "pady": 3}
        
        # Using regular tk.Button with direct color styling for the import button
        
        # CONTROL PANEL WIDGETS -------------------------
        # File selection frame - more compact
        self.file_frame = ttk.LabelFrame(self.control_panel, text="File Selection")
        
        # File path entry and browse button
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.file_frame, textvariable=self.path_var, width=50)
        self.browse_button = tk.Button(self.file_frame, text="Import", command=self.browse_file, 
                                      bg="#90EE90", activebackground="#7CCD7C", 
                                      relief=tk.RAISED, padx=10, pady=2,
                                      borderwidth=2, cursor="hand2")
        self.add_file_button = ttk.Button(self.file_frame, text="+ Add Data", command=self.add_file)
        
        # Quick stats frame - more compact
        self.stats_frame = ttk.LabelFrame(self.control_panel, text="Statistics")
        
        # Statistics labels in a more compact layout
        self.files_label = ttk.Label(self.stats_frame, text="No files loaded")
        self.total_records_label = ttk.Label(self.stats_frame, text="Total Records: 0")
        self.avg_delay_label = ttk.Label(self.stats_frame, text="Avg: 0 min")
        self.min_delay_label = ttk.Label(self.stats_frame, text="Min: 0 min")
        self.max_delay_label = ttk.Label(self.stats_frame, text="Max: 0 min")
        
        # Run button - commented out to remove from GUI
        # self.run_button = ttk.Button(self.control_panel, text="Run Analysis", command=self.run_analysis)
        # Create a dummy button object that's not shown in UI but responds to all method calls
        self.run_button = ttk.Button(self.root)  # Create but don't add to layout
        
        # VISUALIZATION FRAME WIDGETS -------------------------
        # Canvas for the heatmap
        self.canvas_frame = ttk.Frame(self.visualization_frame)
        
        # Status and progress frame
        self.status_frame = ttk.Frame(self.visualization_frame)
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.progress = ttk.Progressbar(self.status_frame, orient="horizontal", mode="determinate")
        
        # Export buttons
        self.export_frame = ttk.Frame(self.visualization_frame)
        self.export_img_button = ttk.Button(
            self.export_frame, text="Export Image", command=self.export_heatmap
        )
        self.export_data_button = ttk.Button(
            self.export_frame, text="Export Data", command=self.export_data
        )
        
        # NAVIGATION FRAME WIDGETS -------------------------
        # Hierarchical time period buttons
        self.periods_frame = ttk.LabelFrame(self.navigation_frame, text="Time Periods")
        
        # Create frames for each level
        self.years_frame = ttk.Frame(self.periods_frame)
        self.months_frame = ttk.Frame(self.periods_frame)
        self.weeks_frame = ttk.Frame(self.periods_frame)
        
        # Labels for each section
        self.years_label = ttk.Label(self.years_frame, text="Years:")
        self.months_label = ttk.Label(self.months_frame, text="Months:")
        self.weeks_label = ttk.Label(self.weeks_frame, text="Weeks:")
        
        # Button containers
        self.years_buttons_frame = ttk.Frame(self.years_frame)
        self.months_buttons_frame = ttk.Frame(self.months_frame)
        self.weeks_buttons_frame = ttk.Frame(self.weeks_frame)
        
        # Help button
        self.help_button = ttk.Button(self.navigation_frame, text="Help", command=self.show_help)
    
    def _setup_layout(self):
        """Set up the layout with optimized space usage to make heatmap dominant."""
        padding = {"padx": 3, "pady": 3}
        
        # Configure the control panel for better spacing
        self.control_panel.columnconfigure(0, weight=2)  # File frame
        self.control_panel.columnconfigure(1, weight=2)  # Stats frame
        self.control_panel.columnconfigure(2, weight=0)  # Run button
        
        # CONTROL PANEL LAYOUT -------------------------
        # File selection frame
        self.file_frame.grid(row=0, column=0, sticky="ew", **padding)
        self.path_entry.pack(side="left", **padding, expand=True, fill="x")
        self.browse_button.pack(side="left", **padding)
        self.add_file_button.pack(side="left", **padding)
        
        # Stats frame
        self.stats_frame.grid(row=0, column=1, sticky="ew", **padding)
        self.files_label.pack(side="top", anchor="w", **padding)
        
        stats_subframe = ttk.Frame(self.stats_frame)
        stats_subframe.pack(fill="x", **padding)
        self.total_records_label.pack(side="left", **padding)
        self.avg_delay_label.pack(side="left", **padding)
        self.min_delay_label.pack(side="left", **padding)
        self.max_delay_label.pack(side="left", **padding)
        
        # VISUALIZATION FRAME LAYOUT -------------------------
        # Canvas - make it dominant by spanning the entire space
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", **padding)
        
        # Status and progress at the bottom
        self.status_frame.grid(row=1, column=0, sticky="ew", **padding)
        self.status_label.pack(side="left", **padding)
        self.progress.pack(side="right", fill="x", expand=True, **padding)
        
        # Export buttons
        self.export_frame.grid(row=2, column=0, sticky="ew", **padding)
        self.export_img_button.pack(side="left", **padding)
        self.export_data_button.pack(side="left", **padding)
        
        # NAVIGATION FRAME LAYOUT -------------------------
        # Configure navigation frame for better spacing
        self.navigation_frame.columnconfigure(0, weight=1)  # Periods
        self.navigation_frame.columnconfigure(1, weight=0)  # Help
        
        # Time periods frame
        self.periods_frame.grid(row=0, column=0, sticky="ew", **padding)
        
        # Years section
        self.years_frame.pack(fill="x", **padding)
        self.years_label.pack(side="left", **padding)
        self.years_buttons_frame.pack(side="left", fill="x", expand=True, **padding)
        
        # Months section (initially hidden)
        self.months_frame.pack(fill="x", **padding)
        self.months_label.pack(side="left", **padding)
        self.months_buttons_frame.pack(side="left", fill="x", expand=True, **padding)
        
        # Weeks section (initially hidden)
        self.weeks_frame.pack(fill="x", **padding)
        self.weeks_label.pack(side="left", **padding)
        self.weeks_buttons_frame.pack(side="left", fill="x", expand=True, **padding)
        
        # Help button
        self.help_button.grid(row=0, column=1, sticky="e", **padding)
    
    def browse_file(self):
        """Open a file dialog to browse for a file."""
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[
                ("All Supported Files", "*.xlsx *.xls *.csv"),
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            # Store file path
            self.file_path = file_path
            self.path_var.set(file_path)
            
            # Disable buttons during analysis
            self.run_button.config(state="disabled")
            self.add_file_button.config(state="disabled")
            
            # Update status to show we're processing
            self.update_status("Loading file, please wait...", progress=True)
            
            # Run in a separate thread to avoid freezing UI
            thread = threading.Thread(target=self._browse_file_thread, args=(file_path,))
            thread.daemon = True
            self.running_threads.append(thread)
            thread.start()

    def _browse_file_thread(self, file_path):
        """Process file in a separate thread after browsing."""
        try:
            # Only proceed if the application is still running
            if not self.is_running:
                return
            
            # Import the file
            self.root.after(0, lambda: self.update_status("Importing file...", progress=True))
            df = self.analyzer.import_file(file_path)
            
            if df is not None:
                # Process the data
                if not self.is_running:
                    return
                
                self.root.after(0, lambda: self.update_status("Processing data...", progress=True))
                self.analyzer.process_data()
                
                # Update the UI with available time periods
                if not self.is_running:
                    return
                
                self.root.after(0, self.update_time_period_buttons)
                
                # Default to yearly granularity instead of monthly
                granularity = "yearly"
                self.selected_granularity.set(granularity)
                
                # Create pivot table
                if not self.is_running:
                    return
                
                if granularity == "combined":
                    self.analyzer.create_pivot_table(granularity="hourly")
                else:
                    self.analyzer.create_pivot_table(granularity=granularity)
                
                # Store the pivot table for the main thread to use
                if not self.is_running:
                    return
                
                self.current_pivot_table = self.analyzer.pivot_table.copy()
                self.current_granularity = granularity
                
                # Signal main thread to create the heatmap with the prepared data
                self.root.after(0, self._create_heatmap_main_thread)
                
                # Update statistics
                stats = self.analyzer.get_statistics()
                if not self.is_running:
                    return
                
                self.root.after(0, lambda: self._update_stats_from_dict(stats))
                
                # Update file information
                files_summary = self.analyzer.get_loaded_files_summary()
                if not self.is_running:
                    return
                
                self.root.after(0, lambda: self.files_label.config(text=files_summary))
                
            else:
                # Handle failed import
                if self.is_running:
                    self.root.after(0, lambda: self.update_status("Error importing file"))
                    self.root.after(0, lambda: self.run_button.config(state="normal"))
                    self.root.after(0, lambda: self.add_file_button.config(state="normal"))
                
        except Exception as e:
            # Handle any exceptions
            if self.is_running:
                error_msg = f"Error processing file: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.update_status("Error processing file"))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                self.root.after(0, lambda: self.add_file_button.config(state="normal"))
                print(f"Error in _browse_file_thread: {str(e)}")
            
    def add_file(self):
        """Open a file dialog to add another file to the analysis."""
        file_path = filedialog.askopenfilename(
            title="Select Additional File",
            filetypes=[
                ("All Supported Files", "*.xlsx *.xls *.csv"),
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            # Start processing in a separate thread
            self.update_status("Adding file, please wait...", progress=True)
            self.run_button.config(state="disabled")
            self.add_file_button.config(state="disabled")
            
            thread = threading.Thread(target=self._add_file_thread, args=(file_path,))
            thread.daemon = True
            self.running_threads.append(thread)
            thread.start()
        
    def _add_file_thread(self, file_path):
        """Background thread for adding a file."""
        try:
            # Only proceed if the application is still running
            if not self.is_running:
                return
            
            # Add the file to the existing dataset
            self.root.after(0, lambda: self.update_status("Adding file...", progress=True))
            df = self.analyzer.add_file(file_path)
            
            if df is not None:
                # Process the combined data
                if not self.is_running:
                    return
                
                self.root.after(0, lambda: self.update_status("Processing data...", progress=True))
                self.analyzer.process_data()
                
                # Update UI with file information
                files_summary = self.analyzer.get_loaded_files_summary()
                
                # Update statistics
                stats = self.analyzer.get_statistics()
                if not self.is_running:
                    return
                
                self.root.after(0, lambda: self._update_stats_from_dict(stats))
                
                # Update time period buttons
                if not self.is_running:
                    return
                
                self.root.after(0, self.update_time_period_buttons)
                
                # Update files label
                if not self.is_running:
                    return
                
                self.root.after(0, lambda: self.files_label.config(text=files_summary))
                
                # Re-run analysis with the combined data
                if not self.is_running:
                    return
                
                granularity = self.selected_granularity.get()
                if granularity == "combined":
                    self.analyzer.create_pivot_table(granularity="hourly")
                else:
                    self.analyzer.create_pivot_table(granularity=granularity)
                
                # Signal main thread to create the heatmap
                if not self.is_running:
                    return
                
                self.root.after(0, self._create_heatmap)
                
                # Update status
                self.root.after(0, lambda: self.update_status(f"Added file: {os.path.basename(file_path)}"))
                
                # Enable buttons
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                self.root.after(0, lambda: self.add_file_button.config(state="normal"))
            else:
                # Update status for error
                if self.is_running:
                    self.root.after(0, lambda: self.update_status("Error adding file"))
                    self.root.after(0, lambda: self.run_button.config(state="normal"))
                    self.root.after(0, lambda: self.add_file_button.config(state="normal"))
                
        except Exception as e:
            # Handle any exceptions
            if self.is_running:
                error_msg = f"Error adding file: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.update_status("Error adding file"))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                self.root.after(0, lambda: self.add_file_button.config(state="normal"))
                print(f"Error in _add_file_thread: {str(e)}")
            
    def run_analysis(self):
        """Run the analysis and display results."""
        if not self.file_path:
            messagebox.showwarning("No File Selected", "Please select a file to analyze first.")
            return
        
        # Disable buttons during analysis
        self.run_button.config(state="disabled")
        self.add_file_button.config(state="disabled")
        
        # Update status to show we're processing
        self.update_status("Running analysis...", progress=True)
        
        # Run the analysis in a separate thread
        thread = threading.Thread(target=self._run_analysis_thread)
        thread.daemon = True
        self.running_threads.append(thread)
        thread.start()

    def _run_analysis_thread(self):
        """Analyze the file in a separate thread."""
        try:
            # Only proceed if the application is still running
            if not self.is_running:
                return
        
            self.root.after(0, lambda: self.update_status("Importing file...", progress=True))
            self.analyzer.import_file(self.file_path)
            
            # Process the data
            if not self.is_running:
                return
            
            self.root.after(0, lambda: self.update_status("Processing data...", progress=True))
            self.analyzer.process_data()
            
            # Update the UI with available time periods 
            if not self.is_running:
                return
            
            self.root.after(0, self.update_time_period_buttons)
            
            # Create pivot table based on selected granularity
            if not self.is_running:
                return
            
            granularity = self.selected_granularity.get()
            if granularity == "combined":
                self.analyzer.create_pivot_table(granularity="hourly")
            else:
                self.analyzer.create_pivot_table(granularity=granularity)
            
            # Store the pivot table for the main thread to use
            if not self.is_running:
                return
            
            self.current_pivot_table = self.analyzer.pivot_table.copy()
            self.current_granularity = granularity
            
            # Signal main thread to create the heatmap with the prepared data
            self.root.after(0, self._create_heatmap_main_thread)
            
            # Update statistics
            if not self.is_running:
                return
            
            stats = self.analyzer.get_statistics()
            self.root.after(0, lambda: self._update_stats_from_dict(stats))
            
        except Exception as e:
            # Handle any exceptions
            if self.is_running:
                error_msg = f"Error in analysis: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.update_status("Error in analysis"))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                self.root.after(0, lambda: self.add_file_button.config(state="normal"))
                print(f"Error in _run_analysis_thread: {str(e)}")
    
    def _create_heatmap(self):
        """Create a heatmap visualization from the pivot table."""
        # This method should only be called from the main thread
        try:
            # Check if data is available
            if self.analyzer.pivot_table is None or self.analyzer.pivot_table.empty:
                error_msg = "No data available to create heatmap"
                self._create_error_figure(error_msg)
                self.update_status("No data to visualize")
                self.run_button.config(state="normal")
                self.add_file_button.config(state="normal")
                return
            
            # Get the pivot table and create the heatmap
            pivot_table = self.analyzer.pivot_table
            current_granularity = self.selected_granularity.get()
            
            # Calculate figure size dynamically based on data dimensions
            # For large datasets, use a more conservative scaling to prevent overflow
            rows = len(pivot_table.index)
            cols = len(pivot_table.columns)
            
            # Define standard dimensions for complete datasets to ensure consistent square sizes
            standard_rows = {"monthly": 12, "weekly": 7, "yearly": rows, "hourly": 1}
            standard_cols = 24  # Hours in a day
            
            
            # Use standard dimensions for calculating aspect ratio to ensure consistent square sizes
            if current_granularity in ['monthly', 'weekly']:
                std_rows = standard_rows.get(current_granularity, rows)
                # Calculate figure size based on standard dimensions rather than actual data size
                # This ensures consistent square sizes regardless of dataset completeness
                height = max(8, min(std_rows * 0.4, 16))
                width = max(10, min(standard_cols * 0.8, 20))
            elif current_granularity == 'yearly':
                # For yearly view, use a more balanced approach to sizing
                # Aim for rectangles with 2:1 ratio (twice as wide as tall)
                row_to_col_ratio = rows / cols
                # Calculate width based on number of columns (hours) - increased for better screen usage
                width = max(16, min(cols * 0.8, 24))  # Increased width for wider rectangles
                # Calculate height based on width and row-to-column ratio, but half as tall for 2:1 ratio
                height = max(6, min(width * row_to_col_ratio * 0.35, 18))  # Adjusted ratio for 2:1 rectangles
                
                # Limit height for very large datasets to prevent excessive stretching
                if rows > 40:
                    height = min(height, 20)
            else:
                # For other views, use the actual data dimensions
                if rows > 20 or cols > 24:
                    height = max(8, min(rows * 0.3, 14))
                    width = max(10, min(cols * 0.6, 18))
                else:
                    height = max(8, min(rows * 0.4, 16))
                    width = max(10, min(cols * 0.8, 20))
            
            # Use non-interactive backend to avoid thread issues
            import matplotlib
            default_backend = matplotlib.get_backend()
            matplotlib.use('Agg')
            
            # Create the figure with extra padding for title and labels
            fig, ax = plt.subplots(figsize=(width, height))
            
            # Set aspect ratio - for yearly view, use 2:1 rectangles instead of squares
            if current_granularity in ['weekly', 'monthly']:
                # Use square cells for weekly and monthly views
                ax.set_aspect('equal', adjustable='box', anchor='C')
            elif current_granularity == 'yearly':
                # For yearly view, use rectangles twice as wide as tall (2:1 ratio)
                # We set aspect to 0.5 to make cells twice as wide as tall
                ax.set_aspect(0.5, adjustable='box', anchor='C')
            
            # Custom colormap with white for NaN/missing values - using updated method to avoid deprecation warning
            try:
                # Modern matplotlib approach (3.7+)
                cmap = matplotlib.colormaps["RdYlGn_r"].copy()
            except (AttributeError, KeyError):
                # Fallback for older versions
                try:
                    cmap = plt.get_cmap("RdYlGn_r").copy()  # Use plt.get_cmap instead of plt.cm.get_cmap
                except:
                    # Last resort fallback
                    cmap = plt.cm.get_cmap("RdYlGn_r").copy()
                    
            cmap.set_bad('white', 1.0)  # Set NaN cells to white
            
            # Create a mask for NaN values
            mask = np.isnan(pivot_table.values)  # Using .values to avoid Series truth value ambiguity
            
            # Determine appropriate linewidth based on view type
            if current_granularity == 'yearly':
                linewidth = 0  # No lines for yearly view to remove spacing between rectangles
            elif current_granularity == 'yearly' and rows > 20:
                linewidth = 0.2  # Thinner lines for yearly view with many rows
            else:
                linewidth = 0.5
            
            # Compute vmin and vmax for adaptive color scaling
            # If it's yearly view, we want to adapt the color scale to show more variation
            vmin, vmax = None, None  # Default values
            if current_granularity == 'yearly':
                # Calculate quartile-based bounds to emphasize the variation in the middle of the data
                # Get the data as numpy array to avoid Series truth value ambiguity
                data_values = pivot_table.values
                if not np.all(mask):  # Using numpy's all instead of mask.all()
                    data_flat = data_values.flatten()
                    data_flat = data_flat[~np.isnan(data_flat)]  # Filter out NaN values
                    
                    if len(data_flat) > 0:
                        # For very low variation data, use percentiles closer to median
                        data_std = np.std(data_flat)
                        data_range = np.max(data_flat) - np.min(data_flat)
                        
                        # If data has low variation, use tighter percentiles to enhance contrast
                        if data_range < 5 or data_std < 2:
                            vmin = np.percentile(data_flat, 30)  # 30th percentile
                            vmax = np.percentile(data_flat, 90)  # 90th percentile
                        else:
                            vmin = np.percentile(data_flat, 10)  # 10th percentile
                            vmax = np.percentile(data_flat, 95)  # 95th percentile
                            
                        # Ensure vmin and vmax are not the same to prevent colormap issues
                        if vmin == vmax:
                            vmin = 0 if vmin == 0 else vmin * 0.9
                            vmax = vmax * 1.1
            
            # Create the heatmap with a color map - without annotations
            sns.heatmap(
                pivot_table, 
                cmap=cmap,
                linewidths=linewidth,
                annot=False,  # No annotations as requested by user
                cbar_kws={'label': 'Average Delay (minutes)'},
                mask=mask,  # Mask NaN values
                vmin=vmin,  # Custom range for color scaling
                vmax=vmax,
                robust=True,  # Use robust quantile-based scaling for color range
                ax=ax
            )
            
            # Set titles and labels
            current_granularity = self.selected_granularity.get()
            title = f"Deployment Delays"
            
            # Optimize tick labels display based on the view type
            if current_granularity == "yearly":
                # Special handling for yearly view to make it more compact and readable
                # Reduce font size for tick labels
                plt.setp(ax.get_xticklabels(), fontsize=6, rotation=45, ha='right')
                
                # For yearly view with many rows, show fewer y-tick labels
                if rows > 25:
                    # Show approximately 20 tick labels (one every N rows)
                    tick_step = max(1, rows // 20)
                    
                    # Create indices that are guaranteed to be within bounds
                    # This ensures we don't try to access indices beyond the size of the array
                    visible_ticks = list(range(0, rows, tick_step))
                    
                    # Always include the first and last tick if not already included
                    if len(visible_ticks) > 0 and visible_ticks[-1] != rows - 1:
                        if rows - 1 not in visible_ticks:  # Only append if not already there
                            visible_ticks.append(rows - 1)
                    
                    # Safety check - ensure all indices are within bounds
                    visible_ticks = [i for i in visible_ticks if 0 <= i < rows]
                    
                    if len(visible_ticks) > 0:  # Only proceed if we have valid ticks
                        # Get current ticks
                        y_ticks = ax.get_yticks()
                        
                        # Extra safety check to ensure we don't have an index error
                        valid_indices = [i for i in visible_ticks if i < len(y_ticks)]
                        
                        if valid_indices:  # Only proceed if we have valid indices
                            # Set visible y-ticks and format them
                            ax.set_yticks([y_ticks[i] for i in valid_indices])
                            ax.set_yticklabels([pivot_table.index[i] for i in valid_indices], 
                                             fontsize=6, rotation=0)
                else:
                    # For smaller datasets, just set the font size
                    plt.setp(ax.get_yticklabels(), fontsize=6, rotation=0)
                
                subtitle = f"Yearly View for {self.selected_year} (Date × Hour)"
            elif current_granularity == "monthly":
                subtitle = "Monthly View (Day × Hour)"
            elif current_granularity == "weekly":
                subtitle = "Weekly View (Day × Hour)"
            else:
                subtitle = "Combined View"
            
            # Use a smaller font size for the title on large heatmaps
            title_fontsize = 14 if (rows <= 20 and cols <= 24) else 12
            ax.set_title(f"{title}\n{subtitle}", fontsize=title_fontsize, pad=10)
            
            # Adjust layout based on view type
            if current_granularity == 'yearly' and rows > 25:
                # More compact layout for large yearly views
                plt.tight_layout(pad=1.2, h_pad=0.8, w_pad=0.8, rect=[0.03, 0.03, 0.97, 0.97])
            elif rows > 20 or cols > 24:
                plt.tight_layout(pad=1.5, h_pad=1.0, w_pad=1.0, rect=[0.05, 0.05, 0.95, 0.95])
            else:
                plt.tight_layout()
            
            # Switch back to the original backend
            matplotlib.use(default_backend)
            
            # Display the figure
            self.display_figure(fig)
            
            # Re-enable buttons
            self.run_button.config(state="normal")
            self.add_file_button.config(state="normal")
            
        except Exception as e:
            error_msg = f"Error creating heatmap: {str(e)}"
            print(error_msg)
            # Create an error figure
            self._create_error_figure(error_msg)
            # Re-enable buttons
            self.run_button.config(state="normal")
            self.add_file_button.config(state="normal")
    
    def update_visualization(self):
        """Update the visualization based on the current settings."""
        if not self.analyzer.has_data():
            messagebox.showinfo("No Data", "No data is loaded. Please import a file first.")
            return
            
        # Disable buttons during update
        self.run_button.config(state="disabled")
        self.add_file_button.config(state="disabled")
        
        # Update status
        self.update_status("Updating visualization...", progress=True)
        
        # Get selected granularity
        granularity = self.selected_granularity.get()
        
        # Run update in a separate thread
        thread = threading.Thread(target=self._update_visualization_thread, args=(granularity,))
        thread.daemon = True
        self.running_threads.append(thread)
        thread.start()

    def _update_visualization_thread(self, granularity):
        """Update visualization in a background thread."""
        try:
            if not self.is_running:
                return
                
            # Create pivot table with selected granularity
            if granularity == "combined":
                # For combined view, we use hourly granularity
                self.analyzer.create_pivot_table(granularity="hourly")
            else:
                self.analyzer.create_pivot_table(granularity=granularity)
        
            # Only proceed if we're still running
            if not self.is_running:
                return
                
            # Prepare data for visualization
            if self.analyzer.pivot_table is None or self.analyzer.pivot_table.empty:
                # Signal main thread to show error
                self.root.after(0, lambda: self.update_status("No data to visualize"))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                self.root.after(0, lambda: self.add_file_button.config(state="normal"))
                return
                
            # We need to pass visualization work to the main thread
            # Store the pivot table for the main thread to use
            self.current_pivot_table = self.analyzer.pivot_table.copy()
            self.current_granularity = granularity
            
            # Signal main thread to create the heatmap with the prepared data
            self.root.after(0, self._create_heatmap_main_thread)
            
            # Update status
            if not self.is_running:
                return
                
            self.root.after(0, lambda: self.update_status(f"Visualization updated ({granularity} view)"))
                
        except Exception as e:
            if self.is_running:
                error_msg = f"Error updating visualization: {str(e)}"
                print(error_msg)
                self.root.after(0, lambda: self.update_status("Error updating visualization"))
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                self.root.after(0, lambda: self.add_file_button.config(state="normal"))
            
    def _create_heatmap_main_thread(self):
        """Create heatmap on the main thread using the prepared data."""
        try:
            # Get the stored pivot table from the worker thread
            pivot_table = self.current_pivot_table
            current_granularity = self.current_granularity
            
            # Check if data is available (should be, but check anyway)
            if pivot_table is None or pivot_table.empty:
                self.update_status("No data to visualize")
                self.run_button.config(state="normal")
                self.add_file_button.config(state="normal")
                return
            
            # Calculate figure size dynamically based on data dimensions
            # For large datasets, use a more conservative scaling to prevent overflow
            rows = len(pivot_table.index)
            cols = len(pivot_table.columns)
            
            # Define standard dimensions for complete datasets to ensure consistent square sizes
            standard_rows = {"monthly": 12, "weekly": 7, "yearly": rows, "hourly": 1}
            standard_cols = 24  # Hours in a day
            
            # Use standard dimensions for calculating aspect ratio to ensure consistent square sizes
            if current_granularity in ['monthly', 'weekly']:
                std_rows = standard_rows.get(current_granularity, rows)
                # Calculate figure size based on standard dimensions rather than actual data size
                # This ensures consistent square sizes regardless of dataset completeness
                height = max(8, min(std_rows * 0.4, 16))
                width = max(10, min(standard_cols * 0.8, 20))
            elif current_granularity == 'yearly':
                # For yearly view, use a more balanced approach to sizing
                # Aim for rectangles with 2:1 ratio (twice as wide as tall)
                row_to_col_ratio = rows / cols
                # Calculate width based on number of columns (hours) - increased for better screen usage
                width = max(16, min(cols * 0.8, 24))  # Increased width for wider rectangles
                # Calculate height based on width and row-to-column ratio, but half as tall for 2:1 ratio
                height = max(6, min(width * row_to_col_ratio * 0.35, 18))  # Adjusted ratio for 2:1 rectangles
                
                # Limit height for very large datasets to prevent excessive stretching
                if rows > 40:
                    height = min(height, 20)
            else:
                # For other views, use the actual data dimensions
                if rows > 20 or cols > 24:
                    height = max(8, min(rows * 0.3, 14))
                    width = max(10, min(cols * 0.6, 18))
                else:
                    height = max(8, min(rows * 0.4, 16))
                    width = max(10, min(cols * 0.8, 20))
            
            # Use non-interactive backend to avoid thread issues
            import matplotlib
            default_backend = matplotlib.get_backend()
            matplotlib.use('Agg')
            
            # Create the figure with extra padding for title and labels
            fig, ax = plt.subplots(figsize=(width, height))
            
            # Set aspect ratio - for yearly view, use 2:1 rectangles instead of squares
            if current_granularity in ['weekly', 'monthly']:
                # Use square cells for weekly and monthly views
                ax.set_aspect('equal', adjustable='box', anchor='C')
            elif current_granularity == 'yearly':
                # For yearly view, use rectangles twice as wide as tall (2:1 ratio)
                # We set aspect to 0.5 to make cells twice as wide as tall
                ax.set_aspect(0.5, adjustable='box', anchor='C')
            
            # Custom colormap with white for NaN/missing values - using updated method to avoid deprecation warning
            try:
                # Modern matplotlib approach (3.7+)
                cmap = matplotlib.colormaps["RdYlGn_r"].copy()
            except (AttributeError, KeyError):
                # Fallback for older versions
                try:
                    cmap = plt.get_cmap("RdYlGn_r").copy()  # Use plt.get_cmap instead of plt.cm.get_cmap
                except:
                    # Last resort fallback
                    cmap = plt.cm.get_cmap("RdYlGn_r").copy()
                    
            cmap.set_bad('white', 1.0)  # Set NaN cells to white
            
            # Create a mask for NaN values
            mask = np.isnan(pivot_table.values)  # Using .values to avoid Series truth value ambiguity
            
            # Determine appropriate linewidth based on view type
            if current_granularity == 'yearly':
                linewidth = 0  # No lines for yearly view to remove spacing between rectangles
            elif current_granularity == 'yearly' and rows > 20:
                linewidth = 0.2  # Thinner lines for yearly view with many rows
            else:
                linewidth = 0.5
            
            # Compute vmin and vmax for adaptive color scaling
            # If it's yearly view, we want to adapt the color scale to show more variation
            vmin, vmax = None, None  # Default values
            if current_granularity == 'yearly':
                # Calculate quartile-based bounds to emphasize the variation in the middle of the data
                # Get the data as numpy array to avoid Series truth value ambiguity
                data_values = pivot_table.values
                if not np.all(mask):  # Using numpy's all instead of mask.all()
                    data_flat = data_values.flatten()
                    data_flat = data_flat[~np.isnan(data_flat)]  # Filter out NaN values
                    
                    if len(data_flat) > 0:
                        # For very low variation data, use percentiles closer to median
                        data_std = np.std(data_flat)
                        data_range = np.max(data_flat) - np.min(data_flat)
                        
                        # If data has low variation, use tighter percentiles to enhance contrast
                        if data_range < 5 or data_std < 2:
                            vmin = np.percentile(data_flat, 30)  # 30th percentile
                            vmax = np.percentile(data_flat, 90)  # 90th percentile
                        else:
                            vmin = np.percentile(data_flat, 10)  # 10th percentile
                            vmax = np.percentile(data_flat, 95)  # 95th percentile
                            
                        # Ensure vmin and vmax are not the same to prevent colormap issues
                        if vmin == vmax:
                            vmin = 0 if vmin == 0 else vmin * 0.9
                            vmax = vmax * 1.1
            
            # Create the heatmap with a color map - without annotations
            sns.heatmap(
                pivot_table, 
                cmap=cmap,
                linewidths=linewidth,
                annot=False,  # No annotations as requested by user
                cbar_kws={'label': 'Average Delay (minutes)'},
                mask=mask,  # Mask NaN values
                vmin=vmin,  # Custom range for color scaling
                vmax=vmax,
                robust=True,  # Use robust quantile-based scaling for color range
                ax=ax
            )
            
            # Set titles and labels
            current_granularity = self.selected_granularity.get()
            title = f"Deployment Delays"
            
            # Optimize tick labels display based on the view type
            if current_granularity == "yearly":
                # Special handling for yearly view to make it more compact and readable
                # Reduce font size for tick labels
                plt.setp(ax.get_xticklabels(), fontsize=6, rotation=45, ha='right')
                
                # For yearly view with many rows, show fewer y-tick labels
                if rows > 25:
                    # Show approximately 20 tick labels (one every N rows)
                    tick_step = max(1, rows // 20)
                    
                    # Create indices that are guaranteed to be within bounds
                    # This ensures we don't try to access indices beyond the size of the array
                    visible_ticks = list(range(0, rows, tick_step))
                    
                    # Always include the first and last tick if not already included
                    if len(visible_ticks) > 0 and visible_ticks[-1] != rows - 1:
                        if rows - 1 not in visible_ticks:  # Only append if not already there
                            visible_ticks.append(rows - 1)
                    
                    # Safety check - ensure all indices are within bounds
                    visible_ticks = [i for i in visible_ticks if 0 <= i < rows]
                    
                    if len(visible_ticks) > 0:  # Only proceed if we have valid ticks
                        # Get current ticks
                        y_ticks = ax.get_yticks()
                        
                        # Extra safety check to ensure we don't have an index error
                        valid_indices = [i for i in visible_ticks if i < len(y_ticks)]
                        
                        if valid_indices:  # Only proceed if we have valid indices
                            # Set visible y-ticks and format them
                            ax.set_yticks([y_ticks[i] for i in valid_indices])
                            ax.set_yticklabels([pivot_table.index[i] for i in valid_indices], 
                                             fontsize=6, rotation=0)
                else:
                    # For smaller datasets, just set the font size
                    plt.setp(ax.get_yticklabels(), fontsize=6, rotation=0)
                
                subtitle = f"Yearly View for {self.selected_year} (Date × Hour)"
            elif current_granularity == "monthly":
                subtitle = "Monthly View (Day × Hour)"
            elif current_granularity == "weekly":
                subtitle = "Weekly View (Day × Hour)"
            else:
                subtitle = "Combined View"
            
            # Use a smaller font size for the title on large heatmaps
            title_fontsize = 14 if (rows <= 20 and cols <= 24) else 12
            ax.set_title(f"{title}\n{subtitle}", fontsize=title_fontsize, pad=10)
            
            # Adjust layout based on view type
            if current_granularity == 'yearly' and rows > 25:
                # More compact layout for large yearly views
                plt.tight_layout(pad=1.2, h_pad=0.8, w_pad=0.8, rect=[0.03, 0.03, 0.97, 0.97])
            elif rows > 20 or cols > 24:
                plt.tight_layout(pad=1.5, h_pad=1.0, w_pad=1.0, rect=[0.05, 0.05, 0.95, 0.95])
            else:
                plt.tight_layout()
            
            # Switch back to the original backend
            matplotlib.use(default_backend)
            
            # Display the figure
            self.display_figure(fig)
            
        except Exception as e:
            error_msg = f"Error creating heatmap: {str(e)}"
            print(error_msg)
            # Create an error figure if possible
            try:
                # Use non-interactive backend for error figure too
                import matplotlib
                default_backend = matplotlib.get_backend()
                matplotlib.use('Agg')
                
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.text(0.5, 0.5, f"Visualization Error:\n\n{error_msg}", 
                        ha='center', va='center', fontsize=12, wrap=True)
                ax.axis('off')
                fig.is_error_figure = True
                
                # Switch back to the original backend
                matplotlib.use(default_backend)
                
                self.display_figure(fig)
            except:
                # Last resort fallback
                print("Could not even create error figure")
        finally:
            # Always re-enable buttons
            self.run_button.config(state="normal")
            self.add_file_button.config(state="normal")
    
    def update_statistics(self):
        """Update the statistics display."""
        stats = self.analyzer.get_statistics()
        
        self.total_records_label.config(
            text=f"Total Records: {stats['total_records']:,}")
        self.avg_delay_label.config(
            text=f"Average Delay: {stats['avg_delay']:.1f} min")
        self.min_delay_label.config(
            text=f"Min Delay: {stats['min_delay']:.1f} min")
        self.max_delay_label.config(
            text=f"Max Delay: {stats['max_delay']:.1f} min")
    
    def update_time_period_buttons(self):
        """Update the time period buttons based on available data."""
        if self.analyzer.cleaned_data is None:
            return
        
        # Clear existing buttons
        for widget in self.months_buttons_frame.winfo_children():
            widget.destroy()
        
        for widget in self.years_buttons_frame.winfo_children():
            widget.destroy()
        
        for widget in self.weeks_buttons_frame.winfo_children():
            widget.destroy()
        
        # Get available years and months
        data = self.analyzer.cleaned_data
        years = sorted(data['Bildankunft'].dt.year.unique())
        
        # Create year buttons (only for years that have data)
        for year in years:
            # Check if there's data for this year
            year_data = data[data['Bildankunft'].dt.year == year]
            if len(year_data) > 0:
                btn = ttk.Button(
                    self.years_buttons_frame, 
                    text=str(year),
                    command=lambda y=year: self.select_year(y)
                )
                btn.pack(side="left", padx=2, pady=2)
        
        # Create month buttons (only for months that have data in the selected year)
        current_year = self.selected_year or (years[0] if years else None)
        if current_year:
            year_data = data[data['Bildankunft'].dt.year == current_year]
            months = sorted(year_data['Bildankunft'].dt.month.unique())
            
            month_names = {
                1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
            }
            
            for month in months:
                # Check if there's data for this month and year
                month_data = year_data[year_data['Bildankunft'].dt.month == month]
                if len(month_data) > 0:
                    btn = ttk.Button(
                        self.months_buttons_frame, 
                        text=month_names.get(month, str(month)),
                        command=lambda m=month, y=current_year: self.select_month_year(m, y)
                    )
                    btn.pack(side="left", padx=2, pady=2)
        
        # Create week buttons (only for weeks that have data in the selected year)
        if current_year in years:
            # Get weeks in the selected year
            year_data = data[data['Bildankunft'].dt.year == current_year]
            
            try:
                # Try to get week numbers - different pandas versions handle this differently
                try:
                    # For newer pandas versions
                    all_weeks = sorted(year_data['Bildankunft'].dt.isocalendar().week.unique())
                except AttributeError:
                    # For older pandas versions
                    all_weeks = sorted(year_data['Bildankunft'].apply(lambda x: x.isocalendar()[1]).unique())
                
                # Create the week buttons (only for weeks that have data)
                for week in all_weeks:
                    try:
                        # Check if there's data for this week
                        week_data = None
                        try:
                            # For newer pandas versions
                            week_data = year_data[year_data['Bildankunft'].dt.isocalendar().week == week]
                        except AttributeError:
                            # For older pandas versions
                            week_data = year_data[year_data['Bildankunft'].apply(lambda x: x.isocalendar()[1]) == week]
                            
                        if week_data is not None and len(week_data) > 0:
                            btn = ttk.Button(
                                self.weeks_buttons_frame, 
                                text=f"W{week}",
                                command=lambda w=week, y=current_year: self.select_week(y, w)
                            )
                            btn.pack(side="left", padx=2, pady=2)
                    except Exception as e:
                        print(f"Error checking data for week {week}: {str(e)}")
                
                # Make sure the week frame is visible if we have week buttons
                if len(self.weeks_buttons_frame.winfo_children()) > 0:
                    self.weeks_frame.pack(fill="x", padx=3, pady=3)
                    self.weeks_label.pack(side="left", padx=3, pady=3)
                    self.weeks_buttons_frame.pack(side="left", fill="x", expand=True, padx=3, pady=3)
                
            except Exception as e:
                # If there's an error getting week data, log it and continue
                print(f"Error creating week buttons: {str(e)}")
                
    def select_month_year(self, month, year):
        """Handle selection of a specific month and year."""
        # Disable buttons during analysis to prevent multiple clicks
        self.run_button.config(state="disabled")
        
        self.selected_month = month
        self.selected_year = year
        self.selected_granularity.set("yearly")
        
        # Update UI to reflect selection
        self.update_status(f"Selecting data for month {month}, year {year}", progress=True)
        
        # Run analysis in a separate thread for better responsiveness
        thread = threading.Thread(target=self._run_month_year_thread, args=(month, year))
        thread.daemon = True
        self.running_threads.append(thread)
        thread.start()
    
    def _run_month_year_thread(self, month, year):
        """Run analysis for a specific month and year in a background thread."""
        try:
            if not self.is_running or self.analyzer.cleaned_data is None:
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                return
            
            # Filter data for the selected month and year
            filtered_df = self.analyzer.cleaned_data.copy()
            filtered_df = filtered_df[
                (filtered_df['Bildankunft'].dt.month == month) & 
                (filtered_df['Jahr'] == year)
            ]
            
            # Check if we have data
            if len(filtered_df) == 0:
                if not self.is_running:
                    return
                self.root.after(0, lambda: self.update_status(f"No data available for {month}/{year}"))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                return
            
            # Store the original data
            original_df = self.analyzer.cleaned_data
            
            # Temporarily replace with filtered data
            self.analyzer.cleaned_data = filtered_df
            
            # Create pivot table with the filtered data
            pivot_table = self.analyzer.create_pivot_table(granularity="daily")
            
            # Restore original data
            self.analyzer.cleaned_data = original_df
            
            if not self.is_running:
                return
                
            # Update visualization with the new figure
            if pivot_table is not None and not pivot_table.empty:
                # Store the pivot table for the main thread to use
                self.current_pivot_table = pivot_table
                self.current_granularity = "yearly"
                
                # Use the main thread to create and display the heatmap
                self.root.after(0, self._create_heatmap_main_thread)
                
                # Update statistics
                stats = {
                    'total_records': len(filtered_df),
                    'avg_delay': filtered_df['Verzögerung_Minuten'].mean(),
                    'min_delay': filtered_df['Verzögerung_Minuten'].min(),
                    'max_delay': filtered_df['Verzögerung_Minuten'].max()
                }
                
                self.root.after(0, lambda: self._update_stats_from_dict(stats))
                self.root.after(0, lambda: self.update_status(f"Analysis complete for {month}/{year}"))
            else:
                self.root.after(0, lambda: self.update_status(f"Could not create visualization for {month}/{year}"))
                
        except Exception as e:
            if not self.is_running:
                return
            error_msg = f"Error analyzing month/year: {str(e)}"
            self.root.after(0, lambda: self.update_status(error_msg))
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", error_msg))
        finally:
            # Always re-enable the button
            if self.is_running:
                self.root.after(0, lambda: self.run_button.config(state="normal"))
    
    def select_year(self, year):
        """Handle selection of a specific year."""
        # Disable buttons during analysis to prevent multiple clicks
        self.run_button.config(state="disabled")
        
        self.selected_month = None
        self.selected_year = year
        self.selected_granularity.set("yearly")
        
        # Update UI to reflect selection
        self.update_status(f"Selecting data for year {year}", progress=True)
        
        # Run analysis in a separate thread for better responsiveness
        thread = threading.Thread(target=self._run_year_thread, args=(year,))
        thread.daemon = True
        self.running_threads.append(thread)
        thread.start()
    
    def _run_year_thread(self, year):
        """Run analysis for a specific year in a background thread."""
        try:
            if not self.is_running or self.analyzer.cleaned_data is None:
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                return
                
            # Filter data for the selected year
            filtered_df = self.analyzer.cleaned_data.copy()
            
            # Use 'Bildankunft' to filter by year rather than 'Jahr' column
            filtered_df = filtered_df[filtered_df['Bildankunft'].dt.year == year]
            
            # Check if we have data
            if len(filtered_df) == 0:
                if not self.is_running:
                    return
                self.root.after(0, lambda: self.update_status(f"No data available for year {year}"))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                return
            
            # Store the original data
            original_df = self.analyzer.cleaned_data
            
            # Temporarily replace with filtered data
            self.analyzer.cleaned_data = filtered_df
            
            # Create pivot table with the filtered data - using month and day
            pivot_table = self.analyzer.create_pivot_table(granularity="yearly")
            
            # Store the pivot table for the main thread to use
            self.current_pivot_table = pivot_table
            self.current_granularity = "yearly"
            
            # Use the main thread to create and display the heatmap
            self.root.after(0, self._create_heatmap_main_thread)
            
            # Update statistics based on filtered data
            stats = {
                'total_records': len(filtered_df),
                'avg_delay': filtered_df['Verzögerung_Minuten'].mean(),
                'min_delay': filtered_df['Verzögerung_Minuten'].min(),
                'max_delay': filtered_df['Verzögerung_Minuten'].max()
            }
            
            # Restore original data
            self.analyzer.cleaned_data = original_df
            
            if not self.is_running:
                return
                
            self.root.after(0, lambda: self._update_stats_from_dict(stats))
            self.root.after(0, lambda: self.update_status(f"Analysis complete for year {year}"))
        except Exception as e:
            if not self.is_running:
                return
            error_msg = f"Error analyzing year: {str(e)}"
            self.root.after(0, lambda: self.update_status(error_msg))
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", error_msg))
        finally:
            # Always re-enable the button
            if self.is_running:
                self.root.after(0, lambda: self.run_button.config(state="normal"))
    
    def select_week(self, year, week_num):
        """Select a specific week to display."""
        if self.analyzer.cleaned_data is None:
            messagebox.showwarning("No Data", "Please run the analysis first.")
            return

        # Update selected values
        self.selected_year = year
        self.selected_week = week_num
        self.selected_month = None
        self.selected_granularity.set("weekly")
        
        # Disable buttons during analysis
        self.run_button.config(state="disabled")
        
        # Update status to show we're processing
        self.update_status(f"Analyzing data for week {week_num} of {year}...", progress=True)
        
        # Run the analysis in a separate thread
        thread = threading.Thread(target=self._run_week_analysis, args=(year, week_num))
        thread.daemon = True
        self.running_threads.append(thread)
        thread.start()

    def _run_week_analysis(self, year, week_num):
        """Run analysis for a specific week."""
        try:
            # Filter data for the selected week
            data = self.analyzer.cleaned_data
            
            try:
                # Try to convert week number to date range
                # The %w format specifier expects 0 for Sunday, but some systems use 1 for Monday
                try:
                    # Try with Monday as first day of week
                    first_day = datetime.strptime(f'{year}-W{week_num}-1', '%Y-W%W-%w')
                except ValueError:
                    # Try with Sunday as first day of week
                    first_day = datetime.strptime(f'{year}-W{week_num}', '%Y-W%W')
            
                last_day = first_day + timedelta(days=6)
                
                # Filter data for the date range
                week_data = data[(data['Bildankunft'].dt.date >= first_day.date()) & 
                                (data['Bildankunft'].dt.date <= last_day.date())]
                
                if len(week_data) == 0:
                    # Try a broader approach - get the week directly from the data
                    try:
                        # For newer pandas versions
                        week_data = data[data['Bildankunft'].dt.isocalendar().week == week_num]
                    except AttributeError:
                        # For older pandas versions
                        week_data = data[data['Bildankunft'].apply(lambda x: x.isocalendar()[1]) == week_num]
                
                if len(week_data) == 0:
                    self.root.after(0, lambda: self.update_status(f"No data available for week {week_num} of {year}"))
                    self.root.after(0, lambda: self.run_button.config(state="normal"))
                    return
                
                # Create a new temporary analyzer with just this data
                temp_analyzer = DeploymentAnalyzer()
                temp_analyzer.cleaned_data = week_data
                
                # Create pivot table for this week
                pivot_table = temp_analyzer.create_pivot_table(granularity="daily")
                
                if not pivot_table.empty:
                    # Store the pivot table for the main thread to use
                    self.current_pivot_table = pivot_table
                    self.current_granularity = "weekly"
                    
                    # Use the main thread to create and display the heatmap
                    self.root.after(0, self._create_heatmap_main_thread)
                    
                    # Update statistics based on filtered data
                    stats = {
                        'total_records': len(week_data),
                        'avg_delay': week_data['Verzögerung_Minuten'].mean(),
                        'min_delay': week_data['Verzögerung_Minuten'].min(),
                        'max_delay': week_data['Verzögerung_Minuten'].max()
                    }
                    
                    self.root.after(0, lambda: self._update_stats_from_dict(stats))
                    self.root.after(0, lambda: self.update_status(f"Analysis complete for week {week_num} of {year}"))
                else:
                    self.root.after(0, lambda: self.update_status(f"Could not create visualization for week {week_num}"))
            
            except ValueError as e:
                self.root.after(0, lambda: self.update_status(f"Error with date conversion: {str(e)}"))
                print(f"Date conversion error: {str(e)}")
        
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Error during week analysis: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", f"An error occurred while analyzing week data: {str(e)}"))
        
        finally:
            # Always re-enable the button
            self.root.after(0, lambda: self.run_button.config(state="normal"))
    
    def update_statistics(self):
        """Update the statistics display."""
        stats = self.analyzer.get_statistics()
        
        self.total_records_label.config(
            text=f"Total Records: {stats['total_records']}")
        self.avg_delay_label.config(
            text=f"Average Delay: {stats['avg_delay']:.1f} min")
        self.min_delay_label.config(
            text=f"Min Delay: {stats['min_delay']:.1f} min")
        self.max_delay_label.config(
            text=f"Max Delay: {stats['max_delay']:.1f} min")
    
    def export_heatmap(self):
        """Export the current heatmap to a file."""
        if self.current_figure is None:
            messagebox.showwarning("No Visualization", "Please run the analysis first.")
            return
        
        # Create a descriptive filename based on current view
        default_filename = self._generate_export_filename("heatmap", ".png")
            
        file_path = filedialog.asksaveasfilename(
            title="Save Heatmap",
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[
                ("PNG Image", "*.png"),
                ("PDF Document", "*.pdf"),
                ("SVG Image", "*.svg"),
                ("JPEG Image", "*.jpg"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.update_status(f"Exporting heatmap to {file_path}")
                
                success = self.analyzer.save_heatmap(self.current_figure, file_path)
                
                if success:
                    self.update_status(f"Heatmap exported to {os.path.basename(file_path)}")
                else:
                    self.update_status("Error exporting heatmap")
                    
            except Exception as e:
                error_msg = f"Error exporting heatmap: {str(e)}"
                messagebox.showerror("Export Error", error_msg)
                self.update_status("Error exporting heatmap")
    
    def export_data(self):
        """Export the cleaned data to a file."""
        if self.analyzer.cleaned_data is None:
            messagebox.showwarning("No Data", "Please run the analysis first.")
            return
        
        # Create a descriptive filename based on current view
        default_filename = self._generate_export_filename("data", ".csv")
            
        file_path = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[
                ("CSV File", "*.csv"),
                ("Excel File", "*.xlsx"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.update_status(f"Exporting data to {file_path}")
                
                success = self.analyzer.export_data(file_path)
                
                if success:
                    self.update_status(f"Data exported to {os.path.basename(file_path)}")
                else:
                    self.update_status("Error exporting data")
                    
            except Exception as e:
                error_msg = f"Error exporting data: {str(e)}"
                messagebox.showerror("Export Error", error_msg)
                self.update_status("Error exporting data")
    
    def show_help(self):
        """Show a help dialog."""
        help_window = tk.Toplevel(self.root)
        help_window.title("deployment-analyse ver. 1.0.0")
        help_window.geometry("700x650")
        help_window.minsize(650, 600)
        
        # Create a frame with scrollable text
        frame = ttk.Frame(help_window)
        frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create a text widget with the scrollbar
        text = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, 
                      font=("Helvetica", 11), padx=10, pady=5)
        text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text.yview)
        
        # Help text
        help_text = """
# deployment-analyse ver. 1.0.0

Copyright © 2025 Axel Schmidt. All rights reserved.

This tool analyzes the processing delays in image deployment systems.

## Getting Started

1. Use the 'Import' button to select your Excel or CSV file.
2. The analysis will run automatically after importing the file.
3. Use the time period controls at the bottom to navigate different views.

## Screen Layout

The screen is divided into three main sections:

1. **Top Control Panel**: Contains file selection, statistics, and the current view indicator.
2. **Center Visualization Area**: Displays the heatmap visualization (the main focus).
3. **Bottom Navigation Panel**: Contains the time period selection controls.

## View Types

The application supports different view types:

- **Yearly View**: Shows patterns across a full year, with dates on the Y-axis 
  and hours on the X-axis. This is the default view after importing data.
- **Monthly View**: Shows daily patterns within a selected month, with days on the Y-axis 
  and hours on the X-axis.
- **Weekly View**: Shows daily patterns within a selected week, with weekdays on the Y-axis 
  and hours on the X-axis.

## Time Period Navigation

The time period buttons at the bottom allow you to:

- Select a specific year to view its yearly pattern
- Select a specific month to view its daily pattern
- Select a specific week to view its daily pattern

## Understanding the Heatmap

- The heatmap displays average processing delays across time periods.
- Darker/more intense colors indicate longer processing delays.
- The scale is in minutes.

## Exporting Results

- Use the 'Export Image' button to save the current heatmap visualization as a PNG file.
- Use the 'Export Data' button to save the processed data as a CSV or Excel file.

## Adding More Data

You can add additional data files by clicking the '+ Add Data' button. This allows you to:

- Combine multiple data sources for analysis
- Compare different time periods or systems
- Build a more comprehensive dataset
"""
        
        # Insert the help text
        text.insert("1.0", help_text)
        text.config(state="disabled")  # Make it read-only
        
        # Add a close button
        button_frame = ttk.Frame(help_window)
        button_frame.pack(pady=15, padx=20, fill="x")
        
        close_button = ttk.Button(button_frame, text="Close", command=help_window.destroy, width=15)
        close_button.pack(side="right")
    
    def _update_stats_from_dict(self, stats):
        """Update the statistics labels with values from the stats dictionary."""
        try:
            # Update statistics labels
            self.total_records_label.config(
                text=f"Total Records: {stats['total_records']:,}")
            self.avg_delay_label.config(
                text=f"Average Delay: {stats['avg_delay']:.1f} min")
            self.max_delay_label.config(
                text=f"Max Delay: {stats['max_delay']:.1f} min")
            self.min_delay_label.config(
                text=f"Min Delay: {stats['min_delay']:.1f} min")
        except Exception as e:
            print(f"Error updating statistics: {str(e)}")
            # Set default values in case of error
            self.total_records_label.config(text="Total Records: N/A")
            self.avg_delay_label.config(text="Average Delay: N/A")
            self.max_delay_label.config(text="Max Delay: N/A")
            self.min_delay_label.config(text="Min Delay: N/A")
    
    def update_status(self, message, progress=False):
        """Update the status bar with a message."""
        # Check if the application is still running
        if not hasattr(self, 'is_running') or not self.is_running:
            return
            
        try:
            self.status_label.config(text=message)
            
            if progress:
                # Reset progress to 0
                self.progress["value"] = 0
                self.progress["maximum"] = 100
                
                # Create a simulation of progress
                def update_progress():
                    try:
                        progress_value = 0
                        
                        # Check if the application is still running
                        while progress_value < 100 and self.is_running:
                            try:
                                progress_value += 5
                                if progress_value > 100:
                                    progress_value = 100
                                
                                # Update the progress bar in the main thread
                                if self.is_running:
                                    self.root.after(0, lambda val=progress_value: self.progress.config(value=val))
                                
                                # Sleep to simulate processing
                                time.sleep(0.1)
                            except Exception as e:
                                print(f"Progress update error: {str(e)}")
                                # In case of errors, just break the loop
                                break
                    except Exception as e:
                        print(f"Progress thread error: {str(e)}")
                
                # Start progress update in a background thread
                progress_thread = threading.Thread(target=update_progress)
                progress_thread.daemon = True
                self.running_threads.append(progress_thread)
                progress_thread.start()
            else:
                self.progress["value"] = 0
        except Exception as e:
            # If any error occurs, just print it and continue
            print(f"Status update error: {str(e)}")
    
    def display_figure(self, fig=None):
        """Display a Matplotlib figure in the GUI."""
        # Ensure this function runs on the main thread
        if threading.current_thread() is not threading.main_thread():
            if not self.is_running:
                return
            self.root.after(0, lambda: self.display_figure(fig))
            return

        try:
            if fig is None and not hasattr(self, 'current_figure'):
                return  # No figure to display
            
            # Use the provided figure or fall back to the current figure
            figure_to_display = fig if fig is not None else self.current_figure
            
            # Store the current figure for future reference
            self.current_figure = figure_to_display
            
            # Clear any existing canvas
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            
            # Create a scrollable frame for large figures
            canvas_scroll_frame = ttk.Frame(self.canvas_frame)
            canvas_scroll_frame.pack(fill="both", expand=True)
            
            # Add scrollbars for large figures
            h_scrollbar = ttk.Scrollbar(canvas_scroll_frame, orient="horizontal")
            v_scrollbar = ttk.Scrollbar(canvas_scroll_frame, orient="vertical")
            
            # Create a new canvas with scrollbars
            canvas = FigureCanvasTkAgg(figure_to_display, master=canvas_scroll_frame)
            canvas.draw()
            
            # Get the canvas widget and configure with scrollbars
            canvas_widget = canvas.get_tk_widget()
            
            # Configure scrollbars
            h_scrollbar.config(command=canvas_widget.xview)
            v_scrollbar.config(command=canvas_widget.yview)
            canvas_widget.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
            
            # Pack scrollbars and canvas
            h_scrollbar.pack(side="bottom", fill="x")
            v_scrollbar.pack(side="right", fill="y")
            canvas_widget.pack(side="left", fill="both", expand=True)
            
            # Make the canvas scrollable
            canvas_widget.config(scrollregion=canvas_widget.bbox("all"))
            
            # Add toolbar if not an error message
            if not getattr(figure_to_display, 'is_error_figure', False):
                toolbar = NavigationToolbar2Tk(canvas, canvas_scroll_frame)
                toolbar.update()
                toolbar.pack(side="bottom", fill="x")
            
            # Update status
            self.update_status("Visualization updated")
            
        except Exception as e:
            error_msg = f"Error displaying figure: {str(e)}"
            print(error_msg)
            if self.is_running:
                self.update_status("Error displaying visualization")
                # Create an error figure if there was an error
                self._create_error_figure(str(e))

    def _create_error_figure(self, error_message):
        """Create a figure with an error message when visualization fails."""
        try:
            # Create a simple figure with the error message
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, f"Visualization Error:\n\n{error_message}", 
                    ha='center', va='center', fontsize=12, wrap=True)
            ax.axis('off')
            
            # Mark this as an error figure to avoid adding toolbar
            fig.is_error_figure = True
            
            # Display the error figure
            self.display_figure(fig)
        except Exception as e:
            # Last resort if even creating an error figure fails
            print(f"Failed to create error figure: {str(e)}")
            self.update_status("Visualization failed")

    def _generate_export_filename(self, prefix, extension):
        """Generate a descriptive filename based on current view."""
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        current_granularity = self.selected_granularity.get()
        if current_granularity == "yearly" and self.selected_year is not None:
            return f"{prefix}_year_{self.selected_year}_{timestamp}{extension}"
        elif current_granularity == "monthly" and self.selected_month is not None and self.selected_year is not None:
            month_name = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            }.get(self.selected_month, f"{self.selected_month}")
            return f"{prefix}_month_{month_name}_{self.selected_year}_{timestamp}{extension}"
        elif current_granularity == "weekly" and self.selected_week is not None and self.selected_year is not None:
            return f"{prefix}_week_{self.selected_week}_{self.selected_year}_{timestamp}{extension}"
        else:  # "hourly" (combined view) or any other case
            return f"{prefix}_{current_granularity}_{timestamp}{extension}"

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Image Deployment Analysis Tool")
    
    parser.add_argument("--file", help="Path to the Excel or CSV file")
    parser.add_argument("--output", help="Path to save the output heatmap")
    parser.add_argument("--gui", action="store_true", help="Start with the GUI interface")
    parser.add_argument("--max-delay", type=float, help="Maximum delay to include (in minutes)")
    
    args = parser.parse_args()
    
    # If no arguments were provided at all, default to GUI mode
    if len(sys.argv) == 1:
        args.gui = True
    
    # Check if the config specifies default GUI mode
    if config_loaded and 'Options' in app_config and 'DefaultGUIMode' in app_config['Options']:
        default_gui = app_config['Options']['DefaultGUIMode'].lower() in ('true', 'yes', '1')
        if default_gui and not any(arg in sys.argv for arg in ('--file', '--output', '--max-delay')):
            print("Using DefaultGUIMode=True from config file")
            args.gui = True
    
    return args

def run_command_line(args):
    """Run the tool in command-line mode."""
    if not args.file:
        print("Error: --file argument is required in command-line mode.")
        return
        
    print(f"Analyzing file: {args.file}")
    
    analyzer = DeploymentAnalyzer()
    
    # Import the file
    df = analyzer.import_file(args.file)
    if df is None:
        print("Error: Failed to import the file.")
        return
        
    print(f"Imported {len(df)} rows from {args.file}")
    
    # Process the data
    cleaned_df = analyzer.process_data()
    if cleaned_df is None:
        print("Error: Failed to process the data.")
        return
        
    print(f"Processed data: {len(cleaned_df)} rows after cleaning")
    
    # Calculate statistics
    stats = analyzer.get_statistics()
    print("\nStatistics:")
    print(f"Total Records: {stats['total_records']:,}")
    print(f"Average Delay: {stats['avg_delay']:.1f} minutes")
    print(f"Minimum Delay: {stats['min_delay']:.1f} minutes")
    print(f"Maximum Delay: {stats['max_delay']:.1f} minutes")
    
    # Create pivot table and heatmap
    pivot = analyzer.create_pivot_table(max_delay=args.max_delay, granularity="daily")
    if pivot is None:
        print("Error: Failed to create pivot table.")
        return
        
    fig = analyzer.create_heatmap()
    if isinstance(fig, str):
        print(f"Error: {fig}")
        return
    elif fig is None:
        print("Error: Failed to create heatmap.")
        return
        
    # Save or display the heatmap
    if args.output:
        success = analyzer.save_heatmap(fig, args.output)
        if success:
            print(f"Saved heatmap to {args.output}")
        else:
            print(f"Error saving heatmap to {args.output}")
    else:
        print("Displaying heatmap (close the window to continue)")
        plt.show()
        
    print("\nAnalysis complete.")

def main():
    """Main entry point for the application."""
    print("Entering main function")
    
    try:
        args = parse_arguments()
        
        print(f"Command-line arguments: {args}")
        
        if args.gui:
            # Start the GUI
            print("Starting GUI mode")
            root = tk.Tk()
            
            # Set exception handler for unhandled exceptions
            def handle_exception(exc_type, exc_value, exc_traceback):
                print("Unhandled exception:")
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                # Save error to a file in case GUI is not visible
                try:
                    with open(os.path.join(logs_dir, 'error.log'), 'a') as f:
                        f.write(f"\n--- Exception at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
                except:
                    pass  # If we can't write to the file, just continue
                
                messagebox.showerror(
                    "Unhandled Exception",
                    f"An unexpected error occurred: {exc_value}\n\nSee logs for details."
                )
            
            # Set up exception handling
            import sys
            sys.excepthook = handle_exception
            
            try:
                app = SimpleAnalysisGUI(root)
                
                # If a file was specified, load it
                if args.file:
                    app.file_path = args.file
                    app.path_var.set(args.file)
                    root.after(100, app.run_analysis)  # Run after UI is fully initialized
                    
                print("Starting Tkinter main loop")
                root.mainloop()
                print("Tkinter main loop ended")
            except Exception as e:
                error_message = f"Error starting the application: {str(e)}"
                print(error_message)
                # Save error to a file
                try:
                    with open(os.path.join(logs_dir, 'gui_error.log'), 'a') as f:
                        f.write(f"\n--- GUI Error at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                        f.write(error_message + "\n")
                        traceback.print_exc(file=f)
                except:
                    pass  # If we can't write to the file, just continue
                
                messagebox.showerror("Application Error", error_message)
                traceback.print_exc()
                try:
                    root.destroy()
                except:
                    pass
        else:
            # Run in command-line mode
            print("Starting command-line mode")
            run_command_line(args)
    except Exception as e:
        error_message = f"Fatal error: {str(e)}"
        print(error_message)
        # Save error to a file
        try:
            with open(os.path.join(logs_dir, 'fatal_error.log'), 'a') as f:
                f.write(f"\n--- Fatal Error at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                f.write(error_message + "\n")
                traceback.print_exc(file=f)
        except:
            pass  # If we can't write to the file, just continue
        
        traceback.print_exc()
        
        # Try to show a message box if possible
        try:
            messagebox.showerror("Fatal Error", error_message)
        except:
            pass

if __name__ == "__main__":
    main()
