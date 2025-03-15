#include <Wire.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

// BLE UUIDs (must match the ones in your Python script)
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// Pin assignments
#define LED1_PIN 33
#define LED2_PIN 32
#define BUTTON_PIN 27    
#define IR_SENSOR_PIN 26 // Stub for IR sensor
#define SPEAKER_PIN 25   

// I2C pins for MPU6050
#define SDA_PIN 21
#define SCL_PIN 22

// BLE globals
BLECharacteristic *pCharacteristic;
BLEServer *pServer;
bool deviceConnected = false;

// Create an MPU6050 instance
Adafruit_MPU6050 mpu;

// --- Tone parameters ---
const int TONE_FREQUENCY = 1000;   // 1 kHz tone
const int TONE_DURATION = 200;     // duration in milliseconds

// Custom BLE server callback to track connection status
class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
    Serial.println("BLE Client Connected");
  }
  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    Serial.println("BLE Client Disconnected");
  }
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 BLE IMU Example");

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

  // --- BLE Setup ---
  BLEDevice::init("ESP32_BLE_Device");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  BLEService *pService = pServer->createService(SERVICE_UUID);
  
  // Create a characteristic that supports READ and NOTIFY
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
                      );
  pCharacteristic->addDescriptor(new BLE2902());
  
  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  // Optionally add the service UUID to the advertisement data
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();
  Serial.println("BLE advertising started");
}

void loop() {
  // --- Flash the LEDs every second ---
  digitalWrite(LED1_PIN, HIGH);
  digitalWrite(LED2_PIN, HIGH);
  delay(500);
  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, LOW);

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
  
  // Compute pitch angle from accelerometer data
  // Formula: pitch = atan2(accY, sqrt(accX^2 + accZ^2)) * (180/PI)
  float pitch = atan2(a.acceleration.y, sqrt(a.acceleration.x * a.acceleration.x + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;
  
  // Print the pitch to Serial
  Serial.print("Pitch: ");
  Serial.print(pitch, 2);
  Serial.println("°");
  
  // --- Update BLE characteristic ---
  // Convert pitch value to a string
  char pitchStr[10];
  dtostrf(pitch, 4, 2, pitchStr); // 4 digits, 2 decimals
  pCharacteristic->setValue(pitchStr);
  
  // Notify connected BLE client, if any
  if (deviceConnected) {
    pCharacteristic->notify();
  }
  
  // Wait for the remainder of the 1-second period
  delay(500);
}
