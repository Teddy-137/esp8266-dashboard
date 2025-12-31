import json
import paho.mqtt.client as mqtt
import dotenv
import os

dotenv.load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt.example.com")
MQTT_PORT = 8883
MQTT_USER = os.getenv("MQTT_USER", "user")
MQTT_PASS = os.getenv("MQTT_PASS", "pass")

TOPIC_RELAY = "ietp/relay"
TOPIC_SENSOR = "ietp/sensor"

relay_state = False


def on_message(client, userdata, msg):
    global relay_state
    if msg.topic == TOPIC_RELAY:
        relay_state = msg.payload.decode() == "ON"


client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set()
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(TOPIC_SENSOR)
client.loop_start()
