"""
数据分析处理器
负责统计分析和洞察生成
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics
import json

from .base_processor import BaseProcessor, ProcessedWorkItem


class DataAnalyzer(BaseProcessor):
    """数据分析处理器"""
    
    def __init__(self, name: str = 'data_analyzer', config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        
        # 分析配置
        self.time_bucket_size = self.config.get('time_bucket_size', 60)  # 时间分桶大小（分钟）
        self.top_n_categories = self.config.get('top_n_categories', 10)  # 显示前N个分类
        self.top_n_keywords = self.config.get('top_n_keywords', 20)      # 显示前N个关键词
        self.min_insight_confidence = self.config.get('min_insight_confidence', 0.7)
    
    def process(self, work_items: List[ProcessedWorkItem]) -> Dict[str, Any]:
        """
        分析工作项数据，生成统计报告
        
        Args:
            work_items: 处理后的工作项列表
            
        Returns:
            分析报告
        """
        self.logger.info(f"开始分析 {len(work_items)} 个工作项")
        
        if not work_items:
            return self._generate_empty_report()
        
        # 收集原始数据用于分析
        original_items = [item.original_item for item in work_items]
        cleaned_items = [item.cleaned_item for item in work_items]
        
        # 执行各项分析
        analysis_results = {
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "total_items": len(work_items),
                "time_range": self._get_time_range(cleaned_items),
                "analyzer": self.name
            },
            "time_analysis": self._analyze_time_distribution(cleaned_items),
            "tool_analysis": self._analyze_tool_usage(cleaned_items),
            "category_analysis": self._analyze_categories(work_items),
            "priority_analysis": self._analyze_priorities(cleaned_items),
            
            "duration_analysis": self._analyze_durations(cleaned_items),
            "keyword_analysis": self._analyze_keywords(work_items),
            "insights": self._generate_insights(work_items, cleaned_items),
            "summary_statistics": self._generate_summary_statistics(work_items, cleaned_items)
        }
        
        self.logger.info("分析完成")
        return analysis_results
    
    def _generate_empty_report(self) -> Dict[str, Any]:
        """生成空报告"""
        return {
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "total_items": 0,
                "time_range": {"start": None, "end": None, "days": 0},
                "analyzer": self.name,
                "note": "没有数据可分析"
            },
            "time_analysis": {"hourly": {}, "daily": {}, "weekly": {}},
            "tool_analysis": {"tools": {}, "total_by_tool": {}},
            "category_analysis": {"categories": {}, "distribution": {}},
            "priority_analysis": {"priorities": {}, "distribution": {}},
            
            "duration_analysis": {"stats": {}, "buckets": {}},
            "keyword_analysis": {"keywords": {}, "top_keywords": []},
            "insights": {"general": [], "time_patterns": [], "tool_usage": []},
            "summary_statistics": {"overall": {}, "averages": {}, "totals": {}}
        }
    
    def _get_time_range(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取时间范围"""
        if not items:
            return {"start": None, "end": None, "days": 0}
        
        start_times = []
        end_times = []
        
        for item in items:
            if 'start_time' in item and item['start_time']:
                try:
                    if isinstance(item['start_time'], str):
                        dt = datetime.fromisoformat(item['start_time'].replace('Z', '+00:00'))
                    else:
                        dt = item['start_time']
                    start_times.append(dt)
                except:
                    pass
            
            if 'end_time' in item and item['end_time']:
                try:
                    if isinstance(item['end_time'], str):
                        dt = datetime.fromisoformat(item['end_time'].replace('Z', '+00:00'))
                    else:
                        dt = item['end_time']
                    end_times.append(dt)
                except:
                    pass
        
        if not start_times:
            return {"start": None, "end": None, "days": 0}
        
        min_start = min(start_times)
        max_end = max(end_times) if end_times else min_start
        
        days = (max_end - min_start).days + 1
        
        return {
            "start": min_start.isoformat(),
            "end": max_end.isoformat(),
            "days": days,
            "start_date": min_start.date().isoformat(),
            "end_date": max_end.date().isoformat()
        }
    
    def _analyze_time_distribution(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析时间分布"""
        hourly_dist = defaultdict(int)
        daily_dist = defaultdict(int)
        weekly_dist = defaultdict(int)
        
        for item in items:
            if 'start_time' in item and item['start_time']:
                try:
                    if isinstance(item['start_time'], str):
                        dt = datetime.fromisoformat(item['start_time'].replace('Z', '+00:00'))
                    else:
                        dt = item['start_time']
                    
                    # 按小时统计
                    hour_key = f"{dt.hour:02d}:00"
                    hourly_dist[hour_key] += 1
                    
                    # 按天统计
                    day_key = dt.date().isoformat()
                    daily_dist[day_key] += 1
                    
                    # 按周统计
                    week_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
                    weekly_dist[week_key] += 1
                    
                except:
                    pass
        
        return {
            "hourly": dict(sorted(hourly_dist.items())),
            "daily": dict(sorted(daily_dist.items())),
            "weekly": dict(sorted(weekly_dist.items())),
            "peak_hour": max(hourly_dist.items(), key=lambda x: x[1]) if hourly_dist else None,
            "peak_day": max(daily_dist.items(), key=lambda x: x[1]) if daily_dist else None,
            "total_hours_covered": len(hourly_dist),
            "total_days_covered": len(daily_dist),
            "total_weeks_covered": len(weekly_dist)
        }
    
    def _analyze_tool_usage(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析工具使用情况"""
        tool_counts = Counter()
        tool_durations = defaultdict(float)
        tool_categories = defaultdict(set)
        
        for item in items:
            tool = item.get('tool', 'unknown')
            tool_counts[tool] += 1
            
            # 统计工具使用时长
            duration = item.get('duration_minutes', 0)
            tool_durations[tool] += duration
            
            # 收集工具的分类
            category = item.get('category', 'other')
            if isinstance(category, list):
                for cat in category:
                    tool_categories[tool].add(cat)
            else:
                tool_categories[tool].add(category)
        
        # 计算工具使用比例
        total_items = len(items)
        total_duration = sum(tool_durations.values())
        
        tool_usage = {}
        for tool, count in tool_counts.most_common():
            duration = tool_durations[tool]
            categories = list(tool_categories[tool])
            
            tool_usage[tool] = {
                "count": count,
                "percentage": (count / total_items * 100) if total_items > 0 else 0,
                "total_duration_minutes": duration,
                "avg_duration_minutes": duration / count if count > 0 else 0,
                "duration_percentage": (duration / total_duration * 100) if total_duration > 0 else 0,
                "categories": categories[:5],  # 最多显示5个分类
                "is_primary_tool": duration > (total_duration / len(tool_counts) * 2) if tool_counts else False
            }
        
        # 找出主要工具
        primary_tools = []
        if tool_usage:
            max_duration = max(t['total_duration_minutes'] for t in tool_usage.values())
            for tool, stats in tool_usage.items():
                if stats['total_duration_minutes'] >= max_duration * 0.7:  # 使用时长达到最高时长的70%
                    primary_tools.append(tool)
        
        return {
            "tools": tool_usage,
            "total_by_tool": dict(tool_counts),
            "primary_tools": primary_tools,
            "most_used_tool": tool_counts.most_common(1)[0] if tool_counts else None,
            "longest_duration_tool": max(tool_durations.items(), key=lambda x: x[1]) if tool_durations else None,
            "tool_diversity": len(tool_counts) / total_items if total_items > 0 else 0
        }
    
    def _analyze_categories(self, work_items: List[ProcessedWorkItem]) -> Dict[str, Any]:
        """分析分类分布"""
        category_counts = Counter()
        category_durations = defaultdict(float)
        category_tools = defaultdict(set)
        
        for item in work_items:
            categories = item.categories
            if not categories:
                categories = ['uncategorized']
            
            for category in categories:
                category_counts[category] += 1
                
                # 统计分类时长
                duration = item.cleaned_item.get('duration_minutes', 0)
                category_durations[category] += duration
                
                # 收集分类使用的工具
                tool = item.cleaned_item.get('tool', 'unknown')
                category_tools[category].add(tool)
        
        total_items = len(work_items)
        total_duration = sum(category_durations.values())
        
        category_analysis = {}
        for category, count in category_counts.most_common(self.top_n_categories):
            duration = category_durations[category]
            tools = list(category_tools[category])
            
            category_analysis[category] = {
                "count": count,
                "percentage": (count / total_items * 100) if total_items > 0 else 0,
                "total_duration_minutes": duration,
                "avg_duration_minutes": duration / count if count > 0 else 0,
                "duration_percentage": (duration / total_duration * 100) if total_duration > 0 else 0,
                "tools": tools[:5],  # 最多显示5个工具
                "is_primary_category": count > (total_items / len(category_counts) * 2) if category_counts else False
            }
        
        # 计算分类多样性
        category_diversity = len(category_counts) / total_items if total_items > 0 else 0
        
        # 找出主要分类
        primary_categories = []
        if category_analysis:
            max_count = max(c['count'] for c in category_analysis.values())
            for category, stats in category_analysis.items():
                if stats['count'] >= max_count * 0.7:  # 数量达到最高数量的70%
                    primary_categories.append(category)
        
        return {
            "categories": category_analysis,
            "distribution": dict(category_counts),
            "primary_categories": primary_categories,
            "most_common_category": category_counts.most_common(1)[0] if category_counts else None,
            "longest_duration_category": max(category_durations.items(), key=lambda x: x[1]) if category_durations else None,
            "category_diversity": category_diversity,
            "total_categories": len(category_counts)
        }
    
    def _analyze_priorities(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析优先级分布"""
        priority_counts = Counter()
        priority_durations = defaultdict(float)
        priority_completion = defaultdict(lambda: {'completed': 0, 'total': 0})
        
        for item in items:
            priority = item.get('priority', 'medium')
            priority_counts[priority] += 1
            
            # 统计优先级时长
            duration = item.get('duration_minutes', 0)
            priority_durations[priority] += duration
            
            # 统计完成情况
            status = item.get('status', 'unknown')
            if status == 'completed':
                priority_completion[priority]['completed'] += 1
            priority_completion[priority]['total'] += 1
        
        total_items = len(items)
        
        priority_analysis = {}
        for priority in ['high', 'medium', 'low', 'unknown']:
            count = priority_counts[priority]
            duration = priority_durations[priority]
            completion = priority_completion[priority]
            
            completion_rate = (completion['completed'] / completion['total'] * 100) if completion['total'] > 0 else 0
            
            priority_analysis[priority] = {
                "count": count,
                "percentage": (count / total_items * 100) if total_items > 0 else 0,
                "total_duration_minutes": duration,
                "avg_duration_minutes": duration / count if count > 0 else 0,
                "completion_rate": completion_rate,
                "completed_count": completion['completed'],
                "total_count": completion['total']
            }
        
        # 计算优先级效率
        high_priority_efficiency = 0
        if priority_analysis.get('high', {}).get('completion_rate', 0) > 0:
            high_priority_efficiency = priority_analysis['high']['completion_rate']
        
        return {
            "priorities": priority_analysis,
            "distribution": dict(priority_counts),
            "high_priority_efficiency": high_priority_efficiency,
            "most_common_priority": priority_counts.most_common(1)[0] if priority_counts else None,
            "completion_rate_by_priority": {
                p: priority_analysis[p]['completion_rate'] for p in priority_analysis
            }
        }
    
    def _analyze_durations(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析工作时长"""
        durations = [float(item.get('duration_minutes', 0) or 0) for item in items]
        if not durations:
            return {"stats": {}, "buckets": {}}
        buckets = {
            "short_0_30": sum(1 for value in durations if value < 30),
            "medium_30_120": sum(1 for value in durations if 30 <= value <= 120),
            "long_120_plus": sum(1 for value in durations if value > 120),
        }
        return {
            "stats": {
                "total_minutes": sum(durations),
                "total_hours": round(sum(durations) / 60, 2),
                "average_minutes": round(sum(durations) / len(durations), 2),
                "max_minutes": max(durations),
                "min_minutes": min(durations),
            },
            "buckets": buckets
        }
    
    def _analyze_keywords(self, work_items: List[ProcessedWorkItem]) -> Dict[str, Any]:
        """分析关键词"""
        keyword_counts = Counter()
        for item in work_items:
            keyword_counts.update(item.keywords or [])
        top_keywords = [
            {"keyword": keyword, "count": count}
            for keyword, count in keyword_counts.most_common(self.top_n_keywords)
        ]
        return {"keywords": dict(keyword_counts), "top_keywords": top_keywords}
    
    def _generate_insights(self, work_items: List[ProcessedWorkItem], items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成基础洞察"""
        insights = []
        if not items:
            return {"general": []}
        total_items = len(items)
        completed = sum(1 for item in items if item.get('status') == 'completed')
        completion_rate = completed / total_items if total_items else 0
        insights.append({"text": f"共收集并分析 {total_items} 个工作项", "confidence": 1.0})
        insights.append({"text": f"任务完成率为 {completion_rate:.0%}", "confidence": 0.8})
        tool_counts = Counter(item.get('tool', 'unknown') for item in items)
        if tool_counts:
            tool, count = tool_counts.most_common(1)[0]
            insights.append({"text": f"最常使用的数据来源是 {tool}，共 {count} 项", "confidence": 0.8})
        return {"general": insights}
    
    def _generate_summary_statistics(self, work_items: List[ProcessedWorkItem], items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成汇总统计"""
        total_items = len(items)
        total_duration_minutes = sum(float(item.get('duration_minutes', 0) or 0) for item in items)
        completed = sum(1 for item in items if item.get('status') == 'completed')
        tools = {item.get('tool', 'unknown') for item in items}
        categories = {item.get('category', 'unknown') for item in items}
        return {
            "overall": {
                "total_work_items": total_items,
                "total_duration_hours": round(total_duration_minutes / 60, 2),
                "unique_tools": len(tools),
                "unique_categories": len(categories),
                "completion_rate_percent": round(completed / total_items * 100, 2) if total_items else 0
            },
            "averages": {
                "avg_duration_minutes": round(total_duration_minutes / total_items, 2) if total_items else 0
            },
            "totals": {
                "total_duration_minutes": round(total_duration_minutes, 2),
                "completed_items": completed
            }
        }
# 注册到工厂
from .base_processor import ProcessorFactory
ProcessorFactory.register('data_analyzer', DataAnalyzer)