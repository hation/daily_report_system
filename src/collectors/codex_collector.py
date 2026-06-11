#!/usr/bin/env python3
"""
Codex收集器
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.collectors.base_collector import BaseCollector, WorkItem


class CodexCollector(BaseCollector):
    """Codex收集器"""

    def __init__(self, name: str = "codex", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        self.logger = logging.getLogger("collector.codex")
        default_db_path = "~/.codex/state_5.sqlite"
        self.db_path = Path(self.config.get("db_path", default_db_path)).expanduser()
        self.query_limit = int(self.config.get("query_limit", 200))

    def collect_work_items(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集工作项"""
        self.logger.info(f"收集Codex工作项: {start_time} - {end_time}")
        if not self.db_path.exists():
            self.logger.warning(f"Codex数据库不存在: {self.db_path}")
            return []

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                rows = self._query_threads(conn, start_time, end_time)
        except Exception as e:
            self.logger.error(f"读取Codex数据库失败: {e}")
            return []

        items = [self._row_to_work_item(row) for row in rows]
        work_items = [item for item in items if item is not None]
        self.logger.info(f"从Codex收集到 {len(work_items)} 个工作项")
        return work_items

    def _query_threads(self, conn: sqlite3.Connection, start_time: datetime, end_time: datetime) -> List[sqlite3.Row]:
        start_ts = int(start_time.timestamp())
        end_ts = int(end_time.timestamp())
        query = """
            SELECT
                id,
                created_at,
                updated_at,
                created_at_ms,
                updated_at_ms,
                cwd,
                title,
                first_user_message,
                source,
                model_provider,
                model,
                tokens_used,
                archived
            FROM threads
            WHERE updated_at BETWEEN ? AND ?
              AND archived = 0
              AND (first_user_message != '' OR title != '')
            ORDER BY updated_at DESC
            LIMIT ?
        """
        return list(conn.execute(query, (start_ts, end_ts, self.query_limit)))

    def _row_to_work_item(self, row: sqlite3.Row) -> Optional[WorkItem]:
        title = self._clean_text(row["title"] or row["first_user_message"] or "Codex会话")
        if not title or self._is_noise_title(title):
            return None

        start_time = self._parse_time(row["created_at"], row["created_at_ms"])
        end_time = self._parse_time(row["updated_at"], row["updated_at_ms"])
        if not start_time or not end_time:
            return None

        cwd = row["cwd"] or ""
        project = self._project_name(cwd)
        first_message = self._clean_text(row["first_user_message"] or "")
        provider = row["model_provider"] or "unknown"
        model = row["model"] or ""
        tokens = int(row["tokens_used"] or 0)
        duration_hours = self._estimate_duration_hours(start_time, end_time, tokens)
        description_parts = [first_message]
        if model:
            description_parts.append(f"模型: {model}")
        if tokens:
            description_parts.append(f"Token使用量: {tokens}")
        description = " | ".join(part for part in description_parts if part)

        return WorkItem(
            id=f"codex_{row['id']}",
            source="codex",
            source_type="ai_session",
            title=f"Codex会话: {title}"[:120],
            description=description[:500],
            start_time=start_time,
            end_time=end_time,
            duration_hours=duration_hours,
            status="completed",
            priority="high" if tokens >= 200000 else "medium",
            tags=["codex", provider, project],
            metadata={
                "thread_id": row["id"],
                "project": project,
                "cwd": cwd,
                "source": row["source"],
                "model_provider": provider,
                "model": model,
                "tokens_used": tokens,
            }
        )

    def _parse_time(self, seconds_value: Any, milliseconds_value: Any = None) -> Optional[datetime]:
        value = milliseconds_value if milliseconds_value else seconds_value
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        if number > 10_000_000_000:
            number = number / 1000
        try:
            return datetime.fromtimestamp(number)
        except (OSError, ValueError):
            return None

    def _clean_text(self, value: Any) -> str:
        text = " ".join(str(value or "").split())
        return text[:220]

    def _is_noise_title(self, title: str) -> bool:
        text = title.lower()
        noise_markers = [
            "只回答 ok",
            "不要读取文件，不要运行命令",
            "你用的什么模型",
            "你现在用的什么模型",
            "你用的什么大模型",
            "支持哪些模型",
        ]
        return any(marker in text for marker in noise_markers)

    def _estimate_duration_hours(self, start_time: datetime, end_time: datetime, tokens: int) -> float:
        actual_hours = max((end_time - start_time).total_seconds() / 3600, 0)
        if actual_hours > 0:
            return round(min(max(actual_hours, 0.1), 3.0), 2)
        if tokens >= 200000:
            return 1.0
        if tokens >= 50000:
            return 0.5
        return 0.25

    def _project_name(self, cwd: str) -> str:
        if not cwd:
            return "未识别项目"
        path = Path(cwd)
        parts = path.parts
        if "workspace" in parts:
            index = parts.index("workspace")
            if index + 1 < len(parts):
                return parts[index + 1].replace("-", "_")
        if "software" in parts:
            index = parts.index("software")
            if index + 1 < len(parts):
                candidate = parts[index + 1]
                if candidate != "workspace":
                    return candidate.replace("-", "_")
        if "Documents" in parts:
            index = parts.index("Documents")
            if index + 1 < len(parts):
                candidate = parts[index + 1]
                if candidate not in {"New project", "Codex"}:
                    return candidate.replace("-", "_")
        if str(cwd).endswith("/New project") or "/Documents/Codex/" in str(cwd):
            return "codex"
        if len(parts) >= 1 and parts[-1]:
            return parts[-1].replace("-", "_")
        return "未识别项目"
