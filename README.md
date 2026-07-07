# AI-Based Machine Stress Detection System for the Textile Industry Using Multi-Sensor Data

## Project Overview

This project is an AI-powered machine stress detection system developed for textile spinning machines. The system collects sensor data using an ESP32 microcontroller, processes the information using machine learning models, and predicts machine stress levels in real time. The goal is to support predictive maintenance, reduce unexpected machine failures, and improve operational efficiency.

---

## Features

- Real-time sensor data acquisition
- Temperature monitoring
- Vibration monitoring
- LCD display for live readings
- Machine stress prediction using an LSTM model
- Web-based interface for monitoring
- Trained machine learning model
- Data preprocessing and visualization

---

## Technologies Used

### Hardware

- ESP32
- Temperature Sensor
- Vibration Sensor
- Current Sensor
- LCD Display

### Software

- Arduino IDE
- Python
- Flask
- Visual Studio Code
- Google Colab
- TensorFlow
- Scikit-learn
- Pandas
- NumPy
- Matplotlib

---

## Project Structure

```
Arduino_Code/
ML_Model/
VS_Code/
Dataset/
Images/

```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/Warishaaaaaaa/AI-Based-Machine-Stress-Detection-System.git
```

### Install Python packages

```bash
pip install -r requirements.txt
```

### Run the Flask application

```bash
python app.py
```

---

## Machine Learning Workflow

1. Collect sensor data.
2. Preprocess the dataset.
3. Train the LSTM model.
4. Save the trained model.
5. Predict machine stress.
6. Display results through the web application.

---

## Results

The trained model successfully predicts machine stress using multi-sensor input data. Model evaluation includes confusion matrix visualization and performance graphs generated during training.

---

## Future Improvements

- Cloud-based monitoring
- IoT dashboard integration
- Mobile application support
- Additional industrial sensors
- Automatic maintenance alerts

---

## Author

Warisha Amjad 

Bachelor of Science in Software Engineering

Final Year Project
