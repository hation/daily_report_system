"""
简化版报告格式化器
专注于工作记录分析，确保不超过飞书消息长度限制（128KB）
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
    max_length: int = 5000  # 默认限制为5000字符


class WorkReportFormatter:
    """工作报告格式化器（简化版，确保不超过飞书限制）"""
    
    def __init__(self, name: str = "work_report_formatter", config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"formatter.{name}")
        
        # 工作报告格式（简化版，优先呈现人读的工作内容）
        self.report_formats = {
            "daily_work_summary": ReportFormat(
                name="daily_work_summary",
                template="daily",
                sections=["header", "content_summary", "project_work", "concrete_work", "key_outputs", "blockers", "recommendations", "overview", "footer"],
                style={"theme": "compact", "compact": True},
                max_length=9000
            ),
            "compact_work_report": ReportFormat(
                name="compact_work_report",
                template="compact",
                sections=["header", "key_metrics", "top_activities", "footer"],
                style={"theme": "minimal", "compact": True},
                max_length=2000  # 更严格限制
            ),
            "executive_work_summary": ReportFormat(
                name="executive_work_summary",
                template="executive",
                sections=["header", "key_highlights", "recommendations", "footer"],
                style={"theme": "executive", "compact": True},
                max_length=1500  # 最严格限制
            )
        }
        
        self.logger.info(f"报告格式化器初始化完成，格式: {list(self.report_formats.keys())}")
    
    def format_report(self, analysis_results: Dict[str, Any], report_type: str = "daily_work_summary") -> str:
        """
        格式化工作报告（简化版）
        
        Args:
            analysis_results: 分析结果
            report_type: 报告类型
            
        Returns:
            格式化后的报告文本
        """
        self.logger.info(f"开始格式化报告，类型: {report_type}")
        
        # 获取报告格式配置
        if report_type not in self.report_formats:
            self.logger.warning(f"未知的报告类型: {report_type}，使用默认格式")
            report_format = self.report_formats["daily_work_summary"]
        else:
            report_format = self.report_formats[report_type]
        
        # 构建报告
        report_parts = []
        
        for section in report_format.sections:
            section_content = self._format_section(section, analysis_results, report_format)
            if section_content:
                report_parts.append(section_content)
        
        # 合并报告
        report = "\n\n".join(report_parts)
        
        # 检查长度
        report_length = len(report.encode('utf-8'))  # 字节长度
        char_length = len(report)
        
        if report_length > 120000:  # 留出8KB余量
            self.logger.warning(f"报告过长 ({report_length} 字节 > 120000)，进行截断")
            # 计算需要保留的字符数（UTF-8中文字符约3字节）
            max_chars = 120000 // 3
            report = report[:max_chars] + "\n\n...（报告过长，已截断）"
        
        self.logger.info(f"报告格式化完成，字符数: {char_length}，字节数: {report_length}")
        return report
    
    def _format_section(self, section: str, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        """格式化单个报告部分"""
        if section == "header":
            return self._format_header(analysis_results, report_format)
        elif section == "content_summary":
            return self._format_content_summary(analysis_results, report_format)
        elif section == "concrete_work":
            return self._format_concrete_work(analysis_results, report_format)
        elif section == "project_work":
            return self._format_project_work(analysis_results, report_format)
        elif section == "key_outputs":
            return self._format_content_key_outputs(analysis_results, report_format)
        elif section == "blockers":
            return self._format_blockers(analysis_results, report_format)
        elif section == "overview":
            return self._format_overview(analysis_results, report_format)
        elif section == "key_metrics":
            return self._format_key_metrics(analysis_results, report_format)
        elif section == "key_insights":
            return self._format_key_insights(analysis_results, report_format)
        elif section == "top_activities":
            return self._format_top_activities(analysis_results, report_format)
        elif section == "key_highlights":
            return self._format_key_highlights(analysis_results, report_format)
        elif section == "recommendations":
            return self._format_recommendations(analysis_results, report_format)
        elif section == "footer":
            return self._format_footer(analysis_results, report_format)
        else:
            return ""
    
    def _format_header(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        """格式化报告头部"""
        report_date = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        if report_format.template == "executive":
            return f"📊 **工作执行摘要**\n📅 {report_date}\n"
        else:
            return f"============================================================\n📊 **每日工作分析报告**\n📅 {report_date}\n============================================================"
    
    def _format_content_summary(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        content_summary = analysis_results.get("content_summary", {})
        summary = content_summary.get("daily_summary", "今日没有收集到可分析的具体工作内容。")
        return f"🧭 **今日工作摘要**\n----------------------------------------\n{summary}"
    
    def _format_project_work(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        project_groups = analysis_results.get("content_summary", {}).get("project_groups", [])
        if not project_groups:
            return ""
        text = "🗂️ **按项目看**\n----------------------------------------\n"
        for group in project_groups[:4]:
            name = group.get("name", "未识别项目")
            count = group.get("count", 0)
            topics = "、".join(group.get("primary_topics", [])[:2]) or "工作记录"
            text += f"• **{name}**：{count} 项，主要涉及{topics}\n"
            for item in group.get("items", [])[:2]:
                title = self._compact_text(item.get("title", "未命名工作"), 58)
                text += f"  - {title}\n"
        return text.rstrip()

    def _format_concrete_work(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        content_summary = analysis_results.get("content_summary", {})
        human_summary_items = content_summary.get("human_summary_items", [])
        activity_groups = content_summary.get("activity_groups", [])
        if not activity_groups and not human_summary_items:
            return "📝 **今天主要做了**\n----------------------------------------\n暂无可展示的具体工作事项。"
        text = "📝 **按主题看**\n----------------------------------------\n"
        if human_summary_items:
            for item in human_summary_items[:5]:
                group = item.get("group", "工作事项")
                summary = self._compact_text(item.get("summary", ""), 150)
                text += f"• **{group}**：{summary}\n"
            return text.rstrip()
        text += "\n📌 **原始工作记录分组**\n"
        for index, group in enumerate(activity_groups[:5], 1):
            group_name = group.get("name", "未分类工作")
            count = group.get("count", 0)
            duration = group.get("total_duration_minutes", 0)
            duration_text = f"，约 {duration / 60:.1f} 小时" if duration else ""
            text += f"{index}. **{group_name}**（{count} 项{duration_text}）\n"
            for item in group.get("items", [])[:4]:
                title = self._compact_text(item.get("title", "未命名工作"), 90)
                description = self._compact_text(item.get("description", ""), 140)
                source = item.get("source", "unknown")
                text += f"   • {title}（来源: {source}）\n"
                if description and description != title:
                    text += f"     - {description}\n"
        return text.rstrip()
    
    def _format_content_key_outputs(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        outputs = analysis_results.get("content_summary", {}).get("key_outputs", [])
        if not outputs:
            return ""
        text = "✅ **关键产出**\n----------------------------------------\n"
        for output in outputs[:5]:
            summary = self._compact_text(output.get("summary") or output.get("title", ""), 90)
            project = output.get("project") or output.get("source", "unknown")
            text += f"• {summary}（{project}）\n"
        return text.rstrip()
    
    def _format_blockers(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        notes = analysis_results.get("content_summary", {}).get("blockers_or_notes", [])
        if not notes:
            return ""
        text = "⚠️ **需要关注的事项**\n----------------------------------------\n"
        for note in notes[:4]:
            title = self._compact_text(note.get("title", ""), 100)
            source = note.get("source", "unknown")
            status = note.get("status", "unknown")
            status_text = "需留意" if status in ("completed", "done") else status
            text += f"• {title}（来源: {source}，状态: {status_text}）\n"
        return text.rstrip()
    
    def _compact_text(self, value: Any, max_length: int) -> str:
        text = str(value or "").strip()
        text = " ".join(text.split())
        if len(text) > max_length:
            return text[:max_length - 1] + "…"
        return text
    
    def _format_overview(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        """格式化工作概览（读取 summary_statistics 或 overview）"""
        overview = analysis_results.get("overview", {})
        stats = analysis_results.get("summary_statistics", {})
        overall = stats.get("overall", overview) if stats else overview
        averages = stats.get("averages", {}) if stats else {}

        total_items = overall.get("total_work_items", overview.get("total_work_items", 0))
        total_hours = overall.get("total_duration_hours", overview.get("total_duration_hours", 0))
        unique_tools = overall.get("unique_tools", overview.get("unique_tools", 0))
        categories = overall.get("unique_categories", overview.get("unique_categories", 0))
        completion_rate = overall.get("completion_rate_percent", overview.get("completion_rate_percent", 0))
        avg_minutes = averages.get("avg_duration_minutes", 0)

        lines = [
            "📈 **数据概览**",
            "----------------------------------------",
            f"📋 总工作项数: {total_items} 个",
        ]
        if total_hours:
            lines.append(f"⏱️ 总工作时长: {float(total_hours):.1f} 小时")
        if avg_minutes:
            lines.append(f"⏲️ 平均每段记录: {float(avg_minutes):.0f} 分钟")
        if completion_rate:
            lines.append(f"✅ 任务闭环率: {float(completion_rate):.1f}%")
        if unique_tools:
            lines.append(f"🛠️ 使用工具数: {unique_tools} 个")
        if categories:
            lines.append(f"🏷️ 工作分类数: {categories} 个")
        return "\n".join(lines)
    
    def _format_key_metrics(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        """格式化关键指标"""
        overview = analysis_results.get("overview", {})
        time_analysis = analysis_results.get("time_analysis", {})
        
        work_items = overview.get("total_work_items", 0)
        total_duration = overview.get("total_duration_hours", 0)
        avg_duration = overview.get("average_duration_minutes", 0)
        completion_rate = overview.get("completion_rate_percent", 0)
        
        peak_time = time_analysis.get("peak_hour", "未知")
        peak_count = time_analysis.get("peak_hour_count", 0)
        
        return f"""
📊 **关键指标**
----------------------------------------
✅ 任务完成率: {completion_rate:.1f}%
⚡ 平均工作时长: {avg_duration:.0f} 分钟
🏆 最活跃时段: {peak_time} ({peak_count} 个工作项)
📅 日均工作项: {(work_items / 1):.1f} 个/天
"""
    
    def _format_key_insights(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        """格式化关键洞察"""
        insights = analysis_results.get("key_insights", [])
        
        if not insights:
            return ""
        
        insight_text = "💡 **关键工作洞察**\n----------------------------------------\n"
        
        for i, insight in enumerate(insights[:3], 1):  # 只显示前3个洞察
            if isinstance(insight, dict):
                text = insight.get("text", "")
                confidence = insight.get("confidence", 0)
                if text:
                    insight_text += f"{i}. {text}"
                    if confidence > 0:
                        insight_text += f" (置信度: {confidence:.0%})"
                    insight_text += "\n"
            else:
                insight_text += f"{i}. {insight}\n"
        
        return insight_text
    
    def _format_top_activities(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        """格式化主要活动"""
        tool_analysis = analysis_results.get("tool_analysis", {})
        category_analysis = analysis_results.get("category_analysis", {})
        priority_analysis = analysis_results.get("priority_analysis", {})
        duration_analysis = analysis_results.get("duration_analysis", {})
        
        top_tools = tool_analysis.get("top_tools") or []
        if not top_tools and isinstance(tool_analysis.get("tools"), dict):
            top_tools = []
            for name, stats in tool_analysis["tools"].items():
                if isinstance(stats, dict):
                    count = stats.get("count", 0)
                    duration = stats.get("total_duration_hours", stats.get("total_duration_minutes", 0) / 60)
                else:
                    count = stats
                    duration = 0
                top_tools.append({"tool_name": name, "count": count, "total_duration_hours": duration})
            top_tools = sorted(top_tools, key=lambda item: item.get("count", 0), reverse=True)
        top_tools = top_tools[:3]
        
        top_categories = category_analysis.get("top_categories") or []
        if not top_categories and isinstance(category_analysis.get("categories"), dict):
            top_categories = []
            for name, stats in category_analysis["categories"].items():
                count = stats.get("count", 0) if isinstance(stats, dict) else stats
                top_categories.append({"category_name": name, "count": count})
            top_categories = sorted(top_categories, key=lambda item: item.get("count", 0), reverse=True)
        top_categories = top_categories[:3]
        
        text = "🎯 **主要活动与分布**\n----------------------------------------\n"
        
        if top_tools:
            text += "🛠️  **主要数据来源/工具**:\n"
            for tool in top_tools:
                name = tool.get("tool_name", "未知")
                count = tool.get("count", 0)
                duration = tool.get("total_duration_hours", 0)
                duration_text = f"，{duration:.1f}小时" if duration else ""
                text += f"  • {name}: {count} 项{duration_text}\n"
        
        if top_categories:
            text += "\n🏷️  **主要工作分类**:\n"
            for category in top_categories:
                name = category.get("category_name", "未知")
                count = category.get("count", 0)
                text += f"  • {name}: {count} 个工作项\n"
        
        if priority_analysis.get("distribution"):
            text += "\n🚦 **优先级分布**:\n"
            for priority, count in priority_analysis["distribution"].items():
                text += f"  • {priority}: {count} 项\n"
        
        duration_stats = duration_analysis.get("stats", {})
        if duration_stats:
            text += "\n⏳ **时长概览**:\n"
            text += f"  • 总时长: {duration_stats.get('total_hours', 0):.1f} 小时\n"
            text += f"  • 平均时长: {duration_stats.get('average_minutes', 0):.0f} 分钟\n"
        
        return text if text.strip() != "🎯 **主要活动与分布**\n----------------------------------------" else ""
    
    def _format_key_highlights(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        """格式化关键亮点（执行摘要用）"""
        overview = analysis_results.get("overview", {})
        insights = analysis_results.get("key_insights", [])
        health_status = analysis_results.get("system_health", {})
        
        work_items = overview.get("total_work_items", 0)
        total_duration = overview.get("total_duration_hours", 0)
        completion_rate = overview.get("completion_rate_percent", 0)
        
        text = "✨ **今日工作亮点**\n----------------------------------------\n"
        text += f"• 完成/记录 {work_items} 个工作项，总计 {total_duration:.1f} 小时\n"
        text += f"• 任务完成率: {completion_rate:.1f}%\n"
        
        if insights:
            for insight in insights[:2] if isinstance(insights, list) else [insights]:
                if isinstance(insight, dict):
                    insight_text = insight.get("text", "")
                    if insight_text:
                        text += f"• {insight_text}\n"
                elif insight:
                    text += f"• {insight}\n"
        
        if health_status:
            text += "\n🩺 **系统健康状态**:\n"
            text += f"  • 状态: {health_status.get('status', 'normal')}\n"
            text += f"  • 数据源成功: {health_status.get('successful_collectors', 0)} 个\n"
            text += f"  • 数据源失败: {health_status.get('failed_collectors', 0)} 个\n"
        
        return text
    
    def _format_recommendations(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        """格式化后续关注与建议"""
        stats = analysis_results.get("summary_statistics", {}) or {}
        overview = stats.get("overall", analysis_results.get("overview", {}))
        content_summary = analysis_results.get("content_summary", {}) or {}
        health_status = analysis_results.get("system_health", {}) or {}
        recommendations = []

        blockers = content_summary.get("blockers_or_notes", [])
        key_outputs = content_summary.get("key_outputs", [])

        total_items = overview.get("total_work_items", 0)
        completion_rate = overview.get("completion_rate_percent", 0)

        if total_items == 0:
            recommendations.append("📥 今日没有可分析的工作记录，建议检查数据源配置与权限")
        if blockers:
            top_titles = [self._compact_text(item.get("title", ""), 40) for item in blockers[:2] if item.get("title")]
            if top_titles:
                recommendations.append("⚠️ 后续关注：" + "、".join(top_titles))
        if completion_rate and float(completion_rate) < 70:
            recommendations.append("✅ 建议：明日优先收敛未完成事项，提升任务闭环率")
        if not key_outputs and total_items > 0:
            recommendations.append('📝 建议：可在工作记录中多写一句"完成了什么"，便于日报自动提炼')
        if health_status.get("failed_collectors", 0) > 0:
            recommendations.append("🩺 建议：优先修复失败数据源，避免日报遗漏关键信息")

        recommendations.append("📅 建议：每日 19:00 自动生成日报，复盘重点事项并为明日列 1-2 项关键目标")

        text = "💡 **后续关注与建议**\n----------------------------------------\n"
        for rec in recommendations[:4]:
            text += f"• {rec}\n"
        return text.rstrip()
    
    def _format_footer(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        """格式化报告尾部"""
        report_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if report_format.template == "executive":
            return f"\n---\n📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            return f"\n============================================================\n📊 报告生成完成 | 统一工作记录系统\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n============================================================"
    
    def get_available_formats(self) -> List[Dict[str, Any]]:
        """获取可用的报告格式"""
        formats = []
        for name, fmt in self.report_formats.items():
            formats.append({
                "name": name,
                "display_name": fmt.name,
                "sections": fmt.sections,
                "max_length": fmt.max_length,
                "style": fmt.style
            })
        return formats
    
    def validate_report_length(self, report: str, report_type: str = "daily_work_summary") -> Dict[str, Any]:
        """验证报告长度"""
        byte_length = len(report.encode('utf-8'))
        char_length = len(report)
        
        if report_type in self.report_formats:
            max_length = self.report_formats[report_type].max_length
        else:
            max_length = 5000
        
        # 飞书限制：131072字节（约128KB）
        feishu_limit = 131072
        
        return {
            "character_count": char_length,
            "byte_count": byte_length,
            "max_recommended_chars": max_length,
            "feishu_limit_bytes": feishu_limit,
            "within_feishu_limit": byte_length <= feishu_limit,
            "within_format_limit": char_length <= max_length,
            "feishu_limit_percent": (byte_length / feishu_limit) * 100 if feishu_limit > 0 else 0
        }


def create_work_report_formatter(config: Dict[str, Any] = None) -> WorkReportFormatter:
    """创建工作报告格式化器"""
    return WorkReportFormatter("work_report_formatter", config)