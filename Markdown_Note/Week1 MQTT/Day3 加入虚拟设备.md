# Day3 加入虚拟设备



## 一、生成温度和 RPM

```python
temperature = random.uniform(32, 40)
rpm = random.randint(1450, 1550)
```

- `temperature` 是小数，所以使用 `random.uniform(32, 40)`。
- `rpm` 是整数，所以使用 `random.randint(1450, 1550)`。

## 二、记录最后一次上报时间

```python
last_seen = time.time()
```

`time.time()` 是获取当前时间的函数，用于表示设备最后一次上报的时间。
