#include <Wire.h>
#include <BluetoothSerial.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>
#include <ArduinoJson.h>

// --- Pin assignments ---
#define LED1_PIN 33
#define LED2_PIN 32
#define UP_BUTTON_PIN 26
#define DOWN_BUTTON_PIN 25
#define SELECT_BUTTON_PIN 27
#define LED_PIN 2

// I2C pins for MPU6050
#define SDA_PIN 21
#define SCL_PIN 22

// --- Create BluetoothSerial instance ---
BluetoothSerial SerialBT;

// --- Create an MPU6050 instance ---
Adafruit_MPU6050 mpu;

// --- Controller settings ---
const int TILT_THRESHOLD = 20;  // Degrees of tilt to trigger up/down
const int DEBOUNCE_MS = 200;    // Debounce time in milliseconds
unsigned long lastButtonTime = 0;
unsigned long lastTiltTime = 0;
unsigned long lastDataSendTime = 0;
unsigned long lastIdBlinkTime = 0;

// Button states
bool lastUpState = HIGH;
bool lastDownState = HIGH;
bool lastSelectState = HIGH;

// Player ID received from PC
int player_id = -1;  // -1 means not assigned yet
bool id_display_mode = true;  // Start in ID display mode
unsigned long id_display_start_time = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Bluetooth Game Controller");

  // Initialize pin modes
  pinMode(UP_BUTTON_PIN, INPUT_PULLUP);
  pinMode(DOWN_BUTTON_PIN, INPUT_PULLUP);
  pinMode(SELECT_BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Show startup pattern - all LEDs blink quickly
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED1_PIN, HIGH);
    digitalWrite(LED2_PIN, HIGH);
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED1_PIN, LOW);
    digitalWrite(LED2_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }

  // Initialize I2C for the MPU6050
  Wire.begin(SDA_PIN, SCL_PIN);
  
  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    // Flash LED to indicate error
    for (int i = 0; i < 5; i++) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      delay(200);
    }
  } else {
    Serial.println("MPU6050 initialized");
    // Configure sensor ranges
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }

  // --- Bluetooth Serial Setup ---
  // Start Bluetooth Serial with a device name that includes a unique identifier
  String deviceName = "ESP32_BT_Controller_" + String(random(1000));
  if(!SerialBT.begin(deviceName.c_str())) {
    Serial.println("An error occurred initializing Bluetooth");
    // Flash LED rapidly to indicate Bluetooth error
    for (int i = 0; i < 10; i++) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      delay(100);
    }
  } else {
    Serial.println("Bluetooth initialized. Name: " + deviceName);
    // Blink main LED twice to indicate success
    for (int i = 0; i < 2; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(200);
      digitalWrite(LED_PIN, LOW);
      delay(200);
    }
  }
  
  // Start ID display mode for 60 seconds
  id_display_start_time = millis();
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Check for player ID message from PC
  if (SerialBT.available()) {
    String message = SerialBT.readStringUntil('\n');
    message.trim();
    
    // Check if this is a player ID message
    if (message.startsWith("PLAYER_ID:")) {
      String id_part = message.substring(10);  // Extract the number after "PLAYER_ID:"
      int new_id = id_part.toInt();
      
      // Only accept valid player IDs (0-3)
      if (new_id >= 0 && new_id <= 3) {
        player_id = new_id;
        Serial.print("Received player ID: ");
        Serial.println(player_id);
        
        // Enter ID display mode for 10 seconds
        id_display_mode = true;
        id_display_start_time = currentMillis;
        
        // Display player ID in binary using LED1 and LED2
        updateIdLEDs();
      }
    }
  }
  
  // Check if we should exit ID display mode
  if (id_display_mode && currentMillis - id_display_start_time > 10000) {
    id_display_mode = false;
    Serial.println("Exiting ID display mode");
  }
  
  // In ID display mode, blink the LEDs in binary pattern
  if (id_display_mode) {
    if (currentMillis - lastIdBlinkTime > 500) {
      lastIdBlinkTime = currentMillis;
      static bool led_state = true;
      
      if (led_state) {
        // Show binary ID pattern
        updateIdLEDs();
      } else {
        // Turn LEDs off briefly for blinking effect
        digitalWrite(LED1_PIN, LOW);
        digitalWrite(LED2_PIN, LOW);
      }
      
      led_state = !led_state;
    }
    
    // In ID display mode, we still process the main status LED and buttons,
    // but don't handle tilt detection
    digitalWrite(LED_PIN, (currentMillis / 200) % 2); // Fast blink of main LED
  } else {
    // Normal operation mode - show ID in binary constantly
    updateIdLEDs();
    
    // --- 1. Check physical buttons ---
    bool upState = digitalRead(UP_BUTTON_PIN);
    bool downState = digitalRead(DOWN_BUTTON_PIN);
    bool selectState = digitalRead(SELECT_BUTTON_PIN);
    
    // Check if UP button was pressed (active LOW)
    if (upState == LOW && lastUpState == HIGH && currentMillis - lastButtonTime > DEBOUNCE_MS) {
      lastButtonTime = currentMillis;
      // Create JSON event
      sendButtonEvent("up");
      digitalWrite(LED_PIN, HIGH);  // Flash LED
      delay(50);
      digitalWrite(LED_PIN, LOW);
    }
    
    // Check if DOWN button was pressed
    if (downState == LOW && lastDownState == HIGH && currentMillis - lastButtonTime > DEBOUNCE_MS) {
      lastButtonTime = currentMillis;
      sendButtonEvent("down");
      digitalWrite(LED_PIN, HIGH);  // Flash LED
      delay(50);
      digitalWrite(LED_PIN, LOW);
    }
    
    // Check if SELECT button was pressed
    if (selectState == LOW && lastSelectState == HIGH && currentMillis - lastButtonTime > DEBOUNCE_MS) {
      lastButtonTime = currentMillis;
      sendButtonEvent("select");
      digitalWrite(LED_PIN, HIGH);  // Flash LED
      delay(50);
      digitalWrite(LED_PIN, LOW);
    }
    
    // Save button states
    lastUpState = upState;
    lastDownState = downState;
    lastSelectState = selectState;
    
    // --- 2. Check IMU for tilt-based control ---
    if (currentMillis - lastTiltTime > 200) {
      lastTiltTime = currentMillis;
      
      sensors_event_t a, g, temp;
      mpu.getEvent(&a, &g, &temp);
      
      // Calculate pitch angle from accelerometer
      float pitch = atan2(a.acceleration.y, sqrt(a.acceleration.x * a.acceleration.x + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;
      
      // Check for significant tilt
      if (pitch > TILT_THRESHOLD) {
        sendTiltEvent("up", pitch);
        digitalWrite(LED_PIN, HIGH);
        delay(20);
        digitalWrite(LED_PIN, LOW);
      } 
      else if (pitch < -TILT_THRESHOLD) {
        sendTiltEvent("down", pitch);
        digitalWrite(LED_PIN, HIGH);
        delay(20);
        digitalWrite(LED_PIN, LOW);
      }
      
      // Every 2 seconds, send the current IMU data regardless
      if (currentMillis - lastDataSendTime > 2000) {
        lastDataSendTime = currentMillis;
        
        // Create a JSON document for the sensor data
        DynamicJsonDocument doc(128);
        doc["type"] = "sensor";
        doc["pitch"] = pitch;
        doc["accel_x"] = a.acceleration.x;
        doc["accel_y"] = a.acceleration.y;
        doc["accel_z"] = a.acceleration.z;
        
        // Serialize and send
        String jsonString;
        serializeJson(doc, jsonString);
        Serial.println(jsonString);
        SerialBT.println(jsonString);
      }
    }
  }
  
  // Short delay to prevent busy-waiting
  delay(10);
}

// Update the ID LEDs to show the player ID in binary
void updateIdLEDs() {
  if (player_id >= 0 && player_id <= 3) {
    // Display binary: 
    // Player 0: 00 (both LEDs off)
    // Player 1: 01 (LED1 off, LED2 on)
    // Player 2: 10 (LED1 on, LED2 off)
    // Player 3: 11 (both LEDs on)
    
    digitalWrite(LED1_PIN, (player_id & 2) ? HIGH : LOW);  // Bit 1
    digitalWrite(LED2_PIN, (player_id & 1) ? HIGH : LOW);  // Bit 0
  } else {
    // No ID assigned yet, flash both LEDs alternately
    unsigned long ms = millis();
    digitalWrite(LED1_PIN, (ms / 500) % 2 == 0 ? HIGH : LOW);
    digitalWrite(LED2_PIN, (ms / 500) % 2 == 1 ? HIGH : LOW);
  }
}

void sendButtonEvent(const char* action) {
  // Create a JSON document
  DynamicJsonDocument doc(128);
  doc["type"] = "button";
  doc["action"] = action;
  doc["timestamp"] = millis();
  
  // Serialize to JSON string
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send via both Serial and Bluetooth
  Serial.println(jsonString);
  SerialBT.println(jsonString);
}

void sendTiltEvent(const char* action, float value) {
  // Create a JSON document
  DynamicJsonDocument doc(128);
  doc["type"] = "tilt";
  doc["action"] = action;
  doc["value"] = value;
  doc["timestamp"] = millis();
  
  // Serialize to JSON string
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send via both Serial and Bluetooth
  Serial.println(jsonString);
  SerialBT.println(jsonString);
}
