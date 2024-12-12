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
    # Using ObjWatch as a context manager
    with objwatch.ObjWatch(['examples/example_usage.py']):
        main()

    # Using the watch function
    obj_watch = objwatch.watch(['examples/example_usage.py'])
    main()
    obj_watch.stop()
