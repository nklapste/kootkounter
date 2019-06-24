#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""argparse and main entry point script"""

import argparse
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from kootkounter import DEFAULT_SQLITE_PATH
from kootkounter.bot import BOT


LOG_LEVEL_STRINGS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


def log_level(log_level_string: str):
    """Argparse type function for determining the specified logging level"""
    if log_level_string not in LOG_LEVEL_STRINGS:
        raise argparse.ArgumentTypeError(
            "invalid choice: {} (choose from {})".format(
                log_level_string,
                LOG_LEVEL_STRINGS
            )
        )
    return getattr(logging, log_level_string, logging.INFO)


def add_log_parser(parser):
    """Add logging options to the argument parser"""
    group = parser.add_argument_group(title="Logging")
    group.add_argument("--log-level", dest="log_level", default="INFO",
                       type=log_level, help="Set the logging output level")
    group.add_argument("--log-dir", dest="log_dir",
                       help="Enable TimeRotatingLogging at the directory "
                            "specified")
    group.add_argument("-v", "--verbose", action="store_true",
                       help="Enable verbose logging")


def init_logging(args, log_file_path):
    """Intake a argparse.parse_args() object and setup python logging"""
    # configure logging
    handlers_ = []
    log_format = logging.Formatter(fmt="[%(asctime)s] [%(levelname)s] - %(message)s")
    if args.log_dir:
        os.makedirs(args.log_dir, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            os.path.join(args.log_dir, log_file_path),
            when="d", interval=1, backupCount=7, encoding="UTF-8",
        )
        file_handler.setFormatter(log_format)
        file_handler.setLevel(args.log_level)
        handlers_.append(file_handler)
    if args.verbose:
        stream_handler = logging.StreamHandler(stream=sys.stderr)
        stream_handler.setFormatter(log_format)
        stream_handler.setLevel(args.log_level)
        handlers_.append(stream_handler)

    logging.basicConfig(
        handlers=handlers_,
        level=args.log_level
    )


def get_parser() -> argparse.ArgumentParser:
    """Create and return the argparse"""
    parser = argparse.ArgumentParser(
        description="Start the kootkounter Discord bot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-tf", "--token-file", dest="token_file",
                        required=True,
                        help="Path to file containing the Discord token for "
                             "the bot")

    parser.add_argument("--database", default=DEFAULT_SQLITE_PATH,
                        help="Path to the SQLITE database to store state")

    add_log_parser(parser)

    return parser


def main() -> int:
    """main entry point"""
    parser = get_parser()
    args = parser.parse_args()

    init_logging(args, "koolkounter.log")
    with open(args.token_file, "r") as f:
        token = f.read().strip()

    BOT.run(token)

    return 0


if __name__ == "__main__":
    sys.exit(main())
