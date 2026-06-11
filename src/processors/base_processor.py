"""
数据处理器基础框架
负责清洗、分类、分析和格式化收集到的工作项
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import re
from collections import defaultdict, Counter


@dataclass
class ProcessedWorkItem:
    """处理后的工作项"""
    original_item: Dict[str, Any]  # 原始工作项
    cleaned_item: Dict[str, Any]   # 清洗后的工作项
    categories: List[str]          # 分类标签
    keywords: List[str]            # 关键词
    sentiment: str                 # 情感倾向: positive, neutral, negative
    importance_score: float        # 重要性评分 (0-1)
    time_blocks: List[Dict[str, Any]]  # 时间块划分
    summary: str                   # 摘要
    metadata: Dict[str, Any]       # 处理元数据


class BaseProcessor:
    """基础数据处理器"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"processor.{name}")
    
    def process(self, work_items: List[Dict[str, Any]]) -> List[ProcessedWorkItem]:
        """
        处理工作项列表
        
        Args:
            work_items: 原始工作项列表
            
        Returns:
            处理后的工作项列表
        """
        self.logger.info(f"开始处理 {len(work_items)} 个工作项")
        
        processed_items = []
        for i, item in enumerate(work_items):
            try:
                processed_item = self._process_single_item(item)
                processed_items.append(processed_item)
                
                if (i + 1) % 10 == 0:
                    self.logger.debug(f"已处理 {i + 1}/{len(work_items)} 个工作项")
                    
            except Exception as e:
                self.logger.error(f"处理工作项 {item.get('id', 'unknown')} 失败: {e}")
        
        self.logger.info(f"处理完成，成功 {len(processed_items)} 个，失败 {len(work_items) - len(processed_items)} 个")
        return processed_items
    
    def _process_single_item(self, item: Dict[str, Any]) -> ProcessedWorkItem:
        """处理单个工作项"""
        # 1. 数据清洗
        cleaned_item = self._clean_data(item)
        
        # 2. 分类
        categories = self._categorize_item(cleaned_item)
        
        # 3. 关键词提取
        keywords = self._extract_keywords(cleaned_item)
        
        # 4. 情感分析
        sentiment = self._analyze_sentiment(cleaned_item)
        
        # 5. 重要性评分
        importance_score = self._calculate_importance(cleaned_item, categories)
        
        # 6. 时间块划分
        time_blocks = self._split_time_blocks(cleaned_item)
        
        # 7. 生成摘要
        summary = self._generate_summary(cleaned_item, categories, keywords)
        
        # 8. 构建元数据
        metadata = {
            "processed_at": datetime.now().isoformat(),
            "processor": self.name,
            "processing_time_ms": None,  # 可以在子类中计算
            "confidence_scores": {
                "categorization": 0.8,  # 分类置信度
                "sentiment": 0.7,       # 情感分析置信度
                "importance": 0.6       # 重要性评分置信度
            }
        }
        
        return ProcessedWorkItem(
            original_item=item,
            cleaned_item=cleaned_item,
            categories=categories,
            keywords=keywords,
            sentiment=sentiment,
            importance_score=importance_score,
            time_blocks=time_blocks,
            summary=summary,
            metadata=metadata
        )
    
    def _clean_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """数据清洗"""
        cleaned = item.copy()
        
        # 清理文本字段
        text_fields = ['title', 'description', 'summary']
        for field in text_fields:
            if field in cleaned and cleaned[field]:
                cleaned[field] = self._clean_text(cleaned[field])
        
        # 标准化时间格式
        time_fields = ['start_time', 'end_time', 'created_at']
        for field in time_fields:
            if field in cleaned and cleaned[field]:
                cleaned[field] = self._normalize_time(cleaned[field])
        
        # 确保必要字段存在
        cleaned.setdefault('duration_minutes', 0)
        cleaned.setdefault('priority', 'medium')
        cleaned.setdefault('status', 'unknown')
        cleaned.setdefault('tags', [])
        
        # 移除空值字段
        cleaned = {k: v for k, v in cleaned.items() if v is not None}
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not isinstance(text, str):
            text = str(text)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊字符（保留中文、英文、数字、标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fff\.,;:!?()\-]', '', text)
        
        # 标准化标点
        text = text.replace('，', ', ').replace('。', '. ').replace('；', '; ')
        
        return text
    
    def _normalize_time(self, time_value: Any) -> str:
        """标准化时间格式"""
        if isinstance(time_value, datetime):
            return time_value.isoformat()
        elif isinstance(time_value, str):
            try:
                # 尝试解析ISO格式
                dt = datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                return dt.isoformat()
            except:
                return time_value
        else:
            return str(time_value)
    
    def _categorize_item(self, item: Dict[str, Any]) -> List[str]:
        """分类工作项"""
        categories = []
        
        # 基于现有分类
        if 'category' in item and item['category']:
            categories.append(item['category'])
        
        # 基于工具类型
        if 'tool' in item and item['tool']:
            categories.append(f"tool:{item['tool']}")
        
        # 基于优先级
        if 'priority' in item and item['priority']:
            categories.append(f"priority:{item['priority']}")
        
        # 基于状态
        if 'status' in item and item['status']:
            categories.append(f"status:{item['status']}")
        
        # 基于持续时间
        duration = item.get('duration_minutes', 0)
        if duration > 120:
            categories.append("long_task")
        elif duration > 30:
            categories.append("medium_task")
        else:
            categories.append("short_task")
        
        return list(set(categories))  # 去重
    
    def _extract_keywords(self, item: Dict[str, Any]) -> List[str]:
        """提取关键词"""
        keywords = set()
        
        # 从标签中提取
        tags = item.get('tags', [])
        if isinstance(tags, list):
            keywords.update([str(tag).lower() for tag in tags[:10]])
        
        # 从标题和描述中提取
        text_fields = ['title', 'description']
        for field in text_fields:
            if field in item and item[field]:
                text = item[field].lower()
                # 简单提取：按空格分割，过滤停用词
                words = re.findall(r'\b\w{3,}\b', text)
                stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'was', 'were', 'have', 'has', 'had'}
                keywords.update([w for w in words if w not in stop_words][:5])
        
        return list(keywords)[:10]  # 最多10个关键词
    
    def _analyze_sentiment(self, item: Dict[str, Any]) -> str:
        """分析情感倾向"""
        text = ''
        if 'title' in item and item['title']:
            text += item['title'] + ' '
        if 'description' in item and item['description']:
            text += item['description']
        
        if not text:
            return "neutral"
        
        text = text.lower()
        
        # 积极词汇
        positive_words = {
            '完成', '成功', '优秀', '良好', '顺利', '解决', '改进', '优化',
            '提升', '增加', '减少', '高效', '快速', '简单', '容易', '开心'
        }
        
        # 消极词汇
        negative_words = {
            '失败', '错误', '问题', '困难', '复杂', '缓慢', '延迟', '卡住',
            'bug', '崩溃', '异常', '警告', '危险', '紧急', '修复', '麻烦'
        }
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_importance(self, item: Dict[str, Any], categories: List[str]) -> float:
        """计算重要性评分 (0-1)"""
        score = 0.5  # 基础分
        
        # 优先级影响
        priority = item.get('priority', 'medium')
        if priority == 'high':
            score += 0.3
        elif priority == 'low':
            score -= 0.2
        
        # 持续时间影响
        duration = item.get('duration_minutes', 0)
        if duration > 120:
            score += 0.2
        elif duration > 60:
            score += 0.1
        
        # 状态影响
        status = item.get('status', '')
        if status == 'completed':
            score += 0.1
        elif status == 'in_progress':
            score += 0.05
        
        # 工具类型影响
        tool = item.get('tool', '')
        if tool in ['hermes', 'openclaw']:  # 核心工具
            score += 0.1
        
        # 确保分数在0-1之间
        return max(0.0, min(1.0, score))
    
    def _split_time_blocks(self, item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """划分时间块"""
        blocks = []
        
        duration = item.get('duration_minutes', 0)
        if duration <= 0:
            return blocks
        
        # 简单划分：每30分钟一个块
        block_size = 30
        num_blocks = max(1, duration // block_size)
        
        for i in range(num_blocks):
            block_start = i * block_size
            block_end = min((i + 1) * block_size, duration)
            
            blocks.append({
                "block_id": i + 1,
                "start_minute": block_start,
                "end_minute": block_end,
                "duration_minutes": block_end - block_start,
                "description": f"时间段 {i + 1}"
            })
        
        return blocks
    
    def _generate_summary(self, item: Dict[str, Any], categories: List[str], keywords: List[str]) -> str:
        """生成摘要"""
        title = item.get('title', '工作项')
        description = item.get('description', '')
        duration = item.get('duration_minutes', 0)
        tool = item.get('tool', '未知工具')
        
        # 构建摘要
        summary_parts = []
        
        # 标题
        if title:
            summary_parts.append(f"标题: {title}")
        
        # 工具和持续时间
        summary_parts.append(f"使用 {tool}，耗时 {duration} 分钟")
        
        # 主要分类
        if categories:
            main_categories = [c for c in categories if not c.startswith(('tool:', 'priority:', 'status:'))]
            if main_categories:
                summary_parts.append(f"分类: {', '.join(main_categories[:3])}")
        
        # 关键词
        if keywords:
            summary_parts.append(f"关键词: {', '.join(keywords[:5])}")
        
        # 简短描述
        if description and len(description) > 50:
            summary_parts.append(f"描述: {description[:100]}...")
        
        return " | ".join(summary_parts)


class ProcessorFactory:
    """处理器工厂"""
    
    _processors = {}
    
    @classmethod
    def register(cls, name: str, processor_class):
        """注册处理器类"""
        cls._processors[name] = processor_class
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any] = None) -> BaseProcessor:
        """创建处理器实例"""
        if name not in cls._processors:
            raise ValueError(f"未知的处理器类型: {name}")
        
        processor_class = cls._processors[name]
        return processor_class(name, config)
    
    @classmethod
    def list_available(cls) -> List[str]:
        """获取可用的处理器列表"""
        return list(cls._processors.keys())


# 注册默认处理器
ProcessorFactory.register('default', BaseProcessor)