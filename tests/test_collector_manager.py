from datetime import datetime

from src.collectors.base_collector import BaseCollector, WorkItem
from src.collectors.collector_manager import CollectorManager


class StaticCollector(BaseCollector):
    def collect_work_items(self, start_time, end_time):
        return [
            WorkItem(
                id="static-1",
                source="test-source",
                source_type="task",
                title="测试工作项",
                description="用于验证收集器管理器",
                start_time=start_time,
                end_time=end_time,
                duration_hours=0.5,
                status="completed",
                priority="medium",
                tags=["test"],
                metadata={},
            )
        ]


def test_collector_manager_returns_standard_collection_result():
    manager = CollectorManager()
    manager.register_collector("static", StaticCollector("static"))

    result = manager.collect_all(
        datetime(2026, 6, 11, 9, 0, 0),
        datetime(2026, 6, 11, 10, 0, 0),
    )

    assert result["success"] is True
    assert len(result["work_items"]) == 1
    assert result["collector_results"]["static"]["success"] is True
    assert result["collector_results"]["static"]["stats"]["total_items"] == 1
    assert result["collection_time_ms"] >= 0


def test_collector_manager_collect_keeps_legacy_list_interface():
    manager = CollectorManager()
    manager.register_collector("static", StaticCollector("static"))

    items = manager.collect(
        datetime(2026, 6, 11, 9, 0, 0),
        datetime(2026, 6, 11, 10, 0, 0),
    )

    assert len(items) == 1
    assert items[0].title == "测试工作项"
