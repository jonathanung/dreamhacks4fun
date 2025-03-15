#!/usr/bin/env python3
"""
ESP32 Event Controller - Connects to multiple ESP32 devices via serial ports
and forwards their events to the Event Controller using individual connections.
Supports both menu navigation and game controls with appropriate thresholds.
"""

import serial
import serial.tools.list_ports
import json
import socket
import time
import argparse
import threading
import sys

class ESP32SerialToEventBridge:
    def __init__(self, host='localhost', port=5555, baud=115200, debug=False):
        self.host = host
        self.port = port
        self.baud_rate = baud
        self.debug = debug
        self.controllers = []
        self.threads = []
        self.running = False
        
        # Track last event times for rate limiting
        self.last_event_time = {}  # {player_id: {"button": timestamp, "tilt_up": timestamp, "tilt_down": timestamp}}
        
        # Track last direction sent for each player
        self.last_direction = {}  # {player_id: {"vertical": "up/down/none"}}
        
        # Timeout to send stop events (effectively disabled with extremely high value)
        self.tilt_timeout = 999999.0  # Essentially never timeout
        
        # Set all thresholds to 0 to disable rate limiting (let programs handle their own rate limiting)
        self.thresholds = {
            "menu": {
                "tilt_up": 0,     # No delay between menu up navigations
                "tilt_down": 0,   # No delay between menu down navigations
                "button": 0       # No delay between menu selections
            },
            "game": {
                "tilt_up": 0,     # No delay between game movements
                "tilt_down": 0,   # No delay between game movements
                "button": 0       # No delay between button actions
            }
        }
        
    def _send_to_event_controller(self, event):
        """Send event to the event controller using a new connection for each event."""
        try:
            # Create a new socket for this event
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # 2 second timeout
            sock.connect((self.host, self.port))
            
            # Send the event without adding a newline character
            sock.sendall(event.encode())
            
            # Close the socket immediately
            sock.close()
            
            if self.debug:
                print(f"Sent event: {event}")
            return True
        except Exception as e:
            print(f"Failed to send event: {e}")
            return False
    
    def _create_generic_controller_event(self, action_type, direction, player_id, angle=None):
        """
        Create a generic controller event that works in multiple contexts.
        
        This is the key to making the controller work across different games and menus.
        Each event contains both raw control info and contextual actions.
        The games/menu can choose which fields to use based on context.
        """
        timestamp = time.time()
        
        # Ensure player_id is an integer
        player_id = int(player_id)
        
        # Base event with all necessary information
        event = {
            "timestamp": timestamp,
            "player_id": player_id,
            "event_source": f"esp32_{player_id}",
            
            # Raw controller action (always included)
            "controller_action": action_type,  # "tilt" or "button"
            
            # Include direction for tilt actions
            "raw_direction": direction if action_type == "tilt" else None,
            
            # Include angle for tilt actions
            "angle": angle if action_type == "tilt" else None,
        }
        
        # Add contextual interpretations of the action
        if action_type == "tilt":
            if direction == "up":
                # For menus: navigate up, for games: move paddle/player up
                event["menu_action"] = "navigate_up"
                event["game_action"] = "move_up"
                event["event_type"] = "controller_input"  # Generic type
                
            elif direction == "down":
                # For menus: navigate down, for games: move paddle/player down
                event["menu_action"] = "navigate_down"
                event["game_action"] = "move_down"
                event["event_type"] = "controller_input"  # Generic type
                
            elif direction == "stop":
                # Special stop event
                event["menu_action"] = "stop"
                event["game_action"] = "stop_vertical"
                event["event_type"] = "controller_input"  # Generic type
        
        elif action_type == "button":
            # For menus: select item, for games: action/fire
            event["menu_action"] = "select"
            event["game_action"] = "action"
            event["event_type"] = "controller_input"  # Generic type
            
        return json.dumps(event)
            
    def _map_to_game_event(self, esp32_event, player_id):
        """Map ESP32 event to a generic game event format that works for multiple contexts."""
        try:
            # Parse the event data
            event_data = json.loads(esp32_event)
            
            # Handle based on event type
            if event_data.get("type") == "button":
                # Create button event
                event = self._create_generic_controller_event("button", None, player_id)
                return event
                
            elif event_data.get("type") == "tilt":
                action = event_data.get("action")
                angle = event_data.get("angle", 0)
                
                if action == "up":
                    # Movement up event
                    return self._create_generic_controller_event("tilt", "up", player_id, angle)
                        
                elif action == "down":
                    # Movement down event
                    return self._create_generic_controller_event("tilt", "down", player_id, angle)
                
                elif action == "stop":
                    # Stop event from deadzone
                    return self._create_generic_controller_event("tilt", "stop", player_id, angle)
                
                print(f"WARNING: Unrecognized tilt action: {action}")
                return None
                        
            # Other events 
            print(f"Unhandled ESP32 event type: {event_data.get('type')}")
            return None
                
        except json.JSONDecodeError:
            print(f"Non-JSON data received from player {player_id}: {esp32_event}")
            # For non-JSON data, create a simple raw event
            return json.dumps({
                "timestamp": time.time(),
                "event_type": "esp32_raw",
                "player_id": player_id,
                "event_source": f"esp32_{player_id}",
                "data": esp32_event
            })
        
    def _handle_esp32_serial(self, serial_port, player_id):
        """Handle events from a single ESP32 device."""
        try:
            port_name = serial_port.port
            print(f"Starting event handling for Player {player_id} on {port_name}")
            
            # Send player ID to ESP32 for LED display
            player_id_message = f"PLAYER_ID:{player_id}\n"
            serial_port.write(player_id_message.encode('utf-8'))
            
            while self.running:
                if serial_port.in_waiting:
                    try:
                        line = serial_port.readline().decode('utf-8').strip()
                        if not line:
                            continue
                            
                        # Map and forward the event
                        game_event = self._map_to_game_event(line, player_id)
                        
                        # Only send if we have a valid event (not None)
                        if game_event:
                            self._send_to_event_controller(game_event)
                            
                    except UnicodeDecodeError:
                        print(f"Player {player_id}: Decode error")
                        continue
                time.sleep(0.01)  # Small delay to prevent CPU hogging
                
        except Exception as e:
            print(f"Error in ESP32 handler for Player {player_id}: {e}")
        finally:
            try:
                serial_port.close()
            except:
                pass
            print(f"Connection closed for Player {player_id}")
    
    def scan_for_esp32_devices(self):
        """Scan for ESP32 devices connected via USB serial."""
        print("Scanning for ESP32 devices...")
        ports = list(serial.tools.list_ports.comports())
        esp32_ports = []
        
        for port in ports:
            # Look for ESP32 in the description or hardware ID
            if 'CP210' in port.description or 'SLAB_USBtoUART' in port.description or 'ESP32' in port.description:
                print(f"Found potential ESP32 device: {port.device} - {port.description}")
                esp32_ports.append(port.device)
            elif self.debug:
                print(f"Skipping non-ESP32 device: {port.device} - {port.description}")
        
        return esp32_ports
    
    def connect_to_esp32_devices(self, ports=None, specified_ports=None):
        """
        Connect to ESP32 devices.
        
        Args:
            ports: If provided, use these ports instead of scanning
            specified_ports: List of explicitly specified ports to use
        """
        if specified_ports:
            # Use explicitly specified ports
            device_ports = specified_ports
        elif ports:
            # Use provided ports
            device_ports = ports
        else:
            # Scan for ports
            device_ports = self.scan_for_esp32_devices()
        
        if not device_ports:
            print("No ESP32 devices found. Please check connections.")
            return False
        
        print(f"Connecting to {len(device_ports)} ESP32 device(s)...")
        
        for i, port_name in enumerate(device_ports):
            try:
                ser = serial.Serial(port_name, self.baud_rate, timeout=1)
                player_id = i  # Assign sequential player IDs (0-based)
                
                # Display the player ID LED pattern for reference
                led_pattern = "unknown"
                if player_id == 0:
                    led_pattern = "Left LED (LED1) on"
                elif player_id == 1:
                    led_pattern = "Right LED (LED2) on"
                elif player_id == 2:
                    led_pattern = "Both LEDs on"
                elif player_id == 3:
                    led_pattern = "Built-in LED on"
                
                print(f"Connected to ESP32 on {port_name} as Player {player_id} - {led_pattern}")
                self.controllers.append((ser, player_id))
            except Exception as e:
                print(f"Failed to connect to ESP32 on {port_name}: {e}")
        
        return len(self.controllers) > 0
    
    def start(self):
        """Start the ESP32 event bridge."""
        self.running = True
        
        # Test connection to event controller
        test_event = json.dumps({
            "event_type": "esp32_bridge_start",
            "timestamp": time.time()
        })
        
        if not self._send_to_event_controller(test_event):
            print("WARNING: Could not connect to event controller. Events may not be processed.")
            print("Make sure your game is running.")
        else:
            print("Successfully connected to event controller")
        
        # Start handler threads for each controller
        for ser, player_id in self.controllers:
            thread = threading.Thread(
                target=self._handle_esp32_serial,
                args=(ser, player_id),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
        
        print(f"ESP32 Serial to Event Bridge running with {len(self.controllers)} controller(s)")
        return True
    
    def stop(self):
        """Stop the ESP32 event bridge."""
        self.running = False
        
        # Close all serial connections
        for ser, _ in self.controllers:
            try:
                ser.close()
            except:
                pass
        
        print("ESP32 Serial to Event Bridge stopped")

def main():
    parser = argparse.ArgumentParser(description='ESP32 Serial to Event Controller Bridge')
    parser.add_argument('--host', default='localhost', help='Event controller host')
    parser.add_argument('--port', type=int, default=5555, help='Event controller port')
    parser.add_argument('--baud', type=int, default=115200, help='Serial baud rate')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--scan', action='store_true', help='Scan for ESP32 devices and exit')
    parser.add_argument('--device', action='append', help='Specify ESP32 device port (can be used multiple times)')
    parser.add_argument('--menu-threshold', type=float, default=0, 
                        help='Threshold time in seconds between menu actions (default: 0, disabled)')
    parser.add_argument('--game-threshold', type=float, default=0, 
                        help='Threshold time in seconds between game actions (default: 0, disabled)')
    
    args = parser.parse_args()
    
    bridge = ESP32SerialToEventBridge(
        host=args.host,
        port=args.port,
        baud=args.baud,
        debug=args.debug
    )
    
    # Set custom thresholds from command line (defaults to 0 = disabled)
    if args.menu_threshold:
        bridge.thresholds["menu"]["tilt_up"] = args.menu_threshold
        bridge.thresholds["menu"]["tilt_down"] = args.menu_threshold
        bridge.thresholds["menu"]["button"] = args.menu_threshold
        
    if args.game_threshold:
        bridge.thresholds["game"]["tilt_up"] = args.game_threshold
        bridge.thresholds["game"]["tilt_down"] = args.game_threshold
    
    if args.scan:
        # Just scan for devices and exit
        devices = bridge.scan_for_esp32_devices()
        if devices:
            print("\nFound ESP32 devices:")
            for i, device in enumerate(devices):
                print(f"  Player {i}: {device}")
        else:
            print("No ESP32 devices found.")
        return
    
    # Connect to specified devices or scan
    if args.device:
        print(f"Using specified devices: {args.device}")
        bridge.connect_to_esp32_devices(specified_ports=args.device)
    else:
        bridge.connect_to_esp32_devices()
    
    if not bridge.controllers:
        print("No ESP32 controllers connected. Exiting.")
        return
    
    try:
        if bridge.start():
            print("\nController LED Status:")
            for i, (_, player_id) in enumerate(bridge.controllers):
                if player_id == 0:
                    print(f"  Player {player_id}: Left LED on")
                elif player_id == 1:
                    print(f"  Player {player_id}: Right LED on")
                elif player_id == 2:
                    print(f"  Player {player_id}: Both LEDs on")
                elif player_id == 3:
                    print(f"  Player {player_id}: Built-in LED on")
            
            print("\nUniversal Controller Setup:")
            print("  • Tilt Up: Menu navigation up / Game movement up")
            print("  • Tilt Down: Menu navigation down / Game movement down")
            print("  • Button Press: Menu select / Game action")
            print(f"  • Menu thresholds: {bridge.thresholds['menu']['tilt_up']:.3f}s (0 = disabled, all events will pass through)")
            print(f"  • Game thresholds: {bridge.thresholds['game']['tilt_up']:.3f}s (0 = disabled, all events will pass through)")
            
            print("\nPress Ctrl+C to stop")
            # Keep the main thread alive
            while bridge.running:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        bridge.stop()

if __name__ == "__main__":
    main()