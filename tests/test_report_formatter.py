from src.formatters.simple_report_formatter import create_work_report_formatter


def test_daily_report_contains_required_sections():
    formatter = create_work_report_formatter()
    report = formatter.format_report({
        "overview": {
            "total_work_items": 3,
            "total_duration_hours": 2.5,
            "unique_tools": 2,
            "unique_categories": 2,
            "average_duration_minutes": 50,
            "completion_rate_percent": 66.7,
        },
        "time_analysis": {"peak_hour": "10:00", "peak_hour_count": 2},
        "tool_analysis": {"top_tools": [{"tool_name": "trae-cn", "count": 2, "total_duration_hours": 1.5}]},
        "category_analysis": {"top_categories": [{"category_name": "memory", "count": 2}]},
        "priority_analysis": {"distribution": {"high": 1, "medium": 2}},
        "duration_analysis": {"stats": {"total_hours": 2.5, "average_minutes": 50}},
        "key_insights": [{"text": "自动日报链路已可用", "confidence": 0.9}],
        "system_health": {"status": "partial", "successful_collectors": 2, "failed_collectors": 1},
    }, "daily_work_summary")

    assert "工作概览" in report
    assert "主要活动与分布" in report
    assert "今日工作亮点" in report
    assert "系统健康状态" in report
    assert "明日建议" in report
