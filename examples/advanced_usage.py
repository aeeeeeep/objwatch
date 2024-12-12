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
