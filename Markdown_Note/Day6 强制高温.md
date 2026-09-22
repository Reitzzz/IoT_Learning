# Day6 强制高温

## 一、Day6 新增了什么

Day6 没有新增 MQTT 协议语法，主要是在 Python 模拟器中增加：

```text
按键 h
    ↓
force_overheat = True
    ↓
temperature = 90
    ↓
temperature_level = ALARM
```

MQTT 部分仍然只是发布 JSON Payload。新增的 `temperature_level` 是项目约定的字段，Broker 不解释它。

## 二、读取按键：msvcrt

```python
import msvcrt
```

`msvcrt` 是 Windows 标准库，不需要安装。

```python
if msvcrt.kbhit():
    key = msvcrt.getwch()
```

含义：

| 语法 | 作用 |
| --- | --- |
| `msvcrt.kbhit()` | 检查是否有按键，不阻塞程序 |
| `msvcrt.getwch()` | 读取一个字符，不需要按 Enter |
| `key.lower()` | 把 `H` 和 `h` 统一处理 |

`msvcrt` 只适用于 Windows。其他系统不能直接使用这段代码。

## 三、修改外部变量：global

文件顶层定义：

```python
force_overheat = False
```

函数内修改它：

```python
def read_keyboard():
    global force_overheat

    if msvcrt.kbhit() and msvcrt.getwch().lower() == "h":
        force_overheat = True
```

如果函数里不写 `global`，`force_overheat = True` 会尝试创建局部变量，而不是修改文件顶层的变量。

## 四、温度等级：函数和条件判断

```python
def get_temperature_level(temperature):
    if temperature < 70:
        return "NORMAL"
    elif temperature <= 85:
        return "WARNING"
    else:
        return "ALARM"
```

边界关系：

```text
temperature < 70        NORMAL
70 <= temperature <= 85 WARNING
temperature > 85        ALARM
```

`return` 会结束函数并把结果交回调用位置：

```python
temperature_level = get_temperature_level(temperature)
```

## 五、接入主循环

每轮循环先检查按键：

```python
read_keyboard()
```

然后决定温度：

```python
if force_overheat:
    temperature = 90
    force_overheat = False
else:
    temperature = random.uniform(32, 40)
```

这里使用单次触发：按一次 `h`，下一条消息温度为 90，之后恢复随机温度。

最后加入 Payload：

```python
data = {
    "temperature": temperature,
    "temperature_level": get_temperature_level(temperature),
    "rpm": rpm,
    "status": device_status,
    "last_seen": time.time(),
}
```

注意区分：

```text
status             设备状态：RUNNING / STOPPED
temperature_level  温度等级：NORMAL / WARNING / ALARM
```

按一次 `h` 后，Subscriber 应收到：

```json
{
  "temperature": 90,
  "temperature_level": "ALARM",
  "rpm": 1460,
  "status": "RUNNING",
  "last_seen": 1758500000
}
```
