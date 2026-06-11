"""
数据收集器模块
统一从各种工具收集工作记录
"""

from .base_collector import BaseCollector, WorkItem
from .trae_cn_collector import TraeCNCollector
from .trae_work_cn_collector import TraeWorkCNCollector
from .codex_collector import CodexCollector
from .pilotdeck_collector import PilotDeckCollector
from .openclaw_collector import OpenClawCollector
from .hermes_collector import HermesCollector
from .collector_manager import CollectorManager, create_default_collector_manager

# 收集器工厂（简化版）
class CollectorFactory:
    """收集器工厂类"""
    
    _collectors = {}
    
    @classmethod
    def register(cls, name, collector_class):
        """注册收集器"""
        cls._collectors[name] = collector_class
    
    @classmethod
    def create(cls, name, config):
        """创建收集器"""
        collector_class = cls._collectors.get(name)
        if not collector_class:
            raise ValueError(f"未知的收集器类型: {name}")
        return collector_class(name, config)
    
    @classmethod
    def get_registered_collectors(cls):
        """获取已注册的收集器"""
        return list(cls._collectors.keys())

# 注册收集器到工厂
CollectorFactory.register('trae-cn', TraeCNCollector)
CollectorFactory.register('trae-work-cn', TraeWorkCNCollector)
CollectorFactory.register('codex', CodexCollector)
CollectorFactory.register('pilotdeck', PilotDeckCollector)
CollectorFactory.register('openclaw', OpenClawCollector)
CollectorFactory.register('hermes', HermesCollector)

__all__ = [
    'BaseCollector',
    'WorkItem',
    'CollectorFactory',
    'TraeCNCollector',
    'TraeWorkCNCollector',
    'CodexCollector',
    'PilotDeckCollector',
    'OpenClawCollector',
    'HermesCollector',
    'CollectorManager',
    'create_default_collector_manager'
]

__version__ = '1.0.0'