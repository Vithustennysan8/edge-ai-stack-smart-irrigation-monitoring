#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <math.h>

// 🔹 Include generated model
#include "model_lr.h"

// WiFi & MQTT
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";

WiFiClient espClient;
PubSubClient client(espClient);

// Pins
int moisturePin = 34;
int ledPin = 4;

// 🔹 Sigmoid function
float sigmoid(float x) {
  return 1.0 / (1.0 + exp(-x));
}

// 🔹 Prediction function (Logistic Regression)
float predict(float m, float t, float h) {
  // Normalize inputs
  float nm = (m - MOISTURE_MEAN) / MOISTURE_STD;
  float nt = (t - TEMP_MEAN) / TEMP_STD;
  float nh = (h - HUMIDITY_MEAN) / HUMIDITY_STD;

  // Linear combination
  float z = W1 * nm + W2 * nt + W3 * nh + BIAS;

  // Sigmoid output
  return sigmoid(z);
}

// MQTT callback
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Incoming message: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

// MQTT reconnect
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32-Plant")) {
      Serial.println("Connected!");
    } else {
      Serial.println("Retrying...");
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

  // WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected");

  // MQTT
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  // high temp (~34–35°C) + low humidity (~40%) → Needs Water
  // lower temp (~26–28°C) + higher humidity (~60–70%) → Soil OK
  // 🔹 Read sensor (simulated in Wokwi)
  int moisture = analogRead(moisturePin);
  float temp = random(34, 38);
  float humidity = random(40, 70);

  Serial.println("\n--- SENSOR DATA ---");
  Serial.print("Moisture: "); Serial.println(moisture);
  Serial.print("Temp: "); Serial.println(temp);
  Serial.print("Humidity: "); Serial.println(humidity);

  // 🔹 ML Prediction
  float result = predict(moisture, temp, humidity);

  String prediction;

  if (result > 0.5) {
    prediction = "Needs Water";
    digitalWrite(ledPin, HIGH);
  } else {
    prediction = "Soil OK";
    digitalWrite(ledPin, LOW);
  }

  Serial.print("Prediction Score: ");
  Serial.println(result);
  Serial.println("Prediction: " + prediction);

  // 🔹 JSON payload
  String payload = "{";
  payload += "\"moisture\": " + String(moisture) + ",";
  payload += "\"temperature\": " + String(temp) + ",";
  payload += "\"humidity\": " + String(humidity) + ",";
  payload += "\"prediction\": \"" + prediction + "\",";
  payload += "\"alert\": " + String((result > 0.5) ? "true" : "false");
  payload += "}";

  Serial.println("Sending: " + payload);

  client.publish("plant/monitor", payload.c_str());

  delay(5000);
}