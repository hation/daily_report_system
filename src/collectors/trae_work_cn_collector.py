#!/usr/bin/env python3
"""
Trae Work CN收集器
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import unquote, urlparse

from src.collectors.base_collector import BaseCollector, WorkItem


class TraeWorkCNCollector(BaseCollector):
    """Trae Work CN收集器"""

    def __init__(self, name: str = "trae-work-cn", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        self.logger = logging.getLogger("collector.trae-work-cn")
        default_path = "~/Library/Application Support/TRAE SOLO CN/User/History/"
        self.history_path = Path(self.config.get("history_path", self.config.get("data_path", default_path))).expanduser()
        self.max_items_per_file = int(self.config.get("max_items_per_file", 1))

    def collect_work_items(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集工作项"""
        self.logger.info(f"收集Trae Work CN工作项: {start_time} - {end_time}")
        if not self.history_path.exists():
            self.logger.warning(f"Trae Work CN历史目录不存在: {self.history_path}")
            return []

        work_items = []
        for entries_path in self.history_path.glob("*/entries.json"):
            item = self._collect_entries_file(entries_path, start_time, end_time)
            if item:
                work_items.append(item)

        self.logger.info(f"从Trae Work CN收集到 {len(work_items)} 个工作项")
        return work_items

    def _collect_entries_file(self, entries_path: Path, start_time: datetime, end_time: datetime) -> Optional[WorkItem]:
        try:
            data = json.loads(entries_path.read_text(encoding="utf-8"))
        except Exception as e:
            self.logger.debug(f"读取Trae Work CN历史文件失败 {entries_path}: {e}")
            return None

        resource = data.get("resource", "")
        entries = data.get("entries", [])
        if not resource or not isinstance(entries, list):
            return None

        matched_entries = []
        for entry in entries:
            timestamp = self._parse_timestamp(entry.get("timestamp"))
            if timestamp and start_time <= timestamp <= end_time:
                matched_entries.append((entry, timestamp))

        if not matched_entries:
            return None

        matched_entries = sorted(matched_entries, key=lambda value: value[1])
        first_time = matched_entries[0][1]
        last_time = matched_entries[-1][1]
        resource_path = self._resource_to_path(resource)
        if self._is_noise_resource(resource_path):
            return None
        project = self._project_name(resource_path)
        file_name = Path(resource_path).name if resource_path else "未知文件"
        edit_count = len(matched_entries)
        title = f"Trae Work CN编辑文件: {file_name}"
        description = f"在项目 {project} 中编辑 {file_name}，产生 {edit_count} 条本地历史记录"

        return WorkItem(
            id=f"trae_work_cn_{entries_path.parent.name}_{int(last_time.timestamp())}",
            source="trae-work-cn",
            source_type="file_activity",
            title=title[:120],
            description=description[:500],
            start_time=first_time,
            end_time=last_time,
            duration_hours=max(0.1, min(edit_count * 0.08, 2.0)),
            status="completed",
            priority="medium",
            tags=["trae-work-cn", "file", project],
            metadata={
                "resource": resource,
                "file_path": resource_path,
                "project": project,
                "edit_count": edit_count,
                "history_path": str(entries_path),
            }
        )

    def _parse_timestamp(self, value: Any) -> Optional[datetime]:
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

    def _resource_to_path(self, resource: str) -> str:
        if not resource:
            return ""
        parsed = urlparse(resource)
        if parsed.scheme == "file":
            return unquote(parsed.path)
        if parsed.scheme == "vscode-userdata":
            return unquote(parsed.path)
        return unquote(resource)

    def _is_noise_resource(self, file_path: str) -> bool:
        text = file_path.lower()
        noise_markers = [
            "/library/application support/trae solo cn/user/settings.json",
            "/library/application support/trae solo cn/workspaces/",
            "vscode-userdata:",
        ]
        return any(marker in text for marker in noise_markers)

    def _project_name(self, file_path: str) -> str:
        if not file_path:
            return "未识别项目"
        path = Path(file_path)
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
        if len(parts) >= 2:
            return parts[-2].replace("-", "_")
        return "未识别项目"
