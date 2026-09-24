# Day9：Command API

> 本日重点：用 POST 接收命令，再把命令发布到 MQTT。相关代码：[main.py](<../../Code/Week2 FastAPI/Day9 Command API/main.py>)

## 目标接口

```text
POST /devices/001/command
```

请求体：

```json
{
  "command": "STOP"
}
```

完整链路：

```text
Swagger / HTTP
        ↓
FastAPI 路由
        ↓
publisher.publish_command()
        ↓
MQTT Broker
        ↓
设备订阅端
```

## Path 参数和 Request Body

```python
@app.post("/devices/{device_id}/command")
def send_command(device_id: str, req: CommandRequest):
    ...
```

代码注释对应：

```text
device_id 来自路径参数；req 是经 CommandRequest 校验后的请求体
```

| 参数 | 来源 | 作用 |
| --- | --- | --- |
| `device_id` | URL 路径参数 | 确定命令发给哪台设备。 |
| `req` | JSON 请求体 | 提供经过校验的命令数据。 |

## Pydantic 请求模型

```python
class CommandRequest(BaseModel):
    command: str
```

它描述请求体的结构。缺少 `command` 或类型错误时，FastAPI/Pydantic 会自动返回 `422`，不需要手写 JSON 解析和字段检查。

## HTTP 错误

```python
if device_id != "001":
    raise HTTPException(status_code=404, detail="设备号错误")

if req.command != "STOP":
    raise HTTPException(status_code=400, detail="暂时不支持该操作")
```

注释强调：

```text
使用 FastAPI 的 HTTPException 返回 HTTP 错误
```

| 状态码 | 含义 |
| --- | --- |
| `404` | 请求的设备不存在。 |
| `400` | 设备存在，但命令不支持。 |
| `422` | 请求体结构不满足 Pydantic 模型。 |

## API 成功不等于设备已经执行

接口返回：

```json
{
  "device_id": "001",
  "command": "STOP",
  "status": "命令已发送"
}
```

`"命令已发送"` 只表示 FastAPI 已经调用 MQTT 发布命令，不表示设备已经变成 `STOPPED`。设备是否执行，要由设备端的状态变化来确认。

## 为什么调用 publisher，而不是把 MQTT 写在 main.py

代码中使用：

```python
import publisher

publisher.publish_command(req.command)
```

相关注释表达了两个边界：

1. `main.py` 导入 publisher 模块并调用发送函数。
2. 由 `publisher.py` 读取发送参数，避免反向导入 `main.py` 中的可变状态。

这样做能避免循环依赖。主程序负责 HTTP，MQTT 模块负责连接 Broker、组装消息、发布和断开连接。

不要为了方便，把一个模块里的可变全局变量到处导入并修改。优先导入模块、函数或常量，让依赖方向保持清楚。

