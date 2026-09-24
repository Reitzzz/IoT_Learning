import json

import paho.mqtt.client as mqtt

from app.config import BROKER, COMMAND_TOPIC, PORT


def publish_command(command: str) -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT, 60)
    client.publish(COMMAND_TOPIC, json.dumps({"command": command}))
    client.disconnect()
