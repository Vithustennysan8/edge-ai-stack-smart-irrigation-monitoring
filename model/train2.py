import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ──────────────────────────────────────────
# 1. GENERATE DATASET
# ──────────────────────────────────────────
np.random.seed(42)
N = 100000

moisture = np.random.randint(0, 4096, N).astype(np.float32)
temp     = np.random.uniform(15, 45,  N).astype(np.float32)
humidity = np.random.uniform(20, 100, N).astype(np.float32)

def label(m, t, h):
    if m < 1200:
        return 1
    elif m > 2800:
        return 0
    else:
        evap_risk = (t / 45.0) + (1 - h / 100.0)
        return 1 if evap_risk > 0.9 else 0

y = np.array([label(m, t, h) for m, t, h in zip(moisture, temp, humidity)])

X = np.column_stack([moisture, temp, humidity])

# ──────────────────────────────────────────
# 2. NORMALIZE
# ──────────────────────────────────────────
X_mean = X.mean(axis=0)
X_std  = X.std(axis=0)
X_norm = (X - X_mean) / X_std

print("=== NORMALIZATION VALUES (SAVE THESE) ===")
print(f"MOISTURE_MEAN = {X_mean[0]}")
print(f"MOISTURE_STD  = {X_std[0]}")
print(f"TEMP_MEAN     = {X_mean[1]}")
print(f"TEMP_STD      = {X_std[1]}")
print(f"HUMIDITY_MEAN = {X_mean[2]}")
print(f"HUMIDITY_STD  = {X_std[2]}")

# ──────────────────────────────────────────
# 3. TRAIN TEST SPLIT
# ──────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_norm, y, test_size=0.2, random_state=42
)

# ──────────────────────────────────────────
# 4. TRAIN MODEL
# ──────────────────────────────────────────
model = LogisticRegression()
model.fit(X_train, y_train)

# ──────────────────────────────────────────
# 5. EVALUATE
# ──────────────────────────────────────────
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"\nAccuracy: {acc * 100:.2f}%")

# ──────────────────────────────────────────
# 6. EXPORT MODEL PARAMETERS
# ──────────────────────────────────────────
weights = model.coef_[0]
bias = model.intercept_[0]

print("\n=== MODEL PARAMETERS ===")
print(f"W1 (moisture) = {weights[0]}")
print(f"W2 (temp)     = {weights[1]}")
print(f"W3 (humidity) = {weights[2]}")
print(f"BIAS          = {bias}")

# ──────────────────────────────────────────
# 7. GENERATE C CODE FOR ESP32
# ──────────────────────────────────────────
c_code = f"""
// Logistic Regression Model for ESP32

// Normalization
const float MOISTURE_MEAN = {X_mean[0]:.6f}f;
const float MOISTURE_STD  = {X_std[0]:.6f}f;
const float TEMP_MEAN     = {X_mean[1]:.6f}f;
const float TEMP_STD      = {X_std[1]:.6f}f;
const float HUMIDITY_MEAN = {X_mean[2]:.6f}f;
const float HUMIDITY_STD  = {X_std[2]:.6f}f;

// Model weights
const float W1 = {weights[0]:.6f}f;
const float W2 = {weights[1]:.6f}f;
const float W3 = {weights[2]:.6f}f;
const float BIAS = {bias:.6f}f;
"""

with open("model_lr.h", "w") as f:
    f.write(c_code)

print("\nmodel_lr.h generated successfully!")