//Project Description
The AI-Based Water Leakage Detection System is an IoT-based monitoring system designed to identify possible water leakage by continuously monitoring water flow, pressure, and other sensor readings. It collects sensor data through an ESP32 microcontroller and transmits the readings over Wi-Fi using the MQTT communication protocol.

The MQTT messages are received through a HiveMQ Cloud broker and displayed on a Streamlit dashboard. The dashboard provides live sensor readings, graphs, system status, and leakage alerts. When abnormal readings indicate a possible leak, the system can display a warning and activate a buzzer, depending on the connected hardware and configured detection logic.

The project aims to reduce water wastage, improve monitoring, and provide early warnings so that users can respond to possible leakage conditions.

//Setup instructions
Step 1: Plotting of Live input output raw data.
Step 2: Configure EMQX Cloud
1. Sign in to your HiveMQ Cloud account.
2. Create or open your MQTTX.
3. Obtain the broker hostname and port.
4. Create MQTT credentials with appropriate permissions.
5. Configure the ESP32 to publish readings to your sensor topic, such as water/sensors.
6. Configure the Python dashboard to subscribe to the same topic.
Step 3: Verify that sensor readings are being published successfully.
A typical MQTT message could look like this:
{
  "flow_rate": 2.5,
  "pressure": 1.8,
  "temperature": 28.4,
  "moisture": 0,
  "status": "NORMAL"
}
These are illustrative values, not actual readings from your hardware. Your firmware and Python application must agree on the message format and field names.
Step 4: Configure the Python application
Organize your project files in a structure similar to this:
AI-Water-Leakage-Detection/
with mqtt.py                  MQTT connection and Dashboard
requirements.txt              Dependencies

.streamlit/secrets.toml       Local secrets

data/                         Optional local records
Step 5: Configure MQTT credentials
Step 6: Run the dashboard locally
Step 7: Push all the Python code in Github Repository.
Step 7: Deploy the dashboard online.
//Usage instructions
Once the hardware, MQTT connection, and dashboard are configured, use the system as follows.
1. Start the system
Power the ESP32 and sensors, verify the Wi-Fi connection, and confirm that the MQTT broker is reachable.
2. Open the dashboard
Launch the local Streamlit application or open its deployed URL. Check the latest flow, pressure, temperature, and moisture readings that are available.
3. Monitor the graphs
Observe the live graphs and compare readings against the system's normal operating range. Look for unexpected flow or pressure changes.
4. Respond to warnings
When the configured detection logic identifies a possible leak, check the displayed status and timestamp. If a buzzer is connected and configured, verify that the local warning operates.
5. Review stored data
Use the saved CSV records or database to review previous readings, investigate abnormal events, and compare normal and suspected leakage conditions.
6. Interpreting system status
Status	Meaning	Recommended action
Normal	Readings are within the configured normal range	Continue monitoring
Leakage suspected	One or more readings meet the configured abnormal conditions	Inspect the pipe and verify the readings
Sensor error	Readings are missing or invalid	Check the sensor wiring and connections
MQTT disconnected	Communication with the broker has failed	Check Wi-Fi, broker settings, credentials, and TLS configuration

A warning indicates a possible leak, not definitive proof. The system's accuracy depends on sensor calibration, detection logic, and the conditions used for testing.
7. Testing the project
Before demonstrating the project, perform these checks:
1. Normal condition: Run the system with no intentional leak and confirm that the readings and status are reasonable.
2. Abnormal condition: Use a safe, controlled test setup to introduce a simulated or actual detectable leakage condition.
3. Pressure variation: Confirm that the dashboard responds to changes in pressure.
4. Sensor failure: Disconnect or simulate a failed sensor input and verify the error-handling behavior.
5. Network interruption: Temporarily interrupt Wi-Fi and verify the reconnection or disconnection message.
6. Data persistence: Restart the dashboard and check whether previously saved records remain available.
7. Alert verification: Confirm that the warning message and buzzer, if installed, respond as intended.


https://github.com/user-attachments/assets/8dc8cf1b-8154-4e38-99fc-3cca5b38de28
