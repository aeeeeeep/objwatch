import argparse
import sys
import runpy
import logging
import os
from .core import ObjWatch
from .logger import get_logger


def main():
    parser = argparse.ArgumentParser(description='ObjWatch: Trace and monitor Python objects.')
    parser.add_argument('-t', '--targets', nargs='+', required=True, help='Files, directories, or modules to watch.')
    parser.add_argument('-s', '--script', nargs=argparse.REMAINDER, help='Script to execute with tracing.')
    parser.add_argument('-r', '--ranks', nargs='+', type=int, help='Ranks to track when using torch.distributed.')
    parser.add_argument(
        '-l',
        '--log-level',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level (default: INFO).',
    )
    parser.add_argument('-o', '--output', default=None, help='File to write logs to.')
    args = parser.parse_args()

    logger = get_logger()
    logger.setLevel(args.log_level.upper())

    if args.output:
        file_handler = logging.FileHandler(args.output)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if not args.script:
        logger.error("No script provided to execute.")
        parser.print_help()
        sys.exit(1)

    script_command = ' '.join(args.script)

    obj_watch = ObjWatch(args.targets, ranks=args.ranks)
    try:
        obj_watch.start()
        script_path = os.path.abspath(script_command)
        if os.path.isfile(script_path):
            sys.argv = [script_path] + args.script[1:]
            runpy.run_path(script_path, run_name="__main__")
        else:
            logger.error(f"Python script {script_path} does not exist.")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Tracing interrupted by user.")
    finally:
        obj_watch.stop()
