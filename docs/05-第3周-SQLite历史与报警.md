# 第 3 周：SQLite + 历史 + 报警

## 本周先学什么

本周要把“只能看当前状态的内存 Demo”变成“能查询历史、记录报警和追踪命令的 Demo”：

1. SQLite 基础：理解数据库文件、表、行、列，以及为什么数据不应只放在 Python 内存里。
2. 最小 SQL：会创建表、插入数据、查询数据，并在需要时更新报警状态。
3. 数据分类：区分持续追加的遥测历史、当前 / 未解除的报警状态和命令日志。
4. 报警生命周期：高温时创建 `OPEN` 报警，温度恢复正常或 RESET 后变为 `RESOLVED`。
5. 幂等 / 去重：同一设备的同一种报警只允许存在一条未解除记录，重复高温不能每秒新增一条。
6. 最小审计记录：每次 START / STOP / RESET 都记录时间、设备、命令和结果。

## 核心概念是什么

> 表中未缩进表示根概念；`↳` 表示一级从属；`↳↳` 表示二级从属。这里表达的是学习上的组成/依赖关系，不代表严格的协议继承关系。

| 概念（层级） | 简单理解 | 本项目中的用法 |
| --- | --- | --- |
| SQLite | 嵌入式关系型数据库，数据保存在一个文件中，不需要单独启动数据库服务器。 | 保存遥测、报警和命令日志。 |
| ↳ 表 / 行 / 列 | 表存放一类数据，行是一条记录，列描述记录的字段。 | `telemetry`、`alarm`、`command_log` 各存一类信息。 |
| ↳↳ `CREATE TABLE` | 定义表名、字段和约束。 | 创建三张最小业务表。 |
| ↳ 持久化 | 程序重启后数据仍然存在，而不是只存在于内存。 | SQLite 文件保存历史和日志。 |
| ↳ `INSERT` | 向表中新增一条或多条记录。 | 每次收到遥测、产生新报警或执行命令时写入。 |
| ↳ `SELECT` | 从表中查询记录。 | 查询设备历史、最近报警和命令日志。 |
| ↳ `UPDATE` | 修改已有记录。 | 把报警从 `OPEN` 更新为 `RESOLVED`，写入 `resolved_at`。 |
| 当前状态 vs. 历史 | 当前状态回答“现在怎样”，历史记录回答“之前发生过什么”。 | 内存 / API 展示当前状态，SQLite 保存每次 telemetry。 |
| 报警状态 | 报警不是一条瞬时消息，而是有生命周期的业务记录。 | `OPEN → RESOLVED`。 |
| ↳ 幂等 / 去重 | 同一事件重复到达时，重复处理不会产生错误的重复结果。 | 已有 `HIGH_TEMP + OPEN` 时，下一条高温只更新当前状态，不新增报警。 |
| Command Log | 对控制操作留下的最小审计记录。 | 记录 `time`、`device_id`、`command`、`result`。 |

### 三类数据的区别

```text
telemetry：每次上报都可以新增，形成时间序列
alarm：围绕一个问题维护状态，避免同一 OPEN 报警重复创建
command_log：每次控制操作都记录结果，便于回看发生过什么
```

高温处理可以理解为一个小状态机：

```text
温度 > 85 且没有 OPEN 报警
        ↓
     创建 OPEN
        ↓ 温度恢复正常或 RESET
     更新为 RESOLVED
```

“不重复插报警”不是让数据库丢掉遥测，而是把两件事分开：遥测仍然按次记录，报警则按“设备 + 类型 + 未解除状态”去重。

### 建议参考

- [Python `sqlite3` 文档](https://docs.python.org/3/library/sqlite3.html)：学习 Python 连接 SQLite、执行 SQL 和读取结果。
- [SQLite：SQL 语言总览](https://www.sqlite.org/lang.html)：按需查 `CREATE TABLE`、`INSERT`、`SELECT`、`UPDATE`。
- [SQLite：CREATE TABLE](https://www.sqlite.org/lang_createtable.html)：理解表、字段和约束。
- [SQLite：INSERT](https://www.sqlite.org/lang_insert.html)：理解如何新增遥测、报警和日志记录。

### 本周学习边界

只做三张表和一个设备，不引入 ORM、迁移框架、复杂索引、完整工单系统或数据分析平台。先确认这条链路能工作：

```text
MQTT telemetry
        ↓
写入 telemetry
        ↓
判断是否高温
        ↓
创建或复用 OPEN 报警
        ↓
API 查询历史和报警
```

## 目标

这一周只保留三件事：

```text
telemetry 历史
alarm
command_log
```

不做复杂工单系统。

## Day 15：SQLite

表只建：

```text
telemetry
alarm
command_log
```

可选再建：

```text
device
```

但不是必须。

## Day 16：遥测历史

设备每次上传：

```text
temperature
rpm
status
timestamp
```

写入 SQLite。

增加：

```text
GET /devices/001/history
```

## Day 17：高温报警

规则：

```text
temperature > 85
→ 创建 HIGH_TEMP 报警
```

报警字段：

```text
id
device_id
type
status
message
created_at
resolved_at
```

## Day 18：不要重复插报警

如果已经存在：

```text
device_id = 001
type = HIGH_TEMP
status = OPEN
```

则下一秒还是高温：

```text
不要再新增
```

这就是当前项目需要理解的最小“幂等 / 状态管理”。

不要单独开一整天学理论。

## Day 19：报警解除

温度恢复正常或 RESET：

```text
OPEN
↓
RESOLVED
```

更新时间：

```text
resolved_at
```

## Day 20：Command Log

记录：

```text
time
device_id
command
result
```

例如：

```text
21:02
001
STOP
SUCCESS
```

## Day 21：第 3 周复盘

此时必须有：

```text
实时状态
历史遥测
高温报警
报警解除
命令日志
```

### 工单

不做完整工单。

最多在报警里加：

```text
suggestion = "检查设备过热"
```

或者：

```text
ticket = "检查 001 号设备过热"
```

即可。
