import socket
import json
import time

def send_test_event(action, host='localhost', port=5555):
    """Send a test event to the game's event controller"""
    event = {
        'action': action,
        'timestamp': time.time(),
        'data': 'Test event'
    }
    
    try:
        # Create socket connection
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        
        # Convert event to JSON and send
        event_json = json.dumps(event)
        client.send(event_json.encode('utf-8'))
        
        client.close()
        print(f"Test event sent: {event}")
        return True
    except Exception as e:
        print(f"Failed to send test event: {e}")
        return False

if __name__ == "__main__":
    print("Testing connection to game event controller...")
    print("Make sure your game is running!")
    
    # Try to send a 'down' event
    print("\nSending 'down' event...")
    success = send_test_event('down')
    
    if success:
        print("Event sent successfully. Did the menu selection move down?")
    else:
        print("Failed to send event. Is your game running with the event controller?")
    
    # Wait a bit
    time.sleep(2)
    
    # Try to send an 'up' event
    print("\nSending 'up' event...")
    success = send_test_event('up')
    
    if success:
        print("Event sent successfully. Did the menu selection move up?")
    else:
        print("Failed to send event. Is your game running with the event controller?")
