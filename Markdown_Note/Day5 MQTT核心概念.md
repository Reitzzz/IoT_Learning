# Day5 MQTT 核心概念

## 一、今天要解决什么

Day 5 不再增加新的业务流程，而是在 Day 4 双向通信的基础上理解：

```text
QoS
Topic
Session
Retained
Last Will
Keep Alive
```

当前代码：

- [config.py](<../Code/Week1 MQTT/Day5 MQTT核心概念/config.py>)
- [publisher.py](<../Code/Week1 MQTT/Day5 MQTT核心概念/publisher.py>)
- [subscriber.py](<../Code/Week1 MQTT/Day5 MQTT核心概念/subscriber.py>)

## 二、Topic：消息发到哪里

Topic 是 MQTT 消息的路由名称。项目继续区分：

```text
telemetry   遥测数据
status      在线、离线、运行状态
command     控制命令
```

Day 5 使用：

```python
TOPIC = "reitzzz-test-92831/device/001/telemetry"
STATUS_TOPIC = "reitzzz-test-92831/device/001/status"
```

Last Will 和 Retained 状态不应占用 Telemetry Topic：

```python
client.will_set(STATUS_TOPIC, ...)
```

如果 Last Will 发布到 Telemetry Topic，会把最新一条完整遥测覆盖成：

```json
{"status": "OFFLINE"}
```

这样新订阅者虽然能收到离线状态，却丢失了温度、RPM 等最后一条遥测字段。

## 三、QoS：消息可靠到什么程度

### 1. QoS 等级

| QoS | 含义 | 特点 |
| --- | --- | --- |
| 0 | 最多一次 | 最快，可能丢失 |
| 1 | 至少一次 | 有确认，可能重复 |
| 2 | 恰好一次 | 最可靠，协议开销最大 |

发布和订阅都可以设置 QoS：

```python
client.publish(TOPIC, message, qos=1)
client.subscribe(TOPIC, qos=1)
```

最终有效 QoS 通常取两者中较小的一个：

```text
effective_qos = min(publish_qos, subscribe_qos)
```

因此下面的组合仍然相当于 QoS 0：

```python
client.publish(TOPIC, message, qos=1)
client.subscribe(TOPIC, qos=0)
```

### 2. 为什么离线缓存演示必须使用 QoS 1/2

只设置持久 Session 还不够：

```python
clean_session=False
```

原因是 `clean_session=False` 只告诉 Broker：

```text
Client 断开后，不要立刻删除它的 Session
```

它不代表 Broker 会无条件保存所有消息。Broker 还需要知道：

```text
这是哪一个 Client 的 Session
要保存哪些订阅匹配的消息
哪些消息有资格进入离线队列
```

因此四个条件分别解决四个不同问题：

| 条件 | 原因 | 不满足时会怎样 |
| --- | --- | --- |
| Subscriber 使用固定 `client_id` | Broker 使用 `client_id` 识别和查找 Session | 重连变成新 Client，找不到原订阅和离线队列 |
| Subscriber 使用 `clean_session=False` | 要求 Broker 在断开后继续保留 Session | Broker 会清理原 Session，订阅和待投递状态失效 |
| Subscriber 订阅 QoS 为 1 或 2 | Broker 把 QoS 1/2 的匹配消息作为 Session 状态保存 | 订阅 QoS 为 0 时，离线消息没有可靠保存义务 |
| Publisher 发布 QoS 为 1 或 2 | Broker 收到具有确认和重传要求的上游消息 | 发布 QoS 为 0 时，Broker 可以直接丢弃该消息 |

### 3. 为什么 QoS 由 Publisher 和 Subscriber 共同决定

MQTT 消息的最终投递级别不是取较大值，而是取较小值：

```text
effective_qos = min(publish_qos, subscribe_qos)
```

例如：

```text
Publisher 发布 QoS 1
Subscriber 订阅 QoS 0
最终有效 QoS 0
```

Subscriber 订阅 QoS 1 不会把 Publisher 的 QoS 0 消息升级成 QoS 1：

```text
Publisher 发布 QoS 0
Subscriber 订阅 QoS 1
最终有效 QoS 0
```

所以想让离线队列测试真正成立，两端都必须至少使用 QoS 1：

```python
client.publish(TOPIC, message, qos=1)
client.subscribe(TOPIC, qos=1)
```

### 4. 为什么 QoS 0 不能保证离线缓存

QoS 0 的语义是“最多一次”：

```text
没有 PUBACK 确认
没有重传流程
没有必须保存到会话状态的义务
```

因此 Broker 在 Subscriber 离线时可以直接丢掉 QoS 0 消息。

某些 Broker 可能额外缓存 QoS 0，但这是实现行为，不是跨 Broker 的可靠保证。

还应区分：

```text
Subscriber 的 Session 决定是否保存发给它的离线消息
Publisher 的 Session 只影响 Publisher 自己尚未完成的 QoS 1/2 发布流程
```

所以这个离线缓存测试中，Publisher 可以不使用固定 `client_id`，也可以使用 `clean_session=True`。真正必须配置持久 Session 的是离线接收消息的 Subscriber。

## 四、Payload：消息里装什么

Topic 决定消息发到哪里，Payload 决定消息内容是什么：

```text
Topic   = 地址
Payload = 正文
```

Publisher 中：

```python
data = {
    "temperature": 34.2,
    "rpm": 1460,
    "status": "RUNNING",
}

message = json.dumps(data)
client.publish(TOPIC, message, qos=1, retain=True)
```

Subscriber 中：

```python
def on_message_action(client, userdata, msg):
    print(msg.payload.decode())
```

收到的 `msg.payload` 是字节数据，需要经过：

```text
msg.payload
    ↓ decode()
JSON 字符串
    ↓ json.loads()
Python 字典
```

## 五、client_id 和 Session

### 1. client_id 是客户端身份

一个 MQTT Client 可以同时发布和订阅，但同一个时刻只能有一个连接使用某个 `client_id`。

```text
同时在线：
相同的 client_id 会互相顶替

先后重连：
相同的 client_id 用于恢复同一个 Session
```

不同程序应该使用不同 ID：

```python
publisher-demo-001
subscriber-demo-001
```

### 2. 不显式设置 client_id

当前环境使用 `paho-mqtt 2.1.0`，默认协议是 MQTT 3.1.1，默认：

```python
clean_session=True
```

此时 Paho 可以发送空 Client ID，由 Broker 为每个连接分配临时身份。因此两个都不写 `client_id` 的客户端通常不会冲突。

但这种身份是临时的：

```text
无法稳定恢复原 Session
重连后通常不是同一个会话
客户端也不知道 Broker 实际分配的 ID
```

如果使用：

```python
clean_session=False
```

必须显式提供固定 `client_id`，否则 Paho 会报错。

### 3. clean_session 的两个值

```python
clean_session=True
```

每次连接建立新 Session，不恢复旧订阅和旧 QoS 流程。

```python
clean_session=False
```

Broker 可以保存 Session，重连时要求使用相同的 `client_id` 恢复。

Session 中可能保存：

```text
订阅关系
尚未完成的 QoS 1/2 发送状态
离线期间排队给这个客户端的 QoS 1/2 消息
```

### 4. Publisher 和 Subscriber 的 Session 区别

| 角色 | Session 的作用 | 不能解决什么 |
| --- | --- | --- |
| Subscriber | 保存订阅，并可能缓存离线期间的 QoS 1/2 消息 | QoS 0 不保证缓存 |
| Publisher | 继续尚未完成的 QoS 1/2 发布流程 | 不会补发 Publisher 当时没有发布的数据 |

### 5. Publisher 的 clean_session 注释

原注释：

```text
clean_session在publisher里的作用：Broker保留尚未完成的 QoS 1/2 发送状态，重连后继续相关协议流程
```

需要补充：

```text
只有使用 QoS 1/2 时，这个效果才明显。
Publisher 的 Session 不会保存 Subscriber 的离线消息。
Publisher 没有发布的消息，也不会因为 Session 被补发。
```

### 6. Subscriber 的 clean_session 注释

原注释：

```text
clean_session=False在subscriber里的作用：Broker在publisher正常 subscriber断连时尽量保留这期间的QoS 1/2消息
```

更准确的表达：

```text
Publisher 保持在线并继续发布 QoS 1/2 消息时，
Broker 可能为使用持久 Session 的离线 Subscriber 缓存匹配消息。
Subscriber 重连时必须使用相同 client_id。
```

需要同时满足：

```text
Subscriber：固定 client_id + clean_session=False
Subscriber：subscribe(..., qos=1 或 2)
Publisher：publish(..., qos=1 或 2)
```

Subscriber 断连时：

```text
Publisher 继续发布
    ↓
Broker 根据 Subscriber 的持久 Session
    ↓
可能为它缓存匹配订阅的 QoS 1/2 消息
    ↓
Subscriber 使用相同 client_id 重连
    ↓
Broker 补发缓存消息
```

Publisher 断连时：

```text
没有新的遥测被发布
    ↓
Publisher 的 Session 不能生成缺失数据
    ↓
需要数据库或消息队列才能保存完整历史
```

## 六、Retained：Broker 保留 Topic 的最新消息

发布时设置：

```python
client.publish(
    STATUS_TOPIC,
    json.dumps({"status": "RUNNING"}),
    qos=1,
    retain=True,
)
```

Broker 会为这个 Topic 保存最新一条 Retained 消息。新的 Subscriber 刚订阅时，即使 Publisher 暂时没有继续发布，也能立即收到它。

清除 Retained 消息：

```python
client.publish(STATUS_TOPIC, None, qos=1, retain=True)
```

Session 和 Retained 的区别：

| 概念 | 作用范围 | 保存内容 |
| --- | --- | --- |
| Session | 某个 client_id | 订阅关系和 QoS 1/2 会话状态 |
| Retained | 某个 Topic | 该 Topic 最新一条 Retained 消息 |

## 七、Last Will：异常断开时的离线状态

Last Will 必须在 `connect()` 之前设置：

```python
client.will_set(
    STATUS_TOPIC,
    payload=json.dumps({"status": "OFFLINE"}),
    qos=1,
    retain=True,
)
```

正确的方法调用是：

```python
client.will_set(...)
```

不是：

```python
client.will_set = (...)
```

Paho 的参数名是：

```python
payload=...
```

不是：

```python
message=...
```

Last Will 的触发条件：

```text
进程被强制结束
网络异常断开
断电
Keep Alive 超时
```

正常调用下面的代码不会触发 Last Will：

```python
client.disconnect()
```

因此：

```text
异常退出    Broker 代发 OFFLINE
正常退出    需要程序主动发布 OFFLINE
```

## 八、Keep Alive：协议层心跳

连接时设置：

```python
client.connect(BROKER, PORT, 60)
```

这里的 `60` 是 Keep Alive 秒数。

它表示客户端长时间没有发送 MQTT 数据时，Paho 需要发送：

```text
PINGREQ
```

Broker 回复：

```text
PINGRESP
```

只写：

```python
client.connect(BROKER, PORT, 60)
```

还不够。Paho 还需要网络循环：

```python
client.loop_start()
```

或者：

```python
client.loop_forever()
```

区别：

| 方法 | 行为 |
| --- | --- |
| `loop_start()` | 后台线程处理网络事件，主线程继续发布数据 |
| `loop_forever()` | 当前线程持续处理网络事件，通常用于 Subscriber |

如果没有网络循环，Paho 不会按预期处理 Keep Alive，也不会发送和检查 PINGREQ、PINGRESP。

即使 Publisher 每秒都在发送消息，也不能把“有业务消息”当成“已经正确实现了 Keep Alive”。

原来的 Keep Alive 注释：

```text
Keep Alive，单位是秒。意思是：连接空闲达到设置时间后，Paho 会发送心跳；Broker 回复 PINGRESP。如果长时间得不到回复，客户端会认为连接断开。
```

需要补充：

```text
Paho 的心跳需要 loop_start() 或 loop_forever() 驱动。
只设置 connect(..., 60) 不会自动发送 PINGREQ。
```
