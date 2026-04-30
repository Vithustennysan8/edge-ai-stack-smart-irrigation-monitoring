#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi & MQTT
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";

WiFiClient espClient;
PubSubClient client(espClient);

// Pin Definitions
int moisturePin = 34;   // Analog pin for moisture sensor
int ledPin = 4;         // indicator LED

// Threshold (adjust based on calibration)
int threshold = 400;

// Callback (receive commands)
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.print("Incoming messages [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);
}

// Reconnect to MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    String clientId = "ESP32-Moisture-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("Connect!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println("try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected");

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // 🔹 Read moisture sensor
  int moistureValue = analogRead(moisturePin);
  int temperatureValue = random(28, 38);
  int humidityValue = random(30, 70);

  Serial.print("Moisture Value: ");
  Serial.println(moistureValue);
  Serial.print("Temperature Value: ");
  Serial.println(temperatureValue);
  Serial.print("Humidity Value: ");
  Serial.println(humidityValue);

  // 🔹 Decision Logic (Temporary - Replace with ML later)
  String prediction;

  if (moistureValue < threshold) {
    prediction = "Needs Water";
    Serial.println("Moisture level is low. Please water the plant.");
    digitalWrite(ledPin, HIGH);  // Turn ON LED
  } else {
    prediction = "Soil OK";
    Serial.println("Moisture level is sufficient.");
    digitalWrite(ledPin, LOW);   // Turn OFF LED
  }


  // 🔹 Prepare JSON payload
  String payload = "{";
  payload += "\"moisture\": " + String(moistureValue) + ",";
  payload += "\"temperature\": " + String(temperatureValue) + ",";
  payload += "\"humidity\": " + String(humidityValue) + ",";
  payload += "\"prediction\": \"" + prediction + "\",";
  payload += "\"alert\": " + String((moistureValue < threshold) ? "true" : "false");
  payload += "}";

  // json template 
  // {
  // "moisture": 512,
  // "temperature": 25,
  // "humidity": 60,
  // "prediction": "Soil OK"
  // }

  Serial.println("send: " + payload);

  // 🔹 Publish to MQTT
  client.publish("plant/monitor", payload.c_str());

  delay(2000);

  /*
  ============================================================
  🔮 TinyML Model Implementation (Currently Disabled)
  ============================================================

  // Example flow:

  // 1. Normalize input
  float input = moistureValue / 1023.0;

  // 2. Run inference
  float output = runModel(input);  // Your TinyML function

  // 3. Interpret result
  if (output > 0.5) {
      prediction = "Needs Water";
  } else {
      prediction = "Soil OK";
  }

  ============================================================
  */
}