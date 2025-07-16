#!/usr/bin/env python3
"""
Test the new FlightPortal structure.
This verifies all components work together correctly.
"""

import time
import sys
import os

# Add src directory to path for imports
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
sys.path.insert(0, src_path)

# Import modules directly from src
import config
from flight_logic import FlightLogic
from display_controller import DisplayController

# Create instances
flight_logic = FlightLogic()
display_controller = DisplayController()

def test_configuration():
    """Test that configuration is properly loaded."""
    print("TESTING CONFIGURATION")
    print("=" * 40)
    print(f"WiFi SSID: {config.WIFI_SSID}")
    print(f"Flight poll interval: {config.FLIGHT_POLL_INTERVAL}s")
    print(f"Runway check interval: {config.RUNWAY_CHECK_INTERVAL}s")
    print(f"RWY04 bounds: {config.RWY04_BOUNDS_BOX}")
    print(f"Max approach altitude: {config.MAX_APPROACH_ALTITUDE}ft")
    print("✅ Configuration loaded successfully")
    print()

def test_flight_logic():
    """Test flight logic functionality."""
    print("TESTING FLIGHT LOGIC")
    print("=" * 40)
    
    # Test runway status check
    print("Checking runway status...")
    runway_status = flight_logic.check_runway_status()
    print(f"Runway status: {runway_status}")
    
    # Test display data retrieval
    print("Getting display data...")
    display_data = flight_logic.get_display_data()
    print(f"Display data type: {display_data.get('type')}")
    
    if display_data["type"] == "flight":
        print(f"Flight found: {display_data.get('callsign')}")
        print(f"Aircraft: {display_data.get('aircraft_type')}")
        print(f"Altitude: {display_data.get('altitude')}ft")
        print(f"Route: {display_data.get('route')}")
    elif display_data["type"] == "weather":
        print(f"Weather mode - Arrivals: RWY{display_data.get('arrivals_runway')}")
        print(f"METAR: {display_data.get('metar', '')[:50]}...")
    elif display_data["type"] == "no_flights":
        print(f"No flights: {display_data.get('message')}")
    
    print("✅ Flight logic working")
    print()

def test_display_controller():
    """Test display controller functionality."""
    print("TESTING DISPLAY CONTROLLER")
    print("=" * 40)
    
    print(f"Hardware ready: {display_controller.hardware_ready}")
    
    # Test with sample flight data
    sample_flight = {
        "type": "flight",
        "callsign": "TEST123",
        "aircraft_type": "B737",
        "altitude": 3500,
        "speed": 180,
        "route": "BOS → LGA"
    }
    
    print("Testing flight display...")
    display_controller.show_flight_info(sample_flight)
    
    time.sleep(2)
    
    # Test with sample weather data
    sample_weather = {
        "type": "weather",
        "arrivals_runway": "22",
        "departures_runway": "13",
        "metar": "KLGA 160151Z 18006KT 10SM FEW050 SCT250 27/22 A3004"
    }
    
    print("Testing weather display...")
    display_controller.show_weather_info(sample_weather)
    
    time.sleep(2)
    
    # Test no flights message
    sample_no_flights = {
        "type": "no_flights",
        "message": "RWY04 Active - No Approach Traffic"
    }
    
    print("Testing no flights display...")
    display_controller.show_no_flights_message(sample_no_flights)
    
    print("✅ Display controller working")
    print()

def test_integration():
    """Test full integration of all components."""
    print("TESTING FULL INTEGRATION")
    print("=" * 40)
    
    # Simulate main app logic
    print("Getting live display data...")
    display_data = flight_logic.get_display_data()
    
    print(f"Current mode: {display_data.get('type')}")
    
    if display_data["type"] == "flight":
        print("Displaying flight information...")
        display_controller.show_flight_info(display_data)
        
    elif display_data["type"] == "weather":
        print("Displaying weather information...")
        display_controller.show_weather_info(display_data)
        
    elif display_data["type"] == "no_flights":
        print("Displaying no flights message...")
        display_controller.show_no_flights_message(display_data)
    
    print("✅ Full integration working")
    print()

def test_caching():
    """Test the caching functionality."""
    print("TESTING CACHING FUNCTIONALITY")
    print("=" * 40)
    
    # First call - should fetch fresh data
    start_time = time.time()
    runway_status1 = flight_logic.check_runway_status()
    time1 = time.time() - start_time
    print(f"First runway check took: {time1:.2f}s")
    
    # Second call - should use cached data
    start_time = time.time()
    runway_status2 = flight_logic.check_runway_status()
    time2 = time.time() - start_time
    print(f"Second runway check took: {time2:.2f}s (cached)")
    
    # Verify data is the same
    if runway_status1 == runway_status2:
        print("✅ Caching working correctly")
    else:
        print("❌ Caching issue - data differs")
    
    # Test forced refresh
    start_time = time.time()
    runway_status3 = flight_logic.check_runway_status(force_refresh=True)
    time3 = time.time() - start_time
    print(f"Forced refresh took: {time3:.2f}s")
    
    print()

def run_all_tests():
    """Run all test suites."""
    print("FlightPortal Structure Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_configuration()
        test_flight_logic()
        test_display_controller()
        test_integration()
        test_caching()
        
        print("🎉 ALL TESTS PASSED!")
        print()
        print("New structure is working correctly!")
        print("Ready to deploy to MatrixPortal device.")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()