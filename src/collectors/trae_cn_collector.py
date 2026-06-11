#!/usr/bin/env python3
"""
Trae CN收集器
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.collectors.base_collector import BaseCollector, WorkItem


class TraeCNCollector(BaseCollector):
    """Trae CN收集器"""
    
    def __init__(self, name: str = "trae-cn", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        self.logger = logging.getLogger("collector.trae-cn")
        self.data_path = Path(self.config.get("data_path", "~/.trae-cn/memory/projects/")).expanduser()
    
    def collect_work_items(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集工作项"""
        self.logger.info(f"收集Trae CN工作项: {start_time} - {end_time}")
        if not self.data_path.exists():
            self.logger.warning(f"Trae CN目录不存在: {self.data_path}")
            return []
        
        work_items = []
        for file_path in self.data_path.rglob("*"):
            if not file_path.is_file() or file_path.suffix.lower() not in {".jsonl", ".json", ".md", ".txt"}:
                continue
            modified_at = datetime.fromtimestamp(file_path.stat().st_mtime)
            if not (start_time <= modified_at <= end_time):
                continue
            if file_path.suffix.lower() == ".jsonl":
                work_items.extend(self._collect_jsonl_file(file_path, start_time, end_time))
            else:
                item = self._create_file_work_item(file_path, modified_at)
                if item:
                    work_items.append(item)
        
        self.logger.info(f"从Trae CN收集到 {len(work_items)} 个工作项")
        return work_items
    
    def _collect_jsonl_file(self, file_path: Path, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        items = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for index, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    item_time = self._parse_time(record.get("message_summary_time") or record.get("timestamp") or record.get("time"))
                    if not item_time:
                        item_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if not (start_time <= item_time <= end_time):
                        continue
                    title = record.get("intent") or record.get("title") or file_path.stem
                    description_parts = [
                        record.get("actions"),
                        record.get("outcome"),
                        record.get("learned"),
                    ]
                    description = " | ".join(str(part) for part in description_parts if part)
                    items.append(WorkItem(
                        id=f"trae_cn_{file_path.stem}_{index}",
                        source="trae-cn",
                        source_type="memory",
                        title=str(title)[:120],
                        description=description[:500],
                        start_time=item_time,
                        end_time=item_time,
                        duration_hours=0.25,
                        status="completed",
                        priority="medium",
                        tags=["trae-cn", self._project_name(file_path)],
                        metadata={"file_path": str(file_path), "project": self._project_name(file_path)}
                    ))
        except Exception as e:
            self.logger.error(f"读取Trae CN文件失败 {file_path}: {e}")
        return items
    
    def _create_file_work_item(self, file_path: Path, modified_at: datetime) -> Optional[WorkItem]:
        try:
            return WorkItem(
                id=f"trae_cn_file_{abs(hash(str(file_path)))}",
                source="trae-cn",
                source_type="file_activity",
                title=f"Trae CN项目文件更新: {file_path.name}",
                description=f"项目 {self._project_name(file_path)} 中的文件近期有更新",
                start_time=modified_at,
                end_time=modified_at,
                duration_hours=0.1,
                status="completed",
                priority="medium",
                tags=["trae-cn", "file", self._project_name(file_path)],
                metadata={"file_path": str(file_path), "project": self._project_name(file_path)}
            )
        except Exception as e:
            self.logger.error(f"创建Trae CN文件工作项失败 {file_path}: {e}")
            return None
    
    def _project_name(self, file_path: Path) -> str:
        try:
            relative = file_path.relative_to(self.data_path)
            return relative.parts[0] if relative.parts else "unknown"
        except ValueError:
            return "unknown"
    
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
