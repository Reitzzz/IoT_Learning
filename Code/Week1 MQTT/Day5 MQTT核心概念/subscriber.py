import paho.mqtt.client as mqtt

from config import BROKER, PORT, TOPIC


def on_message_action(client, userdata, msg):
    print(msg.payload.decode())


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="subscriber-demo-001",
    clean_session=False,
)

# clean_session=False在subscriber里的作用：Broker在publisher正常 subscriber断连时尽量保留这期间的QoS 1/2消息
# 要真正触发离线消息缓存，subscribe 的 qos 必须使用 1 或 2。

client.on_message = on_message_action

client.connect(BROKER, PORT, 60)

client.subscribe(TOPIC, qos=1)

client.loop_forever()
