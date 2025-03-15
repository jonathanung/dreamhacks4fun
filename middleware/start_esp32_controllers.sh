#!/bin/bash
# Script to start multiple ESP32 controllers

# Default settings
HOST="localhost"
PORT=5555
BAUD=115200
DEBUG=false
SCAN_ONLY=false
MENU_THRESHOLD=0.333
GAME_THRESHOLD=0.05
DEVICES=()

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --baud)
            BAUD="$2"
            shift 2
            ;;
        --device)
            DEVICES+=("$2")
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --scan)
            SCAN_ONLY=true
            shift
            ;;
        --menu-threshold)
            MENU_THRESHOLD="$2"
            shift 2
            ;;
        --game-threshold)
            GAME_THRESHOLD="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--host HOST] [--port PORT] [--baud BAUD] [--device PORT] [--debug] [--scan] [--menu-threshold VALUE] [--game-threshold VALUE]"
            exit 1
            ;;
    esac
done

echo "=== ESP32 Serial Event Controller Bridge ==="
echo "Event Controller: $HOST:$PORT"
echo "Baud Rate: $BAUD"
echo "Menu Threshold: ${MENU_THRESHOLD}s"
echo "Game Threshold: ${GAME_THRESHOLD}s"

# Build the command
CMD="python3 $(dirname "$0")/esp32_eventcontroller.py --host $HOST --port $PORT --baud $BAUD --menu-threshold $MENU_THRESHOLD --game-threshold $GAME_THRESHOLD"

if [ "$DEBUG" = true ]; then
    CMD="$CMD --debug"
fi

if [ "$SCAN_ONLY" = true ]; then
    CMD="$CMD --scan"
fi

for device in "${DEVICES[@]}"; do
    CMD="$CMD --device $device"
done

echo ""
echo "Player ID LED Configuration:"
echo "  Player 0: Left LED (LED1) on"
echo "  Player 1: Right LED (LED2) on"
echo "  Player 2: Both LEDs on"
echo "  Player 3: Built-in LED on"
echo ""

echo "Universal Controller Setup:"
echo "  • Tilt Up: Menu navigation up / Game movement up"
echo "  • Tilt Down: Menu navigation down / Game movement down"
echo "  • Button Press: Menu select / Game action"

# Run the command
echo "Starting ESP32 controller bridge..."
$CMD 