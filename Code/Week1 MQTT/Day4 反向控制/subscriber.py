import paho.mqtt.client as mqtt

from config import BROKER, PORT, TOPIC


def on_message_action(client, userdata, msg):
    print(msg.payload.decode())

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message_action

client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
client.loop_forever()
