#!/bin/bash
# Start the ESP32 Bluetooth to Event Controller Bridge

# Default parameters
HOST="localhost"
PORT="5555"
SCAN_TIME="8"
DEBOUNCE="0.2"
DEVICE_NAME="ESP32_BT_Controller"

# Parse command line arguments
while getopts ":h:p:s:d:n:" opt; do
  case $opt in
    h) HOST="$OPTARG" ;;
    p) PORT="$OPTARG" ;;
    s) SCAN_TIME="$OPTARG" ;;
    d) DEBOUNCE="$OPTARG" ;;
    n) DEVICE_NAME="$OPTARG" ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

echo "Starting ESP32 Bluetooth Controllers Bridge..."
echo "Scanning for devices matching: $DEVICE_NAME"
echo "Connect to event controller at: $HOST:$PORT"

# Run the ESPtoPC.py script with the specified parameters
python3 firmware/ESPtoPC.py \
  --host "$HOST" \
  --port "$PORT" \
  --scan-time "$SCAN_TIME" \
  --debounce "$DEBOUNCE" \
  --device-name "$DEVICE_NAME" 