#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Standalone launcher for Deployment Analyzer
This script includes all dependencies and launches the application
"""

import os
import sys
import traceback
import time
import datetime

# Explicitly import all required packages to ensure they're included
try:
    import pandas as pd
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    import seaborn as sns
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    import threading
    import csv
    from datetime import datetime, timedelta
    import logging
    from logging.handlers import RotatingFileHandler
    import openpyxl
    import PIL
    from PIL import Image
    
    print(f"Successfully imported required packages:")
    print(f"pandas {pd.__version__}")
    print(f"numpy {np.__version__}")
    print(f"matplotlib {matplotlib.__version__}")
    print(f"seaborn {sns.__version__}")
    print(f"PIL {PIL.__version__}")
except ImportError as e:
    print(f"ERROR: Failed to import required package: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)

def main():
    print("=== Deployment Analyzer Standalone Launcher ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Get the application path
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        print("Running from frozen executable")
        app_dir = os.path.dirname(sys.executable)
        # Use _MEIPASS if available (for --onefile mode)
        if hasattr(sys, '_MEIPASS'):
            app_dir = sys._MEIPASS
            print(f"Using PyInstaller _MEIPASS: {app_dir}")
    else:
        # Running from script
        print("Running from script")
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Application directory: {app_dir}")
    
    # Create required directories
    log_dir = os.path.join(app_dir, 'logs')
    for dirname in ['data', 'logs', 'output']:
        dir_path = os.path.join(app_dir, dirname)
        if not os.path.exists(dir_path):
            print(f"Creating directory: {dir_path}")
            try:
                os.makedirs(dir_path)
            except Exception as e:
                print(f"Error creating directory {dir_path}: {e}")
    
    # Set up error logging
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'standalone.log')
    with open(log_file, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"\n\n--- Standalone launcher started at {timestamp} ---\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Current directory: {os.getcwd()}\n")
        f.write(f"Application directory: {app_dir}\n")
    
    # Set up args - default to GUI mode if no args
    if len(sys.argv) <= 1:
        args = ['--gui']
    else:
        args = sys.argv[1:]
    
    # Find the main application file
    main_file = os.path.join(app_dir, 'deployment-analyse.py')
    if not os.path.exists(main_file) and getattr(sys, 'frozen', False):
        # Look in _internal directory when running as executable
        main_file = os.path.join(app_dir, '_internal', 'deployment-analyse.py')
    
    print(f"Main application file: {main_file}")
    
    if not os.path.exists(main_file):
        error_msg = f"Error: Could not find main application file: {main_file}"
        print(error_msg)
        with open(os.path.join(log_dir, 'standalone_error.log'), 'a', encoding='utf-8') as f:
            f.write(f"{error_msg}\n")
        
        # Keep the window open if running as executable
        if getattr(sys, 'frozen', False):
            input("Press Enter to exit...")
        
        sys.exit(1)
    
    # Add the application directory to sys.path
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
        
    # Change to the application directory
    os.chdir(app_dir)
    
    try:
        print(f"Running main file: {main_file}")
        with open(main_file, 'r', encoding='utf-8') as f:
            code = compile(f.read(), main_file, 'exec')
            # Create a new global namespace for execution
            globals_dict = {
                '__file__': main_file,
                '__name__': '__main__',
            }
            # Execute the code in the new namespace
            exec(code, globals_dict)
    except Exception as e:
        error_msg = f"Error running main application: {e}\n{traceback.format_exc()}"
        print(error_msg)
        
        # Log the error
        with open(os.path.join(log_dir, 'standalone_error.log'), 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"--- Error at {timestamp} ---\n")
            f.write(error_msg)
            f.write("\n\n")
        
        # Keep the window open if running as executable
        if getattr(sys, 'frozen', False):
            input("Press Enter to exit...")
        
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
        if getattr(sys, 'frozen', False):
            print("\nPress Enter to exit...")
            try:
                input()
            except:
                time.sleep(30)
        sys.exit(1) 