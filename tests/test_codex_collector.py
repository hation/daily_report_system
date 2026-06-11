import sqlite3
from datetime import datetime

from src.collectors.codex_collector import CodexCollector


def create_codex_db(db_path):
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE threads (
                id TEXT PRIMARY KEY,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                created_at_ms INTEGER,
                updated_at_ms INTEGER,
                cwd TEXT NOT NULL,
                title TEXT NOT NULL,
                first_user_message TEXT NOT NULL,
                source TEXT NOT NULL,
                model_provider TEXT NOT NULL,
                model TEXT,
                tokens_used INTEGER NOT NULL DEFAULT 0,
                archived INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


def insert_thread(db_path, title, message, cwd, updated_at, archived=0):
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO threads (
                id, created_at, updated_at, created_at_ms, updated_at_ms, cwd,
                title, first_user_message, source, model_provider, model, tokens_used, archived
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                updated_at - 300,
                updated_at,
                (updated_at - 300) * 1000,
                updated_at * 1000,
                cwd,
                title,
                message,
                "vscode",
                "headroom",
                "gpt-5-codex",
                210000,
                archived,
            ),
        )
        conn.commit()


def test_codex_collector_reads_thread_records(tmp_path):
    db_path = tmp_path / "state_5.sqlite"
    create_codex_db(db_path)
    timestamp = int(datetime(2026, 6, 11, 10, 0, 0).timestamp())
    insert_thread(
        db_path,
        "只读诊断 video-analyzer 项目",
        "总结项目结构、依赖、可用测试命令和潜在风险",
        "/home/example/workspace/video_anlalyer/video-analyzer",
        timestamp,
    )

    collector = CodexCollector(config={"db_path": str(db_path)})
    items = collector.collect(
        datetime(2026, 6, 11, 9, 0, 0),
        datetime(2026, 6, 11, 11, 0, 0),
    )

    assert len(items) == 1
    assert items[0].source == "codex"
    assert items[0].source_type == "ai_session"
    assert items[0].metadata["project"] == "video_anlalyer"
    assert items[0].metadata["tokens_used"] == 210000
    assert items[0].priority == "high"


def test_codex_collector_filters_noise_model_questions(tmp_path):
    db_path = tmp_path / "state_5.sqlite"
    create_codex_db(db_path)
    timestamp = int(datetime(2026, 6, 11, 10, 0, 0).timestamp())
    insert_thread(
        db_path,
        "你用的什么模型",
        "你用的什么模型",
        "/home/example/New project",
        timestamp,
    )

    collector = CodexCollector(config={"db_path": str(db_path)})
    items = collector.collect(
        datetime(2026, 6, 11, 9, 0, 0),
        datetime(2026, 6, 11, 11, 0, 0),
    )

    assert items == []
