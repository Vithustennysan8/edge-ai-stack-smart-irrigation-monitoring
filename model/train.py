import numpy as np
import tensorflow as tf
from tensorflow import keras

# ──────────────────────────────────────────
# 1. GENERATE SYNTHETIC DATASET (1000 samples)
# Features: [moisture_raw (0–4095), temp_C (15–45), humidity_% (20–100)]
# Label   : 1 = Needs Water, 0 = OK
# ──────────────────────────────────────────
np.random.seed(42)
N = 1000

moisture = np.random.randint(0, 4096, N).astype(np.float32)
temp     = np.random.uniform(15, 45,  N).astype(np.float32)
humidity = np.random.uniform(20, 100, N).astype(np.float32)

# Labelling logic:
#   - Low moisture                          → always needs water
#   - High moisture                         → always ok
#   - Mid moisture + high temp + low humid  → needs water (fast evaporation)
#   - Mid moisture + low temp  + high humid → ok (slow evaporation)
def label(m, t, h):
    if m < 1200:
        return 1                      # dry soil — always needs water
    elif m > 2800:
        return 0                      # wet soil — always ok
    else:
        # borderline zone: combine temp and humidity into evaporation risk
        evap_risk = (t / 45.0) + (1 - h / 100.0)   # 0–2 scale
        return 1 if evap_risk > 0.9 else 0

labels = np.array([label(m, t, h) for m, t, h in zip(moisture, temp, humidity)],
                  dtype=np.float32)

X = np.column_stack([moisture, temp, humidity])
y = labels

print(f"Dataset: {N} samples")
print(f"  Needs Water : {int(y.sum())}")
print(f"  OK          : {int((1 - y).sum())}\n")

# ──────────────────────────────────────────
# 2. NORMALIZE
# ──────────────────────────────────────────
X_mean = X.mean(axis=0)
X_std  = X.std(axis=0)
X_norm = (X - X_mean) / X_std

print(f"Moisture — mean: {X_mean[0]:.2f}, std: {X_std[0]:.2f}")
print(f"Temp     — mean: {X_mean[1]:.2f}, std: {X_std[1]:.2f}")
print(f"Humidity — mean: {X_mean[2]:.2f}, std: {X_std[2]:.2f}")
print("Save these — you need them in the ESP32 code!\n")

# ──────────────────────────────────────────
# 3. TRAIN / VALIDATION SPLIT (80 / 20)
# ──────────────────────────────────────────
idx   = np.random.permutation(N)
split = int(0.8 * N)

X_train, X_val = X_norm[idx[:split]], X_norm[idx[split:]]
y_train, y_val = y[idx[:split]],      y[idx[split:]]

# ──────────────────────────────────────────
# 4. BUILD MODEL
# ──────────────────────────────────────────
model = keras.Sequential([
    keras.layers.Input(shape=(3,)),       # 3 inputs now
    keras.layers.Dense(16, activation='relu'),
    keras.layers.Dense(8,  activation='relu'),
    keras.layers.Dense(1,  activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# ──────────────────────────────────────────
# 5. TRAIN WITH EARLY STOPPING
# ──────────────────────────────────────────
early_stop = keras.callbacks.EarlyStopping(
    monitor='val_loss', patience=10, restore_best_weights=True
)

model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=200,
    batch_size=32,
    callbacks=[early_stop],
    verbose=1
)

_, train_acc = model.evaluate(X_train, y_train, verbose=0)
_, val_acc   = model.evaluate(X_val,   y_val,   verbose=0)
print(f"\nTrain accuracy : {train_acc*100:.1f}%")
print(f"Val   accuracy : {val_acc*100:.1f}%")

# ──────────────────────────────────────────
# 6. CONVERT TO TFLITE (quantized int8)
# ──────────────────────────────────────────
def representative_dataset():
    for i in range(len(X_train)):
        yield [X_train[i:i+1]]

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type  = tf.int8
converter.inference_output_type = tf.int8

tflite_model = converter.convert()

with open("model.tflite", "wb") as f:
    f.write(tflite_model)
print(f"\nmodel.tflite saved — size: {len(tflite_model)} bytes")

# ──────────────────────────────────────────
# 7. EXPORT C HEADER FOR ESP32
# ──────────────────────────────────────────
hex_array = ", ".join(f"0x{b:02x}" for b in tflite_model)
c_code = f"""// Auto-generated — paste into your Arduino/Wokwi project

const unsigned char model_data[] = {{
  {hex_array}
}};
const unsigned int model_data_len = {len(tflite_model)};

// Normalization constants — use these to scale inputs before inference
const float MOISTURE_MEAN = {X_mean[0]:.4f}f;
const float MOISTURE_STD  = {X_std[0]:.4f}f;
const float TEMP_MEAN     = {X_mean[1]:.4f}f;
const float TEMP_STD      = {X_std[1]:.4f}f;
const float HUMIDITY_MEAN = {X_mean[2]:.4f}f;
const float HUMIDITY_STD  = {X_std[2]:.4f}f;
"""

with open("model_data.h", "w") as f:
    f.write(c_code)

print("model_data.h saved — copy this into your Wokwi/Arduino project")
print("\nDone!")