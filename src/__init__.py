"""
FlightPortal - LGA Flight Monitoring Application
A modular flight tracking system for runway 04 arrivals.
"""

__version__ = "2.0.0"
__author__ = "FlightPortal Team"

from . import config
from .lga_client import get_current_metar, get_active_runways
from .flight_logic import flight_logic
from .display_controller import display_controller

__all__ = [
    'config',
    'get_current_metar', 
    'get_active_runways',
    'flight_logic',
    'display_controller'
]