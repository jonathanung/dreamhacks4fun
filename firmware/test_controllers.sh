#!/bin/bash
# Script to run the ESP32 controller test

echo "=== ESP32 Controller Test ==="
echo "This script will test the connection to ESP32 controllers"
echo "and verify the player ID assignment and LED display."
echo ""

# Check if the pybluez package is installed
if ! python -c "import bluetooth" &>/dev/null; then
    echo "The 'pybluez' package is not installed."
    echo "Would you like to install it now? (y/n)"
    read -r answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        echo "Installing pybluez..."
        pip install pybluez
    else
        echo "Exiting. Please install pybluez manually and try again."
        exit 1
    fi
fi

# Default parameters
SCAN_TIME=8
DEVICE_NAME="ESP32_BT_Controller"

# Parse command line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --scan-time)
            SCAN_TIME="$2"
            shift 2
            ;;
        --device-name)
            DEVICE_NAME="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--scan-time SECONDS] [--device-name NAME]"
            exit 1
            ;;
    esac
done

echo "Starting ESP32 controller test..."
echo "Scanning for ${DEVICE_NAME} devices for ${SCAN_TIME} seconds"
echo ""

# Run the test script
python test_esp32_connection.py --scan-time "$SCAN_TIME" --device-name "$DEVICE_NAME" 