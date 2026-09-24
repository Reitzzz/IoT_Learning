# Day2 主题与通配符

## 一、要理解的代码

```python
SUBSCRIBE_TOPIC = f"{TOPIC.rsplit('/', 1)[0]}/#"
```

这行代码的作用是：根据 Day1 的具体 Topic，生成一个可以监听设备下所有信息的 Topic 过滤器。

## 二、`TOPIC.rsplit("/", 1)`

`rsplit` 表示从字符串右侧开始分割。

参数 `1` 表示只分割一次，因此只会从最后一个 `/` 的位置切开：

```python
TOPIC = "reitzzz-test-92831/device/001/telemetry"

TOPIC.rsplit("/", 1)
```

得到：

```python
[
    "reitzzz-test-92831/device/001",
    "telemetry"
]
```

## 三、`[0]` 取出设备路径

```python
TOPIC.rsplit("/", 1)[0]
```

`[0]` 表示取列表中的第一个元素，因此结果是：

```text
reitzzz-test-92831/device/001
```

这一部分是设备 Topic 的上级路径。

## 四、拼接 `/#`

在上级路径后面加上 `/#`：

```text
reitzzz-test-92831/device/001/#
```

`/#` 表示监听 `reitzzz-test-92831/device/001` 下面的所有信息。

因此最终得到：

```python
SUBSCRIBE_TOPIC = "reitzzz-test-92831/device/001/#"
```
