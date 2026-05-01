
// Logistic Regression Model for ESP32

// Normalization
const float MOISTURE_MEAN = 2085.345947f;
const float MOISTURE_STD  = 1170.725952f;
const float TEMP_MEAN     = 29.992651f;
const float TEMP_STD      = 8.749629f;
const float HUMIDITY_MEAN = 59.852791f;
const float HUMIDITY_STD  = 22.890285f;

// Model weights
const float W1 = -3.898945f;
const float W2 = 1.114243f;
const float W3 = -1.442031f;
const float BIAS = 0.579533f;
