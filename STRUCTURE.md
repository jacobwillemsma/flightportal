# FlightPortal - New Application Structure

## Overview

The FlightPortal application has been restructured into a clean, modular architecture that separates software logic from hardware control, with intelligent polling based on runway activity.

## Application Behavior

### When Runway 04 is Active (Arrivals)

- **Mode**: Flight Tracking
- **Polling**: Every 30 seconds for flight data
- **Display**: Shows flight information with animations
  - Callsign, aircraft type, altitude, route
  - Plane animation across screen
  - Scrolling text for long information
- **Filter**: Only shows approach traffic <5,000 feet

### When Any Other Runway is Active

- **Mode**: Weather Station
- **Polling**: Every 5 minutes for weather data
- **Display**: Static weather information
  - Current arrival/departure runways
  - METAR wind information
  - No animations (static display)

### Intelligent Polling System

- **ATIS Check**: Every 15 minutes (no cron needed)
- **Flight Data**: Every 30 seconds when RWY04 active
- **Weather Data**: Every 5 minutes when not RWY04
- **Smart Caching**: Avoids unnecessary API calls

## File Structure

```
flightportal/
├── run.py                     # Main entry point
├── requirements.txt           # Dependencies
├── README.md                  # Project documentation
├── code_original.py           # Archived original code
├── src/                       # Source code
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Application orchestrator
│   ├── config.py             # Centralized configuration
│   ├── flight_logic.py       # Flight data and runway logic
│   ├── display_controller.py # Hardware abstraction layer
│   └── lga_client.py         # LGA airport data client
└── test/                      # Test suite
    └── tests.py  # Integration tests
```

## Key Components

### `main.py` - Application Orchestrator

- **Purpose**: Main entry point with intelligent polling loop
- **Key Features**:
  - Different sleep intervals based on runway activity
  - Automatic runway change detection
  - Watchdog feeding during sleep periods
  - Error recovery and graceful shutdown

### `config.py` - Configuration Management

- **Purpose**: Centralized configuration for all components
- **Contains**:
  - WiFi credentials
  - Polling intervals
  - Bounding boxes
  - Display settings
  - Hardware parameters

### `flight_logic.py` - Software Logic Layer

- **Purpose**: Handle all flight data, ATIS, and business logic
- **Key Features**:
  - Smart caching with 15-minute intervals
  - Runway status detection
  - Flight data filtering and parsing
  - Weather information formatting

### `display_controller.py` - Hardware Abstraction

- **Purpose**: All MatrixPortal and LED display operations
- **Key Features**:
  - Hardware initialization and WiFi setup
  - Text scrolling and plane animations
  - Graceful fallback for testing without hardware
  - Watchdog management

### `lga_client.py` - Airport Data Client

- **Purpose**: Clean interface to LGA airport APIs
- **Functions**:
  - `get_current_metar()` → METAR string
  - `get_active_runways()` → {"arrivals": "22", "departures": "13"}

## Benefits of New Structure

### ✅ Clean Separation of Concerns

- **Software logic** isolated from hardware
- **Easy testing** without MatrixPortal device
- **Maintainable** single-responsibility modules

### ✅ Runway-Focused Behavior

- **RWY04 only**: Shows flight data (your view)
- **Other runways**: Weather station mode
- **Automatic switching** based on ATIS

### ✅ Intelligent Polling

- **No external dependencies**: Pure CircuitPython
- **Power efficient**: Longer sleeps when inactive
- **Smart caching**: Reduces API calls
- **Integrated timing**: No cron needed

### ✅ Robust Error Handling

- **Graceful degradation** with cached data
- **Hardware abstraction** for testing
- **Watchdog integration** prevents hangs
- **Network error recovery**

## Deployment

### For MatrixPortal Device

1. Copy all files from `src/` to the device root
2. Update WiFi credentials in `config.py`
3. Rename `main.py` to `code.py` on the device (CircuitPython convention)

### For Testing/Development

1. Install requirements: `pip install -r requirements.txt`
2. Run tests: `python test/tests.py`
3. Run application: `python run.py` (will use test mode)

## Configuration

### Key Settings in `config.py`

```python
# WiFi
WIFI_SSID = "your_network"
WIFI_PASSWORD = "your_password"

# Polling intervals
FLIGHT_POLL_INTERVAL = 30      # RWY04 active
RUNWAY_CHECK_INTERVAL = 900    # ATIS check (15 min)
WEATHER_REFRESH_INTERVAL = 300 # Weather update (5 min)

# Flight filtering
MAX_APPROACH_ALTITUDE = 5000   # Approach traffic only
```

## Testing Results

✅ **All components tested and working**
✅ **Live ATIS integration** (currently RWY22 active)
✅ **Caching system** functioning correctly
✅ **Hardware abstraction** allows desktop testing
✅ **Intelligent polling** switches based on runway

## Current Status

- **Active runway**: RWY22 (arrivals), RWY13 (departures)
- **Mode**: Weather station (showing METAR + runway info)
- **Next runway check**: Automatic every 15 minutes
- **Ready for deployment** to MatrixPortal device

The application will automatically switch to flight tracking mode when LGA switches to runway 04 arrivals!
