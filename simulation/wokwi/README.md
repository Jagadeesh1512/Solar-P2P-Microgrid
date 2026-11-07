# Wokwi ESP32 Smart Meter Simulation

This directory contains the hardware simulation for the IoT Smart Meter node using ESP32.

### Simulated Hardware Features:
- **ESP32 DevKit v4** with virtual WiFi & MQTT connectivity.
- **Solar Generation Potentiometer**: Simulates rooftop photovoltaic output (0.0 to 6.0 kW).
- **Home Load Potentiometer**: Simulates fluctuating real-time domestic appliance loads (0.2 to 5.0 kW).
- **Battery SoC Potentiometer**: Simulates battery storage charge level (20% to 100%).
- **I2C OLED Display (SSD1306)**: Shows live Net Balance (Surplus/Deficit), generation, and grid connection status.
- **Status LEDs / Relays**: Shows grid connection status and battery charging/discharging relay.

### How to Run:
1. **In Browser:**
   - Visit [Wokwi ESP32 Simulator](https://wokwi.com/projects/new/esp32).
   - Paste the contents of `diagram.json` into the **diagram.json** tab.
   - Paste the contents of `sketch.ino` into the **sketch.ino** tab.
   - **Add Required Libraries**:
     - Click the **Library Manager** tab (or the `+` button in the file tabs to add `libraries.txt`).
     - Add:
       ```
       PubSubClient
       Adafruit SSD1306
       Adafruit GFX Library
       ```
   - Click the **Play / Start Simulation** button directly.
   - *(Note: You do not need to click "Save Project" to run the simulation. If you do click save while not logged into Wokwi, it will display a JSON syntax error).*
2. **In VS Code:**
   - Install the **Wokwi Simulator** extension.
   - Open this directory and press `F1` -> `Wokwi: Start Simulator`.
3. The simulated ESP32 connects to `Wokwi-GUEST` and starts broadcasting telemetry to the MQTT broker topic `microgrid/telemetry/house_alpha`.
