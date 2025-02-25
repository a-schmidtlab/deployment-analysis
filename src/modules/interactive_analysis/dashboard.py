"""
Interactive Dashboard

This module provides a web-based interactive dashboard
for the image distribution analysis system.
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Dashboard:
    """
    Class for creating an interactive web dashboard for data analysis.
    """
    
    def __init__(self, db_connection=None, timeline_analyzer=None, anomaly_detector=None):
        """
        Initialize the Dashboard.
        
        Args:
            db_connection: Database connection object.
            timeline_analyzer: TimelineAnalyzer instance.
            anomaly_detector: AnomalyDetector instance.
        """
        self.db_connection = db_connection
        self.timeline_analyzer = timeline_analyzer
        self.anomaly_detector = anomaly_detector
        self.app = None
        self.available_dates = []
        self.data = None
    
    def initialize_app(self):
        """
        Initialize the Dash application.
        
        Returns:
            Dash: The initialized Dash application.
        """
        # Create the Dash app
        self.app = Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
        )
        
        # Set the app title
        self.app.title = "Image Distribution Analysis Dashboard"
        
        # Load available dates from database if connected
        if self.db_connection:
            self.available_dates = self.db_connection.get_distinct_dates()
            if self.available_dates:
                logger.info(f"Loaded {len(self.available_dates)} dates from database")
        
        # Create the app layout
        self._create_layout()
        
        # Register callbacks
        self._register_callbacks()
        
        return self.app
    
    def _create_layout(self):
        """Create the Dash app layout."""
        if self.app is None:
            logger.error("App not initialized")
            return
            
        # Create date range options
        date_ranges = []
        if self.available_dates:
            min_date = min(self.available_dates)
            max_date = max(self.available_dates)
            date_ranges = [
                {"label": "All Data", "value": "all"},
                {"label": "Last 7 Days", "value": "last_7_days"},
                {"label": "Last 30 Days", "value": "last_30_days"},
                {"label": "Custom Range", "value": "custom"}
            ]
        
        # Create granularity options
        granularity_options = [
            {"label": "Minute", "value": "minute"},
            {"label": "Hour", "value": "hour"},
            {"label": "Day", "value": "day"},
            {"label": "Week", "value": "week"},
            {"label": "Month", "value": "month"},
            {"label": "Year", "value": "year"}
        ]
        
        # Create metric options
        metric_options = [
            {"label": "Mean", "value": "mean"},
            {"label": "Median", "value": "median"},
            {"label": "Count", "value": "count"},
            {"label": "Min", "value": "min"},
            {"label": "Max", "value": "max"}
        ]
        
        # Create anomaly detection method options
        anomaly_method_options = [
            {"label": "Z-Score", "value": "zscore"},
            {"label": "IQR", "value": "iqr"},
            {"label": "Percentile", "value": "percentile"},
            {"label": "Absolute Threshold", "value": "absolute"}
        ]
        
        # Create the layout
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col(html.H1("Image Distribution Analysis Dashboard", className="text-center my-4"), width=12)
            ]),
            
            # Control Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Control Panel"),
                        dbc.CardBody([
                            # Data Range Selection
                            html.H5("Data Range"),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        id="date-range-dropdown",
                                        options=date_ranges,
                                        value="all" if self.available_dates else None,
                                        placeholder="Select date range"
                                    )
                                ], width=4),
                                dbc.Col([
                                    dcc.DatePickerRange(
                                        id="date-picker-range",
                                        min_date_allowed=min(self.available_dates) if self.available_dates else None,
                                        max_date_allowed=max(self.available_dates) if self.available_dates else None,
                                        start_date=min(self.available_dates) if self.available_dates else None,
                                        end_date=max(self.available_dates) if self.available_dates else None,
                                        display_format="YYYY-MM-DD",
                                        disabled=True
                                    )
                                ], width=8)
                            ]),
                            
                            html.Hr(),
                            
                            # Analysis Settings
                            html.H5("Analysis Settings"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Time Granularity"),
                                    dcc.Dropdown(
                                        id="granularity-dropdown",
                                        options=granularity_options,
                                        value="hour",
                                        placeholder="Select granularity"
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Metric"),
                                    dcc.Dropdown(
                                        id="metric-dropdown",
                                        options=metric_options,
                                        value="mean",
                                        placeholder="Select metric"
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Update Analysis"),
                                    html.Br(),
                                    dbc.Button("Run Analysis", id="run-analysis-button", color="primary", className="mt-1")
                                ], width=4)
                            ]),
                            
                            html.Hr(),
                            
                            # Anomaly Detection Settings
                            html.H5("Anomaly Detection"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Method"),
                                    dcc.Dropdown(
                                        id="anomaly-method-dropdown",
                                        options=anomaly_method_options,
                                        value="zscore",
                                        placeholder="Select method"
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Threshold"),
                                    dcc.Slider(
                                        id="anomaly-threshold-slider",
                                        min=1,
                                        max=5,
                                        step=0.5,
                                        value=3,
                                        marks={i: str(i) for i in range(1, 6)}
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Detect Anomalies"),
                                    html.Br(),
                                    dbc.Button("Run Detection", id="run-anomaly-button", color="danger", className="mt-1")
                                ], width=4)
                            ])
                        ])
                    ])
                ], width=12)
            ]),
            
            html.Hr(),
            
            # Timeline Analysis Tab
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Timeline Analysis"),
                        dbc.CardBody([
                            dcc.Graph(id="timeline-graph")
                        ])
                    ])
                ], width=12)
            ]),
            
            html.Hr(),
            
            # Weekday-Hour Heatmap
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Weekday-Hour Heatmap"),
                        dbc.CardBody([
                            dcc.Graph(id="heatmap-graph")
                        ])
                    ])
                ], width=12)
            ]),
            
            html.Hr(),
            
            # Anomaly Detection
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Anomaly Detection"),
                        dbc.CardBody([
                            dcc.Graph(id="anomaly-graph"),
                            html.Div(id="anomaly-summary")
                        ])
                    ])
                ], width=12)
            ]),
            
            html.Hr(),
            
            # Footer
            dbc.Row([
                dbc.Col(html.P("Image Distribution Analysis Tool - © 2025", className="text-center"), width=12)
            ])
            
        ], fluid=True)
    
    def _register_callbacks(self):
        """Register Dash callbacks."""
        if self.app is None:
            logger.error("App not initialized")
            return
        
        # Enable/disable date picker based on date range selection
        @self.app.callback(
            [Output("date-picker-range", "disabled"),
             Output("date-picker-range", "start_date"),
             Output("date-picker-range", "end_date")],
            [Input("date-range-dropdown", "value")]
        )
        def update_date_picker(date_range):
            # If no date range is selected, disable the date picker
            if not date_range:
                return True, None, None
                
            # Enable the date picker for custom range
            if date_range == "custom":
                return False, min(self.available_dates) if self.available_dates else None, max(self.available_dates) if self.available_dates else None
                
            # Disable the date picker for predefined ranges and set the dates
            if date_range == "all":
                return True, min(self.available_dates) if self.available_dates else None, max(self.available_dates) if self.available_dates else None
                
            if date_range == "last_7_days":
                end_date = max(self.available_dates) if self.available_dates else None
                if end_date:
                    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
                    return True, start_date, end_date
                
            if date_range == "last_30_days":
                end_date = max(self.available_dates) if self.available_dates else None
                if end_date:
                    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
                    return True, start_date, end_date
                
            return True, None, None
        
        # Update timeline graph based on settings
        @self.app.callback(
            Output("timeline-graph", "figure"),
            [Input("run-analysis-button", "n_clicks")],
            [State("date-range-dropdown", "value"),
             State("date-picker-range", "start_date"),
             State("date-picker-range", "end_date"),
             State("granularity-dropdown", "value"),
             State("metric-dropdown", "value")]
        )
        def update_timeline_graph(n_clicks, date_range, start_date, end_date, granularity, metric):
            # Skip if not triggered or no settings
            if n_clicks is None or not granularity or not metric:
                return go.Figure()
                
            # Load data if needed
            if self.timeline_analyzer:
                # Set date range
                if date_range and date_range != "custom":
                    if date_range == "all":
                        date_range_tuple = None
                    elif date_range == "last_7_days":
                        end_date = max(self.available_dates) if self.available_dates else None
                        if end_date:
                            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
                            date_range_tuple = (start_date, end_date)
                        else:
                            date_range_tuple = None
                    elif date_range == "last_30_days":
                        end_date = max(self.available_dates) if self.available_dates else None
                        if end_date:
                            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
                            date_range_tuple = (start_date, end_date)
                        else:
                            date_range_tuple = None
                else:
                    # Custom date range
                    if start_date and end_date:
                        date_range_tuple = (start_date, end_date)
                    else:
                        date_range_tuple = None
                
                # Load data and run analysis
                self.timeline_analyzer.load_data(date_range=date_range_tuple)
                self.timeline_analyzer.set_time_granularity(granularity)
                time_patterns = self.timeline_analyzer.analyze_time_pattern()
                
                if time_patterns is not None:
                    # Create timeline figure
                    column_name = f"processing_delay_minutes_{metric}"
                    fig = px.line(
                        time_patterns, 
                        x="time_group", 
                        y=column_name,
                        title=f"{metric.capitalize()} Processing Delay by {granularity.capitalize()}",
                        labels={
                            "time_group": granularity.capitalize(),
                            column_name: f"{metric.capitalize()} Processing Delay (minutes)"
                        }
                    )
                    
                    # Customize the figure
                    fig.update_layout(
                        xaxis_title=granularity.capitalize(),
                        yaxis_title=f"{metric.capitalize()} Processing Delay (minutes)",
                        template="plotly_white"
                    )
                    
                    return fig
            
            # Return empty figure if analysis fails
            return go.Figure()
        
        # Update heatmap graph based on settings
        @self.app.callback(
            Output("heatmap-graph", "figure"),
            [Input("run-analysis-button", "n_clicks")],
            [State("date-range-dropdown", "value"),
             State("date-picker-range", "start_date"),
             State("date-picker-range", "end_date")]
        )
        def update_heatmap_graph(n_clicks, date_range, start_date, end_date):
            # Skip if not triggered
            if n_clicks is None:
                return go.Figure()
                
            # Load data if needed
            if self.timeline_analyzer:
                # Set date range
                if date_range and date_range != "custom":
                    if date_range == "all":
                        date_range_tuple = None
                    elif date_range == "last_7_days":
                        end_date = max(self.available_dates) if self.available_dates else None
                        if end_date:
                            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
                            date_range_tuple = (start_date, end_date)
                        else:
                            date_range_tuple = None
                    elif date_range == "last_30_days":
                        end_date = max(self.available_dates) if self.available_dates else None
                        if end_date:
                            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
                            date_range_tuple = (start_date, end_date)
                        else:
                            date_range_tuple = None
                else:
                    # Custom date range
                    if start_date and end_date:
                        date_range_tuple = (start_date, end_date)
                    else:
                        date_range_tuple = None
                
                # Load data and run analysis
                self.timeline_analyzer.load_data(date_range=date_range_tuple)
                pivot_table = self.timeline_analyzer.analyze_weekday_hour_pattern()
                
                if pivot_table is not None:
                    # Sort weekdays in correct order
                    weekday_order = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
                    pivot_table = pivot_table.reindex(weekday_order)
                    
                    # Create heatmap figure
                    fig = px.imshow(
                        pivot_table,
                        labels=dict(x="Hour of Day", y="Weekday", color="Average Processing Delay (minutes)"),
                        x=pivot_table.columns,
                        y=pivot_table.index,
                        color_continuous_scale="YlOrRd",
                        title="Average Processing Delays by Weekday and Hour"
                    )
                    
                    # Add text annotations
                    annotations = []
                    for i, row in enumerate(pivot_table.index):
                        for j, col in enumerate(pivot_table.columns):
                            annotations.append(
                                dict(
                                    x=col,
                                    y=row,
                                    text=str(int(pivot_table.loc[row, col])),
                                    showarrow=False,
                                    font=dict(color="black" if pivot_table.loc[row, col] < 30 else "white")
                                )
                            )
                    
                    fig.update_layout(annotations=annotations)
                    
                    return fig
            
            # Return empty figure if analysis fails
            return go.Figure()
        
        # Update anomaly graph based on settings
        @self.app.callback(
            [Output("anomaly-graph", "figure"),
             Output("anomaly-summary", "children")],
            [Input("run-anomaly-button", "n_clicks")],
            [State("date-range-dropdown", "value"),
             State("date-picker-range", "start_date"),
             State("date-picker-range", "end_date"),
             State("anomaly-method-dropdown", "value"),
             State("anomaly-threshold-slider", "value")]
        )
        def update_anomaly_graph(n_clicks, date_range, start_date, end_date, method, threshold):
            # Skip if not triggered
            if n_clicks is None:
                return go.Figure(), ""
                
            # Load data if needed
            if self.anomaly_detector:
                # Set date range
                if date_range and date_range != "custom":
                    if date_range == "all":
                        date_range_tuple = None
                    elif date_range == "last_7_days":
                        end_date = max(self.available_dates) if self.available_dates else None
                        if end_date:
                            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
                            date_range_tuple = (start_date, end_date)
                        else:
                            date_range_tuple = None
                    elif date_range == "last_30_days":
                        end_date = max(self.available_dates) if self.available_dates else None
                        if end_date:
                            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
                            date_range_tuple = (start_date, end_date)
                        else:
                            date_range_tuple = None
                else:
                    # Custom date range
                    if start_date and end_date:
                        date_range_tuple = (start_date, end_date)
                    else:
                        date_range_tuple = None
                
                # Load data and detect anomalies
                self.anomaly_detector.load_data(date_range=date_range_tuple)
                self.anomaly_detector.set_threshold_method(method, value=threshold)
                anomalies = self.anomaly_detector.detect_anomalies()
                
                if anomalies is not None:
                    # Get summary
                    summary = self.anomaly_detector.get_summary()
                    
                    # Create summary HTML
                    summary_html = html.Div([
                        html.H5("Anomaly Detection Summary"),
                        html.P([
                            f"Total anomalies: {summary['count']} ({summary['percentage']:.2f}% of data)",
                            html.Br(),
                            f"Average anomaly score: {summary['avg_score']:.2f}",
                            html.Br(),
                            f"Min delay: {summary['min_delay']:.2f} minutes",
                            html.Br(),
                            f"Max delay: {summary['max_delay']:.2f} minutes",
                            html.Br(),
                            f"Average delay: {summary['avg_delay']:.2f} minutes"
                        ])
                    ])
                    
                    # Get all data (including normal points)
                    all_data = self.anomaly_detector.data
                    
                    # Create anomaly figure
                    fig = go.Figure()
                    
                    # Add normal data
                    normal_data = all_data[~all_data['is_anomaly']]
                    fig.add_trace(go.Scatter(
                        x=normal_data['bildankunft_timestamp'],
                        y=normal_data['processing_delay_minutes'],
                        mode='markers',
                        marker=dict(color='blue', size=8, opacity=0.5),
                        name='Normal'
                    ))
                    
                    # Add anomalies
                    anomaly_data = all_data[all_data['is_anomaly']]
                    fig.add_trace(go.Scatter(
                        x=anomaly_data['bildankunft_timestamp'],
                        y=anomaly_data['processing_delay_minutes'],
                        mode='markers',
                        marker=dict(color='red', size=12, symbol='x'),
                        name='Anomaly'
                    ))
                    
                    # Add title and labels
                    method_name = {
                        'zscore': 'Z-Score',
                        'iqr': 'IQR',
                        'percentile': 'Percentile',
                        'absolute': 'Absolute Threshold'
                    }.get(method, method)
                    
                    fig.update_layout(
                        title=f'Processing Delay Anomalies ({method_name} Method)',
                        xaxis_title='Time',
                        yaxis_title='Processing Delay (minutes)',
                        template='plotly_white'
                    )
                    
                    return fig, summary_html
            
            # Return empty figure if detection fails
            return go.Figure(), ""
    
    def run_server(self, debug=False, port=8050):
        """
        Run the Dash server.
        
        Args:
            debug (bool): Whether to run in debug mode.
            port (int): Port to run the server on.
        """
        if self.app is None:
            self.initialize_app()
            
        logger.info(f"Starting dashboard server on port {port}")
        self.app.run_server(debug=debug, port=port) 