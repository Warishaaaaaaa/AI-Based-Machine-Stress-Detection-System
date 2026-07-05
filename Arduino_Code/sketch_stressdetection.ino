#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// =========================
// WIFI SETTINGS
// =========================
const char* ssid = "stress";
const char* password = "12345678";
const char* serverUrl = "http://10.219.1.71:5000/data";

// =========================
// PINS
// =========================
#define DHTPIN 4
#define DHTTYPE DHT11

#define RELAY_PIN 33
#define VIBRATION_PIN 34

#define GREEN_LED 25
#define YELLOW_LED 26
#define RED_LED 27

#define BUZZER 14

#define RELAY_ON LOW
#define RELAY_OFF HIGH

// =========================
// THRESHOLDS
// =========================
// const float WARNING_TEMP_MIN = 38.0;
// const float WARNING_TEMP_MAX = 40.0;
// const float STRESS_TEMP = 40.0;

const float NORMAL_TEMP_MAX = 35.0;
const float WARNING_TEMP_MIN = 36.0;
const float WARNING_TEMP_MAX = 37.7;
const float STRESS_TEMP = 40.0;

const float CURRENT_MIN = 0.30;
const float CURRENT_MAX = 0.90;

// =========================
// OBJECTS
// =========================
DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// =========================
// VARIABLES
// =========================
unsigned long lastTimeSent = 0;
const unsigned long sendInterval = 3000;

float current = 0.0;
String statusText = "INIT";

// =========================
// SETUP
// =========================
void setup() {

  Serial.begin(115200);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("Machine Monitor");
  lcd.setCursor(0, 1);
  lcd.print("Starting...");
  delay(2000);

  lcd.clear();

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(VIBRATION_PIN, INPUT);

  pinMode(GREEN_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  pinMode(BUZZER, OUTPUT);

  digitalWrite(RELAY_PIN, RELAY_OFF);

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(YELLOW_LED, LOW);
  digitalWrite(RED_LED, LOW);

  digitalWrite(BUZZER, LOW);

  dht.begin();

  WiFi.begin(ssid, password);

  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connected");

  delay(1500);
  lcd.clear();

  randomSeed(millis());
}

// =========================
// LOOP
// =========================
void loop() {

  float temperature = dht.readTemperature();

  // SW420 vibration sensor
  int vibrationRaw = digitalRead(VIBRATION_PIN);

  // LOW = vibration detected
  int vibration = !vibrationRaw;

  if (isnan(temperature)) {

    Serial.println("DHT ERROR");

    lcd.setCursor(0, 0);
    lcd.print("DHT ERROR       ");

    delay(1000);
    return;
  }

  // =========================
  // STRESS DETECTION
  // =========================

  bool stress = false;

  if (vibration == 1 || temperature > STRESS_TEMP) {
    stress = true;
  }

  if (stress) {

    // MACHINE STOP
    digitalWrite(RELAY_PIN, RELAY_OFF);

    current = 0.0;

    statusText = "STRESS";

    digitalWrite(GREEN_LED, LOW);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(RED_LED, HIGH);

    digitalWrite(BUZZER, HIGH);
  }
  else {

    // MACHINE RUNNING
    digitalWrite(RELAY_PIN, RELAY_ON);

    current = random(
                (int)(CURRENT_MIN * 100),
                (int)(CURRENT_MAX * 100) + 1
              ) / 100.0;

    if (temperature >= WARNING_TEMP_MIN &&
        temperature <= WARNING_TEMP_MAX) {

      statusText = "WARNING";

      digitalWrite(GREEN_LED, LOW);
      digitalWrite(YELLOW_LED, HIGH);
      digitalWrite(RED_LED, LOW);

      digitalWrite(BUZZER, LOW);
    }
    else {

      statusText = "NORMAL";

      digitalWrite(GREEN_LED, HIGH);
      digitalWrite(YELLOW_LED, LOW);
      digitalWrite(RED_LED, LOW);

      digitalWrite(BUZZER, LOW);
    }
  }

  // =========================
  // SERIAL MONITOR
  // =========================

  Serial.print("Temp: ");
  Serial.print(temperature);

  Serial.print(" | Vib: ");
  Serial.print(vibration);

  Serial.print(" | Current: ");
  Serial.print(current, 2);

  Serial.print(" | Status: ");
  Serial.println(statusText);

  // =========================
  // LCD DISPLAY
  // =========================

  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temperature, 1);

  lcd.print(" V:");
  lcd.print(vibration);

  lcd.print("  ");

  lcd.setCursor(0, 1);

  lcd.print("C:");
  lcd.print(current, 2);

  lcd.print(" ");

  lcd.print(statusText);

  lcd.print("   ");

  // =========================
  // SEND TO FLASK
  // =========================

  if ((millis() - lastTimeSent >= sendInterval) &&
      WiFi.status() == WL_CONNECTED) {

    lastTimeSent = millis();

    HTTPClient http;

    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json =
      "{\"temperature\":" + String(temperature, 1) +
      ",\"vibration\":" + String(vibration) +
      ",\"current\":" + String(current, 2) +
      ",\"status\":\"" + statusText + "\"}";

    Serial.println("JSON SENT:");
    Serial.println(json);

    int httpResponseCode = http.POST(json);

    Serial.print("HTTP Response: ");
    Serial.println(httpResponseCode);

    http.end();
  }

  delay(500);
}