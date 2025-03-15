import serial
import socket
import json
import time
import threading
import argparse

class ESP32SerialToEventBridge:
    def __init__(self, serial_port='/dev/ttyUSB0', serial_baudrate=115200, 
                 controller_host='localhost', controller_port=5555):
        # Serial connection to ESP32
        self.serial_port = serial_port
        self.serial_baudrate = serial_baudrate
        self.serial_connection = None
        
        # Socket connection to EventController
        self.controller_host = controller_host
        self.controller_port = controller_port
        
        # Control flags
        self.running = False
    
    def start(self):
        """Start the bridge between ESP32 and EventController"""
        try:
            # Connect to ESP32 via serial
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.serial_baudrate,
                timeout=1
            )
            
            # Start monitoring thread
            self.running = True
            self.thread = threading.Thread(target=self._monitor_serial)
            self.thread.daemon = True
            self.thread.start()
            
            print(f"ESP32 bridge started - listening on {self.serial_port} and forwarding to {self.controller_host}:{self.controller_port}")
            
        except Exception as e:
            print(f"Failed to start ESP32 bridge: {e}")
            if hasattr(self, 'serial_connection') and self.serial_connection:
                self.serial_connection.close()
    
    def _monitor_serial(self):
        """Monitor serial port for events and forward them to EventController"""
        while self.running:
            try:
                # Check for data from ESP32
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line:
                        print(f"Received from ESP32: {line}")
                        
                        # Parse and format event
                        event_data = self._parse_esp32_event(line)
                        if event_data:
                            # Map ESP32 event to game event format
                            game_event = self._map_to_game_event(event_data)
                            
                            # Send to EventController
                            self._send_to_controller(game_event)
            
            except Exception as e:
                print(f"Error in serial monitoring: {e}")
            
            time.sleep(0.01)  # Small delay to prevent CPU hogging
    
    def _parse_esp32_event(self, line):
        """Parse ESP32 output into event format"""
        print("event line: ", line)
        try:
            # Try parsing as JSON first
            return json.loads(line)
        except json.JSONDecodeError:
            # If not JSON, try simple parsing
            if line.startswith("EVENT:"):
                parts = line[6:].split(":", 1)
                event_type = parts[0] if len(parts) > 1 else "generic"
                event_data = parts[1] if len(parts) > 1 else line[6:]
                
                return {
                    "type": event_type,
                    "data": event_data,
                    "timestamp": time.time()
                }
            elif ":" in line:  # Simple key:value format
                key, value = line.split(":", 1)
                return {
                    "type": key.strip(),
                    "data": value.strip(),
                    "timestamp": time.time()
                }
            else:
                # Default format for plain text
                return {
                    "type": "message",
                    "data": line,
                    "timestamp": time.time()
                }
    
    def _map_to_game_event(self, esp32_event):
        """Map ESP32 event format to game event controller format"""
        # Default event structure for the game
        game_event = {
            "action": "unknown",
            "timestamp": time.time()
        }
        
        # Map ESP32 events to game events
        if esp32_event.get("type") == "button":
            # Direct mapping for button actions
            if "action" in esp32_event:
                game_event["action"] = esp32_event["action"]
            # Legacy format support
            elif "data" in esp32_event:
                data = esp32_event["data"].lower()
                if "up" in data:
                    game_event["action"] = "up"
                elif "down" in data:
                    game_event["action"] = "down"
                elif "select" in data:
                    game_event["action"] = "select"
        
        # Add any additional data from the ESP32 event
        if "data" in esp32_event:
            game_event["data"] = esp32_event["data"]
        
        return game_event
    
    def _send_to_controller(self, event_data):
        """Send event data to EventController via socket"""
        try:
            # Create socket connection
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.controller_host, self.controller_port))
            
            # Convert event to JSON and send
            event_json = json.dumps(event_data)
            client.send(event_json.encode('utf-8'))
            
            client.close()
            print(f"Event sent to controller: {event_data}")
            
        except Exception as e:
            print(f"Failed to send event to controller: {e}")
    
    def stop(self):
        """Stop the bridge"""
        self.running = False
        if hasattr(self, 'serial_connection') and self.serial_connection:
            self.serial_connection.close()
        print("ESP32 bridge stopped")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ESP32 Serial to Event Controller Bridge')
    parser.add_argument('--port', type=str, default='COM3', 
                        help='Serial port for ESP32 (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)')
    parser.add_argument('--baud', type=int, default=115200, 
                        help='Baud rate for serial communication')
    parser.add_argument('--host', type=str, default='localhost', 
                        help='Host address for the event controller')
    parser.add_argument('--controller-port', type=int, default=5555, 
                        help='Port for the event controller')
    
    args = parser.parse_args()
    
    # Configure with command line arguments
    bridge = ESP32SerialToEventBridge(
        serial_port=args.port,
        serial_baudrate=args.baud,
        controller_host=args.host,
        controller_port=args.controller_port
    )
    
    # Start the bridge
    bridge.start()
    
    # Keep the program running until interrupted
    try:
        print("Bridge running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        bridge.stop()
        print("Program terminated")