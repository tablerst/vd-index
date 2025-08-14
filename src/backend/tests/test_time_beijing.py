import pytest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# 被测目标：时间工具函数与 Activity 模型的时间校验
from ..services.database.models.base import now_naive, to_naive_beijing
from backend.services.database.models.activity.base import Activity
from pydantic import ValidationError


# ============================
# 基础工具函数测试
# ============================

def test_now_naive_returns_naive_beijing():
    """中文注释：验证 now_naive() 返回的是“无时区的北京时间”。
    断言点：
    - tzinfo 为 None（无时区）
    - 与 Asia/Shanghai 当前时间（去掉 tzinfo）几乎相等（误差 < 3 秒）
    """
    dt = now_naive()
    assert dt.tzinfo is None, "now_naive() 必须返回无时区时间"

    # 使用系统 Asia/Shanghai 当前时间对齐校验
    sh_now = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
    delta = abs(sh_now - dt)
    assert delta < timedelta(seconds=3), f"now_naive 与上海本地时间差过大: {delta}"


def test_to_naive_beijing_from_utc_aware():
    """中文注释：UTC 带时区时间应被转换为北京时间并移除时区信息。"""
    src = datetime(2024, 1, 1, 12, 34, 56, tzinfo=timezone.utc)
    got = to_naive_beijing(src)

    expected = src.astimezone(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
    assert got.tzinfo is None
    assert got == expected


def test_to_naive_beijing_from_naive_passthrough():
    """中文注释：若传入的是 naive 时间，应直接返回（项目约定：naive 即为北京时间）。"""
    src = datetime(2024, 1, 1, 8, 0, 0)  # 视为“无时区北京时间”
    got = to_naive_beijing(src)
    assert got.tzinfo is None
    assert got == src


def test_to_naive_beijing_from_tokyo_to_beijing():
    """中文注释：Tokyo(+09:00) 的时间转换为 Beijing(+08:00) 后应少 1 小时，并去除时区。"""
    src = datetime(2024, 1, 1, 9, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
    got = to_naive_beijing(src)
    assert got == datetime(2024, 1, 1, 8, 0, 0)


# ============================
# Activity 模型字段校验测试
# ============================

def test_activity_date_from_z_string_to_beijing_naive():
    """中文注释：Z 结尾的 ISO 字符串应被解析为 UTC，再转换为“无时区北京时间”。"""
    act = Activity(
        title="t", description="d",
        date="2024-01-01T12:00:00Z",  # UTC 时间
        tags=[], participant_ids=[], participants_total=0,
    )
    # 12:00Z -> 北京时间 +8 小时 = 20:00 当天
    assert act.date.tzinfo is None
    assert act.date == datetime(2024, 1, 1, 20, 0, 0)


def test_activity_date_from_offset_string_rollover_next_day():
    """中文注释：带偏移量字符串跨天转换应正确（例如 -05:00 -> +8 小时可能跨天）。"""
    # 2024-01-01 18:30:00-05:00 == 2024-01-02 07:30:00Z -> 北京 +8 = 2024-01-02 15:30:00
    act = Activity(
        title="t", description="d",
        date="2024-01-01T18:30:00-05:00",
        tags=[], participant_ids=[], participants_total=0,
    )
    assert act.date.tzinfo is None
    assert act.date == datetime(2024, 1, 2, 7, 30, 0)


def test_activity_date_from_naive_datetime_passthrough():
    """中文注释：若传入 naive datetime，应被视为“无时区北京时间”，不应改变。"""
    src = datetime(2024, 7, 1, 9, 10, 11)
    act = Activity(
        title="t", description="d",
        date=src,
        tags=[], participant_ids=[], participants_total=0,
    )
    assert act.date.tzinfo is None
    assert act.date == src


def test_activity_created_updated_defaults_naive_beijing():
    """中文注释：未显式提供 created_at/updated_at 时，默认应为“无时区北京时间”的当前时间。"""
    act = Activity(
        title="t", description="d",
        date=datetime(2024, 1, 1, 8, 0, 0),
        tags=[], participant_ids=[], participants_total=0,
    )
    assert act.created_at.tzinfo is None
    assert act.updated_at.tzinfo is None

    # 与上海当前时间（去 tzinfo）几乎相等（误差 < 3 秒）
    sh_now = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)
    assert abs(act.created_at - sh_now) < timedelta(seconds=3)
    assert abs(act.updated_at - sh_now) < timedelta(seconds=3)


def test_activity_created_updated_from_z_string():
    """中文注释：created_at/updated_at 若以 Z 结尾字符串传入，应转换为北京时间并移除时区。"""
    act = Activity(
        title="t", description="d",
        date=datetime(2024, 1, 1, 8, 0, 0),
        created_at="2024-01-01T16:00:00Z",  # -> 北京 2024-01-02 00:00:00
        updated_at="2024-01-02T00:30:00Z",  # -> 北京 2024-01-02 08:30:00
        tags=[], participant_ids=[], participants_total=0,
    )
    assert act.created_at == datetime(2024, 1, 2, 0, 0, 0)
    assert act.created_at.tzinfo is None
    assert act.updated_at == datetime(2024, 1, 2, 8, 30, 0)
    assert act.updated_at.tzinfo is None


def test_activity_invalid_date_string_raises():
    """中文注释：无效日期字符串应触发验证错误。"""
    with pytest.raises((ValidationError, ValueError)):
        Activity(
            title="t", description="d",
            date="this-is-not-a-date",
            tags=[], participant_ids=[], participants_total=0,
        )


def test_activity_midnight_rollover_from_z():
    """中文注释：UTC 接近午夜时，转换到北京时间应正确跨日。"""
    # 2024-01-01 20:30:00Z -> 北京 2024-01-02 04:30:00
    act = Activity(
        title="t", description="d",
        date="2024-01-01T20:30:00Z",
        tags=[], participant_ids=[], participants_total=0,
    )
    assert act.date == datetime(2024, 1, 2, 4, 30, 0)
    assert act.date.tzinfo is None

