import json
import os
import paho.mqtt.client as mqtt
from threading import Lock

# ================= CONFIG =================

MQTT_BROKER = os.getenv(
    "MQTT_BROKER", "d48a04f1d00f465cb85d1e1d30ff4c4e.s1.eu.hivemq.cloud"
)
MQTT_PORT = 8883
MQTT_USER = os.getenv("MQTT_USER", "hivemq.webclient.1767187870295")
MQTT_PASS = os.getenv("MQTT_PASS", "cPI0:vW$u7;a6l8O?bUD")

TOPIC_SENSOR = "ietp/esp8266/data"
TOPIC_RELAY = "ietp/esp8266/relay"
TOPIC_STATUS = "ietp/esp8266/status"

# ================= SHARED STATE =================

latest_data = {
    "temperature": 0.0,
    "humidity": 0.0,
    "battery": 0,
}

relay_state = False
device_status = "OFFLINE"

state_lock = Lock()

# ================= MQTT CALLBACKS =================


def on_connect(client, userdata, flags, rc):
    print("MQTT connected:", rc)
    client.subscribe(TOPIC_SENSOR)
    client.subscribe(TOPIC_STATUS)


def on_message(client, userdata, msg):
    global relay_state, device_status

    payload = msg.payload.decode()

    with state_lock:
        if msg.topic == TOPIC_SENSOR:
            try:
                data = json.loads(payload)
                latest_data.update(
                    {
                        "temperature": data.get("temperature", 0.0),
                        "humidity": data.get("humidity", 0.0),
                        "battery": data.get("battery", 0),
                    }
                )
            except json.JSONDecodeError:
                print("Invalid sensor JSON")

        elif msg.topic == TOPIC_STATUS:
            device_status = payload


# ================= MQTT CLIENT =================

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()
