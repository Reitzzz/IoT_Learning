# Day10：项目拆分与 APIRouter

> 本日重点：把 Day8 的 GET 和 Day9 的 POST 合并到按资源组织的项目中。相关代码：[app](<../../Code/Week2 FastAPI/Day10 项目拆分/app>)

## Day10 只是移动位置吗

主体上是一次结构性迁移，接口行为不变。真正增加的内容只有：

1. 用 `APIRouter` 把设备接口分组。
2. 用 `include_router` 把路由组挂到主应用。
3. 把模型、业务服务、MQTT 客户端和配置拆开。

Day10 不接真实遥测，不判断在线离线，也不加数据库。

## 拆分后的目录

```text
app/
├─ main.py
├─ config.py
├─ api/
│  └─ devices.py
├─ models/
│  └─ device.py
├─ services/
│  └─ device_service.py
└─ mqtt/
   └─ publisher.py
```

| 文件 | 责任 |
| --- | --- |
| `main.py` | 创建应用，挂载 router。 |
| `api/devices.py` | HTTP 路由、路径参数、状态码和响应。 |
| `models/device.py` | Pydantic 请求模型，不是数据库模型。 |
| `services/device_service.py` | 设备数据、命令规则和业务调用。 |
| `mqtt/publisher.py` | MQTT 连接与发布，名称与 Day9 保持一致。 |
| `config.py` | Broker、端口、设备和 Topic 配置。 |


## APIRouter 是什么

`APIRouter` 是 FastAPI 提供的“路由分组容器”，不是另一个 FastAPI 应用，也不能单独启动服务。

```python
router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("")
def get_devices():
    ...


@router.post("/{device_id}/command")
def send_command(...):
    ...
```

它和原来的写法对应关系是：

```python
# 原来
@app.get("/devices")

# Router 中
@router.get("")
```

Router 定义完路由后，还要在主应用中注册：

```python
app.include_router(devices_router)
```

代码注释强调：如果漏掉 `include_router`，Swagger 里不会出现 `/devices` 接口。

## 按业务资源分组，不按 HTTP 方法分组

设备相关的接口是：

```text
GET  /devices
GET  /devices/{device_id}
POST /devices/{device_id}/command
```

虽然 HTTP 方法不同，但它们都围绕“设备”这一类业务资源，所以放在同一个 `devices` 路由组中。

错误的拆法是机械地按方法分：

```text
get_router.py
post_router.py
```

这样同一个设备业务会分散到不同文件。分组依据是接口操作的业务对象，不是 GET 或 POST。

这里的“资源”指设备、报警、遥测历史这类业务对象。`command` 不是独立资源，而是设备资源下的一次操作，所以仍属于设备路由。

## prefix：统一 URL 前缀

```python
router = APIRouter(prefix="/devices")
```

路径组合规则：

```text
完整路径 = prefix + @router 装饰器里的 path
```

因此：

```text
@router.get("")                      -> GET /devices
@router.get("/{device_id}")          -> GET /devices/{device_id}
@router.post("/{device_id}/command") -> POST /devices/{device_id}/command
```

prefix 已经写了 `/devices`，装饰器里不要重复写：

```python
@router.get("/devices")  # 最终会变成 /devices/devices
```

## tags：Swagger 文档标签

```python
tags=["devices"]
```

`tags` 只影响 Swagger/OpenAPI 文档的分组，例如在 `/docs` 页面中把接口归到 `devices` 分类。

它不改变 URL、HTTP 方法、请求内容、响应内容或业务逻辑。

```text
prefix：决定接口地址是什么
tags：决定接口在 Swagger 文档里归到哪一组
```

## 为什么代码要拆成这个结构

这不是 FastAPI 强制规范，也不是唯一写法。FastAPI 官方示例常使用 `routers/`，这里使用 `api/` 也可以，关键是职责边界清楚。

拆分的收益是让 HTTP、业务规则、数据模型和 MQTT 各管一件事。Day11 加入后台订阅、实时数据和 `last_seen` 后，如果全部继续堆在 `main.py`，HTTP 和 MQTT 会混在一起，测试和排查都会变困难。

当前 `device_service.py` 确实很薄，但它会在后续承担设备状态和业务判断。不要因为文件暂时代码少就提前加入 Repository、Factory、DTO 等更复杂的层。

如果项目永远只有当前三个接口，单文件也可以。现在拆，是为后续持续增加功能和服务边界。

## __init__.py 为什么可以删

Python 3.3 以后支持隐式命名空间包，普通目录没有 `__init__.py` 也可以导入。当前 Day10 学习项目已经删除这些空文件。

需要注意：

- 正式打包时，通常需要明确包结构。
- 如果本地目录名可能和第三方包重名，建议补回 `app/__init__.py`。
- 不要为了假设中的需要保留空文件，等出现实际需求再加。

## Day10 验收

在 `Day10 项目拆分` 目录下运行：

```powershell
python subscriber.py
fastapi dev app/main.py
```

Swagger 中调用：

```text
POST /devices/001/command
Body: {"command": "STOP"}
```

设备订阅端输出 `设备状态：STOPPED`，说明拆分后命令链路仍然有效。

当前 `GET /devices/001` 仍显示写死的 `RUNNING`，这是正常的。真实遥测和在线判断要到 Day11、Day12 才接入。

## 本日易混点

| 问题 | 结论 |
| --- | --- |
| APIRouter 能单独运行吗 | 不能，它只是路由容器，必须挂到 `app`。 |
| 应该 GET 一组、POST 一组吗 | 不应该，应该按业务资源分组。 |
| prefix 会改变业务逻辑吗 | 不会，只决定统一 URL 前缀。 |
| tags 会改变接口地址吗 | 不会，只影响 Swagger 分组。 |
| 项目必须这样拆吗 | 不必须，但符合当前后续任务的分工需要。 |
