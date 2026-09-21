import random
import time
import json
import paho.mqtt.client as mqtt

from config import BROKER,PORT,TOPIC

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)
#创建client对象,publisher和subscriber都属于client

client.connect(BROKER, PORT, 60)

while True:
    temperature = random.uniform(32, 40) #temperature 是小数，所以使用 random.uniform(32, 40)
    rpm = random.randint(1450, 1550) #rpm 是整数，所以使用 random.randint(1450, 1550)
    status = "RUNNING"
    last_seen = time.time() #time的获取当前时间函数 用于表示最后一次上报的时间
    data = {
        "temperature": temperature,
        "rpm": rpm,
        "status": status,
        "last_seen": last_seen
    }

    message = json.dumps(data)

    client.publish(TOPIC,message)
    time.sleep(1)
    #publish(发到哪里,发什么)

client.disconnect()
#发完了消息就断开连接
