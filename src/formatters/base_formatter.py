"""
报告格式化器
负责将分析结果格式化为易读的报告
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import yaml


@dataclass
class ReportFormat:
    """报告格式配置"""
    name: str
    template: str
    sections: List[str]
    style: Dict[str, Any]
    max_length: int = 5000


class BaseFormatter:
    """基础格式化器"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"formatter.{name}")
        
        # 默认报告格式
        self.default_formats = {
            "daily_summary": ReportFormat(
                name="daily_summary",
                template="daily",
                sections=["header", "overview", "time_analysis", "tool_analysis", 
                         "category_analysis", "insights", "recommendations", "footer"],
                style={"theme": "professional", "compact": True},
                max_length=3000
            ),
            "detailed_report": ReportFormat(
                name="detailed_report",
                template="detailed",
                sections=["header", "metadata", "overview", "time_analysis", 
                         "tool_analysis", "category_analysis", "priority_analysis",
                         "sentiment_analysis", "duration_analysis", "keyword_analysis",
                         "insights", "recommendations", "footer"],
                style={"theme": "detailed", "compact": False},
                max_length=8000
            ),
            "executive_summary": ReportFormat(
                name="executive_summary",
                template="executive",
                sections=["header", "key_metrics", "top_insights", 
                         "recommendations", "footer"],
                style={"theme": "executive", "compact": True},
                max_length=1500
            )
        }
    
    def format(self, analysis_results: Dict[str, Any], format_name: str = "daily_summary") -> str:
        """
        格式化分析结果为报告
        
        Args:
            analysis_results: 分析结果
            format_name: 报告格式名称
            
        Returns:
            格式化后的报告文本
        """
        self.logger.info(f"开始格式化报告，格式: {format_name}")
        
        # 获取报告格式
        report_format = self._get_format(format_name)
        
        # 构建报告
        report_parts = []
        
        for section in report_format.sections:
            try:
                section_content = self._format_section(section, analysis_results, report_format)
                if section_content:
                    report_parts.append(section_content)
            except Exception as e:
                self.logger.error(f"格式化章节 {section} 失败: {e}")
        
        # 合并报告
        report = "\n\n".join(report_parts)
        
        # 应用样式
        report = self._apply_style(report, report_format.style)
        
        # 检查长度
        if len(report) > report_format.max_length:
            self.logger.warning(f"报告过长: {len(report)} > {report_format.max_length}，进行截断")
            report = report[:report_format.max_length] + "...\n[报告已截断]"
        
        self.logger.info(f"报告格式化完成，长度: {len(report)} 字符")
        return report
    
    def _get_format(self, format_name: str) -> ReportFormat:
        """获取报告格式"""
        if format_name in self.default_formats:
            return self.default_formats[format_name]
        
        # 如果格式不存在，使用默认格式
        self.logger.warning(f"未知的报告格式: {format_name}，使用默认格式")
        return self.default_formats["daily_summary"]
    
    def _format_section(self, section: str, analysis_results: Dict[str, Any], 
                       report_format: ReportFormat) -> Optional[str]:
        """格式化单个章节"""
        section_methods = {
            "header": self._format_header,
            "metadata": self._format_metadata,
            "overview": self._format_overview,
            "time_analysis": self._format_time_analysis,
            "tool_analysis": self._format_tool_analysis,
            "category_analysis": self._format_category_analysis,
            "priority_analysis": self._format_priority_analysis,
            "sentiment_analysis": self._format_sentiment_analysis,
            "duration_analysis": self._format_duration_analysis,
            "keyword_analysis": self._format_keyword_analysis,
            "insights": self._format_insights,
            "recommendations": self._format_recommendations,
            "footer": self._format_footer,
            "key_metrics": self._format_key_metrics,
            "top_insights": self._format_top_insights
        }
        
        if section in section_methods:
            return section_methods[section](analysis_results, report_format)
        
        return None
    
    def _format_header(self, analysis_results: Dict[str, Any], 
                      report_format: ReportFormat) -> str:
        """格式化报告头部"""
        metadata = analysis_results.get("metadata", {})
        total_items = metadata.get("total_items", 0)
        analyzed_at = metadata.get("analyzed_at", datetime.now().isoformat())
        
        try:
            analyzed_dt = datetime.fromisoformat(analyzed_at.replace('Z', '+00:00'))
            date_str = analyzed_dt.strftime("%Y年%m月%d日")
            time_str = analyzed_dt.strftime("%H:%M")
        except:
            date_str = "未知日期"
            time_str = "未知时间"
        
        header_lines = [
            "=" * 60,
            f"📊 每日工作分析报告",
            f"📅 报告日期: {date_str} {time_str}",
            f"📈 分析工作项: {total_items} 个",
            "=" * 60,
            ""
        ]
        
        return "\n".join(header_lines)
    
    def _format_metadata(self, analysis_results: Dict[str, Any],
                        report_format: ReportFormat) -> str:
        """格式化元数据"""
        metadata = analysis_results.get("metadata", {})
        
        lines = [
            "📋 报告元数据",
            "-" * 40
        ]
        
        if "time_range" in metadata:
            time_range = metadata["time_range"]
            if time_range.get("start_date") and time_range.get("end_date"):
                lines.append(f"📅 时间范围: {time_range['start_date']} 至 {time_range['end_date']}")
                lines.append(f"⏱️  覆盖天数: {time_range.get('days', 0)} 天")
        
        lines.append(f"🔧 分析工具: {metadata.get('analyzer', '未知')}")
        lines.append(f"📊 数据来源: Trae CN, OpenClaw, Hermes Agent")
        
        return "\n".join(lines)
    
    def _format_overview(self, analysis_results: Dict[str, Any],
                        report_format: ReportFormat) -> str:
        """格式化概述"""
        summary_stats = analysis_results.get("summary_statistics", {})
        overall = summary_stats.get("overall", {})
        averages = summary_stats.get("averages", {})
        
        lines = [
            "📈 工作概览",
            "-" * 40
        ]
        
        # 总体统计
        total_duration_hours = overall.get("total_duration_hours", 0)
        total_items = overall.get("total_work_items", 0)
        unique_tools = overall.get("unique_tools", 0)
        unique_categories = overall.get("unique_categories", 0)
        
        lines.append(f"⏱️  总工作时长: {total_duration_hours:.1f} 小时")
        lines.append(f"📋 总工作项数: {total_items} 个")
        lines.append(f"🛠️  使用工具数: {unique_tools} 个")
        lines.append(f"🏷️  工作分类数: {unique_categories} 个")
        
        # 平均统计
        avg_duration = averages.get("avg_duration_minutes", 0)
        avg_importance = averages.get("avg_importance_score", 0)
        
        lines.append(f"📊 平均工作时长: {avg_duration:.1f} 分钟")
        lines.append(f"⭐ 平均重要性评分: {avg_importance:.2f}/1.0")
        
        # 工作效率
        work_rate = overall.get("work_rate_items_per_day", 0)
        lines.append(f"⚡ 日均工作项: {work_rate:.1f} 个/天")
        
        return "\n".join(lines)
    
    def _format_time_analysis(self, analysis_results: Dict[str, Any],
                             report_format: ReportFormat) -> str:
        """格式化时间分析"""
        time_analysis = analysis_results.get("time_analysis", {})
        
        lines = [
            "⏰ 时间分布分析",
            "-" * 40
        ]
        
        # 峰值时间
        peak_hour = time_analysis.get("peak_hour")
        if peak_hour:
            hour, count = peak_hour
            lines.append(f"🏆 最活跃时段: {hour} ({count} 个工作项)")
        
        peak_day = time_analysis.get("peak_day")
        if peak_day:
            day, count = peak_day
            lines.append(f"📅 最忙碌日期: {day} ({count} 个工作项)")
        
        # 时间覆盖
        total_hours = time_analysis.get("total_hours_covered", 0)
        total_days = time_analysis.get("total_days_covered", 0)
        
        lines.append(f"⏱️  活跃时间段: {total_hours} 小时")
        lines.append(f"📅 活跃天数: {total_days} 天")
        
        # 时间分布（简化版）
        hourly_dist = time_analysis.get("hourly", {})
        if hourly_dist:
            lines.append("\n🕐 按小时分布:")
            top_hours = sorted(hourly_dist.items(), key=lambda x: x[1], reverse=True)[:5]
            for hour, count in top_hours:
                lines.append(f"  {hour}: {count} 个工作项")
        
        return "\n".join(lines)