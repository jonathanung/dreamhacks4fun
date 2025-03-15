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
    """Connect to a device, process incoming data, and forward events to the controller."""
    print(f"[Player {player_id+1}] Connecting to {addr}...")
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        # Connect using RFCOMM on channel 1 (default for BluetoothSerial)
        sock.connect((addr, 1))
        print(f"[Player {player_id+1}] Connected successfully.")
        
        # Store the address-to-player mapping
        device_to_player[addr] = player_id
        last_event_time[addr] = 0
        
        while True:
            data = sock.recv(1024)  # Receive up to 1024 bytes
            if not data:
                break
                
            # Process the received data
            try:
                # Get the current time for debouncing
                current_time = time.time()
                
                # Try to parse as JSON first (preferred format)
                try:
                    message = data.decode('utf-8').strip()
                    event_data = json.loads(message)
                    print(f"[Player {player_id+1}] Received JSON event: {event_data}")
                    
                    # Add player_id to the event
                    event_data['player'] = player_id
                    
                    # Check if debounce time has passed
                    if current_time - last_event_time.get(addr, 0) > debounce_time:
                        # Send to event controller
                        send_to_event_controller(event_data, controller_host, controller_port)
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
                            if pitch > 30:
                                event = {'action': 'up', 'player': player_id, 'value': pitch}
                                send_to_event_controller(event, controller_host, controller_port)
                                last_event_time[addr] = current_time
                            elif pitch < -30:
                                event = {'action': 'down', 'player': player_id, 'value': pitch}
                                send_to_event_controller(event, controller_host, controller_port)
                                last_event_time[addr] = current_time
                    except ValueError:
                        # Not a number, might be a string command
                        if "button" in value.lower():
                            if current_time - last_event_time.get(addr, 0) > debounce_time:
                                event = {'action': 'select', 'player': player_id}
                                send_to_event_controller(event, controller_host, controller_port)
                                last_event_time[addr] = current_time
                        elif "up" in value.lower():
                            if current_time - last_event_time.get(addr, 0) > debounce_time:
                                event = {'action': 'up', 'player': player_id}
                                send_to_event_controller(event, controller_host, controller_port)
                                last_event_time[addr] = current_time
                        elif "down" in value.lower():
                            if current_time - last_event_time.get(addr, 0) > debounce_time:
                                event = {'action': 'down', 'player': player_id}
                                send_to_event_controller(event, controller_host, controller_port)
                                last_event_time[addr] = current_time
            
            except Exception as e:
                print(f"[Player {player_id+1}] Error processing data: {e}")
    
    except Exception as e:
        print(f"[Player {player_id+1}] Connection error: {e}")
    finally:
        sock.close()
        print(f"[Player {player_id+1}] Disconnected.")
        if addr in device_to_player:
            del device_to_player[addr]
        if addr in last_event_time:
            del last_event_time[addr]

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
