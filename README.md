# ObjWatch


## Overview

ObjWatch is a powerful Python library designed to simplify the understanding and debugging of large-scale projects. By providing real-time tracing of object attributes and method calls, ObjWatch helps developers gain deeper insights into their codebase, making it easier to identify issues, optimize performance, and enhance code quality.

## Features

- **Comprehensive Tracing**: Monitor method calls and attribute changes across specified files or modules.
- **Flexible Integration**: Easily integrate ObjWatch into your projects using simple interfaces or command-line tools.
- **Enhanced Logging**: Utilize Python's built-in `logging` module for structured and customizable log outputs.
- **Minimal Overhead**: Designed to have minimal impact on your application's performance.
- **Extensible Architecture**: Modular design allows for easy extension and contribution from the open-source community.

## Installation

```bash
pip install .
```

## Getting Started

### Basic Usage

ObjWatch can be used both as a context manager within your Python scripts and as a command-line tool. Below are examples demonstrating both methods.

#### 1. Using ObjWatch as a Context Manager

This method is ideal for integrating ObjWatch directly into your Python code, allowing you to start and stop tracing around specific code blocks.

```python
# Using ObjWatch as a context manager
with objwatch.ObjWatch(['example.py']):
    main()

# Using the watch function
obj_watch = objwatch.watch(['example.py'])
main()
obj_watch.stop()
```

#### 2. Using ObjWatch via Command-Line Interface

ObjWatch also provides a CLI for tracing scripts executed directly or through shell commands, making it versatile for various workflows.

```bash
python3 -m objwatch -t "example.py" -s "python your_script.py"
```

### Example Usage

Here's a comprehensive example demonstrating how to use ObjWatch within a Python script:

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
    # First usage: Context manager
    with objwatch.ObjWatch(['examples/example_usage.py']):
        main()

    # Second usage: watch function
    obj_watch = objwatch.watch(['examples/example_usage.py'])
    main()
    obj_watch.stop()
```

When running the above script, ObjWatch will generate logs similar to the following:

<details>

<summary>Expected Log Output</summary>

```
[2024-12-12 20:34:09] [DEBUG] objwatch: Processed targets: {'examples/example_usage.py'}
[2024-12-12 20:34:09] [INFO] objwatch: Starting ObjWatch tracing.
[2024-12-12 20:34:09] [INFO] objwatch: Starting tracing.         
[2024-12-12 20:34:09] [DEBUG] objwatch: run main                                                        
[2024-12-12 20:34:09] [DEBUG] objwatch: run SampleClass.__init__ 
[2024-12-12 20:34:09] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:09] [DEBUG] objwatch: upd SampleClass.value    
[2024-12-12 20:34:09] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:09] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:09] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:09] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:09] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:09] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:09] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:09] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:09] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.decrement
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.decrement
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.decrement
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [INFO] objwatch: Stopping ObjWatch tracing.
[2024-12-12 20:34:10] [INFO] objwatch: Stopping tracing.
[2024-12-12 20:34:10] [DEBUG] objwatch: Processed targets: {'examples/example_usage.py'}
[2024-12-12 20:34:10] [INFO] objwatch: Starting ObjWatch tracing.
[2024-12-12 20:34:10] [INFO] objwatch: Starting tracing.
[2024-12-12 20:34:10] [DEBUG] objwatch: run main
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.__init__
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.increment
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.decrement
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:10] [DEBUG] objwatch: run SampleClass.decrement
[2024-12-12 20:34:10] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:11] [DEBUG] objwatch: run SampleClass.decrement
[2024-12-12 20:34:11] [DEBUG] objwatch: upd SampleClass.value
[2024-12-12 20:34:11] [INFO] objwatch: Stopping ObjWatch tracing.
[2024-12-12 20:34:11] [INFO] objwatch: Stopping tracing.
```

</details>

## Advanced Usage

### Tracking Multiple Classes and Modules

ObjWatch's flexible architecture allows you to track multiple classes, functions, and modules simultaneously. Here's an example:

```python
import objwatch
import time

class Alpha:
    def action(self):
        self.status = 'active'
        self.status = 'inactive'

class Beta:
    def action(self):
        self.status = 'running'
        self.status = 'stopped'

def main():
    objects = [Alpha(), Beta()]
    for obj in objects:
        obj.action()

if __name__ == '__main__':
    with objwatch.ObjWatch(['examples/advanced_usage.py']):
        main()
```

<details>

<summary>Expected Log Output</summary>

```
[2024-12-12 20:41:19] [DEBUG] objwatch: Processed targets: {'examples/advanced_usage.py'}
[2024-12-12 20:41:19] [INFO] objwatch: Starting ObjWatch tracing.
[2024-12-12 20:41:19] [INFO] objwatch: Starting tracing.
[2024-12-12 20:41:19] [DEBUG] objwatch: run main
[2024-12-12 20:41:19] [DEBUG] objwatch: run Alpha.action
[2024-12-12 20:41:19] [DEBUG] objwatch: upd Alpha.status
[2024-12-12 20:41:19] [DEBUG] objwatch: run Beta.action
[2024-12-12 20:41:19] [DEBUG] objwatch: upd Beta.status
[2024-12-12 20:41:19] [INFO] objwatch: Stopping ObjWatch tracing.
[2024-12-12 20:41:19] [INFO] objwatch: Stopping tracing.
```

</details>

## Configuration

ObjWatch leverages Python's `logging` module, allowing you to customize log levels and outputs according to your needs.

### Setting Log Level and Output File

You can configure the log level and specify an output file using command-line arguments:

```bash
python3 -m objwatch -t "example.py" -s "python your_script.py" --log-level DEBUG --output objwatch.log
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

If you encounter any issues or have questions, feel free to open an issue on the [objwatch](https://github.com/aeeeeeep/objwatch) or reach out via email at [aeeeeeep@proton.me](mailto:aeeeeeep@proton.me).

## Acknowledgements

- Inspired by the need for better debugging and understanding tools in large Python projects.
- Powered by Python's robust tracing and logging capabilities.

