import bluetooth
import threading
import socket
import json
import time
import argparse

# Dictionary to store ESP32 devices and their associated player numbers
device_to_player = {}
last_event_time = {}  # Track last event time for debouncing

def send_to_event_controller(event_data, controller_host='localhost', controller_port=5555):
    """Send an event to the event controller"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((controller_host, controller_port))
        
        # Convert event to JSON and send
        event_json = json.dumps(event_data)
        client.send(event_json.encode('utf-8'))
        
        client.close()
        print(f"Event sent to controller: {event_data}")
        return True
    except Exception as e:
        print(f"Failed to send event to controller: {e}")
        return False

def handle_connection(addr, player_id, controller_host, controller_port, debounce_time):
    """Handle incoming data from a connected ESP32 device"""
    print(f"Handling connection from {addr}, assigned player ID: {player_id}")
    
    # Send the player ID to the ESP32 after connecting
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        sock.connect((addr, 1))
        player_id_msg = f"PLAYER_ID:{player_id}"
        sock.send(player_id_msg.encode())
        print(f"Sent player ID {player_id} to device {addr}")
    except Exception as e:
        print(f"Failed to send player ID to {addr}: {e}")
    
    # Now listen for incoming data
    sock.settimeout(None)  # Set to non-blocking
    last_event_time[addr] = 0  # Initialize last event time
    
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            
            current_time = time.time()
            
            # Try to parse as JSON first (preferred format)
            try:
                message = data.decode('utf-8').strip()
                event_data = json.loads(message)
                print(f"[Player {player_id+1}] Received JSON event: {event_data}")
                
                # Convert to the new universal format
                universal_event = {
                    'event_type': 'controller_input',
                    'player_id': player_id,
                    'timestamp': event_data.get('timestamp', int(current_time * 1000))
                }
                
                # Determine the action type
                event_type = event_data.get('type', '')
                event_action = event_data.get('action', '')
                
                # Map events to universal format
                if event_type == 'button' and event_action == 'press':
                    universal_event['controller_action'] = 'button'
                    universal_event['menu_action'] = 'select'
                    universal_event['game_action'] = 'action'
                elif event_type == 'tilt':
                    universal_event['controller_action'] = 'tilt'
                    if event_action == 'up':
                        universal_event['menu_action'] = 'navigate_up'
                        universal_event['game_action'] = 'move_up'
                    elif event_action == 'down':
                        universal_event['menu_action'] = 'navigate_down'
                        universal_event['game_action'] = 'move_down'
                
                # Check if debounce time has passed
                if current_time - last_event_time.get(addr, 0) > debounce_time:
                    # Send to event controller
                    print(f"Sending universal event: {universal_event}")
                    send_to_event_controller(universal_event, controller_host, controller_port)
                    last_event_time[addr] = current_time
                
            except json.JSONDecodeError:
                # If not valid JSON, try to process as pitch/sensor data
                value = data.decode('utf-8').strip()
                print(f"[Player {player_id+1}] Received raw data: {value}")
                
                # Process pitch or other sensor data
                try:
                    # Try to interpret as pitch/tilt value
                    pitch = float(value)
                    
                    # Simple algorithm to convert pitch to game actions
                    # Debounce these sensor events
                    if current_time - last_event_time.get(addr, 0) > debounce_time:
                        universal_event = {
                            'event_type': 'controller_input',
                            'player_id': player_id,
                            'controller_action': 'tilt',
                            'timestamp': int(current_time * 1000),
                            'value': pitch
                        }
                        
                        if pitch > 30:
                            universal_event['menu_action'] = 'navigate_up'
                            universal_event['game_action'] = 'move_up'
                            send_to_event_controller(universal_event, controller_host, controller_port)
                            last_event_time[addr] = current_time
                        elif pitch < -30:
                            universal_event['menu_action'] = 'navigate_down'
                            universal_event['game_action'] = 'move_down'
                            send_to_event_controller(universal_event, controller_host, controller_port)
                            last_event_time[addr] = current_time
                except ValueError:
                    # Not a number, might be a string command
                    if current_time - last_event_time.get(addr, 0) > debounce_time:
                        universal_event = {
                            'event_type': 'controller_input',
                            'player_id': player_id,
                            'timestamp': int(current_time * 1000)
                        }
                        
                        if "button" in value.lower():
                            universal_event['controller_action'] = 'button'
                            universal_event['menu_action'] = 'select'
                            universal_event['game_action'] = 'action'
                            send_to_event_controller(universal_event, controller_host, controller_port)
                            last_event_time[addr] = current_time
                        elif "up" in value.lower():
                            universal_event['controller_action'] = 'tilt'
                            universal_event['menu_action'] = 'navigate_up'
                            universal_event['game_action'] = 'move_up'
                            send_to_event_controller(universal_event, controller_host, controller_port)
                            last_event_time[addr] = current_time
                        elif "down" in value.lower():
                            universal_event['controller_action'] = 'tilt'
                            universal_event['menu_action'] = 'navigate_down'
                            universal_event['game_action'] = 'move_down'
                            send_to_event_controller(universal_event, controller_host, controller_port)
                            last_event_time[addr] = current_time
                        
        except Exception as e:
            print(f"Error handling data from {addr}: {e}")
            break
    
    sock.close()
    print(f"Connection with {addr} closed")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ESP32 Bluetooth to Event Controller Bridge")
    parser.add_argument('--host', type=str, default='localhost', help='Event controller host address')
    parser.add_argument('--port', type=int, default=5555, help='Event controller port')
    parser.add_argument('--scan-time', type=int, default=8, help='Bluetooth scan duration in seconds')
    parser.add_argument('--debounce', type=float, default=0.2, help='Debounce time for events in seconds')
    parser.add_argument('--device-name', type=str, default='ESP32_BT_Device', 
                        help='Name pattern to identify ESP32 devices')
    
    args = parser.parse_args()
    
    print(f"Scanning for {args.device_name} devices...")
    # Discover nearby Bluetooth devices
    nearby_devices = bluetooth.discover_devices(duration=args.scan_time, lookup_names=True)
    
    # Filter devices that include the ESP32 device name
    devices = [(addr, name) for addr, name in nearby_devices if args.device_name in name]
    
    if not devices:
        print(f"No {args.device_name} devices found.")
        return

    threads = []
    # Create a thread for each device, assigning player numbers 0-3
    for i, (addr, name) in enumerate(devices[:4]):  # Limit to 4 controllers (players 0-3)
        player_id = i  # Players are 0-indexed (0,1,2,3)
        print(f"Found device: {name} ({addr}) - Assigned to Player {player_id+1}")
        t = threading.Thread(target=handle_connection, 
                             args=(addr, player_id, args.host, args.port, args.debounce))
        t.daemon = True
        t.start()
        threads.append(t)

    # Keep the main thread running as long as there are active connections
    try:
        while True:
            if not any(t.is_alive() for t in threads):
                print("All connections lost. Exiting...")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
