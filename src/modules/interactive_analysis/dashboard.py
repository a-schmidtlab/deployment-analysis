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
        self.app.title = "Image Distribution Analysis"
        
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
        date_ranges = [
            {"label": "Last 7 Days", "value": "last_7_days"},
            {"label": "Last 30 Days", "value": "last_30_days"},
            {"label": "All Data", "value": "all"}
        ]
        
        # Create the layout - simplified version
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col(html.H2("Image Distribution Analysis", className="text-center my-3"), width=12)
            ]),
            
            # Time Range Selection - Simplified
            dbc.Row([
                dbc.Col([
                    html.Label("Time Range:"),
                    dcc.Dropdown(
                        id="date-range-dropdown",
                        options=date_ranges,
                        value="last_7_days" if self.available_dates else None,
                        className="mb-3"
                    )
                ], width={"size": 4, "offset": 4})
            ]),
            
            # Statistics Cards Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Total Records", className="card-title text-center"),
                            html.H3(id="stat-total-records", className="text-center text-primary")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Average Delay", className="card-title text-center"),
                            html.H3(id="stat-avg-delay", className="text-center text-primary")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Min Delay", className="card-title text-center"),
                            html.H3(id="stat-min-delay", className="text-center text-success")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Max Delay", className="card-title text-center"),
                            html.H3(id="stat-max-delay", className="text-center text-danger")
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            # Heatmap - Main Focus
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Processing Delays by Weekday and Hour"),
                        dbc.CardBody([
                            dcc.Loading(
                                id="loading-heatmap",
                                type="circle",
                                children=dcc.Graph(id="heatmap-graph")
                            )
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Expandable Analysis Section
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Advanced Analysis ▼",
                        id="toggle-advanced-button",
                        color="secondary",
                        className="mb-3 w-100"
                    ),
                    dbc.Collapse(
                        dbc.Card([
                            dbc.CardBody([
                                # Analysis Controls
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Time Granularity:"),
                                        dcc.Dropdown(
                                            id="granularity-dropdown",
                                            options=[
                                                {"label": "Hour", "value": "hour"},
                                                {"label": "Day", "value": "day"},
                                                {"label": "Week", "value": "week"}
                                            ],
                                            value="hour"
                                        )
                                    ], width=4),
                                    
                                    dbc.Col([
                                        html.Label("Metric:"),
                                        dcc.Dropdown(
                                            id="metric-dropdown",
                                            options=[
                                                {"label": "Mean", "value": "mean"},
                                                {"label": "Median", "value": "median"},
                                                {"label": "Count", "value": "count"}
                                            ],
                                            value="mean"
                                        )
                                    ], width=4),
                                    
                                    dbc.Col([
                                        html.Label("Detect Anomalies:"),
                                        dbc.Switch(
                                            id='anomaly-switch',
                                            label=' Show anomalies',
                                            value=False,
                                            className="mt-2"
                                        )
                                    ], width=4)
                                ], className="mb-3"),
                                
                                # Timeline Graph
                                dcc.Loading(
                                    id="loading-timeline",
                                    type="circle",
                                    children=dcc.Graph(id="timeline-graph")
                                ),
                                
                                # Export Buttons
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button("Export as PNG", id="btn-export-png", color="primary", className="me-2"),
                                        dbc.Button("Export as CSV", id="btn-export-csv", color="primary")
                                    ], width=12, className="d-flex justify-content-end mt-3")
                                ]),
                                
                                # Hidden div for storing anomaly data
                                html.Div(id="anomaly-data-storage", style={"display": "none"})
                            ])
                        ]),
                        id="collapse-advanced",
                        is_open=False
                    )
                ], width=12)
            ]),
            
            # Footer
            dbc.Row([
                dbc.Col(html.P("© 2025 Image Distribution Analysis Tool", className="text-center text-muted mt-3"), width=12)
            ])
            
        ], fluid=True)
    
    def _register_callbacks(self):
        """Register Dash callbacks."""
        if self.app is None:
            logger.error("App not initialized")
            return
        
        # Toggle advanced analysis section
        @self.app.callback(
            [Output("collapse-advanced", "is_open"),
             Output("toggle-advanced-button", "children")],
            [Input("toggle-advanced-button", "n_clicks")],
            [State("collapse-advanced", "is_open")]
        )
        def toggle_advanced_section(n_clicks, is_open):
            if n_clicks:
                return not is_open, "Advanced Analysis ▼" if not is_open else "Advanced Analysis ▲"
            return is_open, "Advanced Analysis ▼"
        
        # Update statistics and heatmap
        @self.app.callback(
            [Output("stat-total-records", "children"),
             Output("stat-avg-delay", "children"),
             Output("stat-min-delay", "children"),
             Output("stat-max-delay", "children"),
             Output("heatmap-graph", "figure"),
             Output("anomaly-data-storage", "children")],
            [Input("date-range-dropdown", "value")]
        )
        def update_main_view(date_range):
            if not date_range:
                return "N/A", "N/A", "N/A", "N/A", go.Figure(), ""
                
            # Handle date range selection
            date_range_tuple = self._get_date_range(date_range)
                
            # Load data
            if not self.timeline_analyzer:
                return "N/A", "N/A", "N/A", "N/A", go.Figure(), ""
                
            self.timeline_analyzer.load_data(date_range=date_range_tuple)
            
            # Create a copy to calculate statistics
            data = self.timeline_analyzer.data.copy()
            
            # Get basic statistics
            total_records = len(data)
            avg_delay = data['processing_delay_minutes'].mean()
            min_delay = data['processing_delay_minutes'].min()
            max_delay = data['processing_delay_minutes'].max()
            
            # Format statistics for display
            total_formatted = f"{total_records:,}"
            avg_formatted = f"{avg_delay:.1f} min"
            min_formatted = f"{min_delay:.1f} min"
            max_formatted = f"{max_delay:.1f} min"
            
            # Get weekday-hour heatmap
            pivot_table = self.timeline_analyzer.analyze_weekday_hour_pattern()
            
            if pivot_table is None:
                heatmap_fig = go.Figure()
            else:
                # Sort weekdays in correct order
                weekday_order = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
                pivot_table = pivot_table.reindex(weekday_order)
                
                # Create heatmap figure
                heatmap_fig = px.imshow(
                    pivot_table,
                    labels=dict(x="Hour of Day", y="Weekday", color="Average Delay (minutes)"),
                    x=pivot_table.columns,
                    y=pivot_table.index,
                    color_continuous_scale="YlOrRd",
                    title=None
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
                
                heatmap_fig.update_layout(annotations=annotations)
                heatmap_fig.update_layout(
                    height=500,
                    margin=dict(l=50, r=50, t=30, b=50)
                )
            
            # Store data for anomaly detection (for use in advanced section)
            anomaly_data = data.to_json(date_format='iso', orient='split') if not data.empty else ""
            
            return total_formatted, avg_formatted, min_formatted, max_formatted, heatmap_fig, anomaly_data
        
        # Update timeline chart in advanced section
        @self.app.callback(
            Output("timeline-graph", "figure"),
            [Input("granularity-dropdown", "value"),
             Input("metric-dropdown", "value"),
             Input("anomaly-switch", "value"),
             Input("anomaly-data-storage", "children")]
        )
        def update_timeline(granularity, metric, show_anomalies, stored_data):
            if not granularity or not metric or not stored_data:
                return go.Figure()
                
            if self.timeline_analyzer:
                # Set time granularity
                self.timeline_analyzer.set_time_granularity(granularity)
                
                # Analyze time patterns
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
                            column_name: f"{metric.capitalize()} Delay (minutes)"
                        }
                    )
                    
                    # Add anomalies if requested
                    if show_anomalies and self.anomaly_detector and stored_data:
                        # Load the data used for the main view
                        data = pd.read_json(stored_data, orient='split')
                        self.anomaly_detector.load_data(data=data)
                        
                        # Set Z-score method with standard threshold
                        self.anomaly_detector.set_threshold_method('zscore', value=3.0)
                        
                        # Detect anomalies
                        anomalies = self.anomaly_detector.detect_anomalies()
                        
                        if anomalies is not None and not anomalies.empty:
                            # Convert to time buckets matching the timeline graph
                            if granularity == 'hour':
                                anomalies['time_bucket'] = anomalies['bildankunft_timestamp'].dt.floor('H')
                            elif granularity == 'day':
                                anomalies['time_bucket'] = anomalies['bildankunft_timestamp'].dt.floor('D')
                            elif granularity == 'week':
                                anomalies['time_bucket'] = anomalies['bildankunft_timestamp'].dt.to_period('W').dt.start_time
                            
                            # Group anomalies by time bucket
                            anomaly_counts = anomalies.groupby('time_bucket').size().reset_index(name='count')
                            
                            # Add scatter points for anomaly counts
                            if not anomaly_counts.empty:
                                # For each time point in the main graph, find matching anomaly counts
                                merged = pd.merge(
                                    time_patterns[['time_group']],
                                    anomaly_counts,
                                    left_on='time_group',
                                    right_on='time_bucket',
                                    how='left'
                                ).fillna(0)
                                
                                # Add scatter trace for anomalies
                                fig.add_trace(
                                    go.Scatter(
                                        x=merged['time_group'],
                                        y=[time_patterns[column_name].max() * 0.2] * len(merged),  # Plot at 20% of max height
                                        mode='markers',
                                        marker=dict(
                                            size=merged['count'] * 2,  # Size based on anomaly count
                                            color='red',
                                            symbol='x'
                                        ),
                                        name='Anomalies',
                                        hovertemplate='%{x}<br>Anomalies: %{text}<extra></extra>',
                                        text=merged['count'].astype(int)
                                    )
                                )
                    
                    # Customize the figure
                    fig.update_layout(
                        xaxis_title=granularity.capitalize(),
                        yaxis_title=f"{metric.capitalize()} Delay (minutes)",
                        template="plotly_white",
                        height=400,
                        margin=dict(l=50, r=50, t=50, b=50)
                    )
                    
                    return fig
            
            # Return empty figure if analysis fails
            return go.Figure()
        
        # Export buttons - placeholder callbacks
        @self.app.callback(
            Output("btn-export-png", "n_clicks"),
            [Input("btn-export-png", "n_clicks")]
        )
        def export_png(n_clicks):
            if n_clicks:
                # Implement PNG export functionality here
                pass
            return None
        
        @self.app.callback(
            Output("btn-export-csv", "n_clicks"),
            [Input("btn-export-csv", "n_clicks")]
        )
        def export_csv(n_clicks):
            if n_clicks:
                # Implement CSV export functionality here
                pass
            return None
    
    def _get_date_range(self, date_range_value):
        """Convert date range dropdown value to date tuple."""
        if not date_range_value or not self.available_dates:
            return None
            
        if date_range_value == 'all':
            return None
            
        end_date = max(self.available_dates) if self.available_dates else None
        if not end_date:
            return None
            
        if date_range_value == 'last_7_days':
            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
            return (start_date, end_date)
            
        elif date_range_value == 'last_30_days':
            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
            return (start_date, end_date)
            
        return None
    
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