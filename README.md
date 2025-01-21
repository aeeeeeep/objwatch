# ObjWatch

[![Documentation](https://img.shields.io/badge/docs-latest-green.svg?style=flat)](https://objwatch.readthedocs.io)
[![License](https://img.shields.io/github/license/aeeeeeep/objwatch)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/objwatch)](https://pypi.org/project/objwatch)
[![Downloads](https://static.pepy.tech/badge/objwatch)](https://pepy.tech/projects/objwatch)
[![Python Versions](https://img.shields.io/pypi/pyversions/objwatch)](https://github.com/aeeeeeep/objwatch)
[![GitHub pull request](https://img.shields.io/badge/PRs-welcome-blue)](https://github.com/aeeeeeep/objwatch/pulls)

\[ English | [中文](README_zh.md) \]

## Overview

ObjWatch is a robust Python library designed to streamline the debugging and monitoring of complex projects. By offering real-time tracing of object attributes and method calls, ObjWatch empowers developers to gain deeper insights into their codebases, facilitating issue identification, performance optimization, and overall code quality enhancement.

**⚠️ Performance Warning**

ObjWatch may impact your application's performance. It is recommended to use it solely in debugging environments.

## Features

- **Nested Structure Tracing**: Visualize and monitor nested function calls and object interactions with clear, hierarchical logging.
- **Enhanced Logging Support**: Leverage Python's built-in `logging` module for structured, customizable log outputs, including support for simple and detailed formats. Additionally, to ensure logs are captured even if the logger is disabled or removed by external libraries, you can set `level="force"`. When `level` is set to `"force"`, ObjWatch bypasses the standard logging handlers and uses `print()` to output log messages directly to the console, ensuring that critical debugging information is not lost.
- **Logging Message Types**: ObjWatch categorizes log messages into various types to provide detailed insights into code execution. The primary types include:
  
  - **`run`**: Indicates the start of a function or class method execution.
  - **`end`**: Signifies the end of a function or class method execution.
  - **`upd`**: Represents the creation of a new variable.
  - **`apd`**: Denotes the addition of elements to data structures like lists, sets, or dictionaries.
  - **`pop`**: Marks the removal of elements from data structures like lists, sets, or dictionaries.
  
  These classifications help developers efficiently trace and debug their code by understanding the flow and state changes within their applications.
- **Multi-GPU Support**: Seamlessly trace distributed PyTorch applications running across multiple GPUs, ensuring comprehensive monitoring in high-performance environments.
- **Custom Wrapper Extensions**: Extend ObjWatch's functionality with custom wrappers, allowing tailored tracing and logging to fit specific project needs.
- **Context Manager & API Integration**: Integrate ObjWatch effortlessly into your projects using context managers or API functions without relying on command-line interfaces.

## Installation

ObjWatch is available on [PyPI](https://pypi.org/project/objwatch). Install it using `pip`:

```bash
pip install objwatch
```

Alternatively, you can clone the latest repository and install from source:

```bash
git clone https://github.com/aeeeeeep/objwatch.git
cd objwatch
pip install .
```

## Getting Started

### Basic Usage

ObjWatch can be utilized as a context manager or through its API within your Python scripts.

#### Using as a Context Manager

```python
import objwatch

def main():
    # Your code
    pass

if __name__ == '__main__':
    with objwatch.ObjWatch(['your_module.py']):
        main()
```

#### Using the API

```python
import objwatch

def main():
    # Your code
    pass

if __name__ == '__main__':
    obj_watch = objwatch.watch(['your_module.py'])
    main()
    obj_watch.stop()
```

### Example Usage

Below is a comprehensive example demonstrating how to integrate ObjWatch into a Python script:

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
    # Using ObjWatch as a context manager
    with objwatch.ObjWatch(['examples/example_usage.py'], output='./objwatch.log', wrapper=BaseWrapper):
        main()

    # Using the watch function
    obj_watch = objwatch.watch(['examples/example_usage.py'], output='./objwatch.log', wrapper=BaseWrapper)
    main()
    obj_watch.stop()

```

When running the above script, ObjWatch will generate logs similar to the following:

<details>

<summary>Expected Log Output</summary>

```
[2025-01-08 20:02:10] [DEBUG] objwatch: Processed targets:
>>>>>>>>>>
examples/example_usage.py
<<<<<<<<<<
[2025-01-08 20:02:10] [WARNING] objwatch: wrapper 'BaseWrapper' loaded
[2025-01-08 20:02:10] [INFO] objwatch: Starting ObjWatch tracing.
[2025-01-08 20:02:10] [INFO] objwatch: Starting tracing.
[2025-01-08 20:02:10] [DEBUG] objwatch:    22 run main <-
[2025-01-08 20:02:10] [DEBUG] objwatch:    10 | run SampleClass.__init__ <- '0':(type)SampleClass, '1':10
[2025-01-08 20:02:10] [DEBUG] objwatch:    11 | end SampleClass.__init__ -> None
[2025-01-08 20:02:10] [DEBUG] objwatch:    13 | run SampleClass.increment <- '0':(type)SampleClass
[2025-01-08 20:02:10] [DEBUG] objwatch:    14 | | upd SampleClass.value None -> 10
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | | upd SampleClass.value 10 -> 11
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | end SampleClass.increment -> None
[2025-01-08 20:02:10] [DEBUG] objwatch:    13 | run SampleClass.increment <- '0':(type)SampleClass
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | | upd SampleClass.value 11 -> 12
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | end SampleClass.increment -> None
[2025-01-08 20:02:10] [DEBUG] objwatch:    13 | run SampleClass.increment <- '0':(type)SampleClass
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | | upd SampleClass.value 12 -> 13
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | end SampleClass.increment -> None
[2025-01-08 20:02:10] [DEBUG] objwatch:    13 | run SampleClass.increment <- '0':(type)SampleClass
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | | upd SampleClass.value 13 -> 14
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | end SampleClass.increment -> None
[2025-01-08 20:02:10] [DEBUG] objwatch:    13 | run SampleClass.increment <- '0':(type)SampleClass
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | | upd SampleClass.value 14 -> 15
[2025-01-08 20:02:10] [DEBUG] objwatch:    15 | end SampleClass.increment -> None
[2025-01-08 20:02:10] [DEBUG] objwatch:    17 | run SampleClass.decrement <- '0':(type)SampleClass
[2025-01-08 20:02:10] [DEBUG] objwatch:    19 | | upd SampleClass.value 15 -> 14
[2025-01-08 20:02:10] [DEBUG] objwatch:    19 | end SampleClass.decrement -> None
[2025-01-08 20:02:10] [DEBUG] objwatch:    17 | run SampleClass.decrement <- '0':(type)SampleClass
[2025-01-08 20:02:10] [DEBUG] objwatch:    19 | | upd SampleClass.value 14 -> 13
[2025-01-08 20:02:10] [DEBUG] objwatch:    19 | end SampleClass.decrement -> None
[2025-01-08 20:02:10] [DEBUG] objwatch:    17 | run SampleClass.decrement <- '0':(type)SampleClass
[2025-01-08 20:02:10] [DEBUG] objwatch:    19 | | upd SampleClass.value 13 -> 12
[2025-01-08 20:02:11] [DEBUG] objwatch:    19 | end SampleClass.decrement -> None
[2025-01-08 20:02:11] [DEBUG] objwatch:    26 end main -> None
[2025-01-08 20:02:11] [INFO] objwatch: Stopping ObjWatch tracing.
[2025-01-08 20:02:11] [INFO] objwatch: Stopping tracing.
```

</details>

## Configuration

ObjWatch offers customizable logging formats and tracing options to suit various project requirements. Utilize the `simple` parameter to toggle between detailed and simplified logging outputs.

### Parameters

- `targets` (list): Files or modules to monitor.
- `exclude_targets` (list, optional): Files or modules to exclude from monitoring.
- `ranks` (list, optional): GPU ranks to track when using `torch.distributed`.
- `output` (str, optional): Path to a file for writing logs.
- `output_xml` (str, optional): Path to the XML file for writing structured logs. If specified, tracing information will be saved in a nested XML format for easy browsing and analysis.
- `level` (str, optional): Logging level (e.g., `logging.DEBUG`, `logging.INFO`, `force` etc.).
- `simple` (bool, optional): Enable simple logging mode with the format `"DEBUG: {msg}"`.
- `wrapper` (ABCWrapper, optional): Custom wrapper to extend tracing and logging functionality.
- `with_locals` (bool, optional): Enable tracing and logging of local variables within functions during their execution.
- `with_globals` (bool, optional): Enable tracing and logging of global variables across function calls.
- `with_module_path` (bool, optional): Control whether to prepend the module path to function names in logs.

## Advanced Usage

### Multi-GPU Support

ObjWatch seamlessly integrates with distributed PyTorch applications, allowing you to monitor and trace operations across multiple GPUs. Specify the ranks you wish to track using the `ranks` parameter.

```python
import objwatch

def main():
    # Your distributed code
    pass

if __name__ == '__main__':
    obj_watch = objwatch.watch(['distributed_module.py'], ranks=[0, 1, 2, 3], output='./dist.log, simple=False)
    main()
    obj_watch.stop()
```

### Custom Wrapper Extensions

ObjWatch provides the `ABCWrapper` abstract base class, enabling users to create custom wrappers that extend and customize the library's tracing and logging capabilities. By subclassing `ABCWrapper`, developers can implement tailored behaviors that execute during function calls and returns, offering deeper insights and specialized monitoring suited to their project's specific needs.

#### ABCWrapper Class

The `ABCWrapper` class defines two essential methods that must be implemented:

- **`wrap_call(self, func_name: str, frame: FrameType) -> str`**:
  
  This method is invoked at the beginning of a function call. It receives the function name and the current frame object, which contains the execution context, including local variables and the call stack. Implement this method to extract, log, or modify information before the function executes.

- **`wrap_return(self, func_name: str, result: Any) -> str`**:
  
  This method is called upon a function's return. It receives the function name and the result returned by the function. Use this method to log, analyze, or alter information after the function has completed execution.

- **`wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]`**:

  This method is triggered when a variable is updated, receiving the old value and the current value. It can be used to log changes to variables, allowing for the tracking and debugging of variable state transitions.

For more details on frame objects, refer to the [official Python documentation](https://docs.python.org/3/library/types.html#types.FrameType).

#### TensorShapeWrapper

As an example of a custom wrapper, ObjWatch includes the `TensorShapeWrapper` class within the `objwatch.wrappers` module. This wrapper automatically logs the shapes of tensors involved in function calls, which is particularly beneficial in machine learning and deep learning workflows where tensor dimensions are critical for model performance and debugging.

#### Creating and Integrating Custom Wrappers

To create a custom wrapper:

1. **Subclass `ABCWrapper`**: Define a new class that inherits from `ABCWrapper` and implement the `wrap_call`, `wrap_return` and `wrap_upd` methods to define your custom behavior.

2. **Initialize ObjWatch with the Custom Wrapper**: When initializing `ObjWatch`, pass your custom wrapper via the `wrapper` parameter. This integrates your custom tracing logic into the ObjWatch tracing process.

By leveraging custom wrappers, you can enhance ObjWatch to capture additional context, perform specialized logging, or integrate with other monitoring tools, thereby providing a more comprehensive and tailored tracing solution for your Python projects.

#### Example Use Cases

For example, the `TensorShapeWrapper` can be integrated as follows:

```python
from objwatch.wrappers import TensorShapeWrapper

# Initialize ObjWatch with the custom TensorShapeWrapper
obj_watch = objwatch.ObjWatch(['your_module.py'], simple=False, wrapper=TensorShapeWrapper))
with obj_watch:
    main()
```

#### Example of Using a Custom Wrapper

It is recommended to refer to the  [`tests/test_torch_train.py`](tests/test_torch_train.py)  file. This file contains a complete example of a PyTorch training process, demonstrating how to integrate ObjWatch for monitoring and logging.

## Support

If you encounter any issues or have questions, feel free to open an issue on the [ObjWatch GitHub repository](https://github.com/aeeeeeep/objwatch) or reach out via email at [aeeeeeep@proton.me](mailto:aeeeeeep@proton.me).

More usage examples can be found in the `examples` directory, which is actively being updated.

## Acknowledgements

- Inspired by the need for better debugging and understanding tools in large Python projects.
- Powered by Python's robust tracing and logging capabilities.
