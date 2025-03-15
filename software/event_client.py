# event_client.py - Client for sending events to the event controller
import socket
import json
import time

def send_event(action, player=None, host='localhost', port=5555, **kwargs):
    """
    Send an event to the event controller
    
    Args:
        action (str): The action to perform (e.g., 'up', 'down', 'select', 'hit')
        player (int): Player number (0-3), optional
        host (str): The host address of the event controller
        port (int): The port of the event controller
        **kwargs: Additional parameters to include in the event
    
    Returns:
        bool: True if the event was sent successfully, False otherwise
    """
    event = {'action': action}
    
    # Add player if specified
    if player is not None:
        event['player'] = player
    
    # Add any additional parameters
    for key, value in kwargs.items():
        event[key] = value
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall(json.dumps(event).encode('utf-8'))
        s.close()
        return True
    except Exception as e:
        print(f"Failed to send event: {e}")
        return False

# Specific event functions for pong
def pong_move_up(player=0, host='localhost', port=5555):
    """Move a player's paddle up (for left/right paddles) or left (for top/bottom paddles)"""
    action = 'up' if player in [1, 3] else 'left'
    return send_event(action, player, host, port)

def pong_move_down(player=0, host='localhost', port=5555):
    """Move a player's paddle down (for left/right paddles) or right (for top/bottom paddles)"""
    action = 'down' if player in [1, 3] else 'right'
    return send_event(action, player, host, port)

def pong_hit(player=0, host='localhost', port=5555):
    """Make a player's paddle hit the ball"""
    return send_event('hit', player, host, port)

# Example usage
if __name__ == "__main__":
    print("Pong Event Client")
    print("1. Player 1 (Top) move left")
    print("2. Player 1 (Top) move right")
    print("3. Player 1 (Top) hit")
    print("4. Player 2 (Right) move up")
    print("5. Player 2 (Right) move down")
    print("6. Player 2 (Right) hit")
    print("7. Exit")
    
    while True:
        choice = input("Enter choice: ")
        
        if choice == '1':
            pong_move_up(0)
            print("Sent: Player 1 move left")
        elif choice == '2':
            pong_move_down(0)
            print("Sent: Player 1 move right")
        elif choice == '3':
            pong_hit(0)
            print("Sent: Player 1 hit")
        elif choice == '4':
            pong_move_up(1)
            print("Sent: Player 2 move up")
        elif choice == '5':
            pong_move_down(1)
            print("Sent: Player 2 move down")
        elif choice == '6':
            pong_hit(1)
            print("Sent: Player 2 hit")
        elif choice == '7':
            break
        else:
            print("Invalid choice")
        
        time.sleep(0.1)  # Slight delay between events 