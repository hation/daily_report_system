"""
管理器模块
包含报告管理器等组件
"""

from .report_manager import ReportManager, create_report_manager

__all__ = [
    'ReportManager',
    'create_report_manager'
]