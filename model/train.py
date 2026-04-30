import numpy as np
import tensorflow as tf
from tensorflow import keras

# ──────────────────────────────────────────
# 1. GENERATE SYNTHETIC DATASET (2000 samples)
# Feature : [temp_C]  — single input
# Label   : 1 = Irrigate (too hot, plant stressed)
#           0 = OK (temperature is fine)
#
# Realistic plant temperature zones:
#   < 10°C  → too cold, don't irrigate
#   10–18°C → cool, ok
#   18–28°C → ideal, ok
#   28–35°C → warm, irrigate
#   > 35°C  → hot, definitely irrigate
# ──────────────────────────────────────────
np.random.seed(42)
N = 2000

temp = np.random.uniform(5, 45, N).astype(np.float32)

def label(t):
    if t < 10:
        return 0   # too cold — no irrigation needed
    elif t <= 28:
        return 0   # comfortable range — ok
    elif t <= 33:
        # borderline zone — probabilistic to add realism
        return 1 if np.random.rand() > 0.3 else 0
    else:
        return 1   # hot — irrigate

labels = np.array([label(t) for t in temp], dtype=np.float32)

X = temp.reshape(-1, 1)
y = labels

print(f"Dataset : {N} samples")
print(f"  Irrigate : {int(y.sum())} samples")
print(f"  OK       : {int((1-y).sum())} samples\n")

# ──────────────────────────────────────────
# 2. NORMALIZE
# ──────────────────────────────────────────
X_mean = X.mean(axis=0)
X_std  = X.std(axis=0)
X_norm = (X - X_mean) / X_std

print(f"Temp — mean: {X_mean[0]:.2f}°C, std: {X_std[0]:.2f}")
print("Save these — needed in ESP32 code!\n")

# ──────────────────────────────────────────
# 3. TRAIN / VALIDATION SPLIT (80 / 20)
# ──────────────────────────────────────────
split = int(0.8 * N)
idx   = np.random.permutation(N)

X_train, X_val = X_norm[idx[:split]], X_norm[idx[split:]]
y_train, y_val = y[idx[:split]],      y[idx[split:]]

# ──────────────────────────────────────────
# 4. BUILD MODEL (tiny — fits ESP32 memory)
# ──────────────────────────────────────────
model = keras.Sequential([
    keras.layers.Input(shape=(1,)),
    keras.layers.Dense(8,  activation='relu'),
    keras.layers.Dense(4,  activation='relu'),
    keras.layers.Dense(1,  activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# ──────────────────────────────────────────
# 5. TRAIN
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

// Normalization constants — use in ESP32 before passing to model
const float TEMP_MEAN = {X_mean[0]:.4f}f;
const float TEMP_STD  = {X_std[0]:.4f}f;
"""

with open("model_data.h", "w") as f:
    f.write(c_code)

print("model_data.h saved — copy into your Wokwi/Arduino project")
print("\nDone!")