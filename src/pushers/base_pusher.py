#!/usr/bin/env python3
"""
基础推送器抽象类
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BasePusher(ABC):
    """基础推送器抽象类"""
    
    def __init__(self, name: str = "base_pusher", config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"pusher.{name}")
    
    @abstractmethod
    def send_message(self, content: str, message_type: str = "default", 
                    target: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送消息"""
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        pass
    
    def _format_target_info(self, target: Dict[str, Any]) -> str:
        """格式化目标信息"""
        if not target:
            return "未指定目标"
        
        target_type = target.get("type", "unknown")
        target_id = target.get("id", target.get("chat_id", "unknown"))
        return f"{target_type}:{target_id}"