import bluetooth
import threading

def handle_connection(addr):
    """Connect to a device and print incoming pitch data."""
    print(f"[{addr}] Attempting connection...")
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        # Connect using RFCOMM on channel 1 (default for BluetoothSerial)
        sock.connect((addr, 1))
        print(f"[{addr}] Connected successfully.")
        while True:
            data = sock.recv(1024)  # Receive up to 1024 bytes
            if not data:
                break
            # Assuming the data is sent as a UTF-8 string
            pitch = data.decode('utf-8').strip()
            print(f"[{addr}] Pitch: {pitch}°")
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
    # Create a thread for each device
    for addr, name in devices:
        print(f"Found device: {name} ({addr})")
        t = threading.Thread(target=handle_connection, args=(addr,))
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
