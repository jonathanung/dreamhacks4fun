// ESP32 Event Relay - Clean version without debug spam

const int BUTTON_PIN = 27;  // Button connected to pin 27 and ground
const int LED_PIN = 2;      // Built-in LED

// Debounce settings
const unsigned long DEBOUNCE_DELAY = 50;
unsigned long lastButtonTime = 0;
int lastButtonState = HIGH;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Configure pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  
  // Indicate startup
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("{\"type\":\"system\",\"action\":\"startup\",\"data\":\"ESP32 Event Controller Ready\"}");
}

void loop() {
  // Read button state
  int buttonState = digitalRead(BUTTON_PIN);
  
  // Check for button press with debounce
  if (buttonState != lastButtonState) {
    if ((millis() - lastButtonTime) > DEBOUNCE_DELAY) {
      lastButtonTime = millis();
      
      if (buttonState == LOW) {
        // Button pressed
        digitalWrite(LED_PIN, HIGH);
        
        // Send event in JSON format for the middleware
        Serial.println("{\"type\":\"button\",\"action\":\"down\",\"data\":\"Button pressed\"}");
      } else {
        // Button released
        digitalWrite(LED_PIN, LOW);
      }
    }
    lastButtonState = buttonState;
  }
  
  // No debug messages in the main loop
  delay(10);
}