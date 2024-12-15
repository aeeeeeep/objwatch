# ObjWatch

![PyPI](https://img.shields.io/pypi/v/objwatch)
![License](https://img.shields.io/github/license/aeeeeeep/objwatch)
![Python Versions](https://img.shields.io/pypi/pyversions/objwatch)

## Overview

ObjWatch is a robust Python library designed to streamline the debugging and monitoring of complex projects. By offering real-time tracing of object attributes and method calls, ObjWatch empowers developers to gain deeper insights into their codebases, facilitating issue identification, performance optimization, and overall code quality enhancement.

**⚠️ Performance Warning**

ObjWatch may impact your application's performance. It is recommended to use it solely in debugging environments.

## Features

- **Nested Structure Tracing**: Visualize and monitor nested function calls and object interactions with clear, hierarchical logging.
- **Enhanced Logging Support**: Leverage Python's built-in `logging` module for structured, customizable log outputs, including support for simple and detailed formats.
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

## Getting Started

### Basic Usage

ObjWatch can be utilized as a context manager or through its API within your Python scripts.

#### Using as a Context Manager

```python
import objwatch

def main():
    # Your application code
    pass

if __name__ == '__main__':
    with objwatch.ObjWatch(['your_module.py']):
        main()
```

#### Using the API

```python
import objwatch

def main():
    # Your application code
    pass

if __name__ == '__main__':
    obj_watch = objwatch.watch(['your_module.py'])
    main()
    obj_watch.stop()
```

### Example Usage

Below is a comprehensive example demonstrating how to integrate ObjWatch into a Python script:

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
    # Using as a Context Manager with Detailed Logging
    with objwatch.ObjWatch(['examples/example_usage.py']):
        main()

    # Using the API with Simple Logging
    obj_watch = objwatch.watch(['examples/example_usage.py'])
    main()
    obj_watch.stop()
```

When running the above script, ObjWatch will generate logs similar to the following:

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

## Configuration

ObjWatch offers customizable logging formats and tracing options to suit various project requirements. Utilize the `simple` parameter to toggle between detailed and simplified logging outputs.

### Parameters

- `targets` (list): Files or modules to monitor.
- `ranks` (list, optional): GPU ranks to track when using `torch.distributed`.
- `output` (str, optional): Path to a file for writing logs.
- `level` (str, optional): Logging level (e.g., `DEBUG`, `INFO`).
- `simple` (bool, optional): Enable simple logging mode with the format `"DEBUG: {msg}"`.
- `wrapper` (FunctionWrapper, optional): Custom wrapper to extend tracing and logging functionality.

## Advanced Usage

### Multi-GPU Support

ObjWatch seamlessly integrates with distributed PyTorch applications, allowing you to monitor and trace operations across multiple GPUs. Specify the ranks you wish to track using the `ranks` parameter.

```python
import objwatch

def main():
    # Your distributed application code
    pass

if __name__ == '__main__':
    obj_watch = objwatch.watch(['distributed_module.py'], ranks=[0, 1, 2, 3], output='./dist.log, simple=False)
    main()
    obj_watch.stop()
```

### Custom Wrapper Extensions

ObjWatch provides the `FunctionWrapper` abstract base class, enabling users to create custom wrappers that extend and customize the library's tracing and logging capabilities. By subclassing `FunctionWrapper`, developers can implement tailored behaviors that execute during function calls and returns, offering deeper insights and specialized monitoring suited to their project's specific needs.

#### FunctionWrapper Class

The `FunctionWrapper` class defines two essential methods that must be implemented:

- **`wrap_call(self, func_name: str, frame: FrameType) -> str`**:
  
  This method is invoked at the beginning of a function call. It receives the function name and the current frame object, which contains the execution context, including local variables and the call stack. Implement this method to extract, log, or modify information before the function executes.

- **`wrap_return(self, func_name: str, result: Any) -> str`**:
  
  This method is called upon a function's return. It receives the function name and the result returned by the function. Use this method to log, analyze, or alter information after the function has completed execution.

For more details on frame objects, refer to the [official Python documentation](https://docs.python.org/3/library/types.html#types.FrameType).

#### TensorShapeLogger

As an example of a custom wrapper, ObjWatch includes the `TensorShapeLogger` class within the `objwatch.wrappers` module. This wrapper automatically logs the shapes of tensors involved in function calls, which is particularly beneficial in machine learning and deep learning workflows where tensor dimensions are critical for model performance and debugging.

#### Creating and Integrating Custom Wrappers

To create a custom wrapper:

1. **Subclass `FunctionWrapper`**: Define a new class that inherits from `FunctionWrapper` and implement the `wrap_call` and `wrap_return` methods to define your custom behavior.

2. **Initialize ObjWatch with the Custom Wrapper**: When initializing `ObjWatch`, pass your custom wrapper via the `wrapper` parameter. This integrates your custom tracing logic into the ObjWatch tracing process.

By leveraging custom wrappers, you can enhance ObjWatch to capture additional context, perform specialized logging, or integrate with other monitoring tools, thereby providing a more comprehensive and tailored tracing solution for your Python projects.

#### Example Use Cases

For example, the `TensorShapeLogger` can be integrated as follows:

```python
from objwatch.wrappers import TensorShapeLogger

# Initialize ObjWatch with the custom TensorShapeLogger
obj_watch = objwatch.ObjWatch(['your_module.py'], simple=False, wrapper=TensorShapeLogger))
with obj_watch:
    main()
```

#### Example of Using a Custom Wrapper

Extend ObjWatch's functionality by creating custom wrappers. This allows you to tailor the tracing and logging mechanisms to fit specific needs within your projects.

```python
from objwatch.wrappers import FunctionWrapper

class CustomWrapper(FunctionWrapper):
    def wrap_call(self, func_name, frame):
        return f" - Called {func_name} with args: {frame.f_locals}"

    def wrap_return(self, func_name, result):
        return f" - {func_name} returned {result}"

# Integrate the custom wrapper
obj_watch = objwatch.watch(['your_module.py'], simple=False, wrapper=CustomWrapper)
main()
obj_watch.stop()
```

## Contributing

Contributions are welcome! Whether you're reporting a bug, suggesting a feature, or submitting a pull request, your input is invaluable to improving ObjWatch.

1. **Fork the Repository**: Click the "Fork" button on the repository page.
2. **Create a Branch**: `git checkout -b feature/YourFeature`
3. **Commit Your Changes**: `git commit -m 'Add some feature'`
4. **Push to the Branch**: `git push origin feature/YourFeature`
5. **Open a Pull Request**

Please ensure your code follows the project's coding standards and includes appropriate tests.

## Support

If you encounter any issues or have questions, feel free to open an issue on the [ObjWatch GitHub repository](https://github.com/aeeeeeep/objwatch) or reach out via email at [aeeeeeep@proton.me](mailto:aeeeeeep@proton.me).

## Acknowledgements

- Inspired by the need for better debugging and understanding tools in large Python projects.
- Powered by Python's robust tracing and logging capabilities.
