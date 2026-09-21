import json
import threading

import paho.mqtt.client as mqtt

from config import BROKER, PORT, TOPIC


# Day1 的 TOPIC 是一个具体主题：.../device/001/telemetry
# Day2 要验证的是它的上级过滤器：.../device/001/#
TOPIC_ROOT = TOPIC.rsplit("/", 1)[0]
SUBSCRIBE_TOPIC = f"{TOPIC_ROOT}/#"

TEST_MESSAGES = {
    f"{TOPIC_ROOT}/telemetry": {
        "temperature": 34.2,
        "rpm": 1460,
        "status": "RUNNING",
    },
    f"{TOPIC_ROOT}/status": {"status": "RUNNING"},
    f"{TOPIC_ROOT}/command": {"command": "STOP"},
}

received_topics = set()
all_messages_received = threading.Event()


def on_message_action(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[收到] topic={msg.topic} payload={payload}")

    received_topics.add(msg.topic)
    if set(TEST_MESSAGES).issubset(received_topics):
        all_messages_received.set()


subscriber = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
subscriber.on_message = on_message_action

publisher = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

try:
    subscriber.connect(BROKER, PORT, 60)
    subscriber.loop_start()
    subscriber.subscribe(SUBSCRIBE_TOPIC)
    print(f"[订阅] {SUBSCRIBE_TOPIC}")

    # 给 Broker 一点时间完成订阅，再开始发布测试消息。
    threading.Event().wait(0.5)

    publisher.connect(BROKER, PORT, 60)
    publisher.loop_start()

    for topic, data in TEST_MESSAGES.items():
        message = json.dumps(data)
        publisher.publish(topic, message).wait_for_publish()
        print(f"[发布] topic={topic} payload={message}")

    success = all_messages_received.wait(timeout=10)
    missing_topics = set(TEST_MESSAGES) - received_topics

    if success:
        print("验证成功：# 过滤器收到了 telemetry、status、command 三类消息。")
    else:
        print(f"验证失败：以下 Topic 未收到：{sorted(missing_topics)}")
        raise SystemExit(1)
finally:
    if publisher.is_connected():
        publisher.disconnect()
    publisher.loop_stop()

    if subscriber.is_connected():
        subscriber.disconnect()
    subscriber.loop_stop()
