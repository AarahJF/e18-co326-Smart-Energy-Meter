#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "EmonLib.h"
#include <EEPROM.h>

LiquidCrystal_I2C lcd(0x27, 20, 4);

// WiFi credentials
const char *ssid = "Eng-Student";
const char *password = "3nG5tuDt";

// MQTT broker
const char *mqtt_server = "91.121.93.94";

// MQTT client
WiFiClient espClient;
PubSubClient client(espClient);

// EnergyMonitor and calibration constants
EnergyMonitor emon;
#define vCalibration 166.6 // Adjusted calibration factor for 230V
#define currCalibration 0.50

// Other variables
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];
int value = 0;
float kWh = 0;
unsigned long lastmillis = millis();
unsigned long timerInterval = 5000; // 5 seconds
unsigned long previousMillis = 0;

void setup_wifi()
{
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char *topic, byte *payload, unsigned int length)
{
  // Handle incoming MQTT messages if needed
}

void reconnect()
{
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str()))
    {
      Serial.println("connected");
      client.publish("device/temp", "hello world");
      client.subscribe("device/led");
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void myTimerEvent()
{
  emon.calcVI(20, 2000);
  kWh = kWh + emon.apparentPower * (millis() - lastmillis) / 3600000000.0;
  yield();
  Serial.print("Vrms: ");
  Serial.print(emon.Vrms, 2);
  Serial.print("V");
  EEPROM.put(0, emon.Vrms);
  delay(100);

  Serial.print("\tIrms: ");
  Serial.print(emon.Irms, 4);
  Serial.print("A");
  EEPROM.put(4, emon.Irms);
  delay(100);

  Serial.print("\tPower: ");
  Serial.print(emon.apparentPower, 4);
  Serial.print("W");
  EEPROM.put(8, emon.apparentPower);
  delay(100);

  Serial.print("\tkWh: ");
  Serial.print(kWh, 5);
  Serial.println("kWh");
  EEPROM.put(12, kWh);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Vrms:");
  lcd.print(emon.Vrms, 2);
  lcd.print("V");
  lcd.setCursor(0, 1);
  lcd.print("Irms:");
  lcd.print(emon.Irms, 4);
  lcd.print("A");
  lcd.setCursor(0, 2);
  lcd.print("Power:");
  lcd.print(emon.apparentPower, 4);
  lcd.print("W");
  lcd.setCursor(0, 3);
  lcd.print("kWh:");
  lcd.print(kWh, 4);
  lcd.print("W");

  lastmillis = millis();
}

void setup()
{
  Serial.begin(115200);
  Wire.begin();
  lcd.begin(20, 4);
  lcd.backlight();
  emon.voltage(35, vCalibration, 1.7);
  emon.current(34, currCalibration);

  lcd.setCursor(3, 0);
  lcd.print("IoT Energy");
  lcd.setCursor(5, 1);
  lcd.print("Meter");
  delay(3000);
  lcd.clear();

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= timerInterval)
  {
    previousMillis = currentMillis;
    myTimerEvent();
  }

  if (currentMillis - lastMsg > 5000)
  {
    lastMsg = currentMillis;
    ++value;

    // Read sensor data
    emon.calcVI(20, 2000);
    float voltage = emon.Vrms;
    float current = emon.Irms;
    float power = emon.apparentPower;
    float kWh = kWh + power * (millis() - lastmillis) / 3600000000.0;

    // Publish the sensor data to MQTT topics
    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", voltage);
    client.publish("device/Voltage", msg);

    snprintf(msg, MSG_BUFFER_SIZE, "%.4f", current);
    client.publish("device/Current", msg);

    snprintf(msg, MSG_BUFFER_SIZE, "%.4f", power);
    client.publish("device/Power", msg);

    snprintf(msg, MSG_BUFFER_SIZE, "%.5f", kWh);
    client.publish("device/kWh", msg);

    // Print the parameter values in the Serial Monitor
    Serial.print("Voltage: ");
    Serial.print(voltage);
    Serial.print(" V  Current: ");
    Serial.print(current);
    Serial.print(" A  Power: ");
    Serial.print(power);
    Serial.print(" W  kWh: ");
    Serial.println(kWh, 5);
  }
}
