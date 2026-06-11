#!/usr/bin/env python3
"""
基础收集器抽象类 - 简化版
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict


@dataclass
class WorkItem:
    """工作项数据结构"""
    id: str
    source: str
    source_type: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    duration_hours: float
    status: str
    priority: str
    tags: List[str]
    metadata: Dict[str, Any]

    @property
    def duration_minutes(self) -> float:
        return round(self.duration_hours * 60, 2)

    @property
    def tool(self) -> str:
        return self.source

    @property
    def category(self) -> str:
        return self.source_type

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["start_time"] = self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time
        data["end_time"] = self.end_time.isoformat() if isinstance(self.end_time, datetime) else self.end_time
        data["duration_minutes"] = self.duration_minutes
        data["tool"] = self.tool
        data["category"] = self.category
        return data


class BaseCollector(ABC):
    """基础收集器抽象类 - 简化版"""
    
    def __init__(self, name: str = "base_collector", config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"collector.{name}")
    
    def collect(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集工作项（主接口）"""
        self.logger.info(f"收集{self.name}工作项: {self._format_time_range(start_time, end_time)}")
        return self.collect_work_items(start_time, end_time)
    
    @abstractmethod
    def collect_work_items(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集工作项（子类实现）"""
        pass
    
    def _test_connection_impl(self) -> bool:
        """测试连接实现"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            items = self.collect(start_time, end_time)
            self.logger.info(f"连接测试成功，收集到 {len(items)} 个工作项")
            return True
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试连接"""
        return self._test_connection_impl()
    
    def get_statistics(self, work_items: List[WorkItem]) -> Dict[str, Any]:
        """获取收集结果统计"""
        total_duration_hours = sum(item.duration_hours for item in work_items)
        return {
            "total_items": len(work_items),
            "total_duration_hours": round(total_duration_hours, 2),
            "total_duration_minutes": round(total_duration_hours * 60, 2),
        }
    
    def cleanup(self):
        """清理资源"""
        return None
    
    def get_required_config_keys(self) -> List[str]:
        """获取必需配置键"""
        return []
    
    def _format_time_range(self, start_time: datetime, end_time: datetime) -> str:
        """格式化时间范围"""
        return f"{start_time.isoformat()} - {end_time.isoformat()}"