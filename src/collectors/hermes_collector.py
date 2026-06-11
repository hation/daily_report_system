#!/usr/bin/env python3
"""
Hermes收集器
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.collectors.base_collector import BaseCollector, WorkItem


class HermesCollector(BaseCollector):
    """Hermes收集器"""
    
    def __init__(self, name: str = "hermes", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        self.logger = logging.getLogger("collector.hermes")
        self.sessions_path = Path(self.config.get("sessions_path", "~/.hermes/sessions/")).expanduser()
        self.memory_path = Path(self.config.get("memory_path", self.config.get("memory_eval_path", "~/.hermes/memory_evaluation/"))).expanduser()
    
    def collect_work_items(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集工作项"""
        self.logger.info(f"收集Hermes工作项: {start_time} - {end_time}")
        work_items = []
        work_items.extend(self._collect_sessions(start_time, end_time))
        work_items.extend(self._collect_memory_evaluations(start_time, end_time))
        self.logger.info(f"从Hermes收集到 {len(work_items)} 个工作项")
        return work_items
    
    def _collect_sessions(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        if not self.sessions_path.exists():
            self.logger.warning(f"Hermes会话目录不存在: {self.sessions_path}")
            return []
        items = []
        for file_path in self.sessions_path.glob("*.json"):
            modified_at = datetime.fromtimestamp(file_path.stat().st_mtime)
            if not (start_time <= modified_at <= end_time):
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                session_time = self._parse_time(data.get("session_start") or data.get("created_at")) or modified_at
                if not (start_time <= session_time <= end_time):
                    continue
                user_messages = self._extract_user_messages(data)
                if not user_messages:
                    continue
                title = user_messages[0][:120]
                description = "\n".join(user_messages[:5])[:800]
                items.append(WorkItem(
                    id=f"hermes_session_{file_path.stem}",
                    source="hermes",
                    source_type="session",
                    title=title,
                    description=description,
                    start_time=session_time,
                    end_time=modified_at,
                    duration_hours=0.5,
                    status="completed",
                    priority="medium",
                    tags=["hermes", "session"],
                    metadata={"file_path": str(file_path), "message_count": len(user_messages)}
                ))
            except Exception as e:
                self.logger.error(f"读取Hermes会话失败 {file_path}: {e}")
        return items
    
    def _collect_memory_evaluations(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        if not self.memory_path.exists():
            self.logger.warning(f"Hermes记忆评估目录不存在: {self.memory_path}")
            return []
        items = []
        for file_path in self.memory_path.glob("daily_check_*.log"):
            modified_at = datetime.fromtimestamp(file_path.stat().st_mtime)
            if not (start_time <= modified_at <= end_time):
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                score = self._extract_health_score(content)
                title = "Hermes记忆系统健康检查"
                description = self._compact_text(content)[:600]
                items.append(WorkItem(
                    id=f"hermes_memory_{file_path.stem}",
                    source="hermes",
                    source_type="system_health",
                    title=title,
                    description=description,
                    start_time=modified_at,
                    end_time=modified_at,
                    duration_hours=0.1,
                    status="completed",
                    priority="high" if score is not None and score < 70 else "medium",
                    tags=["hermes", "memory", "health"],
                    metadata={"file_path": str(file_path), "health_score": score}
                ))
            except Exception as e:
                self.logger.error(f"读取Hermes记忆评估失败 {file_path}: {e}")
        return items
    
    def _extract_user_messages(self, data: Dict[str, Any]) -> List[str]:
        messages = data.get("messages", [])
        result = []
        if isinstance(messages, list):
            for message in messages:
                if not isinstance(message, dict):
                    continue
                if message.get("role") != "user":
                    continue
                content = message.get("content", "")
                if isinstance(content, list):
                    content = " ".join(str(part) for part in content)
                content = self._compact_text(str(content))
                if content:
                    result.append(content)
        return result
    
    def _extract_health_score(self, content: str) -> Optional[int]:
        match = re.search(r"整体健康度[:：]\s*(\d+)/100", content)
        if not match:
            return None
        return int(match.group(1))
    
    def _compact_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
    
    def _parse_time(self, value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        text = str(value)
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d %H:%M:%S"):
            try:
                return datetime.strptime(text[:19], fmt)
            except ValueError:
                pass
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None
