# 第 2 周：FastAPI 接入

## 本周先学什么

本周要学的是“如何用一个 HTTP API 把网页 / Swagger 和 MQTT 设备连接起来”，不是一次学完整个后端框架：

1. FastAPI 应用和路由：启动应用，并为不同 URL + HTTP 方法绑定处理函数。
2. HTTP API 基础：理解路径参数、查询参数、请求体、响应体和常见状态码。
3. Pydantic 数据模型：用模型描述 `POST` 请求的 JSON 结构，并让 FastAPI 做基础校验。
4. API 与 MQTT 的边界：浏览器 / Swagger 使用 HTTP 调 FastAPI，FastAPI 再通过 MQTT 查询或控制设备。
5. 项目拆分：把路由、业务服务和 MQTT 客户端分开，先建立清晰边界，不做复杂架构。
6. 在线 / 离线判断：用每次遥测到达时更新的 `last_seen` 判断设备是否仍在线，Last Will 只作辅助。
7. 基础错误处理：设备不存在返回 404，命令不合法返回 400，MQTT 发送失败要留下日志。

## 核心概念是什么

> 表中未缩进表示根概念；`↳` 表示一级从属；`↳↳` 表示二级从属。这里表达的是学习上的组成/依赖关系，不代表严格的协议继承关系。

| 概念（层级） | 简单理解 | 本项目中的用法 |
| --- | --- | --- |
| FastAPI | 用 Python 编写 HTTP API 的 Web 框架。 | 启动服务，提供设备查询和控制接口。 |
| ↳ 路由 / Endpoint | URL 路径和 HTTP 方法对应的处理入口。 | `GET /devices/001`、`POST /devices/001/command`。 |
| ↳↳ Path 参数 | 放在 URL 路径中的变量，用来定位资源。 | `/devices/{device_id}` 中的 `device_id`。 |
| ↳↳ Query 参数 | 放在 URL `?` 后的可选参数，常用于筛选或分页。 | 后续查询历史时可用于限制时间范围；本周先知道概念。 |
| ↳↳ Request Body | 请求携带的数据，通常使用 JSON。 | `{"command": "STOP"}`。 |
| ↳↳↳ Pydantic 模型 | 描述数据字段和类型，并帮助校验输入。 | 校验 command 是否符合预期结构。 |
| ↳↳ Response Body | API 返回给调用方的数据。 | 返回温度、RPM、状态和 `last_seen`。 |
| ↳ HTTP 状态码 | 用数字表达请求结果。 | 成功用 2xx，设备不存在用 404，非法命令用 400。 |
| ↳ Swagger / OpenAPI | 自动展示和描述 API 的交互文档。 | 在 Swagger 页面点击 STOP 并观察真实设备状态。 |
| `last_seen` | 最近一次收到设备遥测的时间戳。 | 当前时间减去它超过 5 秒，就显示 OFFLINE。 |

### HTTP 和 MQTT 在本项目中的关系

FastAPI 不是设备本身，也不是 MQTT Broker。它是两种通信方式之间的桥梁：

```text
浏览器 / Swagger
        │ HTTP
        ▼
     FastAPI
        │ MQTT
        ▼
    虚拟设备
```

查询状态时，FastAPI 返回自己从 MQTT 收到的真实数据；发送 STOP 时，FastAPI 发布 MQTT 命令，设备执行后再通过状态 / 遥测消息反馈结果。因此，接口“成功返回”与设备“已经完成动作”是两个需要分别观察的事情。

### 建议参考

- [FastAPI：First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)：了解应用启动、路由、自动 Swagger 文档和 OpenAPI。
- [FastAPI：Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/)：理解 `/devices/{device_id}` 这类路径参数。
- [FastAPI：Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)：了解 URL 查询参数。
- [FastAPI：Request Body](https://fastapi.tiangolo.com/tutorial/body/)：理解 Pydantic 模型和 JSON 请求体。
- [FastAPI：Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)：查 400、404 和异常处理。

### 本周学习边界

只做一台写死的设备 `001`，不做设备注册、用户登录、权限、鉴权、复杂异步并发和数据库。数据库放到第 3 周；本周先把：

```text
HTTP 查询 / 命令
        ↓
FastAPI
        ↓
MQTT
        ↓
虚拟设备
```

跑通即可。

## 目标

形成：

```text
Browser / Swagger
       ↓
    FastAPI
       ↓
     MQTT
       ↓
Python Device
```

## Day 8：FastAPI 最小入门

### 视频

黑马 FastAPI：

https://www.bilibili.com/video/BV1zV2QBtE39/

### 只看

```text
FastAPI 启动
GET
POST
Path
Query
Body
Pydantic
```

### 先写死一台设备

```text
DEVICE_ID = "001"
```

不要做设备注册。

### API

```text
GET /devices
GET /devices/001
```

## Day 9：Command API

实现：

```text
POST /devices/001/command
```

Body：

```json
{
  "command": "STOP"
}
```

FastAPI 收到后：

```text
publish MQTT
↓
device/001/command
```

### 验收

Swagger 点 STOP 后：

```text
设备真的变成 STOPPED
```

## Day 10：项目拆分

目录改成：

```text
app/

├─ main.py
├─ api/
│  └─ devices.py
├─ services/
│  └─ device_service.py
├─ mqtt/
│  └─ client.py
└─ models/
```

### 视频只查

```text
Router
项目拆分
异常处理
```

写出来就停。

## Day 11：接收真数据

FastAPI 后台订阅：

```text
device/+/telemetry
device/+/status
```

内存保存：

```python
devices = {}
```

### 验收

```text
GET /devices/001
```

返回的是真正来自 MQTT 的实时数据。

## Day 12：ONLINE / OFFLINE

每次 telemetry 到达：

```text
last_seen = now
```

如果：

```text
now - last_seen > 5s
```

则：

```text
OFFLINE
```

### 注意

Last Will 只是辅助。

OFFLINE 主要以：

```text
last_seen
```

判断。

### 验收

关闭 `device_simulator.py`：

几秒后 API 显示：

```text
OFFLINE
```

## Day 13：异常处理

只做最基本的：

```text
设备不存在 → 404
非法 command → 400
MQTT publish 失败 → 记录日志
```

不要扩展鉴权、权限、用户系统。

## Day 14：第 2 周演示

必须完整跑一遍：

```text
设备启动
↓
API 显示 ONLINE
↓
看到温度 / RPM
↓
Swagger POST STOP
↓
设备 STOPPED
↓
关闭模拟器
↓
API 变 OFFLINE
```

录 1 分钟视频。
