# ObjWatch

[![License](https://img.shields.io/github/license/aeeeeeep/objwatch)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/objwatch)](https://pypi.org/project/objwatch)
[![Downloads](https://static.pepy.tech/badge/objwatch)](https://pepy.tech/projects/objwatch)
[![Python Versions](https://img.shields.io/pypi/pyversions/objwatch)](https://github.com/aeeeeeep/objwatch)
[![GitHub pull request](https://img.shields.io/badge/PRs-welcome-blue)](https://github.com/aeeeeeep/objwatch/pulls)

\[ [English](README.md) | 中文 \]

## 概述

ObjWatch 是一个用于简化复杂项目调试和监控的 Python 工具库。通过实时追踪对象属性和方法调用，ObjWatch 使开发者能够深入了解代码库，帮助识别问题、优化性能并提升代码质量。

**⚠️ 性能警告**

ObjWatch 会影响程序的性能，建议仅在调试环境中使用。

## 功能

- **嵌套结构追踪**：通过清晰的层次化日志，直观地可视化和监控嵌套的函数调用和对象交互。
- **增强的日志支持**：利用 Python 内建的 `logging` 模块进行结构化、可定制的日志输出，支持简单和详细模式。此外，为确保即使 logger 被外部库禁用或删除，你也可以设置 `level="force"`。当 `level` 设置为 `"force"` 时，ObjWatch 将绕过标准的日志处理器，直接使用 `print()` 将日志消息输出到控制台，确保关键的调试信息不会丢失。
- **日志消息类型**：ObjWatch 将日志消息分类，以便提供详细的代码执行信息。主要类型包括：

  - **`run`**：表示函数或类方法的执行开始。
  - **`end`**：表示函数或类方法的执行结束。
  - **`upd`**：表示新变量的创建。
  - **`apd`**：表示向列表、集合或字典等数据结构中添加元素。
  - **`pop`**：表示从列表、集合或字典等数据结构中移除元素。

  这些分类帮助开发者高效地追踪和调试代码，了解程序中的执行流和状态变化。
- **多 GPU 支持**：无缝追踪分布式 PyTorch 程序，支持跨多个 GPU 运行，确保高性能环境中的全面监控。
- **自定义包装器扩展**：通过自定义包装器扩展 ObjWatch 的功能，使其能够根据项目需求进行定制化的追踪和日志记录。
- **上下文管理器和 API 集成**：通过上下文管理器或 API 函数轻松集成 ObjWatch，无需依赖命令行界面。

## 安装

ObjWatch 可通过 [PyPI](https://pypi.org/project/objwatch) 安装。使用 `pip` 安装：

```bash
pip install objwatch
```

## 快速开始

### 基本用法

ObjWatch 可以作为上下文管理器或通过 API 在 Python 脚本中使用。

#### 作为上下文管理器使用

```python
import objwatch

def main():
    # 你的代码
    pass

if __name__ == '__main__':
    with objwatch.ObjWatch(['your_module.py']):
        main()
```

#### 使用 API

```python
import objwatch

def main():
    # 你的代码
    pass

if __name__ == '__main__':
    obj_watch = objwatch.watch(['your_module.py'])
    main()
    obj_watch.stop()
```

### 示例用法

下面是一个综合示例，展示如何将 ObjWatch 集成到 Python 脚本中：

```python
import objwatch
import time

class SampleClass:
    def __init__(self, value):
        self.value = value

    def increment(self):
        self.value += 1
        time.sleep(0.1)

    def decrement(self):
        self.value -= 1
        time.sleep(0.1)

def main():
    obj = SampleClass(10)
    for _ in range(5):
        obj.increment()
    for _ in range(3):
        obj.decrement()

if __name__ == '__main__':
    # 使用上下文管理器并开启详细日志
    with objwatch.ObjWatch(['examples/example_usage.py']):
        main()

    # 使用 API 并开启简单日志
    obj_watch = objwatch.watch(['examples/example_usage.py'])
    main()
    obj_watch.stop()
```

运行以上脚本时，ObjWatch 会生成类似以下内容的日志：

<details>

<summary>Expected Log Output</summary>

```
[2024-12-14 20:40:56] [DEBUG] objwatch: Processed targets: {'examples/example_usage.py'}
[2024-12-14 20:40:56] [INFO] objwatch: Starting ObjWatch tracing.
[2024-12-14 20:40:56] [INFO] objwatch: Starting tracing.
[2024-12-14 20:40:56] [DEBUG] objwatch: run main
[2024-12-14 20:40:56] [DEBUG] objwatch: | run SampleClass.__init__
[2024-12-14 20:40:56] [DEBUG] objwatch: | end SampleClass.__init__
[2024-12-14 20:40:56] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:56] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:56] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:56] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:56] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:56] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.decrement
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.decrement
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.decrement
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.decrement
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.decrement
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.decrement
[2024-12-14 20:40:57] [DEBUG] objwatch: end main
[2024-12-14 20:40:57] [INFO] objwatch: Stopping ObjWatch tracing.
[2024-12-14 20:40:57] [INFO] objwatch: Stopping tracing.
[2024-12-14 20:40:57] [DEBUG] objwatch: Processed targets: {'examples/example_usage.py'}
[2024-12-14 20:40:57] [INFO] objwatch: Starting ObjWatch tracing.
[2024-12-14 20:40:57] [INFO] objwatch: Starting tracing.
[2024-12-14 20:40:57] [DEBUG] objwatch: run main
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.__init__
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.__init__
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:57] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:57] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:58] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:58] [DEBUG] objwatch: | run SampleClass.increment
[2024-12-14 20:40:58] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:58] [DEBUG] objwatch: | end SampleClass.increment
[2024-12-14 20:40:58] [DEBUG] objwatch: | run SampleClass.decrement
[2024-12-14 20:40:58] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:58] [DEBUG] objwatch: | end SampleClass.decrement
[2024-12-14 20:40:58] [DEBUG] objwatch: | run SampleClass.decrement
[2024-12-14 20:40:58] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:58] [DEBUG] objwatch: | end SampleClass.decrement
[2024-12-14 20:40:58] [DEBUG] objwatch: | run SampleClass.decrement
[2024-12-14 20:40:58] [DEBUG] objwatch: | | upd SampleClass.value
[2024-12-14 20:40:58] [DEBUG] objwatch: | end SampleClass.decrement
[2024-12-14 20:40:58] [DEBUG] objwatch: end main
[2024-12-14 20:40:58] [INFO] objwatch: Stopping ObjWatch tracing.
[2024-12-14 20:40:58] [INFO] objwatch: Stopping tracing.
```

</details>

## 配置

ObjWatch 提供可定制的日志格式和追踪选项，适应不同项目需求。使用 `simple` 参数可以在详细和简化日志输出之间切换。

### 参数

- `targets`（列表）：要监控的文件或模块。
- `ranks`（列表，可选）：在使用 `torch.distributed` 时跟踪的 GPU ids。
- `output`（字符串，可选）：写入日志的文件路径。
- `output_xml`（字符串，可选）：用于写入结构化日志的 XML 文件路径。如果指定，将以嵌套的 XML 格式保存追踪信息，便于浏览和分析。
- `level`（字符串，可选）：日志级别（例如 `DEBUG`，`INFO`）。
- `simple`（布尔值，可选）：启用简化日志模式，格式为 `"DEBUG: {msg}"`。
- `wrapper`（FunctionWrapper，可选）：自定义包装器，用于扩展追踪和日志记录功能。
- `with_locals`（布尔值，可选）：启用在函数执行期间对局部变量的追踪和日志记录。
- `with_module_path`（布尔值，可选）：控制是否在日志中的函数名称前添加模块路径前缀。

## 高级用法

### 多 GPU 支持

ObjWatch 无缝集成到分布式 PyTorch 程序中，允许你跨多个 GPU 监控和追踪操作。使用 `ranks` 参数指定要跟踪的 GPU ids。

```python
import objwatch

def main():
    # 你的多卡代码
    pass

if __name__ == '__main__':
    obj_watch = objwatch.watch(['distributed_module.py'], ranks=[0, 1, 2, 3], output='./dist.log', simple=False)
    main()
    obj_watch.stop()
```

### 自定义包装器扩展

ObjWatch 提供了 `FunctionWrapper` 抽象基类，允许用户创建自定义包装器，扩展和定制库的追踪和日志记录功能。通过继承 `FunctionWrapper`，开发者可以实现自定义行为，在函数调用和返回时执行，提供更深入的分析和专门的监控，适应项目的特定需求。

#### FunctionWrapper 类

`FunctionWrapper` 类定义了两个必须实现的核心方法：

- **`wrap_call(self, func_name: str, frame: FrameType) -> str`**：

  该方法在函数调用开始时触发，接收函数名和当前的帧对象，帧对象包含了执行上下文信息，包括局部变量和调用栈。在此方法中可以提取、记录或修改信息，在函数执行前进行处理。

- **`wrap_return(self, func_name: str, result: Any) -> str`**：

  该方法在函数返回时触发，接收函数名和返回的结果。在此方法中可以记录、分析或修改信息，函数执行完成后进行处理。

有关帧对象的更多信息，请参考 [官方 Python 文档](https://docs.python.org/3/library/types.html#types.FrameType)。

#### TensorShapeLogger

作为一个自定义包装器的示例，ObjWatch 在 `objwatch.wrappers` 模块中提供了 `TensorShapeLogger` 类。该包装器自动记录在函数调用中涉及的张量形状，这在机器学习和深度学习工作流中尤其有用，因为张量的维度对于模型性能和调试至关重要。

#### 创建和集成自定义包装器

要创建自定义包装器：

1. **继承 `FunctionWrapper`**：定义一个新的类，继承 `FunctionWrapper` 并实现 `wrap_call` 和 `wrap_return` 方法，以定义你的自定义行为。

2. **使用自定义包装器初始化 ObjWatch**：在初始化 ObjWatch 时，通过 `wrapper` 参数传递你的自定义包装器。这将把你的自定义追踪逻辑集成到 ObjWatch 的追踪过程中。

通过使用自定义包装器，可以增强 ObjWatch，捕获额外的上下文，执行专业的日志记录，或与其他监控工具集成，从而为你的 Python 项目提供更全面和定制化的追踪解决方案。

#### 示例用法

例如，可以如下集成 `TensorShapeLogger`：

```python
from objwatch.wrappers import TensorShapeLogger

# 使用自定义 TensorShapeLogger 初始化 ObjWatch
obj_watch = objwatch.ObjWatch(['your_module.py'], simple=False, wrapper=TensorShapeLogger)
with obj_watch:
    main()
```

#### 使用自定义包装器的示例

通过创建自定义包装器来扩展 ObjWatch 的功能。这使你可以根据项目的特定需求调整追踪和日志记录机制。

```python
from objwatch.wrappers import FunctionWrapper

class CustomWrapper(FunctionWrapper):
    def wrap_call(self, func_name, frame):
        return f" - Called {func_name} with args: {frame.f_locals}"

    def wrap_return(self, func_name, result):
        return f" - {func_name} returned {result}"

# 集成自定义包装器
obj_watch = objwatch.watch(['your_module.py'], simple=False, wrapper=CustomWrapper)
main()
obj_watch.stop()
```

## 支持

如果遇到任何问题或有疑问，请随时在 [ObjWatch GitHub 仓库](https://github.com/aeeeeeep/objwatch) 提交 issue，或通过电子邮件与我们联系 [aeeeeeep@proton.me](mailto:aeeeeeep@proton.me)。

## 致谢

- 灵感来源于对大型 Python 项目更深入理解和便捷调试的需求。
- 基于 Python 强大的追踪和日志记录功能。
