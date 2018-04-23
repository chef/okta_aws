#!/usr/bin/env python3
# pylint: disable=invalid-name,missing-docstring


def test_hour(oa):
    assert oa.friendly_interval(3600) == '1 hour'
    assert oa.friendly_interval(7200) == '2 hours'


def test_minute(oa):
    assert oa.friendly_interval(600) == '10 minutes'
    assert oa.friendly_interval(60) == '1 minute'


def test_fractions(oa):
    assert oa.friendly_interval(5400) == '1.5 hours'
    assert oa.friendly_interval(30) == '0.5 minutes'
