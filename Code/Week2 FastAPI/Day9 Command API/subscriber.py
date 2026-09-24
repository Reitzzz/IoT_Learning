import paho.mqtt.client as mqtt
import json

from config import BROKER, PORT, COMMAND_TOPIC

device_status = "RUNNING"


def action_on_message(client, userdata, msg):
    global device_status

    data = json.loads(msg.payload.decode())

    if data["command"] == "STOP":
        device_status = "STOPPED"
        print("设备状态：", device_status)

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_message = action_on_message

client.connect(BROKER, PORT, 60)

client.subscribe(COMMAND_TOPIC)

client.loop_forever()
