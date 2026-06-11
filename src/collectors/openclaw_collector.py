#!/usr/bin/env python3
"""
OpenClaw数据收集器
从OpenClaw数据库收集工作项
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.collectors.base_collector import BaseCollector, WorkItem


class OpenClawCollector(BaseCollector):
    """OpenClaw数据收集器"""
    
    def __init__(self, name: str = "openclaw", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.logger = logging.getLogger(f"collector.openclaw")
        
        # OpenClaw数据库路径
        self.db_path = str(Path(config.get("db_path", "~/.openclaw/lcm.db")).expanduser())
        self.logger.info(f"OpenClaw数据库路径: {self.db_path}")
        
        # 缓存配置
        self.cache_duration = timedelta(hours=1)
        self.last_collection = None
        self.cached_items = []
    
    def _connect_to_db(self) -> Optional[sqlite3.Connection]:
        """连接到OpenClaw数据库"""
        try:
            if not Path(self.db_path).exists():
                self.logger.error(f"OpenClaw数据库不存在: {self.db_path}")
                return None
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 返回字典形式的结果
            return conn
            
        except Exception as e:
            self.logger.error(f"连接OpenClaw数据库失败: {e}")
            return None
    
    def _query_tasks(self, conn: sqlite3.Connection, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """查询任务数据"""
        try:
            cursor = conn.cursor()
            
            # 查询tasks表
            query = """
            SELECT 
                id, title, description, status, priority, 
                created_at, updated_at, completed_at,
                estimated_time, actual_time, tags, metadata
            FROM tasks 
            WHERE updated_at >= ? AND updated_at <= ?
            ORDER BY updated_at DESC
            """
            
            cursor.execute(query, (
                start_time.isoformat(),
                end_time.isoformat()
            ))
            
            tasks = []
            for row in cursor.fetchall():
                task = dict(row)
                
                # 解析标签
                if task.get("tags"):
                    try:
                        task["tags"] = json.loads(task["tags"])
                    except:
                        task["tags"] = []
                
                # 解析元数据
                if task.get("metadata"):
                    try:
                        task["metadata"] = json.loads(task["metadata"])
                    except:
                        task["metadata"] = {}
                
                tasks.append(task)
            
            self.logger.debug(f"从tasks表查询到 {len(tasks)} 个任务")
            return tasks
            
        except Exception as e:
            self.logger.error(f"查询tasks表失败: {e}")
            return []
    
    def _query_sessions(self, conn: sqlite3.Connection, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """查询会话数据"""
        try:
            cursor = conn.cursor()
            
            # 查询sessions表
            query = """
            SELECT 
                id, session_id, model, provider, start_time, end_time,
                total_tokens, total_cost, metadata, created_at
            FROM sessions 
            WHERE start_time >= ? AND start_time <= ?
            ORDER BY start_time DESC
            """
            
            cursor.execute(query, (
                start_time.isoformat(),
                end_time.isoformat()
            ))
            
            sessions = []
            for row in cursor.fetchall():
                session = dict(row)
                
                # 解析元数据
                if session.get("metadata"):
                    try:
                        session["metadata"] = json.loads(session["metadata"])
                    except:
                        session["metadata"] = {}
                
                sessions.append(session)
            
            self.logger.debug(f"从sessions表查询到 {len(sessions)} 个会话")
            return sessions
            
        except Exception as e:
            self.logger.error(f"查询sessions表失败: {e}")
            return []
    
    def _query_messages(self, conn: sqlite3.Connection, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """查询消息数据"""
        try:
            cursor = conn.cursor()
            columns = self._get_columns(conn, "messages")
            if not columns:
                return []
            time_column = "created_at" if "created_at" in columns else None
            conversation_column = "conversation_id" if "conversation_id" in columns else "session_id" if "session_id" in columns else "id"
            role_column = "role" if "role" in columns else None
            content_column = "content" if "content" in columns else None
            if not time_column or not content_column:
                return []
            query = f"""
            SELECT *
            FROM messages
            WHERE {time_column} >= ? AND {time_column} <= ?
            {"AND role = 'user'" if role_column else ""}
            ORDER BY {time_column} DESC
            LIMIT ?
            """
            cursor.execute(query, (start_time.isoformat(), end_time.isoformat(), self.config.get("query_limit", 100)))
            messages = []
            for row in cursor.fetchall():
                message = dict(row)
                message["conversation_id"] = message.get(conversation_column)
                message["created_at"] = message.get(time_column)
                message["content"] = message.get(content_column)
                messages.append(message)
            self.logger.debug(f"从messages表查询到 {len(messages)} 条消息")
            return messages
            
        except Exception as e:
            self.logger.error(f"查询messages表失败: {e}")
            return []
    
    def _get_tables(self, conn: sqlite3.Connection) -> List[str]:
        """获取数据库表名"""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]
    
    def _get_columns(self, conn: sqlite3.Connection, table_name: str) -> List[str]:
        """获取表字段"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            return [row[1] for row in cursor.fetchall()]
        except Exception:
            return []
    
    def _convert_message_to_work_item(self, message: Dict[str, Any]) -> Optional[WorkItem]:
        """将消息转换为工作项"""
        try:
            created_at = self._parse_datetime(message.get("created_at"))
            if not created_at:
                return None
            content = str(message.get("content") or "").strip()
            if not content or len(content) < self.config.get("min_content_length", 10):
                return None
            for keyword in self.config.get("exclude_keywords", []):
                if keyword and keyword in content:
                    return None
            return WorkItem(
                id=f"openclaw_message_{message.get('id', message.get('conversation_id', abs(hash(content))))}",
                source="openclaw",
                source_type="conversation",
                title=content[:120],
                description=content[:500],
                start_time=created_at,
                end_time=created_at,
                duration_hours=0.2,
                status="completed",
                priority="medium",
                tags=["openclaw", "conversation"],
                metadata={"conversation_id": message.get("conversation_id")}
            )
        except Exception as e:
            self.logger.error(f"转换消息为工作项失败: {e}")
            return None
    
    def _convert_task_to_work_item(self, task: Dict[str, Any]) -> Optional[WorkItem]:
        """将任务转换为工作项"""
        try:
            # 解析时间戳
            created_at = self._parse_datetime(task.get("created_at"))
            updated_at = self._parse_datetime(task.get("updated_at"))
            completed_at = self._parse_datetime(task.get("completed_at"))
            
            if not created_at:
                return None
            
            # 计算持续时间
            duration = 0.0
            if task.get("estimated_time"):
                try:
                    duration = float(task["estimated_time"]) / 3600  # 转换为小时
                except:
                    pass
            
            # 构建工作项
            work_item = WorkItem(
                id=f"openclaw_task_{task.get('id', 'unknown')}",
                source="openclaw",
                source_type="task",
                title=task.get("title", "未命名任务"),
                description=task.get("description", ""),
                start_time=created_at,
                end_time=completed_at or updated_at or created_at,
                duration_hours=duration,
                status=task.get("status", "unknown"),
                priority=task.get("priority", "medium"),
                tags=task.get("tags", []),
                metadata={
                    "task_id": task.get("id"),
                    "actual_time": task.get("actual_time"),
                    "status": task.get("status"),
                    "priority": task.get("priority")
                }
            )
            
            return work_item
            
        except Exception as e:
            self.logger.error(f"转换任务为工作项失败: {e}")
            return None
    
    def _convert_session_to_work_item(self, session: Dict[str, Any]) -> Optional[WorkItem]:
        """将会话转换为工作项"""
        try:
            # 解析时间戳
            start_time = self._parse_datetime(session.get("start_time"))
            end_time = self._parse_datetime(session.get("end_time"))
            
            if not start_time:
                return None
            
            # 计算持续时间
            duration = 0.0
            if start_time and end_time:
                duration = (end_time - start_time).total_seconds() / 3600
            
            # 构建工作项
            work_item = WorkItem(
                id=f"openclaw_session_{session.get('id', 'unknown')}",
                source="openclaw",
                source_type="session",
                title=f"AI会话: {session.get('model', 'unknown')}",
                description=f"提供商: {session.get('provider', 'unknown')}",
                start_time=start_time,
                end_time=end_time or start_time,
                duration_hours=duration,
                status="completed",
                priority="medium",
                tags=["ai-session", session.get("model", "unknown")],
                metadata={
                    "session_id": session.get("session_id"),
                    "model": session.get("model"),
                    "provider": session.get("provider"),
                    "total_tokens": session.get("total_tokens"),
                    "total_cost": session.get("total_cost")
                }
            )
            
            return work_item
            
        except Exception as e:
            self.logger.error(f"转换会话为工作项失败: {e}")
            return None
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not dt_str:
            return None
        
        try:
            # 尝试ISO格式
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # 尝试其他常见格式
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                    try:
                        return datetime.strptime(dt_str, fmt)
                    except ValueError:
                        continue
                
                # 如果都不行，尝试解析时间戳
                try:
                    timestamp = float(dt_str)
                    return datetime.fromtimestamp(timestamp)
                except:
                    pass
                
                self.logger.warning(f"无法解析日期时间: {dt_str}")
                return None
                
            except Exception as e:
                self.logger.error(f"解析日期时间异常: {e}")
                return None
    
    def collect_work_items(self, start_time: datetime, end_time: datetime) -> List[WorkItem]:
        """收集工作项"""
        self.logger.info(f"收集OpenClaw工作项: {self._format_time_range(start_time, end_time)}")
        
        # 检查缓存
        if self.last_collection and (datetime.now() - self.last_collection < self.cache_duration):
            filtered_items = [
                item for item in self.cached_items
                if start_time <= item.start_time <= end_time
            ]
            if filtered_items:
                self.logger.info(f"使用缓存数据: {len(filtered_items)} 个工作项")
                return filtered_items
        
        # 连接到数据库
        conn = self._connect_to_db()
        if not conn:
            self.logger.warning("无法连接OpenClaw数据库，返回空列表")
            return []
        
        work_items = []
        
        try:
            tables = self._get_tables(conn)
            
            if "tasks" in tables:
                tasks = self._query_tasks(conn, start_time, end_time)
                for task in tasks:
                    work_item = self._convert_task_to_work_item(task)
                    if work_item:
                        work_items.append(work_item)
            
            if "sessions" in tables:
                sessions = self._query_sessions(conn, start_time, end_time)
                for session in sessions:
                    work_item = self._convert_session_to_work_item(session)
                    if work_item:
                        work_items.append(work_item)
            
            if "messages" in tables:
                messages = self._query_messages(conn, start_time, end_time)
                for message in messages:
                    work_item = self._convert_message_to_work_item(message)
                    if work_item:
                        work_items.append(work_item)
            
            # 更新缓存
            self.cached_items = work_items
            self.last_collection = datetime.now()
            
            self.logger.info(f"从OpenClaw收集到 {len(work_items)} 个工作项")
            return work_items
            
        except Exception as e:
            self.logger.error(f"收集OpenClaw工作项时出错: {e}")
            return []
        
        finally:
            conn.close()
    
    def get_status(self) -> Dict[str, Any]:
        """获取收集器状态"""
        conn = self._connect_to_db()
        
        if conn:
            try:
                cursor = conn.cursor()
                
                # 获取表信息
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # 获取任务数量
                task_count = 0
                if 'tasks' in tables:
                    cursor.execute("SELECT COUNT(*) FROM tasks")
                    task_count = cursor.fetchone()[0]
                
                # 获取会话数量
                session_count = 0
                if 'sessions' in tables:
                    cursor.execute("SELECT COUNT(*) FROM sessions")
                    session_count = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    "name": self.name,
                    "db_path": self.db_path,
                    "db_exists": True,
                    "tables": tables,
                    "task_count": task_count,
                    "session_count": session_count,
                    "cache_size": len(self.cached_items),
                    "last_collection": self.last_collection.isoformat() if self.last_collection else None
                }
                
            except Exception as e:
                self.logger.error(f"获取OpenClaw状态失败: {e}")
                conn.close()
        
        return {
            "name": self.name,
            "db_path": self.db_path,
            "db_exists": False,
            "tables": [],
            "task_count": 0,
            "session_count": 0,
            "cache_size": len(self.cached_items),
            "last_collection": None
        }