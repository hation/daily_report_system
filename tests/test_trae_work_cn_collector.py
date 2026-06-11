import json
from datetime import datetime

from src.collectors.trae_work_cn_collector import TraeWorkCNCollector


def test_trae_work_cn_collector_reads_history_entries(tmp_path):
    history_dir = tmp_path / "history" / "abc123"
    history_dir.mkdir(parents=True)
    timestamp = int(datetime(2026, 6, 11, 10, 0, 0).timestamp() * 1000)
    entries = {
        "version": 1,
        "resource": "file:///home/example/workspace/headroom/agentops-workflow-design.md",
        "entries": [{"id": "A.md", "source": "工作区编辑", "timestamp": timestamp}],
    }
    (history_dir / "entries.json").write_text(json.dumps(entries), encoding="utf-8")

    collector = TraeWorkCNCollector(config={"history_path": str(tmp_path / "history")})
    items = collector.collect(
        datetime(2026, 6, 11, 9, 0, 0),
        datetime(2026, 6, 11, 11, 0, 0),
    )

    assert len(items) == 1
    assert items[0].source == "trae-work-cn"
    assert items[0].title == "Trae Work CN编辑文件: agentops-workflow-design.md"
    assert items[0].metadata["project"] == "headroom"
    assert items[0].metadata["edit_count"] == 1


def test_trae_work_cn_collector_filters_user_settings(tmp_path):
    history_dir = tmp_path / "history" / "settings"
    history_dir.mkdir(parents=True)
    timestamp = int(datetime(2026, 6, 11, 10, 0, 0).timestamp() * 1000)
    entries = {
        "version": 1,
        "resource": "vscode-userdata:/home/example/Library/Application%20Support/TRAE%20SOLO%20CN/User/settings.json",
        "entries": [{"id": "settings.json", "timestamp": timestamp}],
    }
    (history_dir / "entries.json").write_text(json.dumps(entries), encoding="utf-8")

    collector = TraeWorkCNCollector(config={"history_path": str(tmp_path / "history")})
    items = collector.collect(
        datetime(2026, 6, 11, 9, 0, 0),
        datetime(2026, 6, 11, 11, 0, 0),
    )

    assert items == []
