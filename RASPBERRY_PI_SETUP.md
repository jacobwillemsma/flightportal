# Raspberry Pi Setup Guide for FlightPortal

## Prerequisites on Raspberry Pi Jessie

1. **Install required packages:**
   ```bash
   sudo apt-get update
   sudo apt-get install python2.7-dev python-imaging python-imaging-dev build-essential
   ```

2. **Enable SPI (if not already enabled):**
   ```bash
   sudo raspi-config
   # Navigate to Advanced Options -> SPI -> Enable
   # Reboot when prompted
   ```

## Building the RGB Matrix Library

1. **Copy the project to your Raspberry Pi:**
   ```bash
   # From your Mac, copy the entire flightportal project (includes customized RGB matrix library):
   scp -r /Users/jacob/projects/flighty-project/flightportal pi@your-pi-ip:~/
   ```

2. **On the Raspberry Pi, build the library:**
   ```bash
   cd ~/flightportal/lib/rpi-rgb-led-matrix
   make clean && make
   ```

3. **Install the Python module:**
   ```bash
   # Copy the rgbmatrix.so to Python path
   sudo cp rgbmatrix.so /usr/lib/python2.7/dist-packages/
   
   # Or add current directory to Python path in your script
   ```

## Hardware Wiring for 2x 64x32 Chained Panels

Connect your RGB LED panels to the Raspberry Pi GPIO as follows:

| Panel Pin | RPi GPIO | Pin # | Function |
|-----------|----------|-------|----------|
| R1        | GPIO 17  | 11    | Red 1st bank |
| G1        | GPIO 18  | 12    | Green 1st bank |
| B1        | GPIO 22  | 15    | Blue 1st bank |
| R2        | GPIO 23  | 16    | Red 2nd bank |
| G2        | GPIO 24  | 18    | Green 2nd bank |
| B2        | GPIO 25  | 22    | Blue 2nd bank |
| A         | GPIO 7   | 26    | Row address A |
| B         | GPIO 8   | 24    | Row address B |
| C         | GPIO 9   | 21    | Row address C |
| D         | GPIO 10  | 19    | Row address D |
| OE-       | GPIO 2   | 3     | Output Enable |
| CLK       | GPIO 3   | 5     | Clock |
| STR       | GPIO 4   | 7     | Strobe |
| GND       | GND      | 6,9   | Ground |

**Power:** Each 64x32 panel needs ~3.5A at 5V. Use a dedicated 5V power supply with at least 7A capacity for both panels.

## Testing the Installation

1. **Test the basic library:**
   ```bash
   cd ~/flightportal/lib/rpi-rgb-led-matrix
   sudo python2.7 matrixtest.py
   ```

2. **Test FlightPortal:**
   ```bash
   cd ~/flightportal/src
   sudo python2.7 main.py
   ```

## Important Notes

- **Must run as root:** GPIO access requires root privileges (`sudo`)
- **Display size:** Your code is now configured for 128x32 (2x 64x32 chained)
- **Python version:** Use Python 2.7.9 that's already on Jessie
- **PIL library:** Use the system PIL (python-imaging) rather than Pillow

## FlightPortal Configuration

Your FlightPortal code has been updated with:

- ✅ Support for `Adafruit_RGBmatrix(32, 2)` - 32 rows, 2 chained panels
- ✅ 128x32 display resolution 
- ✅ PIL Image rendering with `matrix.SetImage()`
- ✅ Plane animations across full 128px width
- ✅ Text scrolling optimized for wider display
- ✅ Hardware-specific code paths for both MatrixPortal and Raspberry Pi

## Troubleshooting

- **Import errors:** Ensure `rgbmatrix.so` is in Python path
- **Permission errors:** Always run with `sudo`
- **Display issues:** Check wiring and power supply
- **Compilation errors:** Ensure python2.7-dev is installed

The adapted code will automatically detect Raspberry Pi hardware and use the appropriate display methods.