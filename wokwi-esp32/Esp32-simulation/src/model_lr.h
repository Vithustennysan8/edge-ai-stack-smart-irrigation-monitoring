
// Logistic Regression Model for ESP32

// Normalization
const float MOISTURE_MEAN = 2049.273438f;
const float MOISTURE_STD  = 1181.791260f;
const float TEMP_MEAN     = 30.028700f;
const float TEMP_STD      = 8.658353f;
const float HUMIDITY_MEAN = 60.045368f;
const float HUMIDITY_STD  = 23.112953f;

// Model weights
const float W1 = -4.526343f;
const float W2 = 1.377214f;
const float W3 = -1.697836f;
const float BIAS = 1.033977f;
