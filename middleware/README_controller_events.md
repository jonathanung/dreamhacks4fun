# Handling ESP32 Controller Events

This document explains how to handle ESP32 controller events in your game and menu code.

## Event Format

The ESP32 controllers now send universal events that work in both menu and game contexts. Each event contains multiple fields to allow flexible handling depending on the current context:

```json
{
  "timestamp": 1742076247.059356,
  "player_id": 0,
  "event_source": "esp32_0",
  "event_type": "controller_input",
  "controller_action": "tilt",
  "raw_direction": "up",
  "angle": 30.09578,
  "menu_action": "navigate_up",
  "game_action": "move_up"
}
```

## Using the Events in Different Contexts

### In Main Menu

In the main menu, check for the `menu_action` field to handle navigation:

```python
def handle_event(event):
    # Check if this is a controller input event
    if event.get("event_type") == "controller_input":
        player_id = event.get("player_id")
        
        # Handle menu navigation
        if event.get("menu_action") == "navigate_up":
            menu.move_cursor_up()
            
        elif event.get("menu_action") == "navigate_down":
            menu.move_cursor_down()
            
        elif event.get("menu_action") == "select":
            menu.select_current_item()
```

### In Pong Game

In the Pong game, check for the `game_action` field to handle paddle movement:

```python
def handle_event(event):
    # Check if this is a controller input event
    if event.get("event_type") == "controller_input":
        player_id = event.get("player_id")
        
        # Handle paddle movement
        if event.get("game_action") == "move_up":
            # Move paddle up for this player
            paddles[player_id].move_up()
            
        elif event.get("game_action") == "move_down":
            # Move paddle down for this player
            paddles[player_id].move_down()
            
        elif event.get("game_action") == "action" and event.get("controller_action") == "button":
            # Handle button press (e.g., pause game)
            toggle_pause()
```

### In Shooting Stars Game

In the Shooting Stars game, use the same fields but map them to your specific game mechanics:

```python
def handle_event(event):
    # Check if this is a controller input event
    if event.get("event_type") == "controller_input":
        player_id = event.get("player_id")
        
        # Handle player ship movement
        if event.get("game_action") == "move_up":
            # Move ship up
            ships[player_id].move_up()
            
        elif event.get("game_action") == "move_down":
            # Move ship down
            ships[player_id].move_down()
            
        elif event.get("game_action") == "action" and event.get("controller_action") == "button":
            # Fire weapon
            ships[player_id].fire_weapon()
```

## Thresholds

The event controller automatically applies thresholds to prevent too many events from being sent:

- **Menu Navigation**: Events are throttled to 1/3 second intervals (333ms)
- **Game Actions**: More responsive with only 50ms throttling for movement, 200ms for buttons

You can adjust these thresholds using command line arguments:

```bash
bash middleware/start_esp32_controllers.sh --menu-threshold 0.5 --game-threshold 0.03
```

## Raw Event Access

If needed, you can access the raw controller action and direction:

```python
controller_action = event.get("controller_action")  # "tilt" or "button"
raw_direction = event.get("raw_direction")          # "up" or "down" for tilt actions
angle = event.get("angle")                          # Angle value for tilt actions
```

This gives you full flexibility to handle the events however you need in your specific game context. 