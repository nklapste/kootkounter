#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for __main__.py"""

import argparse
import logging

import pytest

from kootkounter.__main__ import get_parser, log_level, main


def test_get_parser():
    parser = get_parser()
    assert isinstance(parser, argparse.ArgumentParser)


@pytest.mark.parametrize(
    "log_level_string, expected",
    [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
    ]
)
def test_log_level(log_level_string, expected):
    assert log_level(log_level_string) == expected


def test_log_level_invalid():
    with pytest.raises(argparse.ArgumentTypeError):
        log_level("nonsuch")


def test_main_missing_key_arg():
    with pytest.raises(SystemExit):
        main()
