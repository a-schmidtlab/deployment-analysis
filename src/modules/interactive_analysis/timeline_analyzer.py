"""
Timeline Analyzer

This module provides functionality for analyzing image processing
time data across different time periods.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

class TimelineAnalyzer:
    """
    Class for analyzing time-based patterns in image processing data.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize the TimelineAnalyzer.
        
        Args:
            db_connection: Database connection object.
        """
        self.db_connection = db_connection
        self.data = None
        self.time_granularity = 'hour'  # Default granularity
        self.available_granularities = ['minute', 'hour', 'day', 'week', 'month', 'year']
    
    def load_data(self, data=None, date_range=None):
        """
        Load data for analysis, either from a DataFrame or from the database.
        
        Args:
            data (DataFrame): DataFrame containing image processing data.
            date_range (tuple): Start and end date for filtering.
            
        Returns:
            bool: Success status of the operation.
        """
        if data is not None:
            # Data provided directly
            self.data = data.copy()
            logger.info(f"Loaded {len(self.data)} rows from provided DataFrame")
            return True
            
        elif self.db_connection:
            # Fetch data from database
            query = """
                SELECT 
                    bildankunft_timestamp, activation_timestamp, 
                    processing_delay_minutes, weekday, hour, date
                FROM image_data
            """
            
            # Add date filtering if specified
            params = None
            if date_range:
                start_date, end_date = date_range
                query += " WHERE date BETWEEN ? AND ?"
                params = (start_date, end_date)
            
            # Execute query
            try:
                self.data = self.db_connection.query_data(query, params)
                
                # Convert string dates back to datetime
                for col in ['bildankunft_timestamp', 'activation_timestamp', 'date']:
                    if col in self.data.columns:
                        self.data[col] = pd.to_datetime(self.data[col])
                
                logger.info(f"Loaded {len(self.data)} rows from database")
                return True
                
            except Exception as e:
                logger.error(f"Error loading data from database: {str(e)}")
                return False
        else:
            logger.error("No data source provided")
            return False
    
    def set_time_granularity(self, granularity):
        """
        Set the time granularity for analysis.
        
        Args:
            granularity (str): Time granularity ('minute', 'hour', 'day', 'week', 'month', 'year').
            
        Returns:
            bool: Whether the granularity was successfully set.
        """
        if granularity not in self.available_granularities:
            logger.error(f"Invalid granularity '{granularity}'. Valid options: {self.available_granularities}")
            return False
            
        self.time_granularity = granularity
        logger.info(f"Time granularity set to {granularity}")
        return True
    
    def _group_by_time(self):
        """
        Group data by the current time granularity.
        
        Returns:
            DataFrame: Grouped data.
        """
        if self.data is None:
            logger.error("No data loaded")
            return None
            
        # Create copy to avoid modifying original
        df = self.data.copy()
        
        # Ensure bildankunft_timestamp is datetime
        if 'bildankunft_timestamp' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['bildankunft_timestamp']):
                df['bildankunft_timestamp'] = pd.to_datetime(df['bildankunft_timestamp'])
        else:
            logger.error("Required column 'bildankunft_timestamp' not found")
            return None
        
        # Group by time according to granularity
        if self.time_granularity == 'minute':
            df['time_group'] = df['bildankunft_timestamp'].dt.floor('min')
        elif self.time_granularity == 'hour':
            df['time_group'] = df['bildankunft_timestamp'].dt.floor('H')
        elif self.time_granularity == 'day':
            df['time_group'] = df['bildankunft_timestamp'].dt.floor('D')
        elif self.time_granularity == 'week':
            df['time_group'] = df['bildankunft_timestamp'].dt.to_period('W').dt.start_time
        elif self.time_granularity == 'month':
            df['time_group'] = df['bildankunft_timestamp'].dt.to_period('M').dt.start_time
        elif self.time_granularity == 'year':
            df['time_group'] = df['bildankunft_timestamp'].dt.to_period('Y').dt.start_time
        
        # Group by the time group
        grouped = df.groupby('time_group').agg({
            'processing_delay_minutes': ['count', 'mean', 'median', 'min', 'max', 'std']
        })
        
        # Flatten the MultiIndex columns
        grouped.columns = [f"{col[0]}_{col[1]}" for col in grouped.columns]
        
        # Reset index to make time_group a column
        grouped = grouped.reset_index()
        
        return grouped
    
    def analyze_time_pattern(self):
        """
        Analyze processing time patterns based on the current granularity.
        
        Returns:
            DataFrame: Analysis results.
        """
        # Group data by time
        grouped_data = self._group_by_time()
        
        if grouped_data is None:
            return None
            
        logger.info(f"Analyzed time patterns with {len(grouped_data)} {self.time_granularity} groups")
        return grouped_data
    
    def analyze_weekday_hour_pattern(self):
        """
        Create a heatmap of processing times by weekday and hour.
        
        Returns:
            DataFrame: Pivot table of processing times by weekday and hour.
        """
        if self.data is None:
            logger.error("No data loaded")
            return None
            
        # Create weekday-hour pivot table
        try:
            pivot_table = pd.pivot_table(
                self.data,
                values='processing_delay_minutes',
                index='weekday',
                columns='hour',
                aggfunc='mean',
                fill_value=0
            )
            
            # Sort weekdays in correct order
            weekday_order = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
            pivot_table = pivot_table.reindex(weekday_order)
            
            logger.info("Created weekday-hour pattern analysis")
            return pivot_table
            
        except Exception as e:
            logger.error(f"Error creating weekday-hour pattern: {str(e)}")
            return None
    
    def plot_timeline(self, metric='mean', figsize=(15, 8), title=None, color='blue', save_path=None):
        """
        Plot a timeline of processing delays.
        
        Args:
            metric (str): Metric to plot ('count', 'mean', 'median', 'min', 'max').
            figsize (tuple): Figure size.
            title (str): Plot title.
            color (str): Line color.
            save_path (str): Path to save the figure.
            
        Returns:
            matplotlib.figure.Figure: The created figure.
        """
        # Group data by time
        grouped_data = self._group_by_time()
        
        if grouped_data is None:
            return None
            
        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        column_name = f"processing_delay_minutes_{metric}"
        if column_name not in grouped_data.columns:
            logger.error(f"Metric '{metric}' not available")
            return None
            
        ax.plot(grouped_data['time_group'], grouped_data[column_name], '-o', color=color)
        
        # Set title and labels
        ax.set_title(title or f"{metric.capitalize()} Processing Delay by {self.time_granularity.capitalize()}")
        ax.set_xlabel(self.time_granularity.capitalize())
        ax.set_ylabel(f"{metric.capitalize()} Processing Delay (minutes)")
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Tight layout for better spacing
        plt.tight_layout()
        
        # Save figure if path provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Saved timeline plot to {save_path}")
        
        return fig
    
    def plot_weekday_hour_heatmap(self, figsize=(15, 8), cmap='YlOrRd', save_path=None):
        """
        Plot a heatmap of processing delays by weekday and hour.
        
        Args:
            figsize (tuple): Figure size.
            cmap (str): Colormap name.
            save_path (str): Path to save the figure.
            
        Returns:
            matplotlib.figure.Figure: The created figure.
        """
        # Get weekday-hour pivot table
        pivot_table = self.analyze_weekday_hour_pattern()
        
        if pivot_table is None:
            return None
            
        # Create the heatmap
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.heatmap(
            pivot_table,
            cmap=cmap,
            annot=True,
            fmt='.0f',
            cbar_kws={'label': 'Average Processing Delay (minutes)'},
            ax=ax
        )
        
        # Set title and labels
        ax.set_title('Average Processing Delays by Weekday and Hour')
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Weekday')
        
        # Tight layout for better spacing
        plt.tight_layout()
        
        # Save figure if path provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Saved heatmap to {save_path}")
        
        return fig
    
    def compare_time_periods(self, period1, period2, metric='mean'):
        """
        Compare processing delays between two time periods.
        
        Args:
            period1 (tuple): Start and end date of first period.
            period2 (tuple): Start and end date of second period.
            metric (str): Metric to compare ('count', 'mean', 'median', 'min', 'max').
            
        Returns:
            dict: Comparison results.
        """
        if self.data is None:
            logger.error("No data loaded")
            return None
            
        try:
            # Filter data for each period
            start1, end1 = period1
            start2, end2 = period2
            
            # Ensure bildankunft_timestamp is datetime
            if not pd.api.types.is_datetime64_any_dtype(self.data['bildankunft_timestamp']):
                self.data['bildankunft_timestamp'] = pd.to_datetime(self.data['bildankunft_timestamp'])
            
            period1_data = self.data[
                (self.data['bildankunft_timestamp'] >= start1) & 
                (self.data['bildankunft_timestamp'] <= end1)
            ]
            
            period2_data = self.data[
                (self.data['bildankunft_timestamp'] >= start2) & 
                (self.data['bildankunft_timestamp'] <= end2)
            ]
            
            # Calculate statistics
            if metric == 'count':
                stat1 = len(period1_data)
                stat2 = len(period2_data)
                diff = stat2 - stat1
                pct_change = (diff / stat1 * 100) if stat1 > 0 else float('inf')
            else:
                stat1 = getattr(period1_data['processing_delay_minutes'], metric)()
                stat2 = getattr(period2_data['processing_delay_minutes'], metric)()
                diff = stat2 - stat1
                pct_change = (diff / stat1 * 100) if stat1 > 0 else float('inf')
            
            comparison = {
                'period1': {
                    'start': start1,
                    'end': end1,
                    'value': stat1,
                    'count': len(period1_data)
                },
                'period2': {
                    'start': start2,
                    'end': end2,
                    'value': stat2,
                    'count': len(period2_data)
                },
                'difference': diff,
                'percent_change': pct_change
            }
            
            logger.info(f"Compared time periods: {metric} changed by {pct_change:.2f}%")
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing time periods: {str(e)}")
            return None 