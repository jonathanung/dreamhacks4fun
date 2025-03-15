#include <Wire.h>
#include <BluetoothSerial.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>
#include <ArduinoJson.h>

// --- Pin assignments ---
#define LED1_PIN 33       // Left LED
#define LED2_PIN 32       // Right LED
#define BUILTIN_LED_PIN 2 // ESP32 built-in LED
#define BUTTON_PIN 27    
#define IR_SENSOR_PIN 26  // Stub for IR sensor
#define SPEAKER_PIN 25   

// I2C pins for MPU6050
#define SDA_PIN 21
#define SCL_PIN 22

// --- Create BluetoothSerial instance ---
BluetoothSerial SerialBT;

// --- Create an MPU6050 instance ---
Adafruit_MPU6050 mpu;

// --- Event parameters ---
unsigned long lastButtonEvent = 0;
unsigned long lastTiltEvent = 0;
const int DEBOUNCE_TIME = 200;  // ms
const float TILT_THRESHOLD = 20.0; // degrees
bool lastButtonState = HIGH;
float lastPitch = 0.0;

// --- Player ID (assigned by event controller) ---
int player_id = -1;  // -1 means not assigned yet

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Event Relay");

  // Initialize LED pins
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  pinMode(BUILTIN_LED_PIN, OUTPUT);
  
  // Set up input pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(IR_SENSOR_PIN, INPUT);
  pinMode(SPEAKER_PIN, OUTPUT);

  // Initialize I2C for the MPU6050
  Wire.begin(SDA_PIN, SCL_PIN);
  
  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    // Flash LEDs to indicate error
    for (int i = 0; i < 5; i++) {
      digitalWrite(LED1_PIN, HIGH);
      digitalWrite(LED2_PIN, HIGH);
      delay(100);
      digitalWrite(LED1_PIN, LOW);
      digitalWrite(LED2_PIN, LOW);
      delay(100);
    }
  } else {
    // Configure sensor ranges and bandwidth
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("MPU6050 initialized");
  }

  // --- Bluetooth Serial Setup ---
  if(!SerialBT.begin("ESP32_EventRelay")) {
    Serial.println("Bluetooth initialization error");
  } else {
    Serial.println("Bluetooth initialized, device name: ESP32_EventRelay");
  }
  
  // Signal ready state - flash all LEDs
  digitalWrite(LED1_PIN, HIGH);
  digitalWrite(LED2_PIN, HIGH);
  digitalWrite(BUILTIN_LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, LOW);
  digitalWrite(BUILTIN_LED_PIN, LOW);
}

// Function to update LEDs based on player ID
void updatePlayerLEDs() {
  // Turn off all LEDs first
  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, LOW);
  digitalWrite(BUILTIN_LED_PIN, LOW);
  
  // Set LEDs based on player ID
  switch(player_id) {
    case 0:  // Player 0: Left LED on
      digitalWrite(LED1_PIN, HIGH);
      break;
    case 1:  // Player 1: Right LED on
      digitalWrite(LED2_PIN, HIGH);
      break;
    case 2:  // Player 2: Both LEDs on
      digitalWrite(LED1_PIN, HIGH);
      digitalWrite(LED2_PIN, HIGH);
      break;
    case 3:  // Player 3: Only built-in LED on
      digitalWrite(BUILTIN_LED_PIN, HIGH);
      break;
    default: // No player ID assigned yet, flash alternating pattern
      // This will be handled in the main loop for animation
      break;
  }
}

void loop() {
  unsigned long currentMillis = millis();

  // --- Check for player ID message from Serial or Bluetooth ---
  if (Serial.available()) {
    String message = Serial.readStringUntil('\n');
    if (message.startsWith("PLAYER_ID:")) {
      int new_id = message.substring(10).toInt();
      if (new_id >= 0 && new_id <= 3) {
        player_id = new_id;
        Serial.print("Assigned Player ID: ");
        Serial.println(player_id);
        updatePlayerLEDs();
      }
    }
  }
  
  if (SerialBT.available()) {
    String message = SerialBT.readStringUntil('\n');
    if (message.startsWith("PLAYER_ID:")) {
      int new_id = message.substring(10).toInt();
      if (new_id >= 0 && new_id <= 3) {
        player_id = new_id;
        Serial.print("Assigned Player ID from Bluetooth: ");
        Serial.println(player_id);
        updatePlayerLEDs();
      }
    }
  }

  // --- If no player ID assigned yet, show animated pattern ---
  if (player_id < 0) {
    // Create alternating pattern
    if ((currentMillis / 500) % 2 == 0) {
      digitalWrite(LED1_PIN, HIGH);
      digitalWrite(LED2_PIN, LOW);
    } else {
      digitalWrite(LED1_PIN, LOW);
      digitalWrite(LED2_PIN, HIGH);
    }
    // Blink built-in LED more quickly
    digitalWrite(BUILTIN_LED_PIN, (currentMillis / 200) % 2);
  }

  // --- Check Button State ---
  bool buttonState = digitalRead(BUTTON_PIN);
  if (buttonState != lastButtonState && 
      currentMillis - lastButtonEvent > DEBOUNCE_TIME) {
    
    lastButtonEvent = currentMillis;
    lastButtonState = buttonState;
    
    // Button pressed (active LOW)
    if (buttonState == LOW) {
      // Flash appropriate LED based on player ID
      if (player_id >= 0 && player_id <= 3) {
        bool led1_state = digitalRead(LED1_PIN);
        bool led2_state = digitalRead(LED2_PIN);
        bool builtin_led_state = digitalRead(BUILTIN_LED_PIN);
        
        // Inverse LED state briefly for visual feedback
        if (player_id == 0 || player_id == 2) digitalWrite(LED1_PIN, !led1_state);
        if (player_id == 1 || player_id == 2) digitalWrite(LED2_PIN, !led2_state);
        if (player_id == 3) digitalWrite(BUILTIN_LED_PIN, !builtin_led_state);
      }
      
      // Create and send button event
      DynamicJsonDocument doc(128);
      doc["type"] = "button";
      doc["action"] = "press";
      doc["button"] = "main";
      doc["player_id"] = player_id;  // Include player ID in the event
      doc["timestamp"] = currentMillis;
      
      // Serialize to JSON string
      String jsonString;
      serializeJson(doc, jsonString);
      
      // Send via both Serial and Bluetooth
      Serial.println(jsonString);
      SerialBT.println(jsonString);
      
      // Restore LED state
      delay(50);  // Brief flash
      updatePlayerLEDs();
    }
  }

  // --- Read MPU6050 data and detect tilt events ---
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  // Calculate pitch angle
  float pitch = atan2(a.acceleration.y, 
                      sqrt(a.acceleration.x * a.acceleration.x + 
                           a.acceleration.z * a.acceleration.z)) * 180.0 / PI;
  
  // Detect significant tilt changes
  if ((abs(pitch - lastPitch) > 5.0 || 
       currentMillis - lastTiltEvent > 2000) && 
      currentMillis - lastTiltEvent > DEBOUNCE_TIME) {
    
    lastTiltEvent = currentMillis;
    lastPitch = pitch;
    
    // Check if tilted beyond threshold
    if (pitch > TILT_THRESHOLD) {
      // Tilted up - flash appropriate LED
      if (player_id >= 0 && player_id <= 3) {
        bool led1_state = digitalRead(LED1_PIN);
        bool led2_state = digitalRead(LED2_PIN);
        bool builtin_led_state = digitalRead(BUILTIN_LED_PIN);
        
        // Inverse LED state briefly for visual feedback
        if (player_id == 0 || player_id == 2) digitalWrite(LED1_PIN, !led1_state);
        if (player_id == 1 || player_id == 2) digitalWrite(LED2_PIN, !led2_state);
        if (player_id == 3) digitalWrite(BUILTIN_LED_PIN, !builtin_led_state);
      }
      
      // Create and send tilt event
      DynamicJsonDocument doc(128);
      doc["type"] = "tilt";
      doc["action"] = "up";
      doc["angle"] = pitch;
      doc["player_id"] = player_id;  // Include player ID in the event
      doc["timestamp"] = currentMillis;
      
      // Serialize to JSON string
      String jsonString;
      serializeJson(doc, jsonString);
      
      // Send via both Serial and Bluetooth
      Serial.println(jsonString);
      SerialBT.println(jsonString);
      
      // Restore LED state
      delay(50);  // Brief flash
      updatePlayerLEDs();
    } 
    else if (pitch < -TILT_THRESHOLD) {
      // Tilted down - flash appropriate LED
      if (player_id >= 0 && player_id <= 3) {
        bool led1_state = digitalRead(LED1_PIN);
        bool led2_state = digitalRead(LED2_PIN);
        bool builtin_led_state = digitalRead(BUILTIN_LED_PIN);
        
        // Inverse LED state briefly for visual feedback
        if (player_id == 0 || player_id == 2) digitalWrite(LED1_PIN, !led1_state);
        if (player_id == 1 || player_id == 2) digitalWrite(LED2_PIN, !led2_state);
        if (player_id == 3) digitalWrite(BUILTIN_LED_PIN, !builtin_led_state);
      }
      
      // Create and send tilt event
      DynamicJsonDocument doc(128);
      doc["type"] = "tilt";
      doc["action"] = "down";
      doc["angle"] = pitch;
      doc["player_id"] = player_id;  // Include player ID in the event
      doc["timestamp"] = currentMillis;
      
      // Serialize to JSON string
      String jsonString;
      serializeJson(doc, jsonString);
      
      // Send via both Serial and Bluetooth
      Serial.println(jsonString);
      SerialBT.println(jsonString);
      
      // Restore LED state
      delay(50);  // Brief flash
      updatePlayerLEDs();
    } else {
      // Tilted back to normal - flash appropriate LED
      if (player_id >= 0 && player_id <= 3) {
        bool led1_state = digitalRead(LED1_PIN);
        bool led2_state = digitalRead(LED2_PIN);
        bool builtin_led_state = digitalRead(BUILTIN_LED_PIN);
        
        // Inverse LED state briefly for visual feedback
        if (player_id == 0 || player_id == 2) digitalWrite(LED1_PIN, !led1_state);
        if (player_id == 1 || player_id == 2) digitalWrite(LED2_PIN, !led2_state);
        if (player_id == 3) digitalWrite(BUILTIN_LED_PIN, !builtin_led_state);
      }
      
      // Create and send tilt event
      DynamicJsonDocument doc(128);
      doc["type"] = "tilt";
      doc["action"] = "stop";
      doc["player_id"] = player_id;  // Include player ID in the event
      doc["timestamp"] = currentMillis;
      
      // Serialize to JSON string
      String jsonString;
      serializeJson(doc, jsonString);
      
      // Send via both Serial and Bluetooth
      Serial.println(jsonString);
      SerialBT.println(jsonString);

      // Restore LED state
      delay(50);  // Brief flash
      updatePlayerLEDs();
    }
  }
  
  // Brief delay to prevent CPU hogging
  delay(10);
}
