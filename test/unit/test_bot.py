#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""pytests for kootkounter"""

import pytest

from kootkounter.bot import degeneracy_detector, ThrottleException, throttle


@pytest.mark.parametrize(
    "string,expected",
    [
        ("owo are you a koot boi nerd ishh?!?!? oh nuu UWU!",
         ["owo", "koot", "boi", "nerd", "ishh", "nuu", "uwu"]),
        ("I'm a normal person", [])
    ]
)
def test_degeneracy_detector(string, expected):
    assert degeneracy_detector(string) == expected


def test_throttle():
    with pytest.raises(ThrottleException):
        @throttle(100)
        def foobar():
            pass

        foobar()
        foobar()
