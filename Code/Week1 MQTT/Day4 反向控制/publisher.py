import json
import random
import time

import paho.mqtt.client as mqtt

from config import BROKER, COMMAND_TOPIC, PORT, TOPIC


device_status = "RUNNING"


def on_message_action(client, userdata, msg):
    global device_status
    data = json.loads(msg.payload.decode())
    command = data.get("command")

    if command == "STOP":
        device_status = "STOPPED"
    elif command in {"START", "RESET"}:
        device_status = "RUNNING"

    print(f"收到命令：{command}，当前状态：{device_status}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message_action

client.connect(BROKER, PORT, 60)
client.loop_start()
client.subscribe(COMMAND_TOPIC)

while True:
    temperature = random.uniform(32, 40)
    rpm = random.randint(1450, 1550) if device_status == "RUNNING" else 0

    data = {
        "temperature": temperature,
        "rpm": rpm,
        "status": device_status,
        "last_seen": time.time(),
    }

    client.publish(TOPIC, json.dumps(data))
    time.sleep(1)
