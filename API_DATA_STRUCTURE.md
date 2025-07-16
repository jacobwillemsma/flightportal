# FlightRadar24 API Data Structure

This document explains the data structures returned by the FlightRadar24 endpoints used in the flightportal project.

## Overview

The project uses two main endpoints:
1. **Flight Search** - Gets list of flights in a geographic area
2. **Flight Details** - Gets detailed information about a specific flight

## 1. Flight Search Endpoint

**URL Pattern:**
```
https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds=<lat_max>,<lat_min>,<lng_min>,<lng_max>&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1&limit=1
```

**Response Structure:**
```json
{
  "full_count": 16446,
  "version": 4,
  "3b45069d": ["4076B1", 51.95, 0.965, 305, 34000, 350, "", "F-BDWY1", "B738", "G-TAWX", 1752629436, "HRG", "MAN", "BY789", 0, 0, "TOM789", 0, "TUI"]
}
```

### Flight Data Array Fields (index: meaning)
- **0**: Aircraft hex code (e.g., "4076B1")
- **1**: Latitude (51.95)
- **2**: Longitude (0.965)
- **3**: Track/heading in degrees (305)
- **4**: Altitude in feet (34000)
- **5**: Speed in knots (350)
- **6**: Unknown/reserved field
- **7**: Unknown field
- **8**: Aircraft type (e.g., "B738" = Boeing 737-800)
- **9**: Aircraft registration (e.g., "G-TAWX")
- **10**: Timestamp
- **11**: Origin airport code (e.g., "HRG")
- **12**: Destination airport code (e.g., "MAN")
- **13**: Flight number (e.g., "BY789")
- **14**: Unknown field
- **15**: Unknown field
- **16**: Callsign (e.g., "TOM789")
- **17**: Unknown field
- **18**: Airline (e.g., "TUI")

## 2. Flight Details Endpoint

**URL Pattern:**
```
https://data-live.flightradar24.com/clickhandler/?flight=<flight_id>
```

**Response Structure:** (Comprehensive JSON object with the following main sections)

### Aircraft Information
```json
"aircraft": {
  "hex": "40773b",
  "registration": "G-TUMK",
  "model": {
    "code": "B38M",
    "text": "Boeing 737 MAX 8"
  },
  "images": {
    "large": [...],
    "medium": [...],
    "thumbnails": [...]
  }
}
```

### Flight Identification
```json
"identification": {
  "callsign": "TOM6261",
  "id": "3b452cb4",
  "number": {
    "default": "BY6261"
  }
}
```

### Airport Information
```json
"airport": {
  "origin": {
    "code": {"iata": "PFO", "icao": "LCPH"},
    "name": "Paphos International Airport",
    "position": {
      "latitude": 34.718277,
      "longitude": 32.484398,
      "country": {"code": "CYP", "name": "Cyprus"}
    }
  },
  "destination": {
    "code": {"iata": "BRS", "icao": "EGGD"},
    "name": "Bristol Airport",
    "position": {
      "latitude": 51.38266,
      "longitude": -2.71908,
      "country": {"code": "GB", "name": "United Kingdom"}
    }
  }
}
```

### Flight Times
```json
"time": {
  "scheduled": {
    "departure": 1752613800,
    "arrival": 1752631200
  },
  "real": {
    "departure": 1752614160,
    "arrival": null
  },
  "estimated": {
    "arrival": 1752631040
  }
}
```

### Flight Trail (Historical Positions)
```json
"trail": [
  {
    "alt": 33725,
    "hd": 269,
    "lat": 51.417892,
    "lng": -0.276514,
    "spd": 338,
    "ts": 1752629408
  }
]
```

### Airline Information
```json
"airline": {
  "code": {"iata": "X3", "icao": "TUI"},
  "name": "TUI",
  "short": "TUI fly"
}
```

### Flight Status
```json
"status": {
  "text": "Estimated- 02:57",
  "live": true,
  "icon": "green",
  "generic": {
    "status": {
      "color": "green",
      "text": "estimated",
      "type": "arrival"
    }
  }
}
```

## Usage in MatrixPortal Code

The MatrixPortal code (`code.py`) uses these endpoints as follows:

1. **Search for flights** in the configured geographic bounds every 30 seconds
2. **Extract key information** from the flight array (position, altitude, speed, flight number)
3. **Get detailed information** for selected flights using the flight ID
4. **Display information** on the LED matrix, including:
   - Flight number/callsign
   - Aircraft type
   - Altitude and speed
   - Origin and destination airports

## Key Data Points for Display

The project extracts these key fields for display:
- **Flight Number**: `data[16]` from search or `identification.callsign` from details
- **Aircraft Type**: `data[8]` from search or `aircraft.model.code` from details
- **Altitude**: `data[4]` from search (in feet)
- **Speed**: `data[5]` from search (in knots)
- **Position**: `data[1]` (lat), `data[2]` (lng) from search
- **Route**: `data[11]` → `data[12]` from search (origin → destination)