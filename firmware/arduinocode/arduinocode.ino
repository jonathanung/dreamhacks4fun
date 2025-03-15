void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any extra whitespace or newline characters

    if (command == "ON") {
      digitalWrite(LED_BUILTIN, HIGH);
    } else if (command == "OFF") {
      digitalWrite(LED_BUILTIN, LOW);
    }
  }
}
