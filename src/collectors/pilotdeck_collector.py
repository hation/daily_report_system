#!/usr/bin/env python3
"""
PilotDeck收集器
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.collectors.base_collector import BaseCollector, WorkItem


class PilotDeckCollector(BaseCollector):
    """PilotDeck收集器"""

    def __init__(self, name: str = "pilotdeck", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        self.logger = logging.getLogger("collector.pilotdeck")
        default_root = "~/.pilotdeck"
        self.root_path = Path(self.config.get("root_path", default_root)).expanduser()
        self.projects_path = Path(self.config.get("projects_path", self.root_path / "projects")).expanduser()
        self.router_stats_path = Path(self.config.get("router_stats_path", self.root_path / "router" / "stats.jsonl")).expanduser()
        self.workspaces_path = Path(self.config.get("workspaces_path", self.root_path / "memory" / "workspaces")).expanduser()
        self.max_chat_items = int(self.config.get("max_chat_items", 80))
        self.max_stats_items = int(self.config.get("max_stats_items", 120))
        self.max_workspace_items = int(self.config.get("max_workspace_items", 80))

    def collect_work_items(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集工作项"""
        self.logger.info(f"收集PilotDeck工作项: {start_time} - {end_time}")
        if not self.root_path.exists():
            self.logger.warning(f"PilotDeck目录不存在: {self.root_path}")
            return []

        items = []
        items.extend(self._collect_project_chats(start_time, end_time))
        items.extend(self._collect_project_memories(start_time, end_time))
        items.extend(self._collect_router_stats(start_time, end_time))
        items.extend(self._collect_workspace_sessions(start_time, end_time))

        deduped = self._deduplicate_items(items)
        self.logger.info(f"从PilotDeck收集到 {len(deduped)} 个工作项")
        return deduped

    def _collect_project_chats(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        if not self.projects_path.exists():
            return []
        items = []
        for chat_path in self.projects_path.glob("*/chats/*.jsonl"):
            project_dir = chat_path.parents[1]
            project = self._project_name_from_project_dir(project_dir)
            try:
                lines = chat_path.read_text(encoding="utf-8").splitlines()
            except Exception as e:
                self.logger.debug(f"读取PilotDeck聊天文件失败 {chat_path}: {e}")
                continue
            for line in lines[-self.max_chat_items:]:
                item = self._parse_chat_line(line, project, chat_path, start_time, end_time)
                if item:
                    items.append(item)
        return items

    def _parse_chat_line(self, line: str, project: str, chat_path: Path, start_time: datetime, end_time: datetime) -> Optional[WorkItem]:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        entry_type = data.get("type")
        if entry_type != "accepted_input":
            return None
        timestamp = self._parse_datetime(data.get("createdAt") or data.get("completedAt"))
        if not timestamp or not (start_time <= timestamp <= end_time):
            return None
        title = self._extract_chat_title(data)
        if not title or self._is_noise_text(title):
            return None
        return WorkItem(
            id=f"pilotdeck_chat_{data.get('entryId') or data.get('turnId') or int(timestamp.timestamp())}",
            source="pilotdeck",
            source_type="ai_session",
            title=f"PilotDeck会话: {title}"[:120],
            description=title[:500],
            start_time=timestamp,
            end_time=timestamp,
            duration_hours=0.25,
            status="completed",
            priority="medium",
            tags=["pilotdeck", "chat", project],
            metadata={
                "project": project,
                "session_id": data.get("sessionId"),
                "turn_id": data.get("turnId"),
                "entry_type": entry_type,
                "chat_path": str(chat_path),
            }
        )

    def _extract_chat_title(self, data: Dict[str, Any]) -> str:
        messages = data.get("messages") or []
        for message in messages:
            if message.get("role") == "user":
                text = self._extract_content_text(message.get("content"))
                if text:
                    return self._clean_text(text)
        result = data.get("result") or {}
        final_message = result.get("finalMessage") or {}
        text = self._extract_content_text(final_message.get("content"))
        if text:
            return self._clean_text(text)
        return ""

    def _collect_project_memories(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        if not self.projects_path.exists():
            return []
        items = []
        for memory_path in self.projects_path.glob("*/memory/MEMORY.md"):
            modified_at = datetime.fromtimestamp(memory_path.stat().st_mtime)
            if not (start_time <= modified_at <= end_time):
                continue
            project = self._project_name_from_project_dir(memory_path.parents[1])
            summary = self._read_memory_summary(memory_path)
            items.append(WorkItem(
                id=f"pilotdeck_memory_{memory_path.parents[1].name}_{int(modified_at.timestamp())}",
                source="pilotdeck",
                source_type="memory",
                title=f"PilotDeck项目记忆更新: {project}"[:120],
                description=summary[:500] if summary else f"更新 PilotDeck 项目记忆: {project}",
                start_time=modified_at,
                end_time=modified_at,
                duration_hours=0.2,
                status="completed",
                priority="medium",
                tags=["pilotdeck", "memory", project],
                metadata={"project": project, "memory_path": str(memory_path)}
            ))
        return items

    def _collect_router_stats(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        if not self.router_stats_path.exists():
            return []
        items = []
        try:
            lines = self.router_stats_path.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            self.logger.debug(f"读取PilotDeck路由统计失败 {self.router_stats_path}: {e}")
            return []
        for line in lines[-self.max_stats_items:]:
            item = self._parse_stats_line(line, start_time, end_time)
            if item:
                items.append(item)
        return items

    def _parse_stats_line(self, line: str, start_time: datetime, end_time: datetime) -> Optional[WorkItem]:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        started_at = self._parse_datetime(data.get("startedAt"))
        ended_at = self._parse_datetime(data.get("endedAt")) or started_at
        if not started_at or not (start_time <= started_at <= end_time):
            return None
        project = self._project_name(data.get("projectPath") or "")
        usage = data.get("usage") or {}
        total_tokens = int(usage.get("totalTokens") or 0)
        provider = data.get("provider") or "unknown"
        model = data.get("model") or "unknown"
        title = f"PilotDeck模型路由: {project}"
        description = f"使用 {provider}/{model} 处理 {project} 项目会话，token {total_tokens}"
        return WorkItem(
            id=f"pilotdeck_stats_{data.get('turnId') or int(started_at.timestamp())}",
            source="pilotdeck",
            source_type="ai_session",
            title=title[:120],
            description=description[:500],
            start_time=started_at,
            end_time=ended_at,
            duration_hours=self._duration_hours(started_at, ended_at, total_tokens),
            status="completed",
            priority="high" if total_tokens >= 2000 else "medium",
            tags=["pilotdeck", "router", project],
            metadata={
                "project": project,
                "session_id": data.get("sessionId"),
                "turn_id": data.get("turnId"),
                "provider": provider,
                "model": model,
                "total_tokens": total_tokens,
                "project_path": data.get("projectPath"),
            }
        )

    def _collect_workspace_sessions(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        if not self.workspaces_path.exists():
            return []
        items = []
        for db_path in self.workspaces_path.glob("*/control.sqlite"):
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    conn.row_factory = sqlite3.Row
                    rows = self._query_workspace_sessions(conn, start_time, end_time)
            except Exception as e:
                self.logger.debug(f"读取PilotDeck工作区控制库失败 {db_path}: {e}")
                continue
            for row in rows[-self.max_workspace_items:]:
                item = self._workspace_row_to_item(row, db_path)
                if item:
                    items.append(item)
        return items

    def _query_workspace_sessions(self, conn: sqlite3.Connection, start_time: datetime, end_time: datetime) -> List[sqlite3.Row]:
        rows = list(conn.execute("SELECT l0_index_id, session_key, timestamp, messages_json, source, created_at FROM l0_sessions ORDER BY timestamp DESC LIMIT ?", (self.max_workspace_items,)))
        return [row for row in rows if self._timestamp_in_range(row["timestamp"], start_time, end_time)]

    def _workspace_row_to_item(self, row: sqlite3.Row, db_path: Path) -> Optional[WorkItem]:
        timestamp = self._parse_datetime(row["timestamp"])
        if not timestamp:
            return None
        title = self._extract_workspace_title(row["messages_json"])
        if not title or self._is_noise_text(title):
            return None
        workspace_id = db_path.parent.name
        return WorkItem(
            id=f"pilotdeck_workspace_{row['l0_index_id']}",
            source="pilotdeck",
            source_type="ai_session",
            title=f"PilotDeck工作区会话: {title}"[:120],
            description=title[:500],
            start_time=timestamp,
            end_time=timestamp,
            duration_hours=0.25,
            status="completed",
            priority="medium",
            tags=["pilotdeck", "workspace", workspace_id],
            metadata={
                "project": workspace_id,
                "workspace_id": workspace_id,
                "session_key": row["session_key"],
                "control_db": str(db_path),
            }
        )

    def _extract_workspace_title(self, messages_json: str) -> str:
        try:
            messages = json.loads(messages_json)
        except json.JSONDecodeError:
            return ""
        for message in messages:
            if message.get("role") == "user":
                text = self._extract_content_text(message.get("content"))
                if text:
                    return self._clean_text(text)
        return ""

    def _extract_content_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                elif isinstance(item, str):
                    parts.append(item)
            return " ".join(parts)
        return ""

    def _read_memory_summary(self, memory_path: Path) -> str:
        try:
            lines = memory_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            return ""
        useful_lines = [line.strip("# -*\t") for line in lines if line.strip() and not line.startswith("<!--")]
        return "；".join(useful_lines[:3])

    def _project_name_from_project_dir(self, project_dir: Path) -> str:
        cwd_path = project_dir / ".cwd"
        if cwd_path.exists():
            try:
                cwd = cwd_path.read_text(encoding="utf-8").strip()
                if cwd:
                    return self._project_name(cwd)
            except Exception:
                pass
        return self._normalize_project_dir_name(project_dir.name)

    def _normalize_project_dir_name(self, value: str) -> str:
        text = str(value or "")
        prefix = "Users-xingan-Documents-software-workspace-"
        if text.startswith(prefix):
            return text[len(prefix):].replace("-", "_")
        return text.replace("-", "_") or "未识别项目"

    def _project_name(self, path_value: str) -> str:
        if not path_value:
            return "未识别项目"
        path = Path(path_value)
        parts = path.parts
        if "workspace" in parts:
            index = parts.index("workspace")
            if index + 1 < len(parts):
                return parts[index + 1].replace("-", "_")
        if len(parts) >= 1 and parts[-1]:
            return parts[-1].replace("-", "_")
        return "未识别项目"

    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, (int, float)):
            number = float(value)
            if number > 10_000_000_000:
                number = number / 1000
            return datetime.fromtimestamp(number)
        text = str(value).strip()
        try:
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            dt = datetime.fromisoformat(text)
            if dt.tzinfo:
                return dt.astimezone().replace(tzinfo=None)
            return dt
        except ValueError:
            return None

    def _timestamp_in_range(self, value: Any, start_time: datetime, end_time: datetime) -> bool:
        timestamp = self._parse_datetime(value)
        return bool(timestamp and start_time <= timestamp <= end_time)

    def _duration_hours(self, start_time: datetime, end_time: datetime, total_tokens: int) -> float:
        actual = max((end_time - start_time).total_seconds() / 3600, 0)
        if actual > 0:
            return round(min(max(actual, 0.1), 2.0), 2)
        if total_tokens >= 2000:
            return 0.5
        return 0.2

    def _clean_text(self, value: Any) -> str:
        return " ".join(str(value or "").split())[:220]

    def _is_noise_text(self, text: str) -> bool:
        normalized = text.lower()
        noise_markers = [
            "你用的什么大模型",
            "你用的什么模型",
            "反应好慢",
            "load avg",
        ]
        return any(marker in normalized for marker in noise_markers)

    def _deduplicate_items(self, items: List[WorkItem]) -> List[WorkItem]:
        result = []
        seen = set()
        for item in items:
            key = (item.source_type, item.title[:80], item.start_time.isoformat())
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result
