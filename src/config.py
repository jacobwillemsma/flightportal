#!/usr/bin/env python3
"""
FlightPortal Configuration
Centralized configuration for the LGA flight monitoring application.
"""

try:
    from .env_loader import get_env_var, get_bool_env, get_cached_env
except ImportError:
    from env_loader import get_env_var, get_bool_env, get_cached_env

# Load environment variables once
_env_vars = get_cached_env()

# WiFi Configuration (loaded from environment/secrets)
WIFI_SSID = get_env_var("WIFI_SSID", "your_wifi_network", _env_vars)
WIFI_PASSWORD = get_env_var("WIFI_PASSWORD", "your_wifi_password", _env_vars)

# Polling Intervals (seconds)
FLIGHT_POLL_INTERVAL = 30      # How often to check for flights when RWY04 active
RUNWAY_CHECK_INTERVAL = 900    # How often to check ATIS for runway changes (15 minutes)
WEATHER_REFRESH_INTERVAL = 300 # How often to refresh weather when not RWY04 (5 minutes)
SLEEP_WHEN_INACTIVE = 60       # Sleep time when runway not active

# LGA Runway 04 Approach Corridor (the only one we can see)
# NE: 40deg44'29.9"N 73deg54'24.7"W, SW: 40deg42'04.7"N 73deg56'34.2"W (1-mile buffer)
RWY04_BOUNDS_BOX = "40.756132,40.686813,-73.961956,-73.887739"

# Flight Filtering
MAX_APPROACH_ALTITUDE = 5000  # Only show flights below this altitude (approach traffic)

# Display Configuration
FONT_PRIMARY = None  # Will be set to terminalio.FONT in display_controller

# Colors (RGB hex values)
ROW_ONE_COLOUR = 0xEE82EE     # Violet
ROW_TWO_COLOUR = 0x4B0082     # Indigo  
ROW_THREE_COLOUR = 0xFFA500   # Orange
PLANE_COLOUR = 0x4B0082       # Indigo

# Animation and Timing
PAUSE_BETWEEN_LABEL_SCROLLING = 3  # Seconds between scrolling labels
PLANE_SPEED = 0.08                 # Speed of plane animation (pause per pixel)
TEXT_SPEED = 0.08                  # Speed of text scrolling

# FlightRadar24 API Configuration
FLIGHT_SEARCH_TAIL = "&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1&limit=1"

# Request Headers (for FlightRadar24 API)
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "cache-control": "no-store, no-cache, must-revalidate, post-check=0, pre-check=0",
    "accept": "application/json"
}

# Watchdog Configuration
WATCHDOG_TIMEOUT = 16  # seconds

# Display Layout
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

# Memory Management
CHUNK_LENGTH = 1024      # For processing flight details JSON
JSON_SIZE = 14000        # Max JSON size for flight details (bytes)

# Error Handling
MAX_CONNECTION_RETRIES = 3
CONNECTION_TIMEOUT = 10  # seconds

# Debug Settings (can be overridden by environment variables)
DEBUG_MODE = get_bool_env("DEBUG_MODE", False, _env_vars)
PRINT_MEMORY_INFO = get_bool_env("PRINT_MEMORY_INFO", False, _env_vars)