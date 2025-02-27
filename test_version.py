#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify version information
"""

print("Testing version imports...")

try:
    from version import VERSION, APP_VERSION_DISPLAY, VERSION_DATE
    
    print(f"VERSION = '{VERSION}'")
    print(f"APP_VERSION_DISPLAY = '{APP_VERSION_DISPLAY}'")
    print(f"VERSION_DATE = '{VERSION_DATE}'")
    
    # If running in the frozen executable environment, try to import from app folder
    import sys
    import os
    if getattr(sys, 'frozen', False):
        print("Running in frozen environment.")
        app_dir = os.path.dirname(sys.executable)
        print(f"Executable directory: {app_dir}")
    else:
        print("Running in development environment.")
        app_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Script directory: {app_dir}")

except ImportError as e:
    print(f"Error importing version: {e}")
    
print("Test completed.") 