#!/usr/bin/env python
"""
FlightPortal Flight Logic
Handles all flight data, runway detection, and caching logic.
"""

import time
import json
# typing module not available in Python 2.7
try:
    import adafruit_requests as requests
except ImportError:
    import requests  # For testing on desktop

try:
    from .lga_client import get_current_metar, get_active_runways
    from . import config
except ImportError:
    from lga_client import get_current_metar, get_active_runways
    import config

class FlightLogic:
    """Handles flight data and runway logic with smart caching."""
    
    def __init__(self):
        self.last_runway_check = 0
        self.last_weather_refresh = 0
        self.cached_runway_status = None
        self.cached_weather_data = None
        self.cached_metar = None
        
        # Flight data URLs
        self.flight_search_url = "https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds={}{}".format(config.RWY04_BOUNDS_BOX, config.FLIGHT_SEARCH_TAIL)
        self.flight_details_url = "https://data-live.flightradar24.com/clickhandler/?flight="
    
    def check_runway_status(self, force_refresh=False):
        """
        Check current runway status with 15-minute caching.
        
        Args:
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            dict: {"runway_04_active": bool, "arrivals": str, "departures": str, "last_updated": float}
        """
        current_time = time.time()
        
        # Use cached data if within interval and not forcing refresh
        if (not force_refresh and 
            self.cached_runway_status and 
            (current_time - self.last_runway_check) < config.RUNWAY_CHECK_INTERVAL):
            return self.cached_runway_status
        
        # Fetch fresh runway data
        try:
            runways = get_active_runways()
            arrivals = runways.get("arrivals")
            departures = runways.get("departures")
            
            # Check if runway 04 is active for arrivals
            runway_04_active = False
            if arrivals:
                # Remove L/C/R suffixes and check if it's runway 04
                import re
                runway_num = re.sub(r'[LCR]$', '', arrivals)
                runway_04_active = runway_num in ['04', '4']
            
            self.cached_runway_status = {
                "runway_04_active": runway_04_active,
                "arrivals": arrivals,
                "departures": departures,
                "last_updated": current_time
            }
            
            self.last_runway_check = current_time
            
            if config.DEBUG_MODE:
                print "Runway status updated: Arrivals=%s, RWY04_Active=%s" % (arrivals, runway_04_active)
            
            return self.cached_runway_status
            
        except Exception as e:
            print "Error checking runway status: " + str(e)
            
            # Return cached data if available, otherwise default to inactive
            if self.cached_runway_status:
                return self.cached_runway_status
            else:
                return {
                    "runway_04_active": False,
                    "arrivals": None,
                    "departures": None,
                    "last_updated": current_time
                }
    
    def get_runway_04_flights(self):
        """
        Get flight data for runway 04 approach corridor.
        
        Returns:
            dict: Flight data or None if no flights found
        """
        try:
            response = requests.get(
                url=self.flight_search_url, 
                headers=config.REQUEST_HEADERS, 
                timeout=config.CONNECTION_TIMEOUT
            )
            
            if response.status_code != 200:
                print "Flight API returned status %s" % response.status_code
                return None
            
            data = response.json()
            
            # Look for flight data (skip version and full_count keys)
            for flight_id, flight_info in data.items():
                if flight_id not in ['version', 'full_count'] and isinstance(flight_info, list):
                    if len(flight_info) >= 13:  # Valid flight data
                        # Check altitude filter
                        altitude = flight_info[4] if len(flight_info) > 4 else 0
                        if altitude < config.MAX_APPROACH_ALTITUDE:
                            # Parse flight information
                            flight_data = self._parse_flight_data(flight_id, flight_info)
                            if flight_data:
                                return flight_data
            
            # No valid flights found
            return None
            
        except Exception as e:
            print "Error fetching flights: " + str(e)
            return None
    
    def _parse_flight_data(self, flight_id, flight_info):
        """Parse raw flight data into structured format."""
        try:
            if len(flight_info) < 13:
                return None
            
            # Extract flight details (matching original code.py format)
            callsign = flight_info[16] if len(flight_info) > 16 else flight_info[13]
            aircraft_type = flight_info[8] if len(flight_info) > 8 else "Unknown"
            altitude = flight_info[4]
            speed = flight_info[5]
            origin = flight_info[11] if len(flight_info) > 11 else "???"
            destination = flight_info[12] if len(flight_info) > 12 else "LGA"
            
            return {
                "flight_id": flight_id,
                "callsign": callsign or "Unknown",
                "aircraft_type": aircraft_type,
                "altitude": altitude,
                "speed": speed,
                "origin": origin,
                "destination": destination,
                "route": "{} → {}".format(origin, destination)
            }
            
        except Exception as e:
            print "Error parsing flight data: " + str(e)
            return None
    
    def get_weather_display(self, force_refresh=False):
        """
        Get weather and runway information for display.
        
        Args:
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            dict: Weather display data
        """
        current_time = time.time()
        
        # Use cached weather if within interval and not forcing refresh
        if (not force_refresh and 
            self.cached_weather_data and 
            (current_time - self.last_weather_refresh) < config.WEATHER_REFRESH_INTERVAL):
            return self.cached_weather_data
        
        # Fetch fresh weather data
        try:
            metar = get_current_metar()
            runway_status = self.check_runway_status()
            
            self.cached_weather_data = {
                "type": "weather",
                "metar": metar,
                "arrivals_runway": runway_status.get("arrivals", "Unknown"),
                "departures_runway": runway_status.get("departures", "Unknown"),
                "last_updated": current_time
            }
            
            self.last_weather_refresh = current_time
            
            return self.cached_weather_data
            
        except Exception as e:
            print "Error fetching weather: " + str(e)
            
            # Return cached data if available
            if self.cached_weather_data:
                return self.cached_weather_data
            else:
                return {
                    "type": "weather",
                    "metar": "Weather unavailable",
                    "arrivals_runway": "Unknown",
                    "departures_runway": "Unknown",
                    "last_updated": current_time
                }
    
    def get_display_data(self):
        """
        Main function to get appropriate display data based on runway status.
        
        Returns:
            dict: Display data with type indicator
        """
        runway_status = self.check_runway_status()
        
        if runway_status["runway_04_active"]:
            # Runway 04 is active - look for flights
            flight_data = self.get_runway_04_flights()
            
            if flight_data:
                flight_data["type"] = "flight"
                flight_data["runway_status"] = runway_status
                return flight_data
            else:
                # No flights found, but runway 04 is active
                return {
                    "type": "no_flights",
                    "message": "RWY04 Active - No Approach Traffic",
                    "runway_status": runway_status
                }
        else:
            # Different runway active - show weather
            weather_data = self.get_weather_display()
            weather_data["runway_status"] = runway_status
            return weather_data
    
    def refresh_all_data(self):
        """Force refresh of all cached data."""
        self.check_runway_status(force_refresh=True)
        self.get_weather_display(force_refresh=True)

# Global instance for easy access
flight_logic = FlightLogic()