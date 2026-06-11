"""
数据清洗处理器
专门负责数据清洗、去重和标准化
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import re
from collections import defaultdict
import hashlib

from .base_processor import BaseProcessor, ProcessedWorkItem, ProcessorFactory


class DataCleaner(BaseProcessor):
    """数据清洗处理器"""
    
    def __init__(self, name: str = 'data_cleaner', config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        
        # 清洗配置
        self.min_duration = self.config.get('min_duration', 1)  # 最小持续时间（分钟）
        self.max_duration = self.config.get('max_duration', 480)  # 最大持续时间（分钟）
        self.remove_duplicates = self.config.get('remove_duplicates', True)
        self.normalize_timestamps = self.config.get('normalize_timestamps', True)
        self.fill_missing_fields = self.config.get('fill_missing_fields', True)
    
    def process(self, work_items: List[Dict[str, Any]]) -> List[ProcessedWorkItem]:
        """
        清洗工作项数据
        
        Args:
            work_items: 原始工作项列表
            
        Returns:
            清洗后的工作项列表
        """
        self.logger.info(f"开始清洗 {len(work_items)} 个工作项")
        
        # 第一步：基础清洗
        cleaned_items = []
        for item in work_items:
            try:
                cleaned_item = self._basic_clean(item)
                if cleaned_item:
                    cleaned_items.append(cleaned_item)
            except Exception as e:
                self.logger.error(f"基础清洗失败: {e}")
        
        self.logger.info(f"基础清洗后剩余 {len(cleaned_items)} 个工作项")
        
        # 第二步：去重
        if self.remove_duplicates:
            cleaned_items = self._remove_duplicates(cleaned_items)
            self.logger.info(f"去重后剩余 {len(cleaned_items)} 个工作项")
        
        # 第三步：时间标准化
        if self.normalize_timestamps:
            cleaned_items = self._normalize_timestamps(cleaned_items)
        
        # 第四步：填充缺失字段
        if self.fill_missing_fields:
            cleaned_items = self._fill_missing_fields(cleaned_items)
        
        # 第五步：过滤无效数据
        cleaned_items = self._filter_invalid_items(cleaned_items)
        self.logger.info(f"最终清洗后剩余 {len(cleaned_items)} 个工作项")
        
        # 转换为ProcessedWorkItem格式
        processed_items = []
        for item in cleaned_items:
            try:
                processed_item = ProcessedWorkItem(
                    original_item=item.get('_original', item),
                    cleaned_item=item,
                    categories=[],
                    keywords=[],
                    sentiment='neutral',
                    importance_score=0.5,
                    time_blocks=[],
                    summary='',
                    metadata={'cleaned': True}
                )
                processed_items.append(processed_item)
            except Exception as e:
                self.logger.error(f"转换为ProcessedWorkItem失败: {e}")
        
        return processed_items
    
    def _basic_clean(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """基础清洗"""
        if not item:
            return None
        
        cleaned = item.copy()
        
        # 保存原始数据
        cleaned['_original'] = item
        
        # 清理文本字段
        text_fields = ['title', 'description', 'summary', 'content']
        for field in text_fields:
            if field in cleaned:
                cleaned[field] = self._clean_text_field(cleaned[field])
        
        # 清理数值字段
        numeric_fields = ['duration_minutes', 'priority_level', 'importance']
        for field in numeric_fields:
            if field in cleaned:
                cleaned[field] = self._clean_numeric_field(cleaned[field])
        
        # 清理列表字段
        list_fields = ['tags', 'categories', 'keywords', 'participants']
        for field in list_fields:
            if field in cleaned:
                cleaned[field] = self._clean_list_field(cleaned[field])
        
        # 清理时间字段
        time_fields = ['start_time', 'end_time', 'created_at', 'updated_at', 'completed_at']
        for field in time_fields:
            if field in cleaned:
                cleaned[field] = self._clean_time_field(cleaned[field])
        
        # 生成唯一ID（如果不存在）
        if 'id' not in cleaned or not cleaned['id']:
            cleaned['id'] = self._generate_item_id(cleaned)
        
        return cleaned
    
    def _clean_text_field(self, value: Any) -> str:
        """清理文本字段"""
        if value is None:
            return ''
        
        if not isinstance(value, str):
            value = str(value)
        
        # 移除多余空格
        value = re.sub(r'\s+', ' ', value.strip())
        
        # 移除控制字符
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        # 标准化换行符
        value = value.replace('\r\n', '\n').replace('\r', '\n')
        
        # 截断过长的文本
        max_length = self.config.get('max_text_length', 1000)
        if len(value) > max_length:
            value = value[:max_length] + '...'
        
        return value
    
    def _clean_numeric_field(self, value: Any) -> float:
        """清理数值字段"""
        if value is None:
            return 0.0
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # 移除非数字字符
                numeric_str = re.sub(r'[^\d\.\-]', '', value)
                if numeric_str:
                    return float(numeric_str)
        except (ValueError, TypeError):
            pass
        
        return 0.0
    
    def _clean_list_field(self, value: Any) -> List[str]:
        """清理列表字段"""
        if value is None:
            return []
        
        if isinstance(value, str):
            # 尝试解析字符串为列表
            if value.startswith('[') and value.endswith(']'):
                try:
                    import json
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        value = parsed
                except:
                    pass
        
        if not isinstance(value, list):
            value = [value]
        
        # 清理列表中的每个元素
        cleaned_list = []
        for item in value:
            if item is not None:
                cleaned_item = str(item).strip()
                if cleaned_item:
                    cleaned_list.append(cleaned_item)
        
        return cleaned_list
    
    def _clean_time_field(self, value: Any) -> Optional[str]:
        """清理时间字段"""
        if value is None:
            return None
        
        try:
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, (int, float)):
                # 可能是时间戳
                return datetime.fromtimestamp(value).isoformat()
            elif isinstance(value, str):
                # 尝试解析各种时间格式
                formats = [
                    '%Y-%m-%dT%H:%M:%S.%f%z',
                    '%Y-%m-%dT%H:%M:%S%z',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%Y/%m/%d %H:%M:%S',
                    '%Y/%m/%d'
                ]
                
                for fmt in formats:
                    try:
                        dt = datetime.strptime(value, fmt)
                        return dt.isoformat()
                    except:
                        continue
                
                # 如果无法解析，返回原始值
                return value
        except Exception:
            pass
        
        return str(value) if value else None
    
    def _generate_item_id(self, item: Dict[str, Any]) -> str:
        """生成唯一ID"""
        # 使用关键字段生成哈希
        key_fields = ['title', 'start_time', 'tool', 'category']
        key_string = ''
        
        for field in key_fields:
            if field in item and item[field]:
                key_string += str(item[field])
        
        if not key_string:
            key_string = str(datetime.now().timestamp())
        
        # 生成MD5哈希
        hash_obj = hashlib.md5(key_string.encode('utf-8'))
        return f"item_{hash_obj.hexdigest()[:8]}"
    
    def _remove_duplicates(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重"""
        if not items:
            return []
        
        seen_items = set()
        unique_items = []
        
        for item in items:
            # 生成项目签名用于去重
            item_signature = self._get_item_signature(item)
            
            if item_signature not in seen_items:
                seen_items.add(item_signature)
                unique_items.append(item)
            else:
                self.logger.debug(f"发现重复项: {item.get('id', 'unknown')}")
        
        return unique_items
    
    def _get_item_signature(self, item: Dict[str, Any]) -> str:
        """获取项目签名用于去重"""
        # 基于关键字段生成签名
        signature_fields = ['title', 'start_time', 'tool', 'category']
        signature_parts = []
        
        for field in signature_fields:
            value = item.get(field, '')
            if isinstance(value, str):
                signature_parts.append(value[:50])  # 截断长文本
            else:
                signature_parts.append(str(value))
        
        return '|'.join(signature_parts).lower()
    
    def _normalize_timestamps(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """时间标准化"""
        for item in items:
            # 确保时间字段格式一致
            for time_field in ['start_time', 'end_time']:
                if time_field in item and item[time_field]:
                    try:
                        # 尝试解析为datetime
                        if isinstance(item[time_field], str):
                            dt = datetime.fromisoformat(item[time_field].replace('Z', '+00:00'))
                            item[time_field] = dt.isoformat()
                    except:
                        pass
            
            # 计算持续时间（如果缺失）
            if 'duration_minutes' not in item or not item['duration_minutes']:
                item['duration_minutes'] = self._calculate_duration(item)
        
        return items
    
    def _calculate_duration(self, item: Dict[str, Any]) -> float:
        """计算持续时间"""
        start_time = item.get('start_time')
        end_time = item.get('end_time')
        
        if start_time and end_time:
            try:
                if isinstance(start_time, str):
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                else:
                    start_dt = start_time
                
                if isinstance(end_time, str):
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                else:
                    end_dt = end_time
                
                duration = (end_dt - start_dt).total_seconds() / 60
                return max(0, duration)
            except:
                pass
        
        # 使用默认值或从其他字段推断
        default_duration = item.get('estimated_duration', 30)  # 默认30分钟
        return float(default_duration)
    
    def _fill_missing_fields(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """填充缺失字段"""
        for item in items:
            # 填充默认值
            defaults = {
                'priority': 'medium',
                'status': 'unknown',
                'category': 'other',
                'tags': [],
                'tool': 'unknown',
                'importance_score': 0.5
            }
            
            for field, default_value in defaults.items():
                if field not in item or item[field] is None:
                    item[field] = default_value
            
            # 从其他字段推断缺失信息
            if 'category' not in item or item['category'] == 'other':
                item['category'] = self._infer_category(item)
            
            if 'priority' not in item or item['priority'] == 'medium':
                item['priority'] = self._infer_priority(item)
        
        return items
    
    def _infer_category(self, item: Dict[str, Any]) -> str:
        """推断分类"""
        title = item.get('title', '').lower()
        description = item.get('description', '').lower()
        tool = item.get('tool', '').lower()
        
        # 基于关键词推断
        category_keywords = {
            'coding': ['代码', '编程', '开发', '函数', '类', '模块', 'api', '数据库'],
            'research': ['研究', '分析', '调查', '数据', '统计', '报告'],
            'planning': ['计划', '规划', '设计', '架构', '方案', '策略'],
            'debugging': ['调试', '错误', 'bug', '问题', '修复', '异常'],
            'documentation': ['文档', '说明', '指南', '教程', '注释'],
            'meeting': ['会议', '讨论', '沟通', '协调', '合作'],
            'learning': ['学习', '教程', '教育', '培训', '知识']
        }
        
        all_text = f"{title} {description}"
        for category, keywords in category_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                return category
        
        # 基于工具推断
        if tool in ['trae-cn', 'openclaw', 'hermes']:
            return 'ai_assistant'
        
        return 'other'
    
    def _infer_priority(self, item: Dict[str, Any]) -> str:
        """推断优先级"""
        # 基于持续时间
        duration = item.get('duration_minutes', 0)
        if duration > 120:
            return 'high'
        elif duration > 60:
            return 'medium'
        
        # 基于关键词
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        high_priority_words = ['紧急', 'urgent', '立刻', '马上', '尽快', 'critical', '重要']
        
        if any(word in text for word in high_priority_words):
            return 'high'
        
        return 'medium'
    
    def _filter_invalid_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤无效数据"""
        valid_items = []
        
        for item in items:
            # 检查必要字段
            if not item.get('id'):
                self.logger.warning(f"跳过无ID的项: {item}")
                continue
            
            # 检查持续时间
            duration = item.get('duration_minutes', 0)
            if duration < self.min_duration:
                self.logger.debug(f"跳过持续时间过短的项: {duration}分钟")
                continue
            
            if duration > self.max_duration:
                self.logger.debug(f"跳过持续时间过长的项: {duration}分钟")
                continue
            
            # 检查时间有效性
            start_time = item.get('start_time')
            end_time = item.get('end_time')
            if start_time and end_time:
                try:
                    if isinstance(start_time, str):
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    else:
                        start_dt = start_time
                    
                    if isinstance(end_time, str):
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    else:
                        end_dt = end_time
                    
                    if end_dt < start_dt:
                        self.logger.warning(f"跳过时间无效的项: 结束时间早于开始时间")
                        continue
                except:
                    pass
            
            valid_items.append(item)
        
        return valid_items


# 注册到工厂
from .base_processor import ProcessorFactory
ProcessorFactory.register('data_cleaner', DataCleaner)