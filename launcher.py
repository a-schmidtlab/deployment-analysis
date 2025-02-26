#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Launcher for Deployment Analyzer
This script ensures proper path handling and startup for both development and PyInstaller environments.
"""

import os
import sys
import traceback
import time
import datetime
from importlib.machinery import SourceFileLoader
import subprocess
import runpy

def setup_environment():
    """Set up the environment for the application to run properly"""
    # Print startup information
    print(f"Launcher starting - Python {sys.version}")
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
    for dirname in ['data', 'logs', 'output']:
        dir_path = os.path.join(app_dir, dirname)
        if not os.path.exists(dir_path):
            print(f"Creating directory: {dir_path}")
            try:
                os.makedirs(dir_path)
            except Exception as e:
                print(f"Error creating directory {dir_path}: {e}")
    
    # Set up logging for the launcher
    log_dir = os.path.join(app_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Write to the log file
    log_file = os.path.join(log_dir, 'launcher.log')
    with open(log_file, 'a', encoding='utf-8') as f:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"\n\n--- Launcher started at {timestamp} ---\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Current directory: {os.getcwd()}\n")
        f.write(f"Application directory: {app_dir}\n")
        
        # Log Python path
        f.write("Python path:\n")
        for p in sys.path:
            f.write(f"  {p}\n")
    
    return app_dir, log_dir

def find_main_file(app_dir):
    """Find the main application file"""
    # Set up args - default to GUI mode if no args
    if len(sys.argv) <= 1:
        args = ['--gui']
    else:
        args = sys.argv[1:]
    
    # Find the main application file
    locations = [
        os.path.join(app_dir, 'deployment-analyse.py'),
        os.path.join(app_dir, '_internal', 'deployment-analyse.py'),
        os.path.join(app_dir, 'deployment_analyse.py'),
    ]
    
    main_file = None
    for loc in locations:
        if os.path.exists(loc):
            main_file = loc
            break
    
    print(f"Main application file: {main_file}")
    return main_file, args

def write_error(log_dir, error_msg):
    """Write an error message to the log file"""
    try:
        with open(os.path.join(log_dir, 'launcher_error.log'), 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"--- Error at {timestamp} ---\n")
            f.write(error_msg)
            f.write("\n\n")
    except Exception as e:
        print(f"Failed to write to error log: {e}")

def wait_for_input():
    """Wait for user input in a way that won't fail if stdin is lost"""
    if getattr(sys, 'frozen', False):
        print("\nPress Enter to exit (or wait 30 seconds)...")
        try:
            input()
        except:
            print("Input not available, waiting 30 seconds...")
            time.sleep(30)

def main():
    try:
        # Set up the environment
        app_dir, log_dir = setup_environment()
        
        # Find the main file
        main_file, args = find_main_file(app_dir)
        
        if not main_file:
            error_msg = f"Error: Could not find main application file"
            print(error_msg)
            write_error(log_dir, error_msg)
            wait_for_input()
            sys.exit(1)
        
        # Run the main application
        print(f"Launching main application with args: {args}")
        
        # Add the application directory to sys.path
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
            
        # Change to the application directory
        os.chdir(app_dir)
        
        # Try multiple methods to run the application
        success = False
        
        # Method 1: Try direct import
        if not success:
            try:
                print("Attempting direct import...")
                sys.path.insert(0, os.path.dirname(main_file))
                
                # If we're using _internal, try to import packages directly
                if '_internal' in main_file:
                    try:
                        import pandas
                        import numpy
                        import matplotlib
                        print(f"Successfully imported pandas {pandas.__version__}")
                        print(f"Successfully imported numpy {numpy.__version__}")
                        print(f"Successfully imported matplotlib {matplotlib.__version__}")
                    except ImportError as e:
                        print(f"Warning: Could not import a required package: {e}")
                        
                # Try to import the module with the module name format
                module_name = os.path.splitext(os.path.basename(main_file))[0].replace('-', '_')
                print(f"Trying to import module: {module_name}")
                
                module = __import__(module_name)
                if hasattr(module, 'main'):
                    print("Executing main() function...")
                    module.main(args)
                    success = True
            except Exception as e:
                print(f"Error with direct import: {e}")
                traceback_str = traceback.format_exc()
                print(traceback_str)
                write_error(log_dir, f"Direct import error: {e}\n{traceback_str}")
        
        # Method 2: Use SourceFileLoader
        if not success:
            try:
                print("Attempting to load with SourceFileLoader...")
                module_name = os.path.splitext(os.path.basename(main_file))[0].replace('-', '_')
                module = SourceFileLoader(module_name, main_file).load_module()
                if hasattr(module, 'main'):
                    print("Executing main() function...")
                    module.main(args)
                    success = True
                else:
                    print("No main() function found, executing module...")
                    # If no main function, just run the module directly
                    runpy.run_path(main_file, run_name='__main__')
                    success = True
            except Exception as e:
                print(f"Error running with SourceFileLoader: {e}")
                traceback_str = traceback.format_exc()
                print(traceback_str)
                write_error(log_dir, f"SourceFileLoader error: {e}\n{traceback_str}")
        
        # Method 3: Use subprocess as a fallback, but avoid long paths
        if not success:
            try:
                print("Falling back to subprocess...")
                
                # Create a more reliable command with shorter paths
                if getattr(sys, 'frozen', False):
                    # If we're in a PyInstaller environment, we may need to extract 
                    # the module to a temporary location with a shorter path
                    temp_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'deployment_analyzer')
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    
                    temp_script = os.path.join(temp_dir, 'run.py')
                    with open(temp_script, 'w') as f:
                        f.write(f'import sys\nsys.path.insert(0, r"{app_dir}")\n')
                        f.write(f'exec(open(r"{main_file}").read())\n')
                    
                    cmd = [sys.executable, temp_script] + args
                else:
                    cmd = [sys.executable, main_file] + args
                
                print(f"Running command: {cmd}")
                subprocess.run(cmd)
                success = True
            except Exception as e:
                print(f"Error running with subprocess: {e}")
                traceback_str = traceback.format_exc()
                print(traceback_str)
                write_error(log_dir, f"Subprocess error: {e}\n{traceback_str}")
            
    except Exception as e:
        # Log the error
        error_msg = f"Error launching main application: {e}\n{traceback.format_exc()}"
        print(error_msg)
        
        # Try to get log_dir, may not be defined if exception occurred early
        log_dir = getattr(sys, '_MEIPASS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'))
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                log_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Save error to log file
        write_error(log_dir, error_msg)
        
        # Keep the window open if running as executable
        wait_for_input()
        sys.exit(1)

if __name__ == "__main__":
    main() 