# FlightPortal Deployment Guide

curl -O https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh

## For Development/Testing

### 1. Setup Environment

```bash
# Clone/download the project
cd flightportal

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Secrets

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual WiFi credentials
# WIFI_SSID=your_network_name
# WIFI_PASSWORD=your_password
```

### 3. Run the Application

```bash
# Run tests
python test/test_new_structure.py

# Run application (test mode)
python run.py
```

## For MatrixPortal Device

### 1. Prepare the Device

- Install CircuitPython 8.x on your MatrixPortal
- Connect to your computer via USB

### 2. Copy Files to Device

Copy these files from `src/` to the root of the CIRCUITPY drive:

**Required files:**

- `main.py` → rename to `code.py` (CircuitPython convention)
- `config.py`
- `flight_logic.py`
- `display_controller.py`
- `lga_client.py`
- `env_loader.py`

### 3. Create Secrets on Device

Create a file called `.env` on the CIRCUITPY drive:

```
# WiFi Configuration
WIFI_SSID=your_actual_network_name
WIFI_PASSWORD=your_actual_wifi_password

# Optional: Debug settings
DEBUG_MODE=false
PRINT_MEMORY_INFO=false
```

### 4. Device File Structure

Your CIRCUITPY drive should look like:

```
CIRCUITPY/
├── code.py              # (renamed from main.py)
├── config.py
├── flight_logic.py
├── display_controller.py
├── lga_client.py
├── env_loader.py
├── .env                 # Your WiFi secrets
└── lib/                 # CircuitPython libraries (if needed)
```

### 5. Verify Installation

- The device should automatically restart and run the code
- Check the serial console for any error messages
- The display should show either flight data (RWY04 active) or weather info

## Environment Variables

### Required

- `WIFI_SSID` - Your WiFi network name
- `WIFI_PASSWORD` - Your WiFi password

### Optional

- `DEBUG_MODE` - Enable debug logging (true/false)
- `PRINT_MEMORY_INFO` - Show memory usage (true/false)

## Troubleshooting

### Common Issues

**1. WiFi Connection Fails**

- Check SSID and password in `.env`
- Ensure network is 2.4GHz (MatrixPortal doesn't support 5GHz)
- Check signal strength

**2. Import Errors**

- Ensure all required files are copied to the device
- Check that files are not corrupted during transfer

**3. API Errors**

- Device needs internet connection
- Check firewall settings
- FlightRadar24 APIs may have rate limits

**4. Display Issues**

- Check power supply (MatrixPortal needs adequate power)
- Verify LED matrix connections
- Check for hardware initialization errors in serial console

### Debug Mode

Enable debug mode by setting `DEBUG_MODE=true` in your `.env` file for more detailed logging.

## Security Notes

- ✅ **WiFi credentials** are now stored in `.env` (not in code)
- ✅ **`.env` file** is excluded from git (in .gitignore)
- ✅ **Use `.env.example`** as a template for new deployments
- ⚠️ **Never commit** the actual `.env` file to version control

## Updates

To update the application:

1. Pull latest code changes
2. Copy updated files to CIRCUITPY drive
3. Device will automatically restart with new code
