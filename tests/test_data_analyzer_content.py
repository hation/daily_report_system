from src.processors.base_processor import ProcessedWorkItem
from src.processors.data_analyzer import DataAnalyzer


def make_processed_item(title, description, source="trae-cn", category="development", status="completed", project=None):
    cleaned_item = {
        "title": title,
        "description": description,
        "tool": source,
        "source": source,
        "category": category,
        "status": status,
        "priority": "high",
        "duration_minutes": 45,
        "start_time": "2026-06-11T10:00:00",
        "metadata": {"project": project} if project else {},
    }
    return ProcessedWorkItem(
        original_item=cleaned_item,
        cleaned_item=cleaned_item,
        categories=[category],
        keywords=["日报", "报告"],
        sentiment="neutral",
        importance_score=0.8,
        time_blocks=[],
        summary=title,
        metadata=cleaned_item["metadata"],
    )


def test_data_analyzer_generates_content_summary():
    analyzer = DataAnalyzer()
    result = analyzer.process([
        make_processed_item("优化每日工作分析报告内容", "将报告从统计数量调整为展示今天具体做了哪些工作", project="daily_report_system"),
        make_processed_item("补充内容型日报测试", "确保日报包含具体工作事项、关键产出和后续关注点", project="daily_report_system"),
        make_processed_item("检查 video_anlalyer 项目记忆", "确认 MEMORY.md 是否存在", project="video_anlalyer"),
    ])

    content_summary = result["content_summary"]

    assert "今日主要围绕" in content_summary["daily_summary"]
    assert content_summary["activity_groups"]
    assert content_summary["human_summary_items"]
    assert any("日报" in item["summary"] for item in content_summary["human_summary_items"])
    assert content_summary["activity_groups"][0]["items"][0]["title"] in {
        "优化每日工作分析报告内容",
        "补充内容型日报测试",
    }
    assert any(output["title"] == "优化每日工作分析报告内容" for output in content_summary["key_outputs"])
    assert content_summary["project_groups"]
    assert {group["name"] for group in content_summary["project_groups"]} >= {"daily_report_system", "video_anlalyer"}
    assert all(len(item["summary"]) <= 150 for item in content_summary["human_summary_items"])
