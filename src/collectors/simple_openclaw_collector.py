"""
极简版OpenClaw收集器
只获取基本数据，避免复杂错误
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

from .base_collector import BaseCollector, WorkItem


class SimpleOpenClawCollector(BaseCollector):
    """极简版OpenClaw收集器"""
    
    def __init__(self, name: str = "openclaw", config: Dict[str, Any] = None):
        super().__init__(name, config)
        
        # OpenClaw数据库路径
        self.db_path = os.path.expanduser(self.config.get("db_path", "~/.openclaw/lcm.db"))
        self.logger.info(f"OpenClaw数据库路径: {self.db_path}")
    
    def get_required_config_keys(self) -> List[str]:
        """获取必要的配置键列表"""
        return ["db_path"]
    
    def _test_connection_impl(self) -> bool:
        """具体连接测试实现"""
        try:
            if not os.path.exists(self.db_path):
                self.logger.error(f"OpenClaw数据库不存在: {self.db_path}")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查必要的表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ["conversations", "messages"]
            existing_tables = [t for t in required_tables if t in tables]
            
            conn.close()
            
            if len(existing_tables) >= 1:
                self.logger.info(f"OpenClaw数据库验证通过，找到表: {existing_tables}")
                return True
            else:
                self.logger.error(f"OpenClaw数据库缺少必要的表")
                return False
                
        except sqlite3.Error as e:
            self.logger.error(f"连接OpenClaw数据库失败: {e}")
            return False
    
    def collect(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """
        收集OpenClaw工作项（极简版）
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            工作项列表
        """
        self.logger.info(f"收集OpenClaw工作项: {start_time} - {end_time}")
        
        work_items = []
        
        try:
            if not os.path.exists(self.db_path):
                self.logger.warning(f"OpenClaw数据库不存在: {self.db_path}")
                return []
            
            conn = sqlite3.connect(self.db_path)
            
            # 1. 收集会话信息
            session_items = self._collect_simple_sessions(conn, start_time, end_time)
            work_items.extend(session_items)
            
            # 2. 收集消息信息
            message_items = self._collect_simple_messages(conn, start_time, end_time)
            work_items.extend(message_items)
            
            conn.close()
            
            self.logger.info(f"从OpenClaw收集到 {len(work_items)} 个工作项")
            return work_items
            
        except Exception as e:
            self.logger.error(f"收集OpenClaw工作项失败: {e}")
            return []
    
    def _collect_simple_sessions(self, conn, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集简单的会话信息"""
        items = []
        
        try:
            cursor = conn.cursor()
            
            # 简单查询，只获取存在的列
            query = """
            SELECT 
                conversation_id, title, created_at, updated_at
            FROM conversations
            WHERE created_at >= ? AND created_at <= ?
               OR updated_at >= ? AND updated_at <= ?
            ORDER BY created_at DESC
            LIMIT 20
            """
            
            start_ts = start_time.strftime('%Y-%m-%d %H:%M:%S')
            end_ts = end_time.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute(query, (start_ts, end_ts, start_ts, end_ts))
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    conv_id = row[0]
                    title = row[1] or f"会话 {conv_id}"
                    created_at_str = row[2]
                    updated_at_str = row[3]
                    
                    # 解析时间
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00')) if created_at_str else start_time
                        updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00')) if updated_at_str else created_at
                    except:
                        created_at = start_time
                        updated_at = start_time
                    
                    # 创建简单工作项
                    work_item = WorkItem(
                        id=f"openclaw_conv_{conv_id}",
                        source="openclaw",
                        source_type="conversation",
                        title=title,
                        description=f"OpenClaw会话: {title}",
                        content=f"会话ID: {conv_id}",
                        start_time=created_at,
                        end_time=updated_at,
                        duration=0,
                        tags=["openclaw", "conversation"],
                        metadata={"conversation_id": conv_id}
                    )
                    
                    items.append(work_item)
                    
                except Exception as e:
                    self.logger.warning(f"解析会话记录失败: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"查询会话记录失败: {e}")
        
        return items
    
    def _collect_simple_messages(self, conn, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集简单的消息信息"""
        items = []
        
        try:
            cursor = conn.cursor()
            
            # 简单查询，只获取存在的列
            query = """
            SELECT 
                m.message_id, m.conversation_id, m.role, m.content, m.created_at,
                c.title as conversation_title
            FROM messages m
            LEFT JOIN conversations c ON m.conversation_id = c.conversation_id
            WHERE m.created_at >= ? AND m.created_at <= ?
            ORDER BY m.created_at DESC
            LIMIT 30
            """
            
            start_ts = start_time.strftime('%Y-%m-%d %H:%M:%S')
            end_ts = end_time.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute(query, (start_ts, end_ts))
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    msg_id = row[0]
                    conv_id = row[1]
                    role = row[2] or 'unknown'
                    content = row[3] or ''
                    created_at_str = row[4]
                    conversation_title = row[5] or f"会话 {conv_id}"
                    
                    # 只处理用户和助手消息
                    if role not in ['user', 'assistant']:
                        continue
                    
                    # 解析时间
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00')) if created_at_str else start_time
                    except:
                        created_at = start_time
                    
                    # 创建简单工作项
                    work_item = WorkItem(
                        id=f"openclaw_msg_{msg_id}",
                        source="openclaw",
                        source_type="message",
                        title=f"{role}消息: {conversation_title}",
                        description=content[:100] + "..." if len(content) > 100 else content,
                        content=content,
                        start_time=created_at,
                        end_time=created_at + timedelta(minutes=1),
                        duration=1,
                        tags=["openclaw", "message", role],
                        metadata={
                            "message_id": msg_id,
                            "conversation_id": conv_id,
                            "role": role
                        }
                    )
                    
                    items.append(work_item)
                    
                except Exception as e:
                    self.logger.warning(f"解析消息记录失败: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"查询消息记录失败: {e}")
        
        return items
    
    def get_stats(self) -> Dict[str, Any]:
        """获取收集器统计信息"""
        stats = {}
        
        try:
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 统计会话数量
                cursor.execute("SELECT COUNT(*) FROM conversations")
                conv_count = cursor.fetchone()[0]
                
                # 统计消息数量
                cursor.execute("SELECT COUNT(*) FROM messages")
                msg_count = cursor.fetchone()[0]
                
                conn.close()
                
                stats.update({
                    "database_path": self.db_path,
                    "conversation_count": conv_count,
                    "message_count": msg_count,
                    "database_exists": True
                })
            else:
                stats.update({
                    "database_path": self.db_path,
                    "database_exists": False
                })
                
        except Exception as e:
            self.logger.error(f"获取OpenClaw统计信息失败: {e}")
            stats.update({
                "database_path": self.db_path,
                "error": str(e)
            })
        
        return stats


def create_simple_openclaw_collector(config: Dict[str, Any] = None) -> SimpleOpenClawCollector:
    """创建极简版OpenClaw收集器"""
    return SimpleOpenClawCollector("openclaw", config)