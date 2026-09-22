import json
import random

import paho.mqtt.client as mqtt

from config import BROKER, COMMAND_TOPIC, PORT


command = random.choice(["START", "STOP", "RESET"])

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT, 60)

message = json.dumps({"command": command})
client.publish(COMMAND_TOPIC, message)
print(f"已发布：{message}")
client.disconnect()
