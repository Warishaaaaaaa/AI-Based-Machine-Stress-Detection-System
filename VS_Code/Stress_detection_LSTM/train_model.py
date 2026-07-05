import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import to_categorical

# Load dataset
df = pd.read_csv("machine_stress_data.csv")

X = df.drop("label", axis=1).values
y = df["label"].values

# Normalize
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

# Save scaler
joblib.dump(scaler, "model/scaler.pkl")

# Create sequences
def create_sequences(X, y, time_steps=5):

    Xs, ys = [], []

    for i in range(len(X) - time_steps):
        Xs.append(X[i:i+time_steps])
        ys.append(y[i+time_steps])

    return np.array(Xs), np.array(ys)

X_seq, y_seq = create_sequences(X, y)

# One-hot encoding
y_seq = to_categorical(y_seq, num_classes=3)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_seq,
    y_seq,
    test_size=0.2,
    random_state=42
)

# LSTM Model
model = Sequential([
    LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2])),
    Dense(32, activation='relu'),
    Dense(3, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train
model.fit(
    X_train,
    y_train,
    epochs=20,
    batch_size=16,
    validation_data=(X_test, y_test)
)

# Save model
model.save("model/lstm_model.h5")

# Evaluate
loss, accuracy = model.evaluate(X_test, y_test)

print(f"Accuracy: {accuracy * 100:.2f}%")