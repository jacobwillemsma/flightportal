# FlightPortal
Project for displaying the details of planes overhead on LED matrix displays

(video sped up to make the file fit, the speeds and delays are configurable anyway)

https://user-images.githubusercontent.com/103124527/206902629-1f31bd41-d8a8-415e-a35a-625efb20b3d6.MOV

**FlightPortal** supports two hardware platforms:
1. **Adafruit MatrixPortal** with 64x32 LED/RGB Matrix (original implementation)
2. **Raspberry Pi** with RGB LED matrices (supports chaining for larger displays)

Uses FlightRadar24 API-style scraping to display flight details passing overhead. That code being unofficial, it may break at any time!

## Hardware Options

### Option 1: Adafruit MatrixPortal (Original)

You will need:
1. A MatrixPortal (https://www.adafruit.com/product/4745)
2. A P4, 64x32 RGB matrix panel (I get mine from Aliexpress)
3. The case I designed (https://www.thingiverse.com/thing:5701517)
4. An adafruit acrylic diffuser (https://www.adafruit.com/product/4749) - available various places
5. 6 M3 screws (sorry, said M5 before but was looking at the wrong ones, my bad. Think mine are 8mm long, little bit more would be OK, shorter probably a problem)
6. Optional: Uglu dashes to stick the diffuser on, the case holds mine on pretty well though (https://www.protapes.com/products/uglu-600-dashes-sheets)

### Option 2: Raspberry Pi with RGB LED Matrix

You will need:
1. Raspberry Pi (any model with GPIO pins)
2. RGB LED Matrix panels (32x32, 64x32, or chained configurations supported)
3. 5V power supply (3.5A per 32x32 panel)
4. Proper wiring connections (see `RASPBERRY_PI_SETUP.md` for GPIO pinout)

**Advantages of Raspberry Pi version:**
- Support for larger displays (chaining multiple panels)
- More processing power for complex animations
- Better networking capabilities
- Easier development and debugging

## Setup Instructions

### MatrixPortal Setup
Prep the portal as detailed here (https://learn.adafruit.com/adafruit-matrixportal-m4/prep-the-matrixportal), put the code and secrets files on, put your wifi details and the geo box you want to search in the secrets file, and you should be good to go!

### Raspberry Pi Setup
See `RASPBERRY_PI_SETUP.md` for complete installation instructions including:
- Building the RGB matrix library
- GPIO wiring diagrams  
- Python dependencies
- Testing procedures

## Project Structure

```
flightportal/
├── src/                    # Main FlightPortal code
│   ├── main.py            # Entry point
│   ├── display_controller.py  # Hardware abstraction layer
│   ├── config.py          # Configuration settings
│   ├── flight_logic.py    # Flight tracking logic
│   └── lga_client.py      # FlightRadar24 API client
├── lib/                   # Hardware dependencies
│   └── rpi-rgb-led-matrix/    # RGB Matrix library for Raspberry Pi
├── test/                  # Test files
├── RASPBERRY_PI_SETUP.md  # Raspberry Pi installation guide
└── README.md              # This file
```

## Configuration

If you'd like to change the layout, colours or the flight info displayed, all that is pretty configurable. Have a look at `src/config.py` for display settings and `src/main.py` for the main logic. The comments should be fairly self-explanatory if you're comfortable with Python.

The libaries it needs are I think all part of the recommended prep above, but for info they are:

- adafruit_fakerequests
- adafruit_requests
- adafruit_bitmap_font
- adafruit_io
- adafruit_matrixportal
- adafruit_minimqtt
- adafruit_display_text
- adafruit_portalbase

For power, the easiest thing is to use the cable that came with your matrix panel, as long as it has two prongs that go to the screws on the matrixportal. All that's needed is for the portal to connect to the power port on the panel - we're not using much power here (I clock it at about 2w). Any decent usb power supply connected to the portal should do it.

![IMG-2179](https://user-images.githubusercontent.com/103124527/208709167-dd4b6ff2-4c80-4e38-840f-e5b958e2ed78.jpg)

I soldered a connection straight onto the panel's power port as below, for neatness, but that's completely optional. 

![IMG_2125](https://user-images.githubusercontent.com/103124527/206903066-7af5c076-101e-4598-b3ba-0f64766e4162.jpg)
![IMG_2126_small](https://user-images.githubusercontent.com/103124527/206903084-42378ce0-b8d8-4810-a18a-f35b9a509752.jpg)
![IMG_2127_small](https://user-images.githubusercontent.com/103124527/206903089-16d0f7f7-2dc0-4082-a012-0e1c9999a63a.jpg)
![IMG_2128_small](https://user-images.githubusercontent.com/103124527/206903092-0a131b80-cd20-4c8c-b892-9b0a5c1d544b.jpg)

For debugging, use putty or similar, see what COM port the portal is on (device manager in windows will show you), and run a serial connection to that port at 115200. It should print out helpful messages about errors, flights it sees, etc. You can also paste the URLs you see in the code into a browser and check you can find flights, etc.
