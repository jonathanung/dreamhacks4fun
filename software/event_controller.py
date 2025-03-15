import socket
import threading
import json

class EventController:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.events = []
        self.lock = threading.Lock()
    
    def start(self):
        """Start the event controller server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            self.running = True
            
            # Start listening thread
            self.thread = threading.Thread(target=self._listen_for_events)
            self.thread.daemon = True
            self.thread.start()
            print(f"Event controller started on {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to start event controller: {e}")
            self.socket.close()
        
    def _listen_for_events(self):
        """Listen for events from external programs"""
        while self.running:
            try:
                client, _ = self.socket.accept()
                data = client.recv(1024).decode('utf-8')
                client.close()
                
                if data:
                    try:
                        event_data = json.loads(data)
                        with self.lock:
                            self.events.append(event_data)
                    except json.JSONDecodeError:
                        print("Received invalid JSON data")
            except Exception as e:
                if self.running:
                    print(f"Error in event controller: {e}")
    
    def get_events(self):
        """Get and clear the current events"""
        with self.lock:
            events = self.events.copy()
            self.events.clear()
        return events
    
    def stop(self):
        """Stop the event controller"""
        self.running = False
        if self.socket:
            self.socket.close()
