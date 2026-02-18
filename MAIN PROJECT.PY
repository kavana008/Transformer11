#define BLYNK_TEMPLATE_ID "TMPL3c_HiX7m_"
#define BLYNK_TEMPLATE_NAME "Transformer"
#define BLYNK_AUTH_TOKEN "bEaUaYRoRtSgXjEcsjsK4xFDKgp6RawJ"

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include "DHT.h"  // Adafruit DHT library

// ---------------- Wi-Fi credentials ----------------
char ssid[] = "CITNC-Samsung Lab";
char pass[] = "Citnc@2025";

// ---------------- Current Sensor ----------------
const int sensorPin = 34; 
float current = 0;

// ---------------- Voltage Sensor ----------------
const int voltagePin = 32;
float Vrms = 0;
float calibrationFactor = 1.0; // Adjust for your sensor

// ---------------- DHT Sensor ----------------
#define DHTPIN 25
#define DHTTYPE DHT11   // Change to DHT22 if needed
DHT dht(DHTPIN, DHTTYPE);

float temperature = 0;
float humidity = 0;

// ---------------- Blynk Timer ----------------
BlynkTimer timer;

void setup() {
  Serial.begin(115200);

  // Initialize DHT
  dht.begin();

  // Connect to Wi-Fi
  WiFi.begin(ssid, pass);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected");
  Serial.println(WiFi.localIP());

  // Initialize Blynk
  Blynk.config(BLYNK_AUTH_TOKEN);

  // Call sensor updates every 2 seconds
  timer.setInterval(2000L, sendSensorData);
}

void loop() {
  Blynk.run();
  timer.run(); // Non-blocking timer
}

// ---------------- Send data to Blynk ----------------
void sendSensorData() {
  readCurrent();
  readVoltage();
  readDHT();

  Blynk.virtualWrite(V0, temperature); // Temperature
  Blynk.virtualWrite(V1, Vrms);        // Voltage
  Blynk.virtualWrite(V2, current);     // Current
  Blynk.virtualWrite(V3, humidity);    // Humidity

  // ----------- ALERT CONDITIONS -----------
  if (temperature > 50) {
    Blynk.logEvent("high_temperature", "Temperature too high!");
  }

  if (current > 2.0) {
    Blynk.logEvent("high_current", "Overcurrent detected!");
  }
}

// ---------------- Current Reading ----------------
void readCurrent() {
  int sensorValue = analogRead(sensorPin);
  float voltage = sensorValue * (3.3 / 4095.0);
  current = (voltage - 1.65) / 0.185; // ACS712 5A

  if (current < 0) current = 0;

  Serial.print("Current (A): ");
  Serial.println(current);
}

// ---------------- Voltage Reading ----------------
void readVoltage() {
  float Vpeak = 0;
  int sample = 0;

  for (int i = 0; i < 200; i++) {
    sample = analogRead(voltagePin);
    float voltage = (sample / 4095.0) * 3.3 * calibrationFactor;
    if (voltage > Vpeak) Vpeak = voltage;
    delayMicroseconds(100);
  }

  Vrms = Vpeak / 1.414; // RMS
  Serial.print("AC Voltage RMS (V): ");
  Serial.println(Vrms);
}

// ---------------- DHT Reading ----------------
void readDHT() {
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("DHT read failed!");
    temperature = 0;
    humidity = 0;
    return;
  }

  Serial.print("Temperature (C): ");
  Serial.print(temperature);
  Serial.print("  Humidity (%): ");
  Serial.println(humidity);
}