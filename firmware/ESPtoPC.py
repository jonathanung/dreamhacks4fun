import bluetooth
import threading

# Global dictionary to map device addresses to IDs
device_ids = {}

def handle_connection(addr, device_id):
    """Connect to a device, send its assigned ID, and print incoming pitch data."""
    print(f"[{addr}] Attempting connection...")
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        # Connect using RFCOMM on channel 1 (default for BluetoothSerial)
        sock.connect((addr, 1))
        print(f"[{addr}] Connected successfully with assigned ID {device_id}.")
        
        # Broadcast the assigned ID to the ESP32
        id_message = f"Your ID is {device_id}\n"
        sock.send(id_message)
        print(f"[{addr}] Sent ID message: {id_message.strip()}")

        while True:
            data = sock.recv(1024)  # Receive up to 1024 bytes
            if not data:
                break
            # Assuming the data is sent as a UTF-8 string
            pitch = data.decode('utf-8').strip()
            print(f"[ID {device_id} | {addr}] Pitch: {pitch}°")
    except Exception as e:
        print(f"[{addr}] Connection error: {e}")
    finally:
        sock.close()
        print(f"[{addr}] Disconnected.")

def main():
    print("Scanning for ESP32_BT_Device devices...")
    # Discover nearby Bluetooth devices (8-second scan)
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
    
    # Filter devices that include the ESP32 device name
    devices = [(addr, name) for addr, name in nearby_devices if "ESP32_BT_Device" in name]
    
    if not devices:
        print("No ESP32_BT_Device devices found.")
        return

    threads = []
    # Assign an ID to each discovered device in the order they are found
    for i, (addr, name) in enumerate(devices):
        device_ids[addr] = i
        print(f"Found device: {name} ({addr}) assigned ID {i}")
        t = threading.Thread(target=handle_connection, args=(addr, i))
        t.daemon = True
        t.start()
        threads.append(t)

    # Keep the main thread running as long as there are active connections
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == '__main__':
    main()
