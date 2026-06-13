from datetime import datetime

from src.collectors.base_collector import WorkItem
from src.managers.report_manager import ReportManager


class FakeCollectorManager:
    def __init__(self):
        self.time_range = None

    def collect_all(self, time_range):
        self.time_range = time_range
        item_time = datetime(2026, 6, 11, 9, 0, 0)
        item = WorkItem(
            id="fake-1",
            source="trae-cn",
            source_type="memory",
            title="实现日报系统",
            description="打通主链路",
            start_time=item_time,
            end_time=item_time,
            duration_hours=1,
            status="completed",
            priority="high",
            tags=["report"],
            metadata={},
        )
        return {
            "success": True,
            "work_items": [item],
            "collector_results": {
                "fake": {
                    "success": True,
                    "items": [item],
                    "stats": {"total_items": 1},
                    "error": None,
                }
            },
            "collection_time_ms": 1,
        }


class FakeProcessorManager:
    def process_workflow(self, work_items, workflow=None):
        analysis_results = {
            "metadata": {"total_items": len(work_items)},
            "summary_statistics": {
                "overall": {
                    "total_work_items": len(work_items),
                    "total_duration_hours": 1,
                    "unique_tools": 1,
                    "unique_categories": 1,
                    "completion_rate_percent": 100,
                },
                "averages": {"avg_duration_minutes": 60},
            },
            "time_analysis": {"peak_hour": "09:00", "peak_hour_count": 1},
            "tool_analysis": {"top_tools": [{"tool_name": "trae-cn", "count": 1, "total_duration_hours": 1}]},
            "category_analysis": {"top_categories": [{"category_name": "memory", "count": 1}]},
            "insights": {"general": [{"text": "日报链路已跑通", "confidence": 0.9}]},
        }
        return {
            "success": True,
            "processed_items": work_items,
            "intermediate_results": {
                "data_analyzer": {"success": True, "results": analysis_results}
            },
            "execution_time_ms": 1,
        }


class FakeFormatter:
    report_formats = {}

    def format_report(self, analysis_results, format_name):
        period = analysis_results.get("report_period", {})
        return f"日报: {analysis_results['overview']['total_work_items']} 个工作项 {period.get('start_time', '')}"


class FakePusher:
    def send_message(self, content, message_type="text", target=None):
        return {"success": True, "content_length": len(content), "test_mode": True}


def test_report_manager_generates_and_pushes_report(tmp_path):
    manager = ReportManager({
        "backup_path": str(tmp_path),
        "report_types": {
            "daily": {
                "format": "daily_work_summary",
                "target": {"receive_type": "chat", "chat_id": ""},
            }
        },
        "test_mode": True,
    })
    manager.collector_manager = FakeCollectorManager()
    manager.processor_manager = FakeProcessorManager()
    manager.report_formatter = FakeFormatter()
    manager.feishu_pusher = FakePusher()

    result = manager.run_daily_report()

    assert result["success"] is True
    assert result["summary"]["work_items_analyzed"] == 1
    assert len(manager.report_history) == 1
    assert manager.report_history[0]["push_records"][0]["result"]["success"] is True


def test_report_manager_runs_daily_report_with_time_range(tmp_path):
    manager = ReportManager({
        "backup_path": str(tmp_path),
        "report_types": {
            "daily": {
                "format": "daily_work_summary",
                "target": {"receive_type": "chat", "chat_id": ""},
            }
        },
        "test_mode": True,
    })
    collector = FakeCollectorManager()
    manager.collector_manager = collector
    manager.processor_manager = FakeProcessorManager()
    manager.report_formatter = FakeFormatter()
    manager.feishu_pusher = FakePusher()
    time_range = {
        "start_time": "2026-06-01T00:00:00",
        "end_time": "2026-06-07T23:59:59",
    }

    result = manager.run_daily_report(time_range=time_range)

    assert result["success"] is True
    assert result["time_range"] == time_range
    assert collector.time_range == time_range
    assert result["report_generation"]["save_result"]["filename"] == "daily_report_20260601_20260607.md"
    assert "2026-06-01T00:00:00" in result["report_generation"]["report_content"]


def test_report_manager_builds_timestamped_range_filename():
    manager = ReportManager({})
    filename = manager._build_report_filename("daily", {
        "start_time": "2026-06-01T09:00:00",
        "end_time": "2026-06-07T18:30:00",
    })

    assert filename == "daily_report_20260601_090000_20260607_183000.md"
