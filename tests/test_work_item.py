from datetime import datetime

from src.collectors.base_collector import WorkItem


def test_work_item_exposes_processing_fields():
    start = datetime(2026, 6, 11, 9, 0, 0)
    end = datetime(2026, 6, 11, 10, 30, 0)
    item = WorkItem(
        id="item-1",
        source="trae-cn",
        source_type="memory",
        title="实现日报系统",
        description="打通收集、分析、报告链路",
        start_time=start,
        end_time=end,
        duration_hours=1.5,
        status="completed",
        priority="high",
        tags=["daily-report"],
        metadata={"project": "daily_report_system"},
    )

    data = item.to_dict()

    assert item.duration_minutes == 90
    assert item.tool == "trae-cn"
    assert item.category == "memory"
    assert data["duration_minutes"] == 90
    assert data["tool"] == "trae-cn"
    assert data["category"] == "memory"
    assert data["start_time"] == "2026-06-11T09:00:00"
    assert data["end_time"] == "2026-06-11T10:30:00"
