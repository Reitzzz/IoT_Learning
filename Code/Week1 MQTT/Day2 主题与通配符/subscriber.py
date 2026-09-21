import paho.mqtt.client as mqtt

from config import BROKER,PORT,TOPIC

def on_message_action(client, userdata, msg):
    print(msg.payload.decode())


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

SUBSCRIBE_TOPIC = f"{TOPIC.rsplit('/', 1)[0]}/#"

# TOPIC.rsplit("/", 1)：对TOPIC从右侧开始分割字符串，参数 1 表示只分割一次 
# 得到[
#   "reitzzz-test-92831/device/001",
#   "telemetry"
#   ]

# [0] ：取上述结果的第一个元素，即"reitzzz-test-92831/device/001"

# /# :给上述结果加上/# 即reitzzz-test-92831/device/001/#  监听reitzzz-test-92831/device/001下的所有信息


client.on_message = on_message_action


client.connect(BROKER, PORT, 60)

client.subscribe(SUBSCRIBE_TOPIC)


client.loop_forever()
