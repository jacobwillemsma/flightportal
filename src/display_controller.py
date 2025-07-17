#!/usr/bin/env python
"""
FlightPortal Display Controller
Handles all MatrixPortal hardware, LED display, and animations.
"""

import time
import gc
# typing module not available in Python 2.7

try:
    # Try Raspberry Pi RGB Matrix first (Adafruit_RGBmatrix API)
    from rgbmatrix import Adafruit_RGBmatrix
    from PIL import Image, ImageDraw, ImageFont
    import time
    HARDWARE_AVAILABLE = True
    HARDWARE_TYPE = "raspberry_pi"
    print "Raspberry Pi RGB Matrix hardware detected"
except ImportError:
    try:
        # Try MatrixPortal/CircuitPython imports as fallback
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
        HARDWARE_TYPE = "matrixportal"
        print "MatrixPortal hardware detected"
    except ImportError:
        # Running on desktop for testing
        HARDWARE_AVAILABLE = False
        HARDWARE_TYPE = "none"
        print "No matrix hardware available - running in test mode"

try:
    from . import config
except ImportError:
    import config

class DisplayController:
    """Handles all display hardware operations."""
    
    def __init__(self):
        self.hardware_ready = False
        self.hardware_type = HARDWARE_TYPE
        
        # MatrixPortal specific
        self.matrixportal = None
        self.display_group = None
        self.labels = []
        self.plane_group = None
        
        # Raspberry Pi specific
        self.matrix = None
        self.font = None
        self.current_image = None
        
        # Text content for labels
        self.label_short_text = ['', '', '']
        self.label_long_text = ['', '', '']
        
        if HARDWARE_AVAILABLE:
            if self.hardware_type == "raspberry_pi":
                self._init_raspberry_pi_hardware()
            elif self.hardware_type == "matrixportal":
                self._init_matrixportal_hardware()
    
    def _init_raspberry_pi_hardware(self):
        """Initialize Raspberry Pi RGB Matrix hardware."""
        try:
            # Initialize matrix: 32 rows, 2 chained panels (128x32 total)
            self.matrix = Adafruit_RGBmatrix(32, 2)
            
            # Try to load a font (fallback to default if not available)
            try:
                self.font = ImageFont.load_default()
            except:
                self.font = None
            
            # Create initial blank image
            self.current_image = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), (0, 0, 0))
            
            self.hardware_ready = True
            print "Raspberry Pi RGB Matrix initialized successfully (128x32)"
            
        except Exception as e:
            print "Raspberry Pi hardware initialization failed: " + str(e)
            self.hardware_ready = False
    
    def _init_matrixportal_hardware(self):
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
            print "Hardware initialized successfully"
            
        except Exception as e:
            print "Hardware initialization failed: " + str(e)
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
            print "Plane animation setup failed: " + str(e)
    
    def show_flight_info(self, flight_data):
        """
        Display flight information with animations.
        
        Args:
            flight_data: Flight data dictionary
        """
        if not self.hardware_ready:
            self._print_flight_info(flight_data)
            return
        
        if self.hardware_type == "raspberry_pi":
            self._show_flight_info_rpi(flight_data)
        elif self.hardware_type == "matrixportal":
            self._show_flight_info_matrixportal(flight_data)
    
    def _show_flight_info_rpi(self, flight_data):
        """Display flight info on Raspberry Pi RGB Matrix."""
        # Prepare text content
        callsign = flight_data.get("callsign", "Unknown")
        aircraft = flight_data.get("aircraft_type", "")
        altitude = flight_data.get("altitude", 0)
        route = flight_data.get("route", "")
        
        # Create new image for display
        image = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw text lines with colors
        y_positions = [2, 12, 22]
        colors = [
            self._hex_to_rgb(config.ROW_ONE_COLOUR),
            self._hex_to_rgb(config.ROW_TWO_COLOUR), 
            self._hex_to_rgb(config.ROW_THREE_COLOUR)
        ]
        
        # Draw the text
        draw.text((2, y_positions[0]), callsign, fill=colors[0], font=self.font)
        draw.text((2, y_positions[1]), "%s %sft" % (aircraft, altitude), fill=colors[1], font=self.font)
        draw.text((2, y_positions[2]), route[:18] if route else "", fill=colors[2], font=self.font)
        
        # Show on matrix
        self.matrix.SetImage(image.im.id, 0, 0)
        self.current_image = image
        
        # Animate plane
        self._animate_plane_rpi()
        
        # Show scrolling text for long content
        if len(route) > 18:
            self._scroll_text_rpi(route, y_positions[2], colors[2])
        
        if config.DEBUG_MODE:
            print "Displayed flight: %s - %s at %sft" % (callsign, aircraft, altitude)
    
    def _show_flight_info_matrixportal(self, flight_data):
        """Display flight info on MatrixPortal (existing logic)."""
        # Prepare text content
        callsign = flight_data.get("callsign", "Unknown")
        aircraft = flight_data.get("aircraft_type", "")
        altitude = flight_data.get("altitude", 0)
        route = flight_data.get("route", "")
        
        # Short text for static display
        self.label_short_text = [
            callsign[:10],
            "%s %sft" % (aircraft, altitude),
            route[:10] if route else ""
        ]
        
        # Long text for scrolling
        self.label_long_text = [
            callsign,
            "%s at %s feet" % (aircraft, altitude),
            route
        ]
        
        # Display flight with animation
        self._display_with_animation()
        
        if config.DEBUG_MODE:
            print "Displayed flight: %s - %s at %sft" % (callsign, aircraft, altitude)
    
    def show_weather_info(self, weather_data):
        """
        Display weather and runway information (static display).
        
        Args:
            weather_data: Weather data dictionary
        """
        if not self.hardware_ready:
            self._print_weather_info(weather_data)
            return
        
        if self.hardware_type == "raspberry_pi":
            self._show_weather_info_rpi(weather_data)
        elif self.hardware_type == "matrixportal":
            self._show_weather_info_matrixportal(weather_data)
    
    def _show_weather_info_rpi(self, weather_data):
        """Display weather info on Raspberry Pi RGB Matrix."""
        arrivals = weather_data.get("arrivals_runway", "Unknown")
        departures = weather_data.get("departures_runway", "Unknown")
        metar = weather_data.get("metar", "Weather unavailable")
        
        # Extract key weather info from METAR (simplified)
        wind_info = self._extract_wind_from_metar(metar)
        
        # Create new image for display
        image = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw text lines with colors
        y_positions = [2, 12, 22]
        colors = [
            self._hex_to_rgb(config.ROW_ONE_COLOUR),
            self._hex_to_rgb(config.ROW_TWO_COLOUR), 
            self._hex_to_rgb(config.ROW_THREE_COLOUR)
        ]
        
        # Draw the weather text
        draw.text((2, y_positions[0]), "ARR: RWY%s" % arrivals, fill=colors[0], font=self.font)
        draw.text((2, y_positions[1]), "DEP: RWY%s" % departures, fill=colors[1], font=self.font)
        draw.text((2, y_positions[2]), wind_info, fill=colors[2], font=self.font)
        
        # Show on matrix
        self.matrix.SetImage(image.im.id, 0, 0)
        self.current_image = image
        
        if config.DEBUG_MODE:
            print "Displayed weather: ARR=%s, DEP=%s" % (arrivals, departures)
    
    def _show_weather_info_matrixportal(self, weather_data):
        """Display weather info on MatrixPortal (existing logic)."""
        arrivals = weather_data.get("arrivals_runway", "Unknown")
        departures = weather_data.get("departures_runway", "Unknown")
        metar = weather_data.get("metar", "Weather unavailable")
        
        # Extract key weather info from METAR (simplified)
        wind_info = self._extract_wind_from_metar(metar)
        
        # Static text display (no scrolling for weather)
        self.labels[0].text = "ARR: RWY%s" % arrivals
        self.labels[1].text = "DEP: RWY%s" % departures 
        self.labels[2].text = wind_info
        
        # Show static display
        self.matrixportal.display.show(self.display_group)
        
        if config.DEBUG_MODE:
            print "Displayed weather: ARR=%s, DEP=%s" % (arrivals, departures)
    
    def show_no_flights_message(self, message_data):
        """Display message when RWY04 active but no flights."""
        if not self.hardware_ready:
            print message_data.get("message", "No flights")
            return
        
        if self.hardware_type == "raspberry_pi":
            self._show_no_flights_rpi(message_data)
        elif self.hardware_type == "matrixportal":
            self._show_no_flights_matrixportal(message_data)
    
    def _show_no_flights_rpi(self, message_data):
        """Display no flights message on Raspberry Pi RGB Matrix."""
        # Create new image for display
        image = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw text lines with colors
        y_positions = [2, 12, 22]
        colors = [
            self._hex_to_rgb(config.ROW_ONE_COLOUR),
            self._hex_to_rgb(config.ROW_TWO_COLOUR), 
            self._hex_to_rgb(config.ROW_THREE_COLOUR)
        ]
        
        # Draw the message text
        draw.text((2, y_positions[0]), "RWY04 ACTIVE", fill=colors[0], font=self.font)
        draw.text((2, y_positions[1]), "No Approach", fill=colors[1], font=self.font)
        draw.text((2, y_positions[2]), "Traffic", fill=colors[2], font=self.font)
        
        # Show on matrix
        self.matrix.SetImage(image.im.id, 0, 0)
        self.current_image = image
    
    def _show_no_flights_matrixportal(self, message_data):
        """Display no flights message on MatrixPortal (existing logic)."""
        message = message_data.get("message", "RWY04 Active")
        
        self.labels[0].text = "RWY04 ACTIVE"
        self.labels[1].text = "No Approach"
        self.labels[2].text = "Traffic"
        
        self.matrixportal.display.show(self.display_group)
    
    def clear_display(self):
        """Clear the display."""
        if not self.hardware_ready:
            print "Display cleared"
            return
        
        if self.hardware_type == "raspberry_pi":
            self.matrix.Clear()
        elif self.hardware_type == "matrixportal":
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
            print "Plane animation error: " + str(e)
    
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
    
    def _extract_wind_from_metar(self, metar):
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
                return "%s@%skt" % (direction, speed)
            else:
                return "Wind unavailable"
        except Exception:
            return "Wind error"
    
    def _print_flight_info(self, flight_data):
        """Print flight info to console when hardware not available."""
        callsign = flight_data.get("callsign", "Unknown")
        aircraft = flight_data.get("aircraft_type", "")
        altitude = flight_data.get("altitude", 0)
        route = flight_data.get("route", "")
        
        print "=" * 40
        print "FLIGHT DISPLAY"
        print "Callsign: %s" % callsign
        print "Aircraft: %s at %s feet" % (aircraft, altitude)
        print "Route: %s" % route
        print "=" * 40
    
    def _print_weather_info(self, weather_data):
        """Print weather info to console when hardware not available."""
        arrivals = weather_data.get("arrivals_runway", "Unknown")
        departures = weather_data.get("departures_runway", "Unknown")
        metar = weather_data.get("metar", "Weather unavailable")
        
        print "=" * 40
        print "WEATHER DISPLAY"
        print "Arrivals: RWY%s" % arrivals
        print "Departures: RWY%s" % departures
        print "METAR: %s" % metar
        print "=" * 40
    
    def feed_watchdog(self):
        """Feed the hardware watchdog."""
        if HARDWARE_AVAILABLE and self.hardware_type == "matrixportal":
            w.feed()
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            # Handle RGB565 or other formats
            r = (hex_color >> 16) & 0xFF
            g = (hex_color >> 8) & 0xFF
            b = hex_color & 0xFF
            return (r, g, b)
    
    def _animate_plane_rpi(self):
        """Animate plane across the Raspberry Pi RGB Matrix."""
        try:
            # Create plane image
            plane_color = self._hex_to_rgb(config.PLANE_COLOUR)
            
            # Animate plane moving across screen
            for x in range(config.DISPLAY_WIDTH + 20, -20, -2):
                # Create temporary image with current display plus plane
                temp_image = self.current_image.copy()
                draw = ImageDraw.Draw(temp_image)
                
                # Draw simple plane shape (rectangle for now)
                plane_width = 12
                plane_height = 4
                y = 14  # Middle of display
                
                if x >= 0 and x < config.DISPLAY_WIDTH:
                    draw.rectangle(
                        [x, y, min(x + plane_width, config.DISPLAY_WIDTH-1), y + plane_height],
                        fill=plane_color
                    )
                
                # Show on matrix
                self.matrix.SetImage(temp_image.im.id, 0, 0)
                time.sleep(config.PLANE_SPEED)
            
            # Restore original image
            self.matrix.SetImage(self.current_image.im.id, 0, 0)
            
        except Exception as e:
            print "Plane animation error: " + str(e)
    
    def _scroll_text_rpi(self, text, y_pos, color):
        """Scroll text across the Raspberry Pi RGB Matrix."""
        try:
            # Create base image without the scrolling line
            base_image = self.current_image.copy()
            draw_base = ImageDraw.Draw(base_image)
            
            # Clear the line where we'll scroll
            draw_base.rectangle([0, y_pos-1, config.DISPLAY_WIDTH-1, y_pos+9], fill=(0, 0, 0))
            
            # Calculate text width (rough estimate)
            text_width = len(text) * 6  # Approximate character width
            
            # Scroll from right to left
            for x in range(config.DISPLAY_WIDTH, -text_width, -1):
                temp_image = base_image.copy()
                draw = ImageDraw.Draw(temp_image)
                draw.text((x, y_pos), text, fill=color, font=self.font)
                
                self.matrix.SetImage(temp_image.im.id, 0, 0)
                time.sleep(config.TEXT_SPEED)
            
            # Restore original image
            self.matrix.SetImage(self.current_image.im.id, 0, 0)
            
        except Exception as e:
            print "Text scrolling error: " + str(e)

    def cleanup(self):
        """Cleanup display resources."""
        self.clear_display()
        if config.PRINT_MEMORY_INFO:
            gc.collect()
            print "Memory free: %s" % gc.mem_free()

# Global instance for easy access
display_controller = DisplayController()