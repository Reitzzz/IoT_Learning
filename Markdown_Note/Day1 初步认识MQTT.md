# Day1 初步认识 MQTT

## 一、这三个文件做了什么

这三个 Python 文件完成了一个最小的 MQTT 单向通信：

```text
publisher.py
    │ 发布 telemetry 消息
    ▼
MQTT Broker（broker.emqx.io）
    │ 转发给订阅者
    ▼
subscriber.py
    │ 接收并打印消息
```

对应的 MQTT 角色是：

| 文件 | 角色 | 作用 |
| --- | --- | --- |
| `config.py` | 配置模块 | 保存 Broker、端口和 Topic。 |
| `publisher.py` | Publisher | 每隔 1 秒向 Topic 发布一条 JSON 消息。 |
| `subscriber.py` | Subscriber | 订阅 Topic，收到消息后打印出来。 |

## 二、`config.py`：统一保存连接配置

当前代码：

```python
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "reitzzz-test-92831/device/001/telemetry"
```

### 1. Broker

`BROKER` 表示 MQTT Broker 的地址。

Broker 是消息代理服务器，Publisher 不直接把消息发给 Subscriber，而是先发给 Broker，再由 Broker 转发给符合条件的订阅者。

```text
Publisher → Broker → Subscriber
```

本次使用的是公共 Broker：

```text
broker.emqx.io
```

公共 Broker 适合学习和测试，不要发送密码、Token、个人信息等敏感内容。

### 2. Port

`PORT = 1883` 表示连接 MQTT 非加密端口。

常见情况：

```text
1883    普通 MQTT 连接
8883    通常用于 TLS 加密 MQTT 连接
```

当前 Day 1 只使用普通的 1883 端口。

### 3. Topic

`TOPIC` 是消息的主题，也可以理解为消息通道或路由名称：

```text
reitzzz-test-92831/device/001/telemetry
```

可以拆成：

```text
reitzzz-test-92831   项目前缀
device                设备类别
001                   设备编号
telemetry             消息类型
```

Publisher 和 Subscriber 必须使用完全相同的 Topic，否则 Subscriber 收不到消息。

### 4. 从配置模块导入

其他文件通过下面的代码使用配置：

```python
from config import BROKER, PORT, TOPIC
```

这样可以避免在多个文件中重复修改 Broker、端口和 Topic。

## 三、`publisher.py`：发布 MQTT 消息

### 1. 导入模块

```python
import time
import json
import paho.mqtt.client as mqtt
```

作用：

| 模块 | 作用 |
| --- | --- |
| `time` | 使用 `sleep(1)` 控制每秒发送一次。 |
| `json` | 把 Python 字典转换成 JSON 字符串。 |
| `paho.mqtt.client` | 提供 Python MQTT 客户端。 |

### 2. 创建 Client

```python
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)
```

`Client` 表示一个 MQTT 客户端程序。Publisher 和 Subscriber 都是 Client，只是承担的角色不同：

```text
Publisher：主要发布消息
Subscriber：主要订阅消息
```

`CallbackAPIVersion.VERSION2` 表示使用 Paho MQTT 2.x 的回调接口版本。

### 3. 连接 Broker

```python
client.connect(BROKER, PORT, 60)
```

三个参数分别是：

```text
Broker 地址
Broker 端口
Keep Alive 时间：60 秒
```

连接成功后，Client 才能向 Broker 发布消息。

### 4. 创建设备数据

```python
data = {
    "temperature": 34.2,
    "rpm": 1460,
    "status": "RUNNING"
}
```

这里的 `data` 是 Python 字典，模拟一台设备当前的状态：

```text
temperature：温度
rpm：转速
status：设备状态
```

### 5. 把字典转换成 JSON

```python
message = json.dumps(data)
```

MQTT Payload 可以是字符串或字节内容。这里使用 JSON 字符串，便于不同程序读取：

```json
{"temperature": 34.2, "rpm": 1460, "status": "RUNNING"}
```

注意：

```text
Python 字典  --json.dumps-->  JSON 字符串
```

### 6. 发布消息

```python
client.publish(TOPIC, message)
```

`publish` 的两个主要参数是：

```text
TOPIC       发到哪个主题
message     发送的消息内容
```

当前代码把消息发布到：

```text
reitzzz-test-92831/device/001/telemetry
```

### 7. 每秒发送一次

```python
while True:
    ...
    time.sleep(1)
```

`while True` 会持续运行，`time.sleep(1)` 让每次发送之间间隔大约 1 秒。

因此 Publisher 的行为是：

```text
生成数据
↓
转换成 JSON
↓
发布到 Topic
↓
等待 1 秒
↓
重复
```

## 四、`subscriber.py`：订阅并接收消息

### 1. 定义消息回调函数

```python
def on_message_action(client, userdata, msg):
    print(msg.payload.decode())
```

当 Subscriber 收到消息时，Paho 会自动调用这个函数。

`msg.payload` 通常是字节数据，例如：

```text
b'{"temperature": 34.2, "rpm": 1460, "status": "RUNNING"}'
```

`decode()` 把字节转换成 Python 字符串：

```text
bytes  --decode()-->  str
```

当前函数只打印消息内容，没有打印 Topic。后续如果想同时查看来源，可以写成：

```python
print(msg.topic, msg.payload.decode())
```

### 2. 注册回调函数

```python
client.on_message = on_message_action
```

这句话表示：

```text
收到消息时 → 调用 on_message_action
```

这就是事件回调机制。程序不需要手动不断检查消息，Paho 在收到消息后会调用已经注册的函数。

### 3. 连接并订阅 Topic

```python
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
```

Subscriber 需要：

1. 连接同一个 Broker；
2. 订阅 Publisher 发布的同一个 Topic。

只要 Broker、端口或 Topic 不一致，都可能导致收不到消息。

### 4. 持续处理网络消息

```python
client.loop_forever()
```

`loop_forever()` 会持续处理 MQTT 网络事件，并等待新消息。

如果没有这一步，程序可能在订阅后立刻结束，无法持续接收消息。

## 五、完整运行过程

建议先启动 Subscriber，再启动 Publisher。

### 1. 启动 Subscriber

```bash
cd "Week1 MQTT/Day1 初步认识MQTT"
python subscriber.py
```

此时 Subscriber 会连接 Broker 并等待消息。

### 2. 启动 Publisher

另开一个终端：

```bash
cd "Week1 MQTT/Day1 初步认识MQTT"
python publisher.py
```

Publisher 每秒发布一条消息，Subscriber 应该持续打印：

```json
{"temperature": 34.2, "rpm": 1460, "status": "RUNNING"}
```

### 3. 验收结果

Day 1 的核心闭环是：

```text
Publisher
    ↓ publish
Broker
    ↓ forward
Subscriber
    ↓ callback
打印 JSON 消息
```

当前代码已经能够完成：

- 连接公共 MQTT Broker；
- Publisher 每秒发送 JSON；
- Subscriber 订阅相同 Topic；
- Subscriber 通过回调接收并打印消息。

## 六、当前代码的已知边界

### 1. `disconnect()` 暂时不可达

Publisher 中的：

```python
while True:
    ...

client.disconnect()
```

因为 `while True` 不会自然结束，所以末尾的 `disconnect()` 正常情况下不会执行。按 Day 1 的基本学习目标，这不影响当前发送和接收测试；后续学习异常处理时再补充优雅退出即可。

### 2. 数据目前是固定值

每次发送的温度、RPM 和状态都相同：

```text
temperature = 34.2
rpm = 1460
status = RUNNING
```

这在 Day 1 是可以接受的，因为当前重点是先理解 MQTT 通信。之后写虚拟设备时，再改成随机或动态变化的数据。

### 3. 使用公共 Broker

当前 Topic 位于公共 Broker 上。学习阶段可以使用，但多个学习者可能使用相同或相近的 Topic，因此项目实际使用时应该设置更独特的随机前缀，并避免发送敏感信息。

## 七、Day 1 需要记住的知识点

```text
MQTT 是发布 / 订阅协议
Broker 负责转发消息
Client 可以是 Publisher，也可以是 Subscriber
Topic 决定消息的路由
Payload 是消息的具体内容
json.dumps() 把 Python 字典转换成 JSON 字符串
publish() 用来发布消息
subscribe() 用来订阅消息
回调函数处理收到的消息
loop_forever() 让 Subscriber 持续运行
```

最重要的一条链路：

```text
Publisher → Broker → Subscriber
```
