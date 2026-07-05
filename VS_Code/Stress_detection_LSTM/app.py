from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from datetime import datetime
import joblib
import os
import time
from collections import deque

app = Flask(__name__)

# ===============================
# LOAD MODEL & SCALER
# ===============================
MODEL_PATH = "model/lstm_model.h5"
SCALER_PATH = "model/scaler.pkl"

model = None
scaler = None
model_error_message = None

try:
    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        print("✅ Model loaded")
    else:
        print("⚠ Model not found")
except Exception as e:
    model_error_message = str(e)

try:
    if os.path.exists(SCALER_PATH):
        scaler = joblib.load(SCALER_PATH)
        print("✅ Scaler loaded")
    else:
        print("⚠ Scaler not found")
except Exception as e:
    print(e)

# ===============================
# BUFFER FOR LSTM
# ===============================
sequence_buffer = deque(maxlen=5)

# ===============================
# CSV SETUP
# ===============================
CSV_FILE = "dataset/live_data.csv"
os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=[
        "timestamp",
        "temperature",
        "vibration",
        "current",
        "stress_score",
        "status"
    ]).to_csv(CSV_FILE, index=False)

# ===============================
# AUTO TIMEOUT SYSTEM
# ===============================
last_update_time = time.time()
DATA_TIMEOUT = 15  # seconds

# ===============================
# LIVE DATA STORAGE
# ===============================
latest_data = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "temperature": 0,
    "vibration": 0,
    "current": 0,
    "stress_score": 0,
    "status": "NO SIGNAL",
    "model_error": None
}

# =====================================
# HOME PAGE
# =====================================
@app.route("/")
def dashboard():
    return render_template("index.html", error=model_error_message)

# =====================================
# GET LIVE DATA (AUTO RESET IF OFFLINE)
# =====================================
@app.route("/get_data")
def get_data():
    global latest_data

    if time.time() - last_update_time > DATA_TIMEOUT:
        latest_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": 0,
            "vibration": 0,
            "current": 0,
            "stress_score": 0,
            "status": "NO SIGNAL",
            "model_error": model_error_message
        }

    return jsonify(latest_data)

# =====================================
# RECEIVE DATA FROM ESP32
# =====================================
@app.route("/data", methods=["POST"])
def receive_data():
    global latest_data, last_update_time

    last_update_time = time.time()

    data = request.get_json()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    temperature = float(data.get("temperature", 0))
    vibration = float(data.get("vibration", 0))
    current = float(data.get("current", 0))

    # Receive status directly from ESP32
    status = data.get("status", "UNKNOWN")

    # Stress score based on ESP32 status
    if status == "NORMAL":
        stress_score = 20

    elif status == "WARNING":
        stress_score = 60

    elif status == "STRESS":
        stress_score = 100

    else:
        stress_score = 0
    # try:
    #     # ===============================
    #     # ML MODEL
    #     # ===============================
    
    #     if mode is not None and scaler is not None:

    #         input_data = np.array([[temperature, vibration, current]])
    #         scaled = scaler.transform(input_data)
    #         sequence_buffer.append(scaled[0])

    #         if len(sequence_buffer) == 5:
    #             X_input = np.array(sequence_buffer)
    #             X_input = np.expand_dims(X_input, axis=0)

    #             prediction = model.predict(X_input, verbose=0)
    #             predicted_class = np.argmax(prediction)
    #             confidence = float(np.max(prediction)) * 100

    #             if predicted_class == 0:
    #                 status = "Normal"
    #                 stress_score = int(confidence * 0.3)

    #             elif predicted_class == 1:
    #                 status = "Warning"
    #                 stress_score = int(40 + confidence * 0.3)

    #             else:
    #                 status = "Critical"
    #                 stress_score = int(70 + confidence * 0.3)

    #     # ===============================
    #     # FALLBACK
    #     # ===============================
    #     else:
    #         if temperature > 60:
    #             status = "Critical"
    #             stress_score = 80
    #         elif temperature > 45:
    #             status = "Warning"
    #             stress_score = 50
    #         else:
    #             status = "Normal"
    #             stress_score = int(20 + temperature * 0.2)

    # except Exception as e:
    #     print("Inference error:", e)
    #     status = "Error"
    #     stress_score = 0

    # ===============================
    # UPDATE LIVE DATA
    # ===============================
    latest_data = {
        "timestamp": timestamp,
        "temperature": temperature,
        "vibration": vibration,
        "current": current,
        "stress_score": stress_score,
        "status": status,
        "model_error": model_error_message
    }

    # ===============================
    # SAVE TO CSV
    # ===============================
    try:
        pd.DataFrame([{
            "timestamp": timestamp,
            "temperature": temperature,
            "vibration": vibration,
            "current": current,
            "stress_score": stress_score,
            "status": status
        }]).to_csv(
            CSV_FILE,
            mode="a",
            header=False,
            index=False
        )
    except Exception as e:
        print("CSV error:", e)

    print(latest_data)

    return jsonify({
        "message": "Data received",
        "status": status
    })

# =====================================
# RUN SERVER
# =====================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)