#!/usr/bin/env python
"""
FlightPortal Main Application
Orchestrates the flight monitoring application with intelligent polling.

This is the main entry point for the MatrixPortal device.
"""

import time
import gc
# typing module not available in Python 2.7

try:
    # CircuitPython specific imports
    from microcontroller import watchdog as w
    HARDWARE_AVAILABLE = True
except ImportError:
    # Running on desktop for testing
    HARDWARE_AVAILABLE = False
    print "Running in test mode without hardware"

try:
    from . import config
    from .flight_logic import flight_logic
    from .display_controller import display_controller
except ImportError:
    import config
    from flight_logic import FlightLogic
    from display_controller import DisplayController
    
    # Create instances when imported directly
    flight_logic = FlightLogic()
    display_controller = DisplayController()

class FlightPortalApp:
    """Main application orchestrator."""
    
    def __init__(self):
        self.last_runway_check = 0
        self.last_weather_refresh = 0
        self.last_flight_id = None
        self.current_display_mode = None  # 'flight', 'weather', 'no_flights'
        
        print "FlightPortal Starting..."
        print "Hardware available: %s" % HARDWARE_AVAILABLE
        
        # Initialize display
        if not display_controller.hardware_ready and HARDWARE_AVAILABLE:
            print "Display initialization failed!"
            return
        
        print "FlightPortal Ready!"
    
    def run(self):
        """Main application loop with intelligent polling."""
        print "Starting main loop..."
        
        while True:
            try:
                current_time = time.time()
                
                # Check for runway changes every 15 minutes
                if (current_time - self.last_runway_check) >= config.RUNWAY_CHECK_INTERVAL:
                    print "Checking runway status..."
                    flight_logic.check_runway_status(force_refresh=True)
                    self.last_runway_check = current_time
                
                # Get current display data
                display_data = flight_logic.get_display_data()
                
                # Handle different display modes
                if display_data["type"] == "flight":
                    self._handle_flight_display(display_data)
                    sleep_time = config.FLIGHT_POLL_INTERVAL
                    
                elif display_data["type"] == "no_flights":
                    self._handle_no_flights_display(display_data)
                    sleep_time = config.FLIGHT_POLL_INTERVAL  # Keep checking for flights
                    
                elif display_data["type"] == "weather":
                    self._handle_weather_display(display_data, current_time)
                    sleep_time = config.SLEEP_WHEN_INACTIVE
                    
                else:
                    print "Unknown display type: %s" % display_data.get('type')
                    sleep_time = config.SLEEP_WHEN_INACTIVE
                
                # Feed watchdog and sleep
                self._sleep_with_watchdog(sleep_time)
                
                # Periodic memory cleanup
                if config.PRINT_MEMORY_INFO:
                    gc.collect()
                    print "Memory free: %s" % gc.mem_free()
                
            except KeyboardInterrupt:
                print "Shutting down..."
                break
                
            except Exception as e:
                print "Main loop error: " + str(e)
                self._sleep_with_watchdog(30)  # Wait before retrying
    
    def _handle_flight_display(self, display_data):
        """Handle displaying flight information."""
        flight_id = display_data.get("flight_id")
        
        if flight_id == self.last_flight_id and self.current_display_mode == "flight":
            # Same flight, keep showing it
            if config.DEBUG_MODE:
                print "Continuing to display flight %s" % flight_id
        else:
            # New flight or mode change
            print "New flight found: %s (%s)" % (display_data.get('callsign'), flight_id)
            display_controller.clear_display()
            display_controller.show_flight_info(display_data)
            self.last_flight_id = flight_id
            self.current_display_mode = "flight"
    
    def _handle_no_flights_display(self, display_data):
        """Handle displaying 'no flights' message when RWY04 is active."""
        if self.current_display_mode != "no_flights":
            print "RWY04 active but no approach traffic found"
            display_controller.show_no_flights_message(display_data)
            self.current_display_mode = "no_flights"
            self.last_flight_id = None
    
    def _handle_weather_display(self, display_data, current_time):
        """Handle displaying weather information."""
        # Refresh weather data periodically
        if (current_time - self.last_weather_refresh) >= config.WEATHER_REFRESH_INTERVAL:
            print "Refreshing weather data..."
            display_data = flight_logic.get_weather_display(force_refresh=True)
            self.last_weather_refresh = current_time
        
        if self.current_display_mode != "weather":
            arrivals = display_data.get("arrivals_runway", "Unknown")
            print "Arrivals on runway %s - showing weather" % arrivals
            display_controller.show_weather_info(display_data)
            self.current_display_mode = "weather"
            self.last_flight_id = None
    
    def _sleep_with_watchdog(self, sleep_time):
        """Sleep while feeding the watchdog periodically."""
        if HARDWARE_AVAILABLE:
            # Feed watchdog every 5 seconds during sleep
            for _ in range(0, sleep_time, 5):
                display_controller.feed_watchdog()
                time.sleep(min(5, sleep_time))
                sleep_time -= 5
                if sleep_time <= 0:
                    break
        else:
            # Simple sleep for testing
            time.sleep(min(sleep_time, 10))  # Cap sleep for testing
    
    def cleanup(self):
        """Cleanup application resources."""
        print "Cleaning up..."
        display_controller.cleanup()

def main():
    """Main entry point."""
    app = FlightPortalApp()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print "Application interrupted by user"
    except Exception as e:
        print "Application error: " + str(e)
    finally:
        app.cleanup()

if __name__ == "__main__":
    main()