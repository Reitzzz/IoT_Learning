# 第 1 周：先把 MQTT 双向闭环跑起来

## 本周先学什么

本周不追求学完整套物联网课程，只先掌握“设备如何通过 MQTT 发消息、收命令”所需要的概念和最小 Python 用法：

1. MQTT 的通信模型：客户端不直接互相连接，而是通过 Broker 转发消息。
2. 发布 / 订阅：一个客户端向 Topic 发布消息，订阅了匹配 Topic 的客户端接收消息。
3. Python MQTT 客户端：连接 Broker、发布消息、订阅 Topic、处理收到消息的回调。
4. 设备消息设计：区分遥测数据、设备状态和控制命令，并使用 JSON 作为消息内容。
5. 基础可靠性概念：先理解 QoS、Retained、Last Will、Keep Alive；本周实现只使用 QoS 0，并用 Last Will 辅助表示离线。

## 核心概念是什么

> 表中未缩进表示根概念；`↳` 表示一级从属；`↳↳` 表示二级从属。这里表达的是学习上的组成/依赖关系，不代表严格的协议继承关系。

| 概念（层级） | 简单理解 | 本项目中的用法 |
| --- | --- | --- |
| MQTT | 面向设备和消息的轻量级发布 / 订阅协议。 | 连接虚拟设备、控制端和后续 FastAPI。 |
| ↳ Client | 连接到 Broker 的程序。发布者和订阅者都属于 Client，一个 Client 也可以同时发布和订阅。 | `publisher.py`、`subscriber.py`、`device_simulator.py`、MQTTX。 |
| ↳↳ Publisher / Subscriber | Publisher 发布消息；Subscriber 订阅并接收消息。 | 模拟设备发布 telemetry，设备订阅 command。 |
| ↳ Broker | 消息代理服务器，负责接收消息并转发给匹配的订阅者。 | `broker.emqx.io:1883`。 |
| ↳ Topic | 消息的路由名称，可以理解为消息通道；订阅者通过 Topic Filter 选择要接收的消息。 | `{PREFIX}/device/001/telemetry` 等。 |
| ↳ Payload | Topic 携带的具体内容。 | `{"temperature": 34.2, "rpm": 1460, "status": "RUNNING"}`。 |
| ↳ QoS | 消息投递保证等级：QoS 0 是“最多一次”，可能丢失但实现简单。 | 本周统一使用 QoS 0，不先引入重试和重复消息处理。 |
| ↳ Retained | Broker 为 Topic 保留最近一条状态消息，新订阅者可以马上收到它。 | 先理解概念，当前 Demo 不把它当作主要在线判断依据。 |
| ↳ Last Will | Client 非正常断开时，由 Broker 代发预先设置的消息。 | 用一个 OFFLINE 状态辅助演示断线。 |
| ↳ Keep Alive | Client 在空闲时发送心跳，帮助双方发现连接是否失效。 | 先知道用途，不在本周深入调参。 |

其中，`telemetry`、`status`、`command` 不是 MQTT 协议强制规定的关键字，而是本项目约定的 Topic 分类：

```text
telemetry：温度、RPM 等测量数据
status：RUNNING、STOPPED、OFFLINE 等状态
command：START、STOP、RESET 等控制命令
```

### 建议参考

- [菜鸟教程：MQTT 入门介绍](https://www.runoob.com/w3cnote/mqtt-intro.html)：先看发布者、Broker、订阅者、Topic、Payload 和 QoS。
- [MQTT 5.0 官方规范](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)：需要确认 QoS、Retained、Last Will 等定义时再查，不要求通读。
- [EMQX：Python 使用 MQTT](https://www.emqx.com/en/blog/how-to-use-mqtt-in-python)：结合 Python 代码理解连接、发布和订阅。

### 本周学习边界

先不展开 QoS 1/2 的重试语义、复杂 Session、权限认证、TLS、集群 Broker 等内容。只要能完成：

```text
虚拟设备 → 发布 telemetry → Broker → 控制端收到
控制端 → 发布 command → Broker → 虚拟设备改变状态
```

就达到了本周的学习目标。

## 目标

最终形成：

```text
Python 虚拟设备
    ↓ telemetry
MQTT Broker
    ↑ command
控制端
```

## Day 1：Python MQTT 最小通信

### 只学

```text
Broker
Publisher
Subscriber
Topic
Publish / Subscribe
```

### 视频

Python paho-mqtt 入门：

https://www.bilibili.com/video/BV1qL4y1b7nU/

只看够用部分。

### 官方参考

EMQX Python MQTT 教程：

https://www.emqx.com/en/blog/how-to-use-mqtt-in-python

### 安装

```bash
pip install paho-mqtt
```

### 今天必须写

```text
publisher.py
subscriber.py
config.py
```

Publisher 每秒发：

```json
{
  "temperature": 34.2,
  "rpm": 1460,
  "status": "RUNNING"
}
```

Subscriber 能收到。

### 验收

你能解释：

```text
Publisher → Broker → Subscriber
```

并且两个 Python 程序真的通信。

## Day 2：MQTTX + Topic

### 安装

MQTTX：

https://mqttx.app/zh/downloads

### 做

连接：

```text
broker.emqx.io:1883
```

订阅：

```text
zcufe-demo-你的随机串/device/001/#
```

运行 Publisher 后，MQTTX 能看到消息。

### 验收

你能解释：

```text
telemetry
status
command
```

为什么分开。

## Day 3：写虚拟设备

新建：

```text
device_simulator.py
```

设备字段：

```text
temperature
rpm
status
last_seen
```

默认：

```text
temperature = 32~40
rpm = 1450~1550
status = RUNNING
```

每秒上报一次。

## Day 4：加入反向控制

设备订阅：

```text
device/001/command
```

支持：

```text
START
STOP
RESET
```

例如收到：

```json
{
  "command": "STOP"
}
```

设备变为：

```text
status = STOPPED
rpm = 0
```

### 验收

在 MQTTX 手动发 STOP 后，Python 模拟器真的停止。

## Day 5：MQTT 核心概念

### 视频

尚硅谷 MQTT：

https://www.bilibili.com/video/BV1HADnYFEXn/

### 只查这些

```text
QoS
Topic
Session
Retained
Last Will
Keep Alive
```

### 当前实现要求

QoS：

```text
先全部 QoS 0
```

Last Will：

```text
做一个 OFFLINE 状态即可
```

看到够用就关视频。

## Day 6：加入强制高温

不要依赖随机数等半天。

给模拟器加一个：

```text
force_overheat
```

例如输入：

```text
h
```

直接：

```text
temperature = 90
```

正常阈值保留：

```text
< 70      NORMAL
70~85     WARNING
> 85      ALARM
```

这样演示可控。

## Day 7：第 1 周复盘

目录：

```text
industrial-device-demo/

├─ config.py
├─ device_simulator.py
├─ publisher.py
├─ subscriber.py
└─ README.md
```

README 只写：

- 项目是什么
- Broker
- Topic
- START / STOP / RESET
- 如何运行

### 第 1 周自测

问自己：

> 这个过程是否比以前写商城 CRUD 更愿意继续？

如果答案很差，不要急着再开 ROS2 / Agent 新赛道。
