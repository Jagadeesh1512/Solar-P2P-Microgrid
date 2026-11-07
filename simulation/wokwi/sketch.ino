/*
  Decentralized Solar Microgrid - ESP32 Smart Meter Node
  Simulation Environment: Wokwi (ESP32 + Potentiometers + Relays + OLED Display)
  
  Measures:
  - Solar Generation (Simulated via Potentiometer 1 on Pin 34)
  - Home Load Consumption (Simulated via Potentiometer 2 on Pin 35)
  - Battery Voltage / SoC (Calculated or Potentiometer 3 on Pin 32)
  - Relay 1: Grid Tie-in / Islanding Switch (Pin 18)
  - Relay 2: Battery Charge/Discharge Controller (Pin 19)
  - I2C OLED (SDA: 21, SCL: 22) displays live Net Balance & Status
*/

#define MQTT_MAX_PACKET_SIZE 512
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Pin Definitions
const int PIN_SOLAR_ADC = 34;
const int PIN_LOAD_ADC = 35;
const int PIN_BATTERY_ADC = 32;
const int PIN_RELAY_GRID = 18;
const int PIN_RELAY_BATTERY = 19;
const int PIN_STATUS_LED = 2;

// Household Identity
const char* HOUSEHOLD_ID = "house_alpha";
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";

// MQTT Broker (Public test broker or local broker)
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC_TELEMETRY = "microgrid/telemetry/house_alpha";
const char* MQTT_TOPIC_CONTROL = "microgrid/control/house_alpha";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL = 1000; // 1 second

// Simulation State
float solarKw = 0.0;
float loadKw = 0.0;
float batterySoc = 75.0; // %
float netBalanceKw = 0.0;
bool gridRelayActive = true;
bool batteryRelayActive = true;

void setupOled() {
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    return;
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 10);
  display.println(F("Solar Smart Meter"));
  display.println(F("Booting ESP32..."));
  display.display();
}

void updateOled() {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(1);
  display.print(F("Node: "));
  display.println(HOUSEHOLD_ID);
  
  display.print(F("Solar: "));
  display.print(solarKw, 2);
  display.println(F(" kW"));

  display.print(F("Load : "));
  display.print(loadKw, 2);
  display.println(F(" kW"));

  display.print(F("Net  : "));
  if (netBalanceKw >= 0) display.print(F("+"));
  display.print(netBalanceKw, 2);
  display.println(F(" kW"));

  display.print(F("Batt : "));
  display.print(batterySoc, 1);
  display.println(F(" %"));

  display.print(F("Relay: "));
  display.println(gridRelayActive ? F("GRID CONNECTED") : F("ISLANDED"));

  display.display();
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Control message received: ");
  Serial.println(message);

  // Flexible check for false/true regardless of JSON whitespace or formatting
  if (message.indexOf("false") >= 0 || message.indexOf("\"grid_relay\":0") >= 0) {
    gridRelayActive = false;
    digitalWrite(PIN_RELAY_GRID, LOW);
    Serial.println("-> Action: Relay Cutoff triggered (ISLANDED)");
  } else if (message.indexOf("true") >= 0 || message.indexOf("\"grid_relay\":1") >= 0) {
    gridRelayActive = true;
    digitalWrite(PIN_RELAY_GRID, HIGH);
    Serial.println("-> Action: Relay Reconnected triggered (GRID CONNECTED)");
  }
  updateOled();
}

void reconnectMqtt() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32-SmartMeter-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe(MQTT_TOPIC_CONTROL);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 2 seconds");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  pinMode(PIN_RELAY_GRID, OUTPUT);
  pinMode(PIN_RELAY_BATTERY, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);
  
  digitalWrite(PIN_RELAY_GRID, HIGH);
  digitalWrite(PIN_RELAY_BATTERY, HIGH);
  digitalWrite(PIN_STATUS_LED, HIGH);

  setupOled();

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");

  client.setBufferSize(512);
  client.setKeepAlive(60);
  client.setServer(MQTT_BROKER, MQTT_PORT);
  client.setCallback(mqttCallback);
}

void loop() {
  if (!client.connected()) {
    reconnectMqtt();
  }
  client.loop();

  // Read Simulated Sensor Voltages (0-4095 ADC scale converted to kW)
  int rawSolar = analogRead(PIN_SOLAR_ADC);
  int rawLoad = analogRead(PIN_LOAD_ADC);
  int rawBatt = analogRead(PIN_BATTERY_ADC);

  // Scale: 0-4095 -> 0.0 to 6.0 kW peak solar
  solarKw = (rawSolar / 4095.0) * 6.0;
  // Scale: 0-4095 -> 0.2 to 5.0 kW home load
  loadKw = 0.2 + (rawLoad / 4095.0) * 4.8;
  // Scale: 0-4095 -> 20% to 100% battery SoC
  batterySoc = 20.0 + (rawBatt / 4095.0) * 80.0;

  netBalanceKw = solarKw - loadKw;

  if (millis() - lastTelemetryTime > TELEMETRY_INTERVAL) {
    lastTelemetryTime = millis();
    updateOled();

    // Construct Telemetry JSON Payload
    char jsonBuffer[256];
    snprintf(jsonBuffer, sizeof(jsonBuffer),
      "{\"household_id\":\"%s\",\"solar_kw\":%.2f,\"load_kw\":%.2f,\"net_kw\":%.2f,\"battery_soc\":%.1f,\"grid_relay\":%s}",
      HOUSEHOLD_ID,
      solarKw,
      loadKw,
      netBalanceKw,
      batterySoc,
      gridRelayActive ? "true" : "false"
    );

    boolean sent = client.publish(MQTT_TOPIC_TELEMETRY, jsonBuffer);
    Serial.print("Publishing telemetry: ");
    Serial.print(jsonBuffer);
    Serial.println(sent ? " -> [SUCCESS]" : " -> [FAILED]");
  }
}
