import json
import paho.mqtt.client as mqtt

from config import BROKER, PORT, COMMAND_TOPIC


def publish_command(command: str):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT, 60)

    message = json.dumps({"command": command})
    client.publish(COMMAND_TOPIC, message)

    client.disconnect()