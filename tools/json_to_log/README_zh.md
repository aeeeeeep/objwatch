# JSON到日志转换器（ObjWatch）

\[ [English](README.md) | 中文 \]

此工具将ObjWatch生成的JSON输出文件转换为人类可读的日志格式，使分析和理解追踪结果更加容易。

## 功能特点

- 将ObjWatch JSON输出转换为可读日志格式
- 使用缩进和调用深度标记保留调用层次结构
- 以结构化方式格式化配置信息
- 包含版本、开始时间和系统信息等运行时数据
- 处理不同的事件类型（函数调用、返回、变量更新等）
- 提供命令行界面，支持自定义输出路径

## 使用方法

```bash
python3 json_to_log.py <json文件> [-o <输出文件>]
```

### 参数说明

- `<json文件>`: ObjWatch生成的输入JSON文件路径
- `-o, --output <输出文件>`: （可选）输出日志文件路径
  - 如果未指定，工具将创建一个与输入JSON文件同名但扩展名为`.log`的日志文件

### 示例

```bash
# 将objwatch.json转换为objwatch.log
python3 json_to_log.py objwatch.json

# 将objwatch.json转换为custom_output.log
python3 json_to_log.py objwatch.json -o custom_output.log
```

## 输出格式

生成的日志文件包括：

1. 包含运行时信息的头部部分
2. 结构化格式的配置详细信息
3. 带有缩进表示调用深度的事件日志
4. （终端输出）使用颜色编码区分不同事件类型

每个日志条目以行号开始，后跟表示调用深度的缩进，使执行流程易于跟踪。

## 事件类型

转换器处理以下事件类型：

- **函数调用** (`run`): 当函数或方法开始执行时
- **函数返回** (`end`): 当函数或方法完成执行时
- **变量更新** (`upd`): 当变量被修改时
- **集合操作** (`apd`/`pop`): 当元素被添加到或从集合中移除时
