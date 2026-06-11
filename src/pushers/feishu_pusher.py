#!/usr/bin/env python3
"""
飞书推送器 - 支持流式输出功能
将长报告拆分为多个消息，解决飞书128KB限制问题
"""

import json
import logging
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import requests
from urllib.parse import urljoin

from src.pushers.base_pusher import BasePusher


class FeishuPusher(BasePusher):
    """飞书推送器 - 支持流式输出"""
    
    def __init__(self, name: str = "feishu_pusher", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.logger = logging.getLogger(f"feishu_pusher")
        
        # 飞书配置
        self.app_id = config.get("app_id", "")
        self.app_secret = config.get("app_secret", "")
        self.encrypt_key = config.get("encrypt_key", "")
        self.verification_token = config.get("verification_token", "")
        self.default_chat_id = config.get("default_chat_id", "")
        self.test_mode = config.get("test_mode", False)
        
        # API端点
        self.base_url = "https://open.feishu.cn/open-apis"
        
        # 令牌管理
        self.access_token = None
        self.token_expiry = None
        
        # 流式输出配置
        self.max_message_length = config.get("max_message_length", 131072)  # 飞书限制
        self.chunk_size = config.get("chunk_size", 4000)  # 每个消息块大小
        self.delay_between_chunks = config.get("delay_between_chunks", 1.0)  # 消息间隔秒数
        
        # 消息缓存（用于避免重复发送）
        self.message_cache = {}
        self.cache_expiry = timedelta(minutes=5)
        
        self.logger.info(f"飞书推送器初始化完成，应用ID: {self.app_id[:8]}...")
        self.logger.info(f"流式输出配置: 块大小={self.chunk_size}, 最大消息长度={self.max_message_length}")
    
    def get_access_token(self) -> Optional[str]:
        """获取飞书访问令牌"""
        try:
            # 检查令牌是否有效
            if self.access_token and self.token_expiry:
                if datetime.now() < self.token_expiry:
                    self.logger.debug("使用缓存的访问令牌")
                    return self.access_token
            
            self.logger.info("获取新的飞书访问令牌")
            
            url = urljoin(self.base_url, "/auth/v3/app_access_token")
            headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result["tenant_access_token"]
                # 令牌有效期通常是2小时，我们提前5分钟刷新
                self.token_expiry = datetime.now() + timedelta(seconds=result.get("expire", 7200) - 300)
                self.logger.info("成功获取飞书访问令牌")
                return self.access_token
            else:
                self.logger.error(f"获取令牌失败: {result}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取飞书访问令牌异常: {e}")
            return None
    
    def _split_message(self, content: str) -> List[str]:
        """将长消息拆分为多个块"""
        if len(content) <= self.max_message_length:
            return [content]
        
        self.logger.info(f"消息过长({len(content)}字符)，拆分为多个块")
        
        chunks = []
        current_chunk = ""
        lines = content.split('\n')
        
        for line in lines:
            # 如果当前块加上这行会超过限制，保存当前块
            if len(current_chunk) + len(line) + 1 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
            
            # 添加这行到当前块
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)
        
        self.logger.info(f"消息拆分为 {len(chunks)} 个块")
        return chunks
    
    def _send_single_message(self, content: str, chat_id: str, message_type: str = "daily_work_report") -> Dict[str, Any]:
        """发送单个消息"""
        if self.test_mode:
            self.logger.info(f"[测试模式] 模拟发送消息到 {chat_id}")
            return {
                "success": True,
                "message_id": f"test_{int(time.time())}",
                "chat_id": chat_id,
                "content_length": len(content)
            }
        
        try:
            token = self.get_access_token()
            if not token:
                return {"success": False, "error": "无法获取访问令牌"}
            
            url = urljoin(self.base_url, f"/im/v1/messages?receive_id_type=chat_id")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            # 构建消息内容
            message_data = {
                "receive_id": chat_id,
                "msg_type": "text",
                "content": json.dumps({"text": content}, ensure_ascii=False)
            }
            
            # 添加消息类型标记（用于追踪）
            if message_type:
                message_data["uuid"] = f"{message_type}_{int(time.time())}"
            
            self.logger.debug(f"准备发送飞书消息，类型: {message_type}")
            response = requests.post(url, headers=headers, json=message_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    message_id = result.get("data", {}).get("message_id")
                    self.logger.info(f"飞书消息发送成功，消息ID: {message_id}")
                    return {
                        "success": True,
                        "message_id": message_id,
                        "chat_id": chat_id,
                        "content_length": len(content)
                    }
                else:
                    error_msg = result.get("msg", "未知错误")
                    self.logger.error(f"飞书API返回错误: {error_msg}")
                    return {"success": False, "error": error_msg}
            else:
                self.logger.error(f"飞书消息发送失败，HTTP状态码: {response.status_code}")
                return {"success": False, "error": f"HTTP请求失败: {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"发送飞书消息异常: {e}")
            return {"success": False, "error": str(e)}
    
    def send_streaming_message(self, content: str, chat_id: str = None, 
                              message_type: str = "daily_work_report") -> Dict[str, Any]:
        """发送流式消息（自动拆分长消息）"""
        chat_id = chat_id or self.default_chat_id
        if not chat_id:
            return {"success": False, "error": "未指定聊天ID"}
        
        # 检查消息是否已发送过（避免重复）
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        cache_key = f"{message_type}_{content_hash}"
        
        if cache_key in self.message_cache:
            cache_time = self.message_cache[cache_key]
            if datetime.now() - cache_time < self.cache_expiry:
                self.logger.info(f"消息已发送过（5分钟内），跳过重复发送")
                return {"success": True, "skipped": True, "reason": "duplicate"}
        
        # 拆分消息
        chunks = self._split_message(content)
        
        if len(chunks) == 0:
            return {"success": False, "error": "消息内容为空"}
        
        results = []
        total_sent = 0
        
        # 发送消息头
        header = f"📊 **{self._get_report_title(message_type)}**\n"
        header += f"📝 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"📋 报告共 {len(chunks)} 部分\n"
        header += "─" * 40 + "\n"
        
        header_result = self._send_single_message(header, chat_id, f"{message_type}_header")
        if header_result.get("success"):
            results.append(header_result)
            total_sent += 1
        
        # 发送各个部分
        for i, chunk in enumerate(chunks):
            # 添加进度指示器
            progress = f"📄 **第 {i+1}/{len(chunks)} 部分**\n"
            chunk_with_progress = progress + chunk
            
            chunk_result = self._send_single_message(chunk_with_progress, chat_id, f"{message_type}_part_{i+1}")
            results.append(chunk_result)
            
            if chunk_result.get("success"):
                total_sent += 1
                self.logger.info(f"✅ 发送第 {i+1}/{len(chunks)} 部分成功")
            else:
                self.logger.error(f"❌ 发送第 {i+1}/{len(chunks)} 部分失败: {chunk_result.get('error')}")
            
            # 在消息之间添加延迟（避免发送过快）
            if i < len(chunks) - 1:
                time.sleep(self.delay_between_chunks)
        
        # 发送消息尾
        footer = "\n" + "─" * 40 + "\n"
        footer += f"✅ **报告发送完成**\n"
        footer += f"📊 总部分数: {len(chunks)}\n"
        footer += f"✅ 成功发送: {total_sent}\n"
        footer += f"⏰ 完成时间: {datetime.now().strftime('%H:%M:%S')}"
        
        footer_result = self._send_single_message(footer, chat_id, f"{message_type}_footer")
        if footer_result.get("success"):
            results.append(footer_result)
            total_sent += 1
        
        # 缓存消息发送记录
        self.message_cache[cache_key] = datetime.now()
        
        # 清理过期缓存
        self._clean_cache()
        
        # 汇总结果
        success = total_sent > 0
        return {
            "success": success,
            "total_chunks": len(chunks),
            "chunks_sent": total_sent,
            "results": results,
            "content_hash": content_hash,
            "message_type": message_type
        }
    
    def _get_report_title(self, message_type: str) -> str:
        """获取报告标题"""
        titles = {
            "daily_work_report": "每日工作报告",
            "weekly_work_report": "每周工作报告",
            "monthly_work_report": "月度工作报告",
            "test_report": "测试报告",
            "error_alert": "错误告警"
        }
        return titles.get(message_type, "工作报告")
    
    def _clean_cache(self):
        """清理过期缓存"""
        now = datetime.now()
        expired_keys = []
        
        for key, timestamp in self.message_cache.items():
            if now - timestamp > self.cache_expiry:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.message_cache[key]
        
        if expired_keys:
            self.logger.debug(f"清理了 {len(expired_keys)} 个过期缓存项")
    
    def send_message(self, content: str, message_type: str = "daily_work_report", 
                    target: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送消息（主接口）"""
        if not target:
            target = {
                "chat_id": self.default_chat_id,
                "description": "默认目标"
            }
        
        chat_id = target.get("chat_id")
        if not chat_id:
            if self.test_mode:
                self.logger.info("[测试模式] 未指定聊天ID，跳过真实推送")
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "missing_chat_id_in_test_mode",
                    "content_length": len(content),
                    "test_mode": True
                }
            return {"success": False, "error": "未指定聊天ID"}
        
        # 根据消息长度决定使用哪种发送方式
        if len(content) <= self.max_message_length:
            self.logger.info(f"发送单条消息（{len(content)}字符）")
            return self._send_single_message(content, chat_id, message_type)
        else:
            self.logger.info(f"发送流式消息（{len(content)}字符，超过限制）")
            return self.send_streaming_message(content, chat_id, message_type)
    
    def test_connection(self) -> Dict[str, Any]:
        """测试飞书连接"""
        self.logger.info("测试飞书连接")
        
        if not self.test_mode:
            token = self.get_access_token()
            if not token:
                return {"success": False, "error": "无法获取访问令牌"}
        
        # 测试发送简短消息
        test_content = (
            "🔧 **飞书连接测试**\n\n"
            "✅ 统一工作记录系统连接测试成功！\n\n"
            "系统状态: 正常\n"
            "测试时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
            "版本: v1.0.0\n"
            "流式输出: 已启用"
        )
        
        result = self.send_message(test_content, "test_report", {
            "chat_id": self.default_chat_id,
            "description": "测试连接"
        })
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """获取推送器状态"""
        token_valid = self.access_token and self.token_expiry and datetime.now() < self.token_expiry
        
        return {
            "name": self.name,
            "app_id": self.app_id[:8] + "..." if self.app_id else "未设置",
            "default_chat_id": self.default_chat_id,
            "token_valid": token_valid,
            "test_mode": self.test_mode,
            "cache_size": len(self.message_cache),
            "max_message_length": self.max_message_length,
            "chunk_size": self.chunk_size
        }


def create_feishu_pusher(config: Dict[str, Any]) -> FeishuPusher:
    """创建飞书推送器实例"""
    return FeishuPusher("feishu_pusher", config)