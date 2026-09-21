import time
import json
import paho.mqtt.client as mqtt

from config import BROKER,PORT,TOPIC

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)


client.connect(BROKER, PORT, 60)

while True:
    data = {
        "temperature": 34.2,
        "rpm": 1460,
        "status": "RUNNING"
    }

    message = json.dumps(data)

    client.publish(TOPIC,message)
    time.sleep(1)
    #publish(发到哪里,发什么)

client.disconnect()
#发完了消息就断开连接
