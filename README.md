# Smart Irrigation Monitoring System

An IoT-based intelligent plant monitoring system that uses a capacitive soil moisture sensor and real-time weather data to predict watering needs using **Machine Learning** on the edge.

## Report
Report in a root folder with a name of **"Group 14.pdf"**

## Project Overview

This project monitors soil moisture, temperature, and humidity, then uses a lightweight **Logistic Regression** model running directly on the ESP32 to intelligently decide whether the plant needs water or not. Sensor data and predictions are sent via MQTT to a Node-RED dashboard for real-time remote monitoring.

## Key Features

- Real-time soil moisture sensing using capacitive sensor
- Fetches live temperature & humidity from OpenWeather API
- Lightweight Logistic Regression model deployed on ESP32 (edge inference)
- MQTT communication for data transmission
- Professional visualization dashboard using Node-RED
- Fully simulated using Wokwi

## Technologies Used

- **Microcontroller**: ESP32
- **Sensor**: Capacitive Soil Moisture Sensor
- **ML Model**: Logistic Regression (scikit-learn)
- **Simulation**: Wokwi
- **Development**: PlatformIO + VS Code
- **Communication**: MQTT (HiveMQ)
- **Dashboard**: Node-RED
- **Weather API**: OpenWeatherMap

## Hardware Connections

| Component                    | ESP32 Pin     |
|-----------------------------|---------------|
| Soil Moisture Sensor (Signal)| GPIO 34      |
| Soil Moisture Sensor (VCC)  | 3.3V         |
| Soil Moisture Sensor (GND)  | GND          |
| LED (Alert)                 | GPIO 4       |

## How It Works

1. ESP32 reads soil moisture from capacitive sensor
2. Fetches current temperature & humidity from OpenWeather API
3. Normalizes the values and runs Logistic Regression inference
4. Predicts “Needs Water” or “Soil OK”
5. Publishes all data to MQTT topic `plant/monitor`
6. Node-RED dashboard displays real-time readings and prediction

## Repository Contents

- `main.cpp` - Main firmware
- `model_lr.h` - Generated Logistic Regression model parameters
- `platformio.ini` - Project configuration
- Wokwi simulation files

---

**Developed by Group 14**  
(E/19/174, E/20/099, E/20/338, E/20/416)
