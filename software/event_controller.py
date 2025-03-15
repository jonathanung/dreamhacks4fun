import socket
import threading
import json
import time

class EventController:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.events = []
        self.latest_events = {}  # Dictionary to track the latest event for each player
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
            if self.socket:
                self.socket.close()
        
    def _listen_for_events(self):
        """Listen for events from external programs"""
        while self.running:
            try:
                self.socket.settimeout(0.5)  # Add timeout for easier shutdown
                try:
                    client, _ = self.socket.accept()
                    data = client.recv(1024).decode('utf-8')
                    client.close()
                    
                    if data:
                        try:
                            event_data = json.loads(data)
                            print(f"Event controller received: {event_data}")  # Debug print
                            
                            with self.lock:
                                # Add to regular events list for debug/backward compatibility
                                self.events.append(event_data)
                                
                                # Store/update the latest event for this player
                                player_id = event_data.get('player_id')
                                if player_id is not None:
                                    # Add timestamp for processing management
                                    event_data['received_at'] = time.time()
                                    # Store as the latest event for this player
                                    self.latest_events[player_id] = event_data
                                    print(f"Updated latest event for player {player_id}: {event_data.get('controller_action')} - {event_data.get('raw_direction')}")
                                    
                        except json.JSONDecodeError:
                            print(f"Received invalid JSON data: {data}")
                except socket.timeout:
                    # This is expected, just continue
                    pass
            except Exception as e:
                if self.running:
                    print(f"Error in event controller: {e}")
            
            time.sleep(0.01)  # Small delay to prevent CPU hogging
    
    def peek_events(self):
        """Get current events without clearing them - useful for debugging"""
        with self.lock:
            events = self.events.copy()
        return events
    
    def get_events(self):
        """Get the current events - returns ONLY the latest event for each player"""
        with self.lock:
            current_time = time.time()
            
            # Return only the latest events (one per player)
            events = list(self.latest_events.values())
            
            # Track which events we're returning now
            for event in events:
                event['processed_at'] = current_time
            
            # Keep events list manageable size (for debug/compatibility)
            self.events = [e for e in self.events if current_time - e.get('received_at', 0) < 2.0]
            
            # Clear the latest events dictionary - will be repopulated with new events
            self.latest_events.clear()
            
        # Only log if events were found
        if events:
            print(f"Event controller returning {len(events)} events")
        return events
    
    def flush_old_events(self):
        """Remove events that have been processed for a certain amount of time"""
        current_time = time.time()
        expiration_time = 2.0  # Keep events for 2 seconds after first read
        
        with self.lock:
            # Filter out events that have been around too long
            self.events = [event for event in self.events 
                          if 'processed_at' not in event or 
                             current_time - event['processed_at'] < expiration_time]
    
    def stop(self):
        """Stop the event controller"""
        self.running = False
        if self.socket:
            self.socket.close()
