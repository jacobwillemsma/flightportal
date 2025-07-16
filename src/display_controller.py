#!/usr/bin/env python3
"""
FlightPortal Display Controller
Handles all MatrixPortal hardware, LED display, and animations.
"""

import time
import gc
from typing import Dict, Any, Optional

try:
    # MatrixPortal/CircuitPython imports
    import board
    import terminalio
    import displayio
    import framebufferio
    import rgbmatrix
    import busio
    import neopixel
    from digitalio import DigitalInOut
    from adafruit_matrixportal.matrixportal import MatrixPortal
    from adafruit_portalbase.network import HttpError
    from adafruit_esp32spi import adafruit_esp32spi
    from adafruit_esp32spi import adafruit_esp32spi_wifimanager
    import adafruit_display_text.label
    import adafruit_requests as requests
    from microcontroller import watchdog as w
    from watchdog import WatchDogMode
    HARDWARE_AVAILABLE = True
except ImportError:
    # Running on desktop for testing
    HARDWARE_AVAILABLE = False
    print("Hardware not available - running in test mode")

try:
    from . import config
except ImportError:
    import config

class DisplayController:
    """Handles all display hardware operations."""
    
    def __init__(self):
        self.hardware_ready = False
        self.matrixportal = None
        self.display_group = None
        self.labels = []
        self.plane_group = None
        
        # Text content for labels
        self.label_short_text = ['', '', '']
        self.label_long_text = ['', '', '']
        
        if HARDWARE_AVAILABLE:
            self._init_hardware()
    
    def _init_hardware(self):
        """Initialize MatrixPortal and display hardware."""
        try:
            # Configure watchdog
            w.timeout = config.WATCHDOG_TIMEOUT
            w.mode = WatchDogMode.RESET
            
            # Initialize ESP32 SPI
            esp32_cs = DigitalInOut(board.ESP_CS)
            esp32_ready = DigitalInOut(board.ESP_BUSY)
            esp32_reset = DigitalInOut(board.ESP_RESET)
            
            spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
            esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
            
            # Status LED
            status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
            
            # WiFi setup
            secrets = {"ssid": config.WIFI_SSID, "password": config.WIFI_PASSWORD}
            wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(
                esp, secrets, status_light, debug=False, attempts=1
            )
            
            # MatrixPortal setup
            self.matrixportal = MatrixPortal(
                headers=config.REQUEST_HEADERS,
                esp=esp,
                rotation=0,
                debug=config.DEBUG_MODE
            )
            
            # Initialize display
            self._setup_display()
            
            self.hardware_ready = True
            print("Hardware initialized successfully")
            
        except Exception as e:
            print(f"Hardware initialization failed: {e}")
            self.hardware_ready = False
    
    def _setup_display(self):
        """Setup the LED matrix display and text labels."""
        if not self.matrixportal:
            return
        
        # Create text labels
        self.labels = []
        y_positions = [2, 12, 22]  # Vertical positions for 3 lines
        colors = [config.ROW_ONE_COLOUR, config.ROW_TWO_COLOUR, config.ROW_THREE_COLOUR]
        
        for i in range(3):
            label = adafruit_display_text.label.Label(
                terminalio.FONT,
                text="",
                color=colors[i],
                x=1,
                y=y_positions[i]
            )
            self.labels.append(label)
        
        # Create display group
        self.display_group = displayio.Group()
        for label in self.labels:
            self.display_group.append(label)
        
        # Setup plane animation group (simplified from original)
        self._setup_plane_animation()
        
        # Show initial display
        self.matrixportal.display.show(self.display_group)
    
    def _setup_plane_animation(self):
        """Setup plane animation bitmap (simplified version)."""
        try:
            # Create a simple plane sprite group
            self.plane_group = displayio.Group()
            
            # For now, just create a simple colored rectangle to represent plane
            # Original code had a bitmap, but this is simplified
            plane_bitmap = displayio.Bitmap(12, 8, 2)
            plane_palette = displayio.Palette(2)
            plane_palette[0] = 0x000000  # Transparent
            plane_palette[1] = config.PLANE_COLOUR  # Plane color
            
            # Draw a simple plane shape
            for x in range(8, 12):
                for y in range(3, 5):
                    plane_bitmap[x, y] = 1
            
            plane_sprite = displayio.TileGrid(plane_bitmap, pixel_shader=plane_palette)
            self.plane_group.append(plane_sprite)
            
        except Exception as e:
            print(f"Plane animation setup failed: {e}")
    
    def show_flight_info(self, flight_data: Dict[str, Any]):
        """
        Display flight information with animations.
        
        Args:
            flight_data: Flight data dictionary
        """
        if not self.hardware_ready:
            self._print_flight_info(flight_data)
            return
        
        # Prepare text content
        callsign = flight_data.get("callsign", "Unknown")
        aircraft = flight_data.get("aircraft_type", "")
        altitude = flight_data.get("altitude", 0)
        route = flight_data.get("route", "")
        
        # Short text for static display
        self.label_short_text = [
            callsign[:10],
            f"{aircraft} {altitude}ft",
            route[:10] if route else ""
        ]
        
        # Long text for scrolling
        self.label_long_text = [
            callsign,
            f"{aircraft} at {altitude} feet",
            route
        ]
        
        # Display flight with animation
        self._display_with_animation()
        
        if config.DEBUG_MODE:
            print(f"Displayed flight: {callsign} - {aircraft} at {altitude}ft")
    
    def show_weather_info(self, weather_data: Dict[str, Any]):
        """
        Display weather and runway information (static display).
        
        Args:
            weather_data: Weather data dictionary
        """
        if not self.hardware_ready:
            self._print_weather_info(weather_data)
            return
        
        arrivals = weather_data.get("arrivals_runway", "Unknown")
        departures = weather_data.get("departures_runway", "Unknown")
        metar = weather_data.get("metar", "Weather unavailable")
        
        # Extract key weather info from METAR (simplified)
        wind_info = self._extract_wind_from_metar(metar)
        
        # Static text display (no scrolling for weather)
        self.labels[0].text = f"ARR: RWY{arrivals}"
        self.labels[1].text = f"DEP: RWY{departures}" 
        self.labels[2].text = wind_info
        
        # Show static display
        self.matrixportal.display.show(self.display_group)
        
        if config.DEBUG_MODE:
            print(f"Displayed weather: ARR={arrivals}, DEP={departures}")
    
    def show_no_flights_message(self, message_data: Dict[str, Any]):
        """Display message when RWY04 active but no flights."""
        if not self.hardware_ready:
            print(message_data.get("message", "No flights"))
            return
        
        message = message_data.get("message", "RWY04 Active")
        
        self.labels[0].text = "RWY04 ACTIVE"
        self.labels[1].text = "No Approach"
        self.labels[2].text = "Traffic"
        
        self.matrixportal.display.show(self.display_group)
    
    def clear_display(self):
        """Clear the display."""
        if not self.hardware_ready:
            print("Display cleared")
            return
        
        for label in self.labels:
            label.text = ""
        
        self.matrixportal.display.show(self.display_group)
    
    def _display_with_animation(self):
        """Display flight info with plane animation and text scrolling."""
        if not self.hardware_ready:
            return
        
        # Show static text first
        for i, text in enumerate(self.label_short_text):
            self.labels[i].text = text
        
        self.matrixportal.display.show(self.display_group)
        time.sleep(config.PAUSE_BETWEEN_LABEL_SCROLLING)
        
        # Plane animation
        self._animate_plane()
        
        # Scroll long text
        for i, long_text in enumerate(self.label_long_text):
            if len(long_text) > len(self.label_short_text[i]):
                self._scroll_label(self.labels[i], long_text)
                self.labels[i].text = self.label_short_text[i]
                self.labels[i].x = 1
                time.sleep(config.PAUSE_BETWEEN_LABEL_SCROLLING)
    
    def _animate_plane(self):
        """Simple plane animation across the screen."""
        if not self.plane_group or not self.hardware_ready:
            return
        
        try:
            self.matrixportal.display.show(self.plane_group)
            
            # Move plane from right to left
            for x in range(config.DISPLAY_WIDTH + 12, -12, -1):
                self.plane_group.x = x
                w.feed()  # Feed watchdog
                time.sleep(config.PLANE_SPEED)
            
            # Return to main display
            self.matrixportal.display.show(self.display_group)
            
        except Exception as e:
            print(f"Plane animation error: {e}")
    
    def _scroll_label(self, label, text):
        """Scroll text across the display."""
        if not self.hardware_ready:
            return
        
        label.text = text
        label.x = config.DISPLAY_WIDTH
        
        # Scroll from right to left
        end_position = -label.bounding_box[2] if hasattr(label, 'bounding_box') else -100
        
        for x in range(config.DISPLAY_WIDTH, end_position, -1):
            label.x = x
            w.feed()  # Feed watchdog
            time.sleep(config.TEXT_SPEED)
    
    def _extract_wind_from_metar(self, metar: str) -> str:
        """Extract wind information from METAR string."""
        if not metar:
            return "No wind data"
        
        try:
            # Look for wind pattern like "18006KT"
            import re
            wind_match = re.search(r'(\d{3})(\d{2,3})KT', metar)
            if wind_match:
                direction = wind_match.group(1)
                speed = wind_match.group(2).lstrip('0') or '0'
                return f"{direction}@{speed}kt"
            else:
                return "Wind unavailable"
        except Exception:
            return "Wind error"
    
    def _print_flight_info(self, flight_data: Dict[str, Any]):
        """Print flight info to console when hardware not available."""
        callsign = flight_data.get("callsign", "Unknown")
        aircraft = flight_data.get("aircraft_type", "")
        altitude = flight_data.get("altitude", 0)
        route = flight_data.get("route", "")
        
        print("=" * 40)
        print(f"FLIGHT DISPLAY")
        print(f"Callsign: {callsign}")
        print(f"Aircraft: {aircraft} at {altitude} feet")
        print(f"Route: {route}")
        print("=" * 40)
    
    def _print_weather_info(self, weather_data: Dict[str, Any]):
        """Print weather info to console when hardware not available."""
        arrivals = weather_data.get("arrivals_runway", "Unknown")
        departures = weather_data.get("departures_runway", "Unknown")
        metar = weather_data.get("metar", "Weather unavailable")
        
        print("=" * 40)
        print(f"WEATHER DISPLAY")
        print(f"Arrivals: RWY{arrivals}")
        print(f"Departures: RWY{departures}")
        print(f"METAR: {metar}")
        print("=" * 40)
    
    def feed_watchdog(self):
        """Feed the hardware watchdog."""
        if HARDWARE_AVAILABLE:
            w.feed()
    
    def cleanup(self):
        """Cleanup display resources."""
        self.clear_display()
        if config.PRINT_MEMORY_INFO:
            gc.collect()
            print(f"Memory free: {gc.mem_free()}")

# Global instance for easy access
display_controller = DisplayController()