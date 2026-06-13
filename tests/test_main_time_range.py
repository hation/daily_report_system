from datetime import datetime

import pytest

from src.main import build_preset_time_range, build_time_range, parse_datetime_arg


def test_parse_datetime_arg_expands_start_date():
    assert parse_datetime_arg("2026-06-01") == datetime(2026, 6, 1, 0, 0, 0)


def test_parse_datetime_arg_expands_end_date():
    assert parse_datetime_arg("2026-06-07", is_end=True) == datetime(2026, 6, 7, 23, 59, 59)


def test_parse_datetime_arg_accepts_datetime_with_space():
    assert parse_datetime_arg("2026-06-01 09:30:00") == datetime(2026, 6, 1, 9, 30, 0)


def test_build_time_range_requires_both_start_and_end():
    with pytest.raises(Exception, match="必须同时提供"):
        build_time_range("2026-06-01", None)


def test_build_time_range_rejects_invalid_order():
    with pytest.raises(Exception, match="不能晚于"):
        build_time_range("2026-06-07", "2026-06-01")


def test_build_time_range_returns_iso_values():
    assert build_time_range("2026-06-01", "2026-06-07") == {
        "start_time": "2026-06-01T00:00:00",
        "end_time": "2026-06-07T23:59:59",
    }


def test_build_preset_time_range_supports_yesterday_keyword():
    now = datetime(2026, 6, 14, 10, 30, 15)

    assert build_preset_time_range("昨日", now=now) == {
        "start_time": "2026-06-13T00:00:00",
        "end_time": "2026-06-13T23:59:59",
    }


def test_build_preset_time_range_supports_last_7_days_keyword():
    now = datetime(2026, 6, 14, 10, 30, 15)

    assert build_preset_time_range("最近7天", now=now) == {
        "start_time": "2026-06-08T00:00:00",
        "end_time": "2026-06-14T10:30:15",
    }


def test_build_preset_time_range_supports_last_30_days_keyword():
    now = datetime(2026, 6, 14, 10, 30, 15)

    assert build_preset_time_range("最近一个月", now=now) == {
        "start_time": "2026-05-16T00:00:00",
        "end_time": "2026-06-14T10:30:15",
    }


def test_build_time_range_rejects_preset_and_explicit_range_together():
    with pytest.raises(Exception, match="不能和"):
        build_time_range("2026-06-01", "2026-06-07", "昨日")


def test_build_time_range_accepts_preset_keyword():
    result = build_time_range(range_value="yesterday")

    assert "start_time" in result
    assert "end_time" in result
