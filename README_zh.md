<div align="center">
  <img src="docs/resource/objwatch-logo.png" alt="ObjWatch Logo" style="width: 256px; height: auto; vertical-align: middle; margin-right: 128px;" />
</div>

# ObjWatch

[![Nightly Test Status](https://github.com/aeeeeeep/objwatch/actions/workflows/nightly-test.yml/badge.svg)](https://github.com/aeeeeeep/objwatch/actions/workflows/nightly-test.yml)
[![Documentation](https://img.shields.io/badge/docs-latest-green.svg?style=flat)](https://objwatch.readthedocs.io)
[![License](https://img.shields.io/github/license/aeeeeeep/objwatch)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/objwatch)](https://pypi.org/project/objwatch)
[![Downloads](https://static.pepy.tech/badge/objwatch)](https://pepy.tech/projects/objwatch)
[![Python Versions](https://img.shields.io/pypi/pyversions/objwatch)](https://github.com/aeeeeeep/objwatch)
[![GitHub pull request](https://img.shields.io/badge/PRs-welcome-blue)](https://github.com/aeeeeeep/objwatch/pulls)

\[ [English](README.md) | 中文 \]

## 🔭 概述

ObjWatch 是一款面向对象的 Python 调试库，支持对模块、类、成员、方法、函数、全局变量及局部变量进行可配置的嵌套追踪与监控，并兼容多进程场景。它帮助开发者深入洞察代码运行细节，快速定位问题、优化性能并全面提升代码质量。⚠️**该工具会影响程序的性能，建议仅在调试环境中使用。**

[ObjWatch Log Viewer](tools/vscode_extension) 扩展插件已在 [VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=aeeeeeep.objwatch-log-viewer) 推出，通过智能语法高亮、层级结构识别和灵活的折叠功能，大幅提升 ObjWatch 日志易读性。

## 📦 安装

可通过 [PyPI](https://pypi.org/project/objwatch) 安装。使用 `pip` 安装：

```bash
pip install objwatch
```

也可以克隆最新的源码安装：

```bash
git clone https://github.com/aeeeeeep/objwatch.git
cd objwatch
pip install -e .
```

## ⚙️ 配置

ObjWatch 提供可定制的日志格式和追踪选项，适应不同项目需求。

### 参数

- `targets` (列表) ：要监控的文件路径、模块、类、类成员、类方法、函数、全局变量或 Python 对象。具体语法格式如下：
  - 模块对象：直接传入模块实例
  - 类对象：直接传入类定义
  - 实例方法：直接传入方法实例
  - 函数对象：直接传入函数实例
  - 字符串格式：
    - 模块：'package.module'
    - 类：'package.module:ClassName'
    - 类属性：'package.module:ClassName.attribute'
    - 类方法：'package.module:ClassName.method()'
    - 函数：'package.module:function()'
    - 全局变量：'package.module::GLOBAL_VAR'

  示例演示混合使用对象和字符串：
  ```python
  from package.models import User
  from package.utils import format_str

  with objwatch.ObjWatch([
      User,                  # 直接监控类对象
      format_str,            # 直接监控函数对象
      'package.config::DEBUG_MODE'  # 字符串格式全局变量
  ]):
      main()
  ```
- `exclude_targets` (列表，可选) ：要排除监控的文件或模块。
- `with_locals` (布尔值，可选) ：启用在函数执行期间对局部变量的追踪和日志记录。
- `with_globals` (布尔值，可选) ：启用跨函数调用的全局变量追踪和日志记录。当你输入的 `targets` 列表中包含全局变量时，需要同时启用此选项。
- `output` (字符串，可选) ：写入日志的文件路径，必须以 '.objwatch' 结尾，用于 ObjWatch Log Viewer 扩展插件。
- `output_json` (字符串，可选) ：用于写入结构化日志的 JSON 文件路径。如果指定，将以嵌套的 JSON 格式保存追踪信息，便于后续分析工作。
- `level` (字符串，可选) ：日志级别 (例如 `logging.DEBUG`，`logging.INFO`，`force` 等) 。为确保即使 logger 被外部库禁用或删除，日志仍然有效，可以设置 `level` 为 `"force"`，这将绕过标准的日志处理器，直接使用 `print()` 将日志消息输出到控制台，确保关键的调试信息不会丢失。
- `simple` (布尔值，可选) ：默认值为 True，禁用简化日志模式，格式为 `"[{time}] [{level}] objwatch: {msg}"`。
- `wrapper` (ABCWrapper，可选) ：自定义包装器，用于扩展追踪和日志记录功能，详见下文。
- `framework` (字符串，可选)：需要使用的多进程框架模块。
- `indexes` (列表，可选)：需要在多进程环境中跟踪的 ids。
- `output_mode` (字符串，可选)：日志输出模式。选项：'std', 'zmq'。默认为 'std'。
- `zmq_endpoint` (字符串，可选)：'zmq' 模式的 ZeroMQ 端点。默认为 "tcp://127.0.0.1:5555"。
- `zmq_topic` (字符串，可选)：'zmq' 模式的 ZeroMQ 主题。默认为 ""。
- `auto_start_consumer` (布尔值，可选)：是否自动启动 ZeroMQ 消费者。默认为 True。

## 🚀 快速开始

### 基本用法

ObjWatch 可以作为上下文管理器或通过 API 在 Python 脚本中使用。

#### 作为上下文管理器使用

```python
import objwatch

def main():
    # 你的代码
    pass

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
import time
import objwatch
from objwatch.wrappers import BaseWrapper


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
    # 使用上下文管理器并开启日志
    with objwatch.ObjWatch(['examples/example_usage.py'], output='./log.objwatch', wrapper=BaseWrapper):
        main()

    # 使用 API 并开启日志
    obj_watch = objwatch.watch(['examples/example_usage.py'], output='./log.objwatch', wrapper=BaseWrapper)
    main()
    obj_watch.stop()
```

运行以上脚本时，ObjWatch 会生成类似以下内容的日志：

<details>

<summary>Expected Log Output</summary>

```
Starting ObjWatch tracing.
================================================================================
# ObjWatch Log
> Version:        /
> Start Time:     /
> System Info:    /
> Python Version: /

## Config:
* targets:
  - examples/example_usage.py
* exclude_targets: None
* framework: None
* indexes: None
* output: ./log.objwatch
* output_json: ./objwatch.json
* level: DEBUG
* simple: True
* wrapper: BaseWrapper
* with_locals: False
* with_globals: False

## Targets:
{}

## Filename Targets:
* examples/example_usage.py

## Exclude Filename Targets:
* None
================================================================================
   35 run __main__.main <- 
   23   run __main__.SampleClass.__init__ <- '0':(type)SampleClass, '1':10
   23   end __main__.SampleClass.__init__ -> None
   25   run __main__.SampleClass.increment <- '0':(type)SampleClass
   14     upd SampleClass.value None -> 10
   14     upd SampleClass.value 10 -> 11
   25   end __main__.SampleClass.increment -> None
   25   run __main__.SampleClass.increment <- '0':(type)SampleClass
   14     upd SampleClass.value 11 -> 12
   25   end __main__.SampleClass.increment -> None
   25   run __main__.SampleClass.increment <- '0':(type)SampleClass
   14     upd SampleClass.value 12 -> 13
   25   end __main__.SampleClass.increment -> None
   25   run __main__.SampleClass.increment <- '0':(type)SampleClass
   14     upd SampleClass.value 13 -> 14
   25   end __main__.SampleClass.increment -> None
   25   run __main__.SampleClass.increment <- '0':(type)SampleClass
   14     upd SampleClass.value 14 -> 15
   25   end __main__.SampleClass.increment -> None
   27   run __main__.SampleClass.decrement <- '0':(type)SampleClass
   18     upd SampleClass.value 15 -> 14
   27   end __main__.SampleClass.decrement -> None
   27   run __main__.SampleClass.decrement <- '0':(type)SampleClass
   18     upd SampleClass.value 14 -> 13
   27   end __main__.SampleClass.decrement -> None
   27   run __main__.SampleClass.decrement <- '0':(type)SampleClass
   18     upd SampleClass.value 13 -> 12
   27   end __main__.SampleClass.decrement -> None
   35 end __main__.main -> None
Stopping ObjWatch tracing.
```

</details>

## ✨ 功能

- **🎯 灵活的目标监控**：支持多种目标选择模式，如文件路径，模块，类，类成员，类方法，函数，全局变量。
- **🌳 嵌套结构追踪**：通过清晰的层次化日志，直观地可视化和监控嵌套的函数调用和对象交互。
- **📝 增强的日志支持**：利用 Python 内建的 `logging` 模块进行结构化、可定制的日志输出，支持简单和详细模式。
- **📋 日志消息类型**：ObjWatch 将日志消息分类，以便提供详细的代码执行信息。主要类型包括：

  - **`run`**：表示函数或类方法的执行开始。
  - **`end`**：表示函数或类方法的执行结束。
  - **`upd`**：表示新变量的创建。
  - **`apd`**：表示向数据结构中添加元素。
  - **`pop`**：表示从数据结构中移除元素。

  这些分类帮助开发者高效地追踪和调试代码，了解程序中的执行流和状态变化。

- **📊 结构化日志格式**：ObjWatch 使用一致的日志格式，便于解析和分析：

  **标准日志结构**：

  ```python
  f"{lineno:>5} {'  '*call_depth}{event_type} {object_string} {message_string}"
  ```

  **多进程日志结构**：

  ```python
  f"[#{process_id}] {lineno:>5} {'  '*call_depth}{event_type} {object_string} {message_string}"
  ```

  其中：

  - `lineno`：行号（右对齐，5个字符）
  - `call_depth`：调用栈深度（每级缩进2个空格）
  - `event_type`：事件类型（run, end, upd, apd, pop）
  - `object_string`：对象标识符（如 `SampleClass.value`）
  - `message_string`：事件特定消息（如 `None -> 10`）
  - `process_id`：多进程环境中的进程标识符

- **🔥 多进程支持**：无缝追踪分布式程序，支持跨多个进程/GPU 运行，确保高性能环境中的全面监控。
- **🔌 自定义包装器扩展**：通过自定义包装器扩展功能，使其能够根据项目需求进行定制化的追踪和日志记录。
- **🎛️ 上下文管理器和 API 集成**：通过上下文管理器或 API 函数轻松集成，无需依赖命令行界面。

## 🪁 高级用法

### 多进程支持

无缝集成到多进程程序中，允许你跨多个进程监控和追踪操作。使用 `indexes` 参数指定要跟踪的进程索引。

支持的框架：
- `torch.distributed`: PyTorch 分布式环境，用于多 GPU 支持
- `multiprocessing`: Python 内置的多进程库，用于并行处理
- 自定义框架：扩展支持其他多进程框架

```python
import objwatch

def main():
    # 多进程代码
    pass

if __name__ == '__main__':
    obj_watch = objwatch.watch(['multi_process_module.py'], indexes=[0, 1, 2, 3], output='./mp.objwatch')
    main()
    obj_watch.stop()
```

#### 自定义框架扩展

你可以通过向 MPHandls 类添加 `_check_init_{framework_name}` 方法来扩展对自定义多进程框架的支持。该方法应该：

1. 检查框架是否已初始化
2. 如果已初始化，设置 `self.initialized = True`
3. 设置 `self.index` 为当前进程索引
4. 设置 `self.sync_fn` 为同步函数（如果不需要则为 None）

自定义框架示例：

```python
class MPHandls:
    # ... 现有代码 ...
    
    def _check_init_custom_framework(self) -> None:
        """
        自定义框架初始化检查。
        将 'custom_framework' 替换为你的实际框架名称。
        """
        try:
            import custom_framework
            if custom_framework.is_initialized():
                self.initialized = True
                self.index = custom_framework.get_current_rank()
                self.sync_fn = custom_framework.barrier
                log_info(f"custom_framework 已初始化。索引: {self.index}")
        except ImportError:
            log_error("自定义框架不可用")
            raise ValueError("自定义框架不可用")
```

要使用你的自定义框架，请在配置中指定框架名称：

```python
obj_watch = objwatch.watch(['your_module.py'], framework='custom_framework', indexes=[0, 1])
```

### 自定义包装器扩展

ObjWatch 提供了 `ABCWrapper` 抽象基类，允许用户创建自定义包装器，扩展和定制库的追踪和日志记录功能。通过继承 `ABCWrapper`，开发者可以实现自定义行为，在函数调用和返回时执行，提供更深入的分析和专门的监控，适应项目的特定需求。

#### ABCWrapper 类

`ABCWrapper` 类定义了三个必须实现的核心方法：

- **`wrap_call(self, func_name: str, frame: FrameType) -> str`**：

  该方法在函数调用开始时触发，接收函数名和当前的帧对象，帧对象包含了执行上下文信息，包括局部变量和调用栈。在此方法中可以提取、记录或修改信息，在函数执行前进行处理。

- **`wrap_return(self, func_name: str, result: Any) -> str`**：

  该方法在函数返回时触发，接收函数名和返回的结果。在此方法中可以记录、分析或修改信息，函数执行完成后进行处理。

- **`wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]`**：

  该方法在变量更新时触发，接收旧值和当前值。可用于记录变量的变化，分析其变化过程，从而跟踪和调试变量状态的变化。

有关帧对象的更多信息，请参考 [官方 Python 文档](https://docs.python.org/3/c-api/frame.html)。

#### 支持的 Wrapper

下表概述了目前支持的 Wrapper，每个 Wrapper 提供了针对不同跟踪和日志记录需求的专业功能：

| **Wrapper**                                                         | **描述**                                                                                         |
|---------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| [**BaseWrapper**](objwatch/wrappers/base_wrapper.py)                | 实现了基本的日志记录功能，用于监控函数调用和返回。                                                  |
| [**CPUMemoryWrapper**](objwatch/wrappers/cpu_memory_wrapper.py)     | 使用 `psutil.virtual_memory()` 获取 CPU 内存统计信息，支持选择特定的指标，用于在函数执行过程中监控 CPU 内存使用情况。 |
| [**TensorShapeWrapper**](objwatch/wrappers/tensor_shape_wrapper.py) | 记录 `torch.Tensor` 对象的形状，适用于机器学习和深度学习工作流中的调试与性能分析。                   |
| [**TorchMemoryWrapper**](objwatch/wrappers/torch_memory_wrapper.py) | 使用 `torch.cuda.memory_stats()` 获取 GPU 内存统计信息，支持选择特定的指标，用于监控 GPU 显存使用情况，包括分配、预留和释放内存等。 |

#### TensorShapeWrapper

作为一个自定义包装器的示例，在 `objwatch.wrappers` 模块中提供了 `TensorShapeWrapper` 类。该包装器自动记录在函数调用中涉及的张量形状，这在机器学习和深度学习工作流中尤其有用，因为张量的维度对于模型性能和调试至关重要。

#### 创建和集成自定义包装器

要创建自定义包装器：

1. **继承 `ABCWrapper`**：定义一个新的类，继承 `ABCWrapper` 并实现 `wrap_call`，`wrap_return` 和 `wrap_upd` 方法，以定义你的自定义行为。

2. **使用自定义包装器初始化 ObjWatch**：在初始化时，通过 `wrapper` 参数传递你的自定义包装器。这将把你的自定义追踪逻辑集成到追踪过程中。

通过使用自定义包装器，可以捕获额外的上下文，执行专业的日志记录，或与其他监控工具集成，从而为你的 Python 项目提供更全面和定制化的追踪解决方案。

#### 示例用法

例如，可以如下集成 `TensorShapeWrapper`：

```python
from objwatch.wrappers import TensorShapeWrapper

# 使用自定义 TensorShapeWrapper 初始化
obj_watch = objwatch.ObjWatch(['your_module.py'], wrapper=TensorShapeWrapper)
with obj_watch:
    main()
```

## 💬 支持

如果遇到任何问题或有疑问，请随时在 [ObjWatch GitHub 仓库](https://github.com/aeeeeeep/objwatch) 提交 issue，或通过电子邮件与我联系 [aeeeeeep@proton.me](mailto:aeeeeeep@proton.me)。

更多使用示例可以在 `examples` 目录中找到，我们正在积极更新这个目录。

## 🙏 致谢

- 灵感来源于对大型 Python 项目更深入理解和便捷调试的需求。
- 基于 Python 强大的追踪和日志记录功能。
