#include <Wire.h>
#include <BluetoothSerial.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

// --- Pin assignments ---
#define LED1_PIN 33   // Represents bit 0 (LSB)
#define LED2_PIN 32   // Represents bit 1
#define BUTTON_PIN 27    
#define IR_SENSOR_PIN 26 // Stub for IR sensor
#define SPEAKER_PIN 25   

// I2C pins for MPU6050
#define SDA_PIN 21
#define SCL_PIN 22

// --- Create BluetoothSerial instance ---
BluetoothSerial SerialBT;

// --- Create an MPU6050 instance ---
Adafruit_MPU6050 mpu;

// --- Tone parameters ---
const int TONE_FREQUENCY = 1000;   // 1 kHz tone
const int TONE_DURATION = 200;     // duration in milliseconds

// Global variable for device ID (-1 means not set yet)
int deviceID = -1;

// Function to update LED outputs based on deviceID
// LED1 = bit 0, LED2 = bit 1
void updateLEDsWithID() {
  // Display the deviceID in binary on LED1 and LED2.
  digitalWrite(LED1_PIN, (deviceID & 0x01) ? HIGH : LOW);
  digitalWrite(LED2_PIN, (deviceID & 0x02) ? HIGH : LOW);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Bluetooth Serial IMU Example");

  // Initialize LED pins
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  
  // Set up stub pins (for future use)
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(IR_SENSOR_PIN, INPUT);
  pinMode(SPEAKER_PIN, OUTPUT);

  // Initialize I2C for the MPU6050
  Wire.begin(SDA_PIN, SCL_PIN);
  
  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  // Configure sensor ranges and bandwidth as needed
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.println("MPU6050 initialized");

  // --- Bluetooth Serial Setup ---
  // Start Bluetooth Serial with a device name.
  if (!SerialBT.begin("ESP32_BT_Device")) {
    Serial.println("An error occurred initializing Bluetooth");
  } else {
    Serial.println("Bluetooth initialized. Waiting for connections...");
  }
}

void loop() {
  // --- Check if we have received our ID from Bluetooth ---
  if (SerialBT.available()) {
    String incoming = SerialBT.readStringUntil('\n');
    incoming.trim();
    Serial.print("Received via Bluetooth: ");
    Serial.println(incoming);
    // Look for the expected ID message format
    if (incoming.startsWith("Your ID is ")) {
      String idStr = incoming.substring(String("Your ID is ").length());
      int id = idStr.toInt();
      deviceID = id;
      Serial.print("Assigned deviceID: ");
      Serial.println(deviceID);
    }
  }
  
  // --- Display ID on LEDs ---
  if (deviceID >= 0) {
    updateLEDsWithID();
  } else {
    // If no ID yet, flash both LEDs as a waiting indicator.
    static unsigned long lastToggle = 0;
    static bool toggleState = false;
    if (millis() - lastToggle > 500) {
      lastToggle = millis();
      toggleState = !toggleState;
      digitalWrite(LED1_PIN, toggleState ? HIGH : LOW);
      digitalWrite(LED2_PIN, toggleState ? HIGH : LOW);
    }
  }

  // --- Check Button for tone output ---
  // Assuming active LOW: when pressed, digitalRead returns LOW.
  if (digitalRead(BUTTON_PIN) == LOW) {
    // Play a 1kHz tone for TONE_DURATION milliseconds.
    tone(SPEAKER_PIN, TONE_FREQUENCY, TONE_DURATION);
    // Debounce delay to avoid retriggering too quickly.
    delay(300);
  }

  // --- Read MPU6050 data ---
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  // Compute pitch angle from accelerometer data.
  // Formula: pitch = atan2(accY, sqrt(accX^2 + accZ^2)) * (180/PI)
  float pitch = atan2(a.acceleration.y, sqrt(a.acceleration.x * a.acceleration.x + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;
  
  // Print the pitch to Serial monitor.
  Serial.print("Pitch: ");
  Serial.print(pitch, 2);
  Serial.println("°");
  
  // --- Transmit pitch data over Bluetooth Serial ---
  // This will send the pitch to any connected Bluetooth clients.
  char pitchStr[10];
  dtostrf(pitch, 4, 2, pitchStr);  // Format the pitch value as a string
  SerialBT.println(pitchStr);
  
  // Short delay before repeating the loop.
  delay(500);
}
