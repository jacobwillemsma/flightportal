#!/usr/bin/env python3
"""
FlightPortal Entry Point
Run this file to start the application.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from src.main import main

if __name__ == "__main__":
    main()