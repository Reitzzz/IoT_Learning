# Day8：FastAPI 最小入门

> 本日重点：启动 FastAPI，理解 `app`、路由、路径参数、内存数据和 GET。相关代码：[main.py](<../../Code/Week2 FastAPI/Day8 FastAPI 最小入门/main.py>)

## 先把三个对象分清

```python
app = FastAPI()

DEVICE_ID = "001"
devices = {
    DEVICE_ID: {
        "device_id": DEVICE_ID,
        "temperature": 36.5,
        "rpm": 1500,
        "status": "RUNNING",
        "last_seen": None,
    }
}
```

| 对象 | 作用 |
| --- | --- |
| `app` | FastAPI/ASGI 应用对象，负责接收请求和调度路由。 |
| `devices` | 当前写死的设备数据，只保存在内存里。 |
| `DEVICE_ID` | 当前示例只做一台设备，设备号先写死为 `001`。 |

## GET /devices

```python
@app.get("/devices")
def get_devices():
    return list(devices.values())
```

这里的注释是：

```text
返回 devices 中所有设备信息组成的列表
```

`devices` 是字典，`devices.values()` 取出所有设备对象，再通过 `list(...)` 转成列表作为 HTTP 响应。

路由装饰器的本质是：

```text
HTTP GET + /devices  ->  调用 get_devices()
```

## GET /devices/{device_id}

```python
@app.get("/devices/{device_id}")
def get_device(device_id: str):
    device = devices.get(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device
```

这里的注释是：

```text
查询特定 device 的信息
```

`{device_id}` 是路径参数。访问 `/devices/001` 时，FastAPI 会把 URL 中的 `001` 传给函数参数 `device_id`。

如果字典里找不到设备，就返回 `404`：

```python
raise HTTPException(status_code=404, detail="设备不存在")
```



