import json
import sqlite3
from datetime import datetime

from src.collectors.pilotdeck_collector import PilotDeckCollector


def test_pilotdeck_collector_reads_project_memory(tmp_path):
    project_dir = tmp_path / "projects" / "Users-xingan-Documents-software-workspace-video_anlalyer"
    memory_dir = project_dir / "memory"
    memory_dir.mkdir(parents=True)
    (project_dir / ".cwd").write_text("/home/example/workspace/video_anlalyer", encoding="utf-8")
    memory_path = memory_dir / "MEMORY.md"
    memory_path.write_text("# 项目记忆\n- 完成视频分析链路梳理\n", encoding="utf-8")

    collector = PilotDeckCollector(config={"root_path": str(tmp_path), "projects_path": str(tmp_path / "projects")})
    items = collector.collect(
        datetime(2026, 6, 11, 0, 0, 0),
        datetime.now(),
    )

    memory_items = [item for item in items if item.source_type == "memory"]
    assert len(memory_items) == 1
    assert memory_items[0].source == "pilotdeck"
    assert memory_items[0].metadata["project"] == "video_anlalyer"


def test_pilotdeck_collector_reads_router_stats(tmp_path):
    router_dir = tmp_path / "router"
    router_dir.mkdir(parents=True)
    stats = {
        "sessionId": "web:s1",
        "turnId": "turn-1",
        "projectPath": "/home/example/workspace/fintech-mentor",
        "provider": "volcengine-agent-plan",
        "model": "deepseek-v3.2",
        "usage": {"totalTokens": 2351},
        "startedAt": "2026-06-11T10:00:00Z",
        "endedAt": "2026-06-11T10:05:00Z",
    }
    (router_dir / "stats.jsonl").write_text(json.dumps(stats, ensure_ascii=False) + "\n", encoding="utf-8")

    collector = PilotDeckCollector(config={"root_path": str(tmp_path), "router_stats_path": str(router_dir / "stats.jsonl")})
    items = collector.collect(
        datetime(2026, 6, 11, 17, 0, 0),
        datetime(2026, 6, 11, 19, 0, 0),
    )

    stats_items = [item for item in items if item.title.startswith("PilotDeck模型路由")]
    assert len(stats_items) == 1
    assert stats_items[0].metadata["project"] == "fintech_mentor"
    assert stats_items[0].priority == "high"


def test_pilotdeck_collector_reads_workspace_sessions(tmp_path):
    workspace_dir = tmp_path / "memory" / "workspaces" / "abc123"
    workspace_dir.mkdir(parents=True)
    db_path = workspace_dir / "control.sqlite"
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE l0_sessions (
                l0_index_id TEXT PRIMARY KEY,
                session_key TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                messages_json TEXT NOT NULL,
                source TEXT NOT NULL,
                indexed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        messages = json.dumps([{"role": "user", "content": "请总结 PilotDeck 项目结构"}], ensure_ascii=False)
        conn.execute(
            "INSERT INTO l0_sessions VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("idx-1", "web:s1", "2026-06-11T10:00:00Z", messages, "pilotdeck", 0, "2026-06-11T10:00:00Z"),
        )
        conn.commit()

    collector = PilotDeckCollector(config={"root_path": str(tmp_path), "workspaces_path": str(tmp_path / "memory" / "workspaces")})
    items = collector.collect(
        datetime(2026, 6, 11, 17, 0, 0),
        datetime(2026, 6, 11, 19, 0, 0),
    )

    workspace_items = [item for item in items if item.title.startswith("PilotDeck工作区会话")]
    assert len(workspace_items) == 1
    assert workspace_items[0].metadata["workspace_id"] == "abc123"
