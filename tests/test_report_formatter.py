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
        "content_summary": {
            "daily_summary": "今日主要完成日报系统报告内容优化。",
            "human_summary_items": [
                {
                    "group": "日报系统与报告优化",
                    "summary": "优化日报系统与报告展示，共 2 项，重点是优化每日工作分析报告内容；补充内容型日报测试。",
                    "details": ["优化每日工作分析报告内容", "补充内容型日报测试"],
                    "count": 2,
                }
            ],
            "project_groups": [
                {
                    "name": "daily_report_system",
                    "count": 2,
                    "primary_topics": ["日报系统与报告优化"],
                    "items": [
                        {"title": "优化每日工作分析报告内容"},
                        {"title": "补充内容型日报测试"},
                    ],
                }
            ],
            "activity_groups": [
                {
                    "name": "日报系统与报告优化",
                    "count": 2,
                    "total_duration_minutes": 90,
                    "items": [
                        {
                            "title": "优化每日工作分析报告内容",
                            "description": "将日报从统计数量调整为展示今天具体做了哪些工作",
                            "source": "trae-cn",
                        },
                        {
                            "title": "补充内容型日报测试",
                            "description": "确保报告中出现具体工作事项和关键产出",
                            "source": "trae-cn",
                        },
                    ],
                }
            ],
            "key_outputs": [
                {
                    "title": "日报内容结构完成优化",
                    "description": "新增今日工作摘要、今日具体工作和关键产出章节",
                    "source": "trae-cn",
                }
            ],
            "blockers_or_notes": [],
        },
        "system_health": {"status": "partial", "successful_collectors": 2, "failed_collectors": 1},
    }, "daily_work_summary")

    assert "今日工作摘要" in report
    assert "按项目看" in report
    assert "按主题看" in report
    assert "daily_report_system" in report
    assert "优化日报系统与报告展示" in report
    assert "关键产出" in report
    assert "日报内容结构完成优化" in report
    assert "数据概览" in report
    assert "后续关注与建议" in report
    assert "总工作项数" in report
