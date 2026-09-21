import paho.mqtt.client as mqtt

from config import BROKER,PORT,TOPIC

def on_message_action(client, userdata, msg):
    print(msg.payload.decode())
#处理接收到的信息 其中decode用于将bytes转为Python字符串

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)
#创建client对象,publisher和subscriber都属于client

client.on_message = on_message_action
#将该client收到信息的行为设置为on_message_action函数

client.connect(BROKER, PORT, 60)

client.subscribe(TOPIC)
#订阅这个topic

client.loop_forever()
#持久运行
