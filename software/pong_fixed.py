def process_middleware_events(self):
    """Process events from middleware controllers."""
    print("\n@@@ PONG DEBUG: process_middleware_events called @@@")
    
    if not self.event_controller:
        print("@@@ PONG DEBUG: No event controller found @@@")
        return
        
    try:
        # Get new events from middleware
        print("@@@ PONG DEBUG: Getting events from event controller @@@")
        events = self.event_controller.get_events()
        
        # If there are events, process them
        if events:
            print(f"@@@ PONG DEBUG: Processing {len(events)} middleware events @@@")
            
            for event in events:
                print(f"@@@ PONG DEBUG: Processing event: {event} @@@")
                
                # Process based on event type or format
                if "game_action" in event and "controller_action" in event:
                    player_id = event.get("player_id")
                    controller_action = event.get("controller_action")
                    
                    print(f"@@@ PONG DEBUG: Player {player_id}, action {controller_action} @@@")
                    
                    # Process the event based on the controller action
                    if controller_action == "tilt":
                        raw_direction = event.get("raw_direction")
                        
                        print(f"@@@ PONG DEBUG: Tilt {raw_direction} for player {player_id} @@@")
                        
                        # Process for each player
                        if player_id == 0:  # Top player (WASD controls)
                            if raw_direction == "up" and self.players_alive[0]:
                                print("@@@ PONG DEBUG: Player 0 moving LEFT @@@")
                                self.paddles[0].start_move("left")
                            elif raw_direction == "down" and self.players_alive[0]:
                                print("@@@ PONG DEBUG: Player 0 moving RIGHT @@@")
                                self.paddles[0].start_move("right")
                            elif raw_direction == "stop" and self.players_alive[0]:
                                print("@@@ PONG DEBUG: Player 0 STOPPING @@@")
                                self.paddles[0].stop_move("left")
                                self.paddles[0].stop_move("right")
                                
                        elif player_id == 1:  # Right player (arrow controls)
                            if raw_direction == "up" and self.players_alive[1]:
                                print("@@@ PONG DEBUG: Player 1 moving UP @@@")
                                self.paddles[1].start_move("up")
                            elif raw_direction == "down" and self.players_alive[1]:
                                print("@@@ PONG DEBUG: Player 1 moving DOWN @@@")
                                self.paddles[1].start_move("down")
                            elif raw_direction == "stop" and self.players_alive[1]:
                                print("@@@ PONG DEBUG: Player 1 STOPPING @@@")
                                self.paddles[1].stop_move("up")
                                self.paddles[1].stop_move("down")
                                
                        elif player_id == 2:  # Bottom player (IJKL controls)
                            if raw_direction == "up" and self.players_alive[2]:
                                print("@@@ PONG DEBUG: Player 2 moving RIGHT @@@")
                                self.paddles[2].start_move("right")
                            elif raw_direction == "down" and self.players_alive[2]:
                                print("@@@ PONG DEBUG: Player 2 moving LEFT @@@")
                                self.paddles[2].start_move("left")
                            elif raw_direction == "stop" and self.players_alive[2]:
                                print("@@@ PONG DEBUG: Player 2 STOPPING @@@")
                                self.paddles[2].stop_move("left")
                                self.paddles[2].stop_move("right")
                                
                        elif player_id == 3:  # Left player (YUXB controls)
                            if raw_direction == "up" and self.players_alive[3]:
                                print("@@@ PONG DEBUG: Player 3 moving UP @@@")
                                self.paddles[3].start_move("up")
                            elif raw_direction == "down" and self.players_alive[3]:
                                print("@@@ PONG DEBUG: Player 3 moving DOWN @@@")
                                self.paddles[3].start_move("down")
                            elif raw_direction == "stop" and self.players_alive[3]:
                                print("@@@ PONG DEBUG: Player 3 STOPPING @@@")
                                self.paddles[3].stop_move("up")
                                self.paddles[3].stop_move("down")
                    
                    elif controller_action == "button":
                        # Trigger hit if player exists, is active, and it's past the cooldown
                        if 0 <= player_id < len(self.players_alive) and self.players_alive[player_id]:
                            if self.game_started and self.paddles[player_id].hit_timer == 0:
                                print(f"@@@ PONG DEBUG: Player {player_id} HIT @@@")
                                self.paddles[player_id].hit()
                else:
                    # Fallback for unrecognized event formats
                    print(f"@@@ PONG DEBUG: Unrecognized event format: {event} @@@")
        else:
            print("@@@ PONG DEBUG: No events to process @@@")
    except Exception as e:
        print(f"@@@ PONG DEBUG: Error processing middleware events: {e} @@@")
        import traceback
        traceback.print_exc() 