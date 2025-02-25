"""
Anomaly Detector

This module provides functionality for detecting anomalies in
image processing delay data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Class for detecting anomalies in image processing delay data.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize the AnomalyDetector.
        
        Args:
            db_connection: Database connection object.
        """
        self.db_connection = db_connection
        self.data = None
        self.anomalies = None
        self.threshold_method = 'zscore'  # Default method
        self.threshold_value = 3.0  # Default z-score threshold
        self.available_methods = ['zscore', 'iqr', 'percentile', 'absolute']
    
    def load_data(self, data=None, date_range=None):
        """
        Load data for anomaly detection, either from a DataFrame or from the database.
        
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
    
    def set_threshold_method(self, method, value=None):
        """
        Set the threshold method and value for anomaly detection.
        
        Args:
            method (str): Threshold method ('zscore', 'iqr', 'percentile', 'absolute').
            value (float): Threshold value.
            
        Returns:
            bool: Whether the method was successfully set.
        """
        if method not in self.available_methods:
            logger.error(f"Invalid method '{method}'. Valid options: {self.available_methods}")
            return False
            
        self.threshold_method = method
        
        if value is not None:
            self.threshold_value = value
            
        logger.info(f"Threshold method set to {method} with value {self.threshold_value}")
        return True
    
    def detect_anomalies(self):
        """
        Detect anomalies in the processing delay data.
        
        Returns:
            DataFrame: Anomalies detected in the data.
        """
        if self.data is None:
            logger.error("No data loaded")
            return None
            
        if 'processing_delay_minutes' not in self.data.columns:
            logger.error("Required column 'processing_delay_minutes' not found")
            return None
            
        # Create a copy to avoid modifying the original
        df = self.data.copy()
        df['is_anomaly'] = False
        df['anomaly_score'] = 0.0
        
        # Apply the selected detection method
        try:
            if self.threshold_method == 'zscore':
                # Z-score method
                mean = df['processing_delay_minutes'].mean()
                std = df['processing_delay_minutes'].std()
                df['anomaly_score'] = np.abs((df['processing_delay_minutes'] - mean) / std)
                df['is_anomaly'] = df['anomaly_score'] > self.threshold_value
                
            elif self.threshold_method == 'iqr':
                # IQR method
                Q1 = df['processing_delay_minutes'].quantile(0.25)
                Q3 = df['processing_delay_minutes'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - self.threshold_value * IQR
                upper_bound = Q3 + self.threshold_value * IQR
                df['anomaly_score'] = np.maximum(
                    (lower_bound - df['processing_delay_minutes']) / IQR,
                    (df['processing_delay_minutes'] - upper_bound) / IQR
                )
                df['anomaly_score'] = df['anomaly_score'].clip(lower=0)
                df['is_anomaly'] = (df['processing_delay_minutes'] < lower_bound) | (df['processing_delay_minutes'] > upper_bound)
                
            elif self.threshold_method == 'percentile':
                # Percentile method
                threshold_pct = 100 - self.threshold_value
                upper_bound = df['processing_delay_minutes'].quantile(threshold_pct / 100)
                df['anomaly_score'] = df['processing_delay_minutes'] / upper_bound
                df['is_anomaly'] = df['processing_delay_minutes'] > upper_bound
                
            elif self.threshold_method == 'absolute':
                # Absolute threshold method
                df['anomaly_score'] = df['processing_delay_minutes'] / self.threshold_value
                df['is_anomaly'] = df['processing_delay_minutes'] > self.threshold_value
            
            # Store anomalies for later use
            self.anomalies = df[df['is_anomaly']]
            
            anomaly_count = len(self.anomalies)
            anomaly_percent = (anomaly_count / len(df)) * 100
            logger.info(f"Detected {anomaly_count} anomalies ({anomaly_percent:.2f}% of data)")
            
            return self.anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return None
    
    def get_summary(self):
        """
        Get a summary of detected anomalies.
        
        Returns:
            dict: Summary of anomalies.
        """
        if self.anomalies is None or len(self.anomalies) == 0:
            logger.warning("No anomalies detected or detect_anomalies() not called yet")
            return {
                'count': 0,
                'percentage': 0,
                'avg_score': 0,
                'method': self.threshold_method,
                'threshold': self.threshold_value
            }
            
        total_count = len(self.data) if self.data is not None else 0
        
        summary = {
            'count': len(self.anomalies),
            'percentage': (len(self.anomalies) / total_count) * 100 if total_count > 0 else 0,
            'avg_score': self.anomalies['anomaly_score'].mean(),
            'max_score': self.anomalies['anomaly_score'].max(),
            'min_delay': self.anomalies['processing_delay_minutes'].min(),
            'max_delay': self.anomalies['processing_delay_minutes'].max(),
            'avg_delay': self.anomalies['processing_delay_minutes'].mean(),
            'method': self.threshold_method,
            'threshold': self.threshold_value
        }
        
        # Add time-based summaries if timestamps are available
        if 'bildankunft_timestamp' in self.anomalies.columns:
            # Most common weekdays
            if 'weekday' in self.anomalies.columns:
                weekday_counts = self.anomalies['weekday'].value_counts()
                summary['weekday_distribution'] = weekday_counts.to_dict()
                
            # Most common hours
            if 'hour' in self.anomalies.columns:
                hour_counts = self.anomalies['hour'].value_counts()
                summary['hour_distribution'] = hour_counts.to_dict()
        
        return summary
    
    def plot_anomalies(self, figsize=(15, 8), save_path=None):
        """
        Plot the anomalies against the normal data.
        
        Args:
            figsize (tuple): Figure size.
            save_path (str): Path to save the figure.
            
        Returns:
            matplotlib.figure.Figure: The created figure.
        """
        if self.data is None:
            logger.error("No data loaded")
            return None
            
        if self.anomalies is None:
            logger.warning("No anomalies detected or detect_anomalies() not called yet")
            return None
            
        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Ensure bildankunft_timestamp is datetime
        if 'bildankunft_timestamp' in self.data.columns:
            if not pd.api.types.is_datetime64_any_dtype(self.data['bildankunft_timestamp']):
                self.data['bildankunft_timestamp'] = pd.to_datetime(self.data['bildankunft_timestamp'])
        
        # Sort data by timestamp
        sorted_data = self.data.sort_values('bildankunft_timestamp')
        
        # Plot normal data
        normal_data = sorted_data[~sorted_data['is_anomaly']]
        ax.scatter(
            normal_data['bildankunft_timestamp'],
            normal_data['processing_delay_minutes'],
            color='blue',
            alpha=0.5,
            label='Normal'
        )
        
        # Plot anomalies
        anomaly_data = sorted_data[sorted_data['is_anomaly']]
        ax.scatter(
            anomaly_data['bildankunft_timestamp'],
            anomaly_data['processing_delay_minutes'],
            color='red',
            marker='x',
            s=100,
            label='Anomaly'
        )
        
        # Set title and labels
        method_name = {
            'zscore': 'Z-Score',
            'iqr': 'IQR',
            'percentile': 'Percentile',
            'absolute': 'Absolute Threshold'
        }.get(self.threshold_method, self.threshold_method)
        
        ax.set_title(f'Processing Delay Anomalies ({method_name} Method)')
        ax.set_xlabel('Time')
        ax.set_ylabel('Processing Delay (minutes)')
        
        # Add grid and legend
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Tight layout for better spacing
        plt.tight_layout()
        
        # Save figure if path provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Saved anomaly plot to {save_path}")
        
        return fig
    
    def annotate_anomalies(self, annotations):
        """
        Add annotations to detected anomalies.
        
        Args:
            annotations (dict): Dictionary mapping anomaly indices to annotations.
            
        Returns:
            DataFrame: Anomalies with annotations.
        """
        if self.anomalies is None:
            logger.warning("No anomalies detected or detect_anomalies() not called yet")
            return None
            
        # Create a copy to avoid modifying the original
        annotated_anomalies = self.anomalies.copy()
        
        # Add annotation column if it doesn't exist
        if 'annotation' not in annotated_anomalies.columns:
            annotated_anomalies['annotation'] = ""
            
        # Add annotations
        for idx, annotation in annotations.items():
            if idx in annotated_anomalies.index:
                annotated_anomalies.loc[idx, 'annotation'] = annotation
            else:
                logger.warning(f"Anomaly index {idx} not found")
        
        logger.info(f"Added {len(annotations)} annotations to anomalies")
        
        # Update the stored anomalies
        self.anomalies = annotated_anomalies
        
        return annotated_anomalies 