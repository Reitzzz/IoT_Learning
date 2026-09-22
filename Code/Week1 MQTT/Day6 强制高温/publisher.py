import json
import msvcrt
import random
import time

import paho.mqtt.client as mqtt

from config import BROKER, COMMAND_TOPIC, PORT, TOPIC


device_status = "RUNNING"
force_overheat = False


def read_keyboard():
    global force_overheat

    if msvcrt.kbhit() and msvcrt.getwch().lower() == "h":
        force_overheat = True
        print("已触发强制高温")


def get_temperature_level(temperature):
    if temperature < 70:
        return "NORMAL"
    elif temperature <= 85:
        return "WARNING"
    else:
        return "ALARM"


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
    read_keyboard()

    if force_overheat:
        temperature = 90
        force_overheat = False
    else:
        temperature = random.uniform(32, 40)

    rpm = random.randint(1450, 1550) if device_status == "RUNNING" else 0

    data = {
        "temperature": temperature,
        "temperature_level": get_temperature_level(temperature),
        "rpm": rpm,
        "status": device_status,
        "last_seen": time.time(),
    }

    client.publish(TOPIC, json.dumps(data))
    time.sleep(1)
