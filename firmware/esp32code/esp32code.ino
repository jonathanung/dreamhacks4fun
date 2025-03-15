#include <Wire.h>
#include <BluetoothSerial.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

// --- Pin assignments ---
#define LED1_PIN 33
#define LED2_PIN 32
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

// --- LED timing ---
unsigned long lastLedToggleTime = 0;
bool ledsOn = false;

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
  if(!SerialBT.begin("ESP32_BT_Device")) {
    Serial.println("An error occurred initializing Bluetooth");
  } else {
    Serial.println("Bluetooth initialized. Waiting for connections...");
  }
}

void loop() {
  unsigned long currentMillis = millis();

  // --- Flash the LEDs every second ---
  if(currentMillis - lastLedToggleTime >= 1000) {
    lastLedToggleTime = currentMillis;
    ledsOn = !ledsOn;
    digitalWrite(LED1_PIN, ledsOn ? HIGH : LOW);
    digitalWrite(LED2_PIN, ledsOn ? HIGH : LOW);
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
  // This will send the data to all connected Bluetooth clients.
  char pitchStr[10];
  dtostrf(pitch, 4, 2, pitchStr);  // Format the pitch value as a string
  SerialBT.println(pitchStr);
  
  // Wait a short interval before repeating.
  delay(500);
}
