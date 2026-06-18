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
                },
                {
                    "group": "代码开发与问题修复",
                    "summary": "推进代码开发与问题修复，共 1 项，重点是修复报告换行展示。",
                    "details": ["修复报告换行展示"],
                    "count": 1,
                },
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
                },
                {
                    "name": "report_display",
                    "count": 1,
                    "primary_topics": ["代码开发与问题修复"],
                    "items": [
                        {"title": "修复报告换行展示"},
                    ],
                },
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
                    "summary": "日报内容结构完成优化",
                    "description": "新增今日工作摘要、今日具体工作和关键产出章节",
                    "source": "trae-cn",
                    "project": "daily_report_system",
                    "output_type": "output",
                },
                {
                    "title": "B",
                    "summary": "B",
                    "description": "完成5个Task、推送5个commit到GitHub、新增9个测试",
                    "source": "trae-cn",
                    "project": "system",
                    "output_type": "output",
                },
            ],
            "blockers_or_notes": [],
        },
        "system_health": {"status": "partial", "successful_collectors": 2, "failed_collectors": 1},
    }, "daily_work_summary")

    assert "今日工作摘要" in report
    assert "按项目看" in report
    assert "按主题看" in report
    assert "daily_report_system" in report
    assert "report_display" in report
    assert "优化日报系统与报告展示" in report
    assert "代码开发与问题修复" in report
    assert "• **daily_report_system**" in report
    assert "有力支持。\n\n• **report_display**" in report
    assert "• **日报系统与报告优化**" in report
    assert "为相关领域提供了支持。\n\n• **代码开发与问题修复**" in report
    assert "关键产出" in report
    assert "日报内容结构完成优化" in report
    assert "项目：daily_report_system" in report
    assert "类型：可交付产出" in report
    assert "来源：trae-cn" in report
    assert "说明：新增今日工作摘要、今日具体工作和关键产出章节" in report
    assert "完成5个Task、推送5个commit到GitHub" in report
    assert "**B**" not in report
    assert "解决了相关问题" not in report
    assert "实现了实际价值" not in report
    assert "数据概览" in report
    assert "后续关注与建议" in report
    assert "总工作项数" in report
