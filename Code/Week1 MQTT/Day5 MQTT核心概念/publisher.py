import json
import time

import paho.mqtt.client as mqtt

from config import BROKER, PORT, STATUS_TOPIC, TOPIC

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="publisher-demo-001",
    clean_session=False,
)

# clean_session在publisher里的作用：Broker保留尚未完成的 QoS 1/2 发送状态，重连后继续相关协议流程

client.will_set(
    STATUS_TOPIC,
    payload=json.dumps({"status": "OFFLINE"}),
    qos=1,
    retain=True,
)

client.connect(BROKER, PORT, 60)
# Keep Alive，单位是秒。意思是：连接空闲达到设置时间后，Paho 会发送心跳；Broker 回复 PINGRESP。如果长时间得不到回复，客户端会认为连接断开。
# Paho 的心跳需要 loop_start() 或 loop_forever() 驱动，仅设置 Keep Alive 不会自动发送 PINGREQ。
client.loop_start()
client.publish(
    STATUS_TOPIC,
    json.dumps({"status": "RUNNING"}),
    qos=1,
    retain=True,
)

while True:
    data = {
        "temperature": 34.2,
        "rpm": 1460,
        "status": "RUNNING",
    }

    message = json.dumps(data)
    client.publish(TOPIC, message, qos=1, retain=True)
    #qos=0：最多发送一次 不填参数则默认为qos=0
    #下面使用 qos=1，用于演示 Broker 对持久 Session 的 QoS 1/2 离线消息缓存。
    #retain=True：Broker保留Publisher发送的最新一条消息，转发给新加群的Subscriber
    time.sleep(1)
