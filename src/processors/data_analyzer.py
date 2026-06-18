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
import ast

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
            "content_summary": self._analyze_work_content(work_items, cleaned_items),
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
            "content_summary": {"daily_summary": "今日没有收集到可分析的具体工作内容。", "human_summary_items": [], "activity_groups": [], "key_outputs": [], "blockers_or_notes": []},
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

    def _analyze_work_content(self, work_items: List[ProcessedWorkItem], items: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not items:
            return {"daily_summary": "今日没有收集到可分析的具体工作内容。", "human_summary_items": [], "activity_groups": [], "key_outputs": [], "blockers_or_notes": []}
        normalized_items = []
        for index, item in enumerate(items):
            source_processed = work_items[index] if index < len(work_items) else None
            original_title = self._clean_content_text(item.get('title') or item.get('summary') or item.get('content') or '')
            description = self._clean_content_text(item.get('description') or item.get('content') or '')

            # 尝试从对话式内容中提取工作目的
            transformed_title = self._extract_work_purpose(original_title, description)

            # 如果能提取到工作目的，使用转换后的标题
            if transformed_title:
                title = transformed_title
            else:
                title = original_title

            if not title and description:
                title = description[:80]
            if not title:
                continue
            if self._is_content_noise(title, description):
                continue
            source = item.get('tool') or item.get('source') or 'unknown'
            category = item.get('category') or item.get('source_type') or '工作记录'
            metadata = item.get('metadata') if isinstance(item.get('metadata'), dict) else {}
            project = self._infer_project_name(item, metadata)
            normalized_items.append({
                "title": title,
                "description": description,
                "source": source,
                "category": category,
                "project": project,
                "status": item.get('status', 'unknown'),
                "priority": item.get('priority', 'medium'),
                "duration_minutes": float(item.get('duration_minutes', 0) or 0),
                "start_time": item.get('start_time') or item.get('created_at'),
                "keywords": source_processed.keywords if source_processed else [],
                "importance_score": source_processed.importance_score if source_processed else 0.5
            })
        activity_groups = self._group_by_activity_topic(normalized_items)
        project_groups = self._group_by_project(normalized_items)
        human_summary_items = self._build_human_summary_items(activity_groups)
        key_outputs = self._extract_key_outputs(normalized_items)
        blockers_or_notes = self._extract_blockers_or_notes(normalized_items)
        daily_summary = self._build_daily_summary(activity_groups, key_outputs, blockers_or_notes, project_groups)
        return {
            "daily_summary": daily_summary,
            "human_summary_items": human_summary_items[:8],
            "activity_groups": activity_groups[:6],
            "project_groups": project_groups[:5],
            "key_outputs": key_outputs[:6],
            "blockers_or_notes": blockers_or_notes[:5]
        }

    def _group_by_activity_topic(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return []
        buckets: Dict[str, List[Dict[str, Any]]] = {}
        topic_order: List[str] = []
        for item in items:
            topic = self._pick_activity_topic(item)
            if topic not in buckets:
                buckets[topic] = []
                topic_order.append(topic)
            buckets[topic].append(item)
        activity_groups = []
        for topic in topic_order:
            group_items = sorted(buckets[topic], key=lambda value: (value.get('importance_score', 0) or 0, value.get('duration_minutes', 0) or 0), reverse=True)
            activity_groups.append({
                "name": topic,
                "count": len(group_items),
                "total_duration_minutes": round(sum(value.get('duration_minutes', 0) for value in group_items), 2),
                "items": group_items[:5]
            })
        activity_groups.sort(key=lambda group: (group['count'], group['total_duration_minutes']), reverse=True)
        return activity_groups

    def _group_by_project(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        buckets: Dict[str, List[Dict[str, Any]]] = {}
        for item in items:
            project = item.get('project') or '未识别项目'
            buckets.setdefault(project, []).append(item)
        project_groups = []
        for project, project_items in buckets.items():
            sorted_items = sorted(project_items, key=lambda value: (value.get('importance_score', 0) or 0, value.get('duration_minutes', 0) or 0), reverse=True)
            topics = Counter(self._pick_activity_topic(item) for item in sorted_items)
            project_groups.append({
                "name": project,
                "count": len(sorted_items),
                "total_duration_minutes": round(sum(value.get('duration_minutes', 0) for value in sorted_items), 2),
                "primary_topics": [topic for topic, _ in topics.most_common(3)],
                "items": sorted_items[:4]
            })
        project_groups.sort(key=lambda group: (group['count'], group['total_duration_minutes']), reverse=True)
        return project_groups

    def _infer_project_name(self, item: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        project = metadata.get('project') or item.get('project') or item.get('workspace')
        if project:
            return self._normalize_project_name(project)
        text = f"{item.get('title', '')} {item.get('description', '')} {metadata.get('file_path', '')}".lower()
        project_markers = [
            ("daily_report_system", ["daily_report_system", "日报系统", "每日工作分析报告", "飞书推送", "report_formatter", "data_analyzer"]),
            ("video_anlalyer", ["video_anlalyer", "video_analyzer", "视频分析"]),
            ("headroom", ["headroom"]),
            ("podcast", ["podcast", "播客"]),
        ]
        for project_name, markers in project_markers:
            if any(marker in text for marker in markers):
                return project_name
        return "未识别项目"

    def _normalize_project_name(self, value: Any) -> str:
        project = str(value or '').strip()
        if not project:
            return "未识别项目"
        normalized = project.split('/')[-1] if '/' in project else project
        lower = normalized.lower()
        known_projects = {
            "daily-report-system": "daily_report_system",
            "daily_report_system": "daily_report_system",
            "video-anlalyer": "video_anlalyer",
            "video_anlalyer": "video_anlalyer",
            "video-analyzer": "video_anlalyer",
            "headroom": "headroom",
        }
        for marker, display_name in known_projects.items():
            if marker in lower:
                return display_name
        if lower.startswith('-users-'):
            parts = [part for part in normalized.split('-') if part]
            return parts[-1].replace('-', '_') if parts else "未识别项目"
        return normalized.replace('-', '_')

    def _pick_activity_topic(self, item: Dict[str, Any]) -> str:
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        keywords_zh = [w for w in item.get('keywords', []) or [] if any('\u4e00' <= char <= '\u9fff' for char in w)]
        topic_rules = [
            {
                "name": "日报系统与报告优化",
                "keywords": ["日报", "daily report", "daily_report", "报告", "飞书", "lark", "feishu", "推送", "消息", "飞书消息", "report_formatter", "data_analyzer"],
                "negative_keywords": ["周报", "月报", "不是日报", "非日报", "与日报无关", "报告无关"]
            },
            {
                "name": "技术学习与研究",
                "keywords": ["学习", "研究", "调研", "资料", "教程", "课程", "论文", "源码阅读", "原理", "机制", "技术选型", "方案对比", "benchmark", "best practice", "api docs", "documentation", "how to", "what is"],
                "negative_keywords": ["修复", "fix", "bug", "提交", "部署", "上线", "发布", "合并", "测试通过", "验证通过", "实现了", "已实现", "已完成"]
            },
            {
                "name": "代码开发与问题修复",
                "keywords": ["修复", "fix", "实现", "开发", "代码", "test", "测试", "pytest", "lint", "调试", "debug", "bug", "重构", "compile", "compileall", "单测", "接口", "函数"],
                "negative_keywords": ["学习", "教程", "资料", "技术调研", "方案调研", "源码阅读", "只是了解", "只读"]
            },
            {
                "name": "文档与项目整理",
                "keywords": ["readme", "文档", "部署文档", "归档", "archive", "脚本", "script", "整理", "目录", "markdown", "md", "说明", "清单"],
                "negative_keywords": ["文档报错", "文档测试失败", "api docs", "documentation"]
            },
            {
                "name": "数据源与采集",
                "keywords": ["trae", "hermes", "openclaw", "collector", "收集", "采集", "数据源", "数据来源", "记忆", "同步", "ingest"],
                "negative_keywords": ["学习", "研究", "调研", "教程"]
            },
            {
                "name": "需求沟通与方案设计",
                "keywords": ["需求", "方案", "设计", "讨论", "计划", "优化方向", "思路", "评审", "对齐", "确认边界", "排期"],
                "negative_keywords": ["测试通过", "验证通过", "已实现", "已修复", "发布上线"]
            }
        ]
        for rule in topic_rules:
            keywords = rule.get("keywords", [])
            negative_keywords = rule.get("negative_keywords", [])
            if any(keyword in text for keyword in keywords) and not any(keyword in text for keyword in negative_keywords):
                return rule["name"]
        category = str(item.get('category') or item.get('source') or '')
        category_mapping = {
            "memory": "记忆与项目上下文",
            "conversation": "沟通与会话记录",
            "health_check": "系统健康检查",
            "file_activity": "项目文件活动",
            "ai_session": "AI 编程会话",
            "development": "代码开发与问题修复",
            "learning": "技术学习与研究",
            "research": "技术学习与研究"
        }
        if category in category_mapping:
            return category_mapping[category]
        if keywords_zh:
            best = max(keywords_zh, key=len)
            return best if len(best) >= 2 else '其他工作'
        display = category.replace('_', ' ').title() if category and category.isascii() else category
        return display or '其他工作'

    def _clean_content_text(self, value: Any) -> str:
        text = str(value or '').strip()
        text = ' '.join(text.split())
        return text[:300]

    def _is_content_noise(self, title: str, description: str) -> bool:
        text = f"{title} {description}".lower()
        title_lower = title.lower()

        # 过滤系统噪音
        noise_markers = [
            "context compaction",
            "reference only",
            "previous summary",
            "important: you are running as a scheduled cron job",
            "delivery: your final response",
            "system-reminder",
            "knowledge cutoff",
            "active task user requested",
            "active task 用户要求"
        ]
        if any(marker in text for marker in noise_markers):
            return True

        # 过滤太短的标题（只有数字和符号）
        if len(title) <= 10 and any(char.isdigit() for char in title) and "-" in title:
            return True

        # 纯粹的确认类内容（没有实际工作目的）
        pure_confirmation = [
            "确认信息",
            "确认配置",
            "确认部署",
            "确认任务",
            "确认完成",
            "确认进度",
            "确认状态"
        ]
        if title_lower in [s.lower() for s in pure_confirmation]:
            return True

        return False

    def _extract_work_purpose(self, title: str, description: str) -> Optional[str]:
        """
        从对话式内容中提取实际工作目的
        如果能提取到有意义的工作目的，返回转换后的标题；否则返回None
        """
        title_lower = title.lower()

        # 定义对话模式到工作目的的转换规则
        transform_rules = [
            # (匹配模式, 转换前缀)
            ("用户询问", "排查"),
            ("询问", "了解"),
            ("问你", "了解"),
            ("你能", "尝试"),
            ("你可以", "尝试"),
            ("是否可以", "评估"),
            ("是否能", "评估"),
            ("为什么", "分析"),
            ("为什么不", "分析"),
            ("为何", "分析"),
            ("怎么", "研究"),
            ("怎么不", "研究"),
            ("怎么样", "评估"),
            ("什么是", "学习"),
            ("什么叫", "学习"),
            ("能否", "评估"),
            ("是否", "确认"),
            ("有没有", "查找"),
            ("有什么", "梳理"),
            ("需要", "规划"),
            ("能不能", "评估"),
            ("可以不", "评估"),
            ("应该", "评估"),
            ("不应该", "评估"),
            ("是否应该", "评估"),
        ]

        # 尝试提取工作目的
        for pattern, prefix in transform_rules:
            if title_lower.startswith(pattern):
                # 提取模式后面的内容作为工作内容
                purpose = title[len(pattern):].strip()
                if purpose:
                    # 清理结尾的疑问词
                    purpose = purpose.rstrip("？").rstrip("?").rstrip("。").rstrip(".")
                    return f"{prefix}{purpose}"

        # 简单命令转换
        simple_action_map = {
            "继续之前的任务": "继续执行任务",
            "执行命令": "执行系统命令",
            "帮助推送代码": "协助代码推送",
            "将代码推送到线上": "代码推送上线",
            "用户表示要尝试执行某项操作": "准备执行操作",
            "用户表示先开始操作": "启动任务执行",
            "开始操作": "启动任务执行",
            "开始工作": "启动工作项",
            "开始任务": "启动任务",
        }

        if title_lower in simple_action_map:
            return simple_action_map[title_lower]

        return None

    def _infer_activity_group(self, item: Dict[str, Any]) -> str:
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        rules = [
            ("日报系统与报告优化", ["日报", "report", "daily", "报告", "飞书", "lark", "feishu", "推送"]),
            ("代码开发与问题修复", ["修复", "fix", "实现", "开发", "代码", "test", "测试", "pytest", "lint"]),
            ("文档与项目整理", ["readme", "文档", "部署", "归档", "archive", "脚本", "script"]),
            ("数据源与采集", ["trae", "hermes", "openclaw", "collector", "收集", "采集", "数据源"]),
            ("需求沟通与方案设计", ["需求", "方案", "设计", "讨论", "计划", "优化", "有没有", "看看", "继续", "可以"])
        ]
        for group_name, keywords in rules:
            if any(keyword in text for keyword in keywords):
                return group_name
        category = str(item.get('category') or item.get('source') or '其他工作')
        category_mapping = {
            "memory": "记忆与项目上下文",
            "conversation": "沟通与会话记录",
            "health_check": "系统健康检查",
            "file_activity": "项目文件活动",
            "ai_session": "AI 编程会话",
            "development": "代码开发与问题修复"
        }
        if category in category_mapping:
            return category_mapping[category]
        return category.replace('_', ' ').title() if category.isascii() else category

    def _build_human_summary_items(self, activity_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        summary_items = []
        for group in activity_groups[:6]:
            group_name = group.get('name', '其他工作')
            item_summaries = []
            seen = set()
            for item in group.get('items', [])[:4]:
                summary = self._summarize_item_for_human(item)
                if not summary:
                    continue
                dedup_key = summary[:36]
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)
                item_summaries.append(summary)
            if item_summaries:
                details = item_summaries[:2]
                summary_items.append({
                    "group": group_name,
                    "summary": self._merge_group_summary(group_name, details, group.get('count', len(details))),
                    "details": details,
                    "count": group.get('count', len(details))
                })
        return summary_items

    def _summarize_item_for_human(self, item: Dict[str, Any]) -> str:
        raw_title = item.get('title', '')
        title = self._normalize_human_sentence(raw_title)
        description = self._normalize_human_sentence(item.get('description', ''))
        if 'trae cn项目文件更新' in title.lower():
            filename = raw_title.split(':', 1)[-1].strip() if ':' in raw_title else raw_title
            filename = self._compact_text_for_summary(filename)
            return f"更新项目上下文文件 {filename}" if filename else "更新项目上下文文件"
        if 'hermes记忆系统健康检查' in title.lower() or 'hermes' == title.lower():
            return "检查 Hermes 记忆系统运行状态"
        if title:
            compact_title = ''.join(title.split())
            if len(compact_title) <= 2 and description:
                return self._derive_summary_from_description(description)
            return self._compact_sentence(title, 250)
        return self._compact_sentence(description, 250)

    def _derive_summary_from_description(self, description: str) -> str:
        parts = [part.strip() for part in description.replace('；', '、').split('、') if part.strip()]
        if parts:
            return self._compact_sentence('、'.join(parts[:2]), 120)
        return self._compact_sentence(description, 120)

    def _normalize_human_sentence(self, value: Any) -> str:
        text = self._clean_content_text(value)
        if not text:
            return ""
        if text.startswith('[') and ']' in text:
            parsed = self._parse_list_like_text(text)
            if parsed:
                return '、'.join(parsed[:4])
        text = text.replace(" | ", "；")
        text = text.replace("['", "").replace("']", "")
        text = text.replace("', '", "、")
        return self._compact_sentence(text, 180)

    def _parse_list_like_text(self, text: str) -> List[str]:
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except (ValueError, SyntaxError):
            return []
        return []

    def _compact_sentence(self, text: str, max_length: int) -> str:
        text = ' '.join(str(text or '').split())
        if len(text) > max_length:
            return text[:max_length - 1] + '…'
        return text

    def _compact_text_for_summary(self, text: str) -> str:
        text = ' '.join(str(text or '').split())
        return text[:100]

    def _merge_group_summary(self, group_name: str, item_summaries: List[str], total_count: int = 0) -> str:
        cleaned = [self._compact_sentence(s.strip().rstrip('。.'), 64) for s in item_summaries if s and s.strip()]
        if not cleaned:
            return ""
        action_map = {
            "日报系统与报告优化": "优化日报系统与报告展示",
            "文档与项目整理": "整理项目文档和上下文资产",
            "数据源与采集": "维护数据源与采集链路",
            "代码开发与问题修复": "推进代码开发和问题修复",
            "需求沟通与方案设计": "梳理需求、方案和后续计划",
            "系统健康检查": "检查系统健康状态",
            "记忆与项目上下文": "更新项目记忆与上下文",
            "项目文件活动": "整理项目文件变更",
            "沟通与会话记录": "沉淀沟通和会话记录",
            "AI 编程会话": "使用 AI 编程工具推进问题诊断和开发"
        }
        action = action_map.get(group_name, f"处理{group_name}相关工作")
        count_text = f"，共 {total_count} 项" if total_count and total_count > len(cleaned) else ""
        details = '；'.join(cleaned[:2])
        return self._compact_sentence(f"{action}{count_text}，重点是{details}。", 150)

    def _extract_key_outputs(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        outputs = []
        seen_titles = set()
        output_keyword_groups = {
            "output": ["完成", "实现", "修复", "提交", "生成", "新增", "更新", "归档", "部署", "发布", "上线", "交付", "合并", "验证通过", "测试通过", "产出", "落地", "completed", "fixed", "added", "updated", "merged", "released", "deployed", "success"],
            "decision": ["决定", "确认", "明确", "敲定", "选定", "采用", "不采用", "批准", "定稿", "评审通过", "达成一致", "decision", "decided", "confirmed", "approved"],
            "progress": ["推进", "进行", "梳理", "分析", "排查", "定位", "验证", "测试", "整理", "补充", "优化", "迭代", "研究", "调研", "review", "debug", "investigate", "progress"]
        }
        for item in items:
            text = f"{item.get('title', '')} {item.get('description', '')}".lower()
            output_type, matched_keywords = self._classify_output_type(text, output_keyword_groups)
            significance = self._score_output_significance(item, output_type, matched_keywords)
            if item.get('priority') == 'high' or output_type or significance >= 0.62:
                summary = self._summarize_item_for_human(item)
                description = self._normalize_human_sentence(item.get('description', ''))
                if self._is_low_information_summary(summary, description):
                    continue
                dedup_key = (summary or item.get('title', ''))[:40]
                if dedup_key in seen_titles:
                    continue
                seen_titles.add(dedup_key)
                outputs.append({
                    "title": item.get('title', ''),
                    "summary": self._compact_sentence(summary or item.get('title', ''), 250),
                    "source": item.get('source', 'unknown'),
                    "project": item.get('project', '未识别项目'),
                    "description": self._normalize_human_sentence(item.get('description', ''))[:120],
                    "output_type": output_type or "progress",
                    "significance": significance
                })
        outputs.sort(key=lambda output: output.get('significance', 0), reverse=True)
        return outputs

    def _is_low_information_summary(self, summary: str, description: str = "") -> bool:
        text = f"{summary or ''} {description or ''}".strip()
        compact = ''.join(text.split())
        if len(compact) <= 1:
            return True
        if len(compact) <= 2 and compact.isascii():
            return True
        low_value_summaries = {"相关工作", "工作记录", "项目分析", "分析模式", "修改模式"}
        return str(summary or '').strip() in low_value_summaries and not str(description or '').strip()

    def _classify_output_type(self, text: str, keyword_groups: Dict[str, List[str]]) -> Tuple[Optional[str], List[str]]:
        matched_by_type = {
            output_type: [keyword for keyword in keywords if keyword in text]
            for output_type, keywords in keyword_groups.items()
        }
        priority_order = ["decision", "output", "progress"]
        for output_type in priority_order:
            if matched_by_type.get(output_type):
                return output_type, matched_by_type[output_type]
        return None, []

    def _score_output_significance(self, item: Dict[str, Any], output_type: Optional[str], matched_keywords: List[str]) -> float:
        score = float(item.get('importance_score', 0.5) or 0.5) * 0.45
        priority = item.get('priority')
        if priority == 'high':
            score += 0.18
        elif priority == 'medium':
            score += 0.08
        status = str(item.get('status', '')).lower()
        if status in ('completed', 'done', 'closed', 'resolved', 'success', 'succeeded'):
            score += 0.12
        type_weights = {"decision": 0.2, "output": 0.22, "progress": 0.12}
        score += type_weights.get(output_type or '', 0)
        score += min(len(matched_keywords), 4) * 0.035
        duration = float(item.get('duration_minutes', 0) or 0)
        if duration >= 120:
            score += 0.08
        elif duration >= 45:
            score += 0.04
        if item.get('project') and item.get('project') != '未识别项目':
            score += 0.04
        return round(max(0.0, min(score, 1.0)), 2)

    def _extract_blockers_or_notes(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        notes = []
        note_keywords = ["失败", "错误", "报错", "异常", "阻塞", "卡住", "风险", "问题", "无法", "不能", "超时", "为空", "缺失", "缺少", "不存在", "未找到", "待确认", "待处理", "failed", "failure", "error", "blocked", "missing", "not found", "timeout", "cannot"]
        exclude_keywords = ["已完成", "完成修复", "修复完成", "已修复", "已解决", "解决完成", "问题解决", "没有问题", "未发现问题", "无需处理", "不再阻塞", "验证通过", "测试通过", "成功", "通过", "resolved", "fixed", "passed", "success", "completed"]
        done_statuses = {'completed', 'done', 'closed', 'resolved', 'success', 'succeeded', 'passed', 'finished'}
        attention_statuses = {'failed', 'failure', 'blocked', 'error', 'pending', 'todo', 'open', 'unresolved'}
        seen_titles = set()
        for item in items:
            title = self._normalize_human_sentence(item.get('title', ''))
            description = self._normalize_human_sentence(item.get('description', ''))
            text = f"{title} {description}".lower()
            status = str(item.get('status', 'unknown') or 'unknown').lower()
            if status in done_statuses:
                continue
            if any(keyword in text for keyword in exclude_keywords):
                continue
            is_blocker_keyword = any(keyword in text for keyword in note_keywords)
            is_incomplete = status in attention_statuses
            if is_blocker_keyword or is_incomplete:
                dedup_key = title[:40]
                if not dedup_key or dedup_key in seen_titles:
                    continue
                seen_titles.add(dedup_key)
                notes.append({
                    "title": title,
                    "source": item.get('source', 'unknown'),
                    "status": status
                })
        return notes

    def _build_daily_summary(self, activity_groups: List[Dict[str, Any]], key_outputs: List[Dict[str, Any]], blockers_or_notes: List[Dict[str, Any]], project_groups: List[Dict[str, Any]] = None) -> str:
        """生成自然语言描述的每日工作总结"""
        if not activity_groups:
            return "今日没有收集到可分析的具体工作内容。"

        # 分析主要工作目的
        main_purposes = self._analyze_work_purposes(activity_groups)

        # 分析解决的问题
        solved_problems = self._analyze_solved_problems(key_outputs, activity_groups)

        # 分析实际进展
        actual_progress = self._analyze_actual_progress(key_outputs)

        # 分析阻塞事项
        blockers_analysis = self._analyze_blockers(blockers_or_notes)

        # 总结核心价值
        core_value = self._summarize_core_value(activity_groups, key_outputs)

        # 构建自然语言摘要
        summary_parts = []

        # 1. 主要目的和重点
        if main_purposes:
            summary_parts.append(f"今日工作主要{main_purposes}")

        # 2. 解决的问题
        if solved_problems:
            summary_parts.append(f"解决了{solved_problems}")

        # 3. 实际进展
        if actual_progress:
            summary_parts.append(f"取得了{actual_progress}")

        # 4. 阻塞事项
        if blockers_analysis:
            summary_parts.append(f"需要注意{blockers_analysis}")
        elif key_outputs:
            summary_parts.append("暂未发现需要特别关注的阻塞事项")

        # 5. 核心价值
        if core_value:
            summary_parts.append(f"整体来看，{core_value}")

        # 如果没有分析出具体内容，使用备选方案
        if not summary_parts:
            group_names = [group.get('name', '') for group in activity_groups[:3] if group.get('name')]
            project_text = ""
            if project_groups:
                recognized_projects = [group.get('name') for group in project_groups if group.get('name') and group.get('name') != '未识别项目']
                if recognized_projects:
                    shown_projects = '、'.join(recognized_projects[:3])
                    extra_count = len(recognized_projects) - 3
                    extra_text = f"等 {len(recognized_projects)} 个已识别项目" if extra_count > 0 else f"{len(recognized_projects)} 个已识别项目"
                    project_text = f"，覆盖 {shown_projects}（{extra_text}）"
            return f"今日主要围绕{'、'.join(group_names)}展开工作{project_text}。形成了 {len(key_outputs)} 项关键产出。"

        return "。".join(summary_parts) + "。"

    def _analyze_work_purposes(self, activity_groups: List[Dict[str, Any]]) -> str:
        """分析工作目的"""
        if not activity_groups:
            return ""

        # 主题到目的的映射
        purpose_mapping = {
            "代码开发与问题修复": "推进技术实现和问题解决",
            "文档与项目整理": "整理项目文档和优化工作流程",
            "数据源与采集": "维护数据收集和分析功能",
            "需求沟通与方案设计": "梳理需求和规划方案",
            "日报系统与报告优化": "优化报告生成和展示效果",
            "系统健康检查": "检查系统运行状态",
            "记忆与项目上下文": "更新项目记忆和上下文",
            "项目文件活动": "处理项目文件相关工作",
            "沟通与会话记录": "进行工作沟通和会话记录",
            "技术学习与研究": "进行技术学习和研究"
        }

        main_groups = [group.get('name', '') for group in activity_groups[:3] if group.get('name')]
        purposes = []
        for group in main_groups:
            if group in purpose_mapping:
                purposes.append(purpose_mapping[group])
            else:
                purposes.append(f"处理{group}相关工作")

        if len(purposes) == 1:
            return purposes[0]
        elif len(purposes) == 2:
            return f"{purposes[0]}和{purposes[1]}"
        else:
            return f"{'、'.join(purposes[:-1])}和{purposes[-1]}"

    def _analyze_solved_problems(self, key_outputs: List[Dict[str, Any]], activity_groups: List[Dict[str, Any]]) -> str:
        """分析解决的问题"""
        if not key_outputs:
            return "一些基础工作"

        # 从关键产出中提取解决的问题
        problems = []
        problem_keywords = {
            "修复": "技术问题",
            "解决": "运行问题",
            "优化": "性能问题",
            "完善": "功能缺陷",
            "更新": "版本问题",
            "检查": "系统问题",
            "规划": "设计方案",
            "实现": "功能需求",
            "确认": "需求问题"
        }

        for output in key_outputs[:3]:  # 取最重要的3个产出
            title = output.get('title', '')
            summary = output.get('summary', '')
            text = f"{title} {summary}".lower()

            for keyword, problem_type in problem_keywords.items():
                if keyword in text:
                    # 提取具体问题描述
                    problem_desc = self._extract_problem_description(text, keyword)
                    problems.append(f"{problem_desc}{problem_type}")
                    break

        if not problems:
            # 从活动组中推断
            group_names = [group.get('name', '') for group in activity_groups[:2] if group.get('name')]
            if group_names:
                return f"{'、'.join(group_names)}相关的工作问题"
            return "日常工作问题"

        if len(problems) == 1:
            return problems[0]
        elif len(problems) == 2:
            return f"{problems[0]}和{problems[1]}"
        else:
            return f"{'、'.join(problems[:-1])}和{problems[-1]}"

    def _extract_problem_description(self, text: str, keyword: str) -> str:
        """从文本中提取问题描述"""
        # 简单的提取逻辑，可以根据需要扩展
        if "端口" in text:
            return "端口"
        elif "配置" in text:
            return "配置"
        elif "功能" in text:
            return "功能"
        elif "数据" in text:
            return "数据"
        elif "系统" in text:
            return "系统"
        elif "代码" in text:
            return "代码"
        else:
            return ""

    def _analyze_actual_progress(self, key_outputs: List[Dict[str, Any]]) -> str:
        """分析实际进展"""
        if not key_outputs:
            return "一些基础进展"

        progress_types = []
        for output in key_outputs[:3]:  # 取最重要的3个产出
            output_type = output.get('output_type', 'progress')
            if output_type == 'output':
                progress_types.append("具体功能实现")
            elif output_type == 'decision':
                progress_types.append("重要决策确认")
            elif output_type == 'progress':
                progress_types.append("工作阶段推进")

        if not progress_types:
            return f"{len(key_outputs)}项工作进展"

        # 去重并统计
        type_counts = {}
        for progress_type in progress_types:
            type_counts[progress_type] = type_counts.get(progress_type, 0) + 1

        progress_parts = []
        for progress_type, count in type_counts.items():
            progress_parts.append(f"{count}项{progress_type}")

        if len(progress_parts) == 1:
            return progress_parts[0]
        elif len(progress_parts) == 2:
            return f"{progress_parts[0]}和{progress_parts[1]}"
        else:
            return f"{'、'.join(progress_parts[:-1])}和{progress_parts[-1]}"

    def _analyze_blockers(self, blockers_or_notes: List[Dict[str, Any]]) -> str:
        """分析阻塞事项"""
        if not blockers_or_notes:
            return ""

        blocker_types = []
        blocker_keywords = {
            "失败": "执行失败",
            "错误": "运行错误",
            "阻塞": "流程阻塞",
            "问题": "技术问题",
            "无法": "功能无法使用",
            "缺失": "资源缺失",
            "超时": "响应超时"
        }

        for blocker in blockers_or_notes[:2]:  # 取最重要的2个阻塞项
            title = blocker.get('title', '').lower()
            for keyword, blocker_type in blocker_keywords.items():
                if keyword in title:
                    blocker_types.append(blocker_type)
                    break

        if not blocker_types:
            return f"{len(blockers_or_notes)}个需要关注的事项"

        if len(blocker_types) == 1:
            return f"{blocker_types[0]}的问题"
        else:
            return f"{'、'.join(blocker_types[:-1])}和{blocker_types[-1]}等问题"

    def _summarize_core_value(self, activity_groups: List[Dict[str, Any]], key_outputs: List[Dict[str, Any]]) -> str:
        """总结核心价值"""
        if not activity_groups and not key_outputs:
            return "完成了日常基础工作"

        # 根据工作类型总结价值
        value_mapping = {
            "代码开发与问题修复": "为后续开发打下了坚实基础",
            "文档与项目整理": "优化了工作流程和文档质量",
            "数据源与采集": "提升了数据收集和分析能力",
            "需求沟通与方案设计": "明确了后续工作方向",
            "日报系统与报告优化": "改善了工作报告的质量和可读性",
            "技术学习与研究": "积累了新的技术知识和经验"
        }

        # 优先使用活动组的价值总结
        for group in activity_groups[:2]:
            group_name = group.get('name', '')
            if group_name in value_mapping:
                return value_mapping[group_name]

        # 如果没有匹配，根据产出类型总结
        if key_outputs:
            output_types = set()
            for output in key_outputs[:3]:
                output_type = output.get('output_type', 'progress')
                output_types.add(output_type)

            if 'output' in output_types:
                return "实现了具体功能，为项目提供了实际价值"
            elif 'decision' in output_types:
                return "明确了关键决策，为后续工作提供了方向"
            elif 'progress' in output_types:
                return "推进了工作进展，为项目发展奠定了基础"

        return "为项目发展提供了有力支持"

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
