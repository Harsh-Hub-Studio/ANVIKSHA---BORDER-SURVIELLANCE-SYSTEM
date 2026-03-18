import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# Settings from your project
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "border/alerts"

client = mqtt.Client()

try:
    client.connect(MQTT_BROKER, MQTT_PORT)
    
    # Simulate a fake intruder detection
    fake_data = {
        "type": "INTRUSION",
        "message": "CRITICAL: Suspicious activity detected near Sector 7",
        "timestamp": datetime.now().isoformat(),
        "location": "23.81606, 86.44212",
        "confidence": 0.98
    }

    print(f"Sending mock alert to {MQTT_TOPIC}...")
    client.publish(MQTT_TOPIC, json.dumps(fake_data))
    client.disconnect()
    print("Success! Check your browser dashboard.")

except Exception as e:
    print(f"Error: Could not connect to MQTT. Is Mosquitto running? \n{e}")