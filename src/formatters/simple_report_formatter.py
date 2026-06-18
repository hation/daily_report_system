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
        period = self._format_report_period(analysis_results.get("report_period"))
        if period:
            title, range_text = period
            if report_format.template == "executive":
                return f"📊 **{title}**\n📅 报告范围：{range_text}"
            return f"📊 **{title}**\n📅 报告范围：{range_text}"

        report_date = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        if report_format.template == "executive":
            return f"📊 **工作执行摘要**\n📅 {report_date}"
        return f"📊 **每日工作分析报告**\n📅 {report_date}"

    def _format_report_period(self, period: Optional[Dict[str, Any]]) -> Optional[tuple]:
        if not period:
            return None
        start_time = datetime.fromisoformat(period["start_time"])
        end_time = datetime.fromisoformat(period["end_time"])
        range_text = f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
        if start_time.date() == end_time.date():
            title = f"{start_time.strftime('%Y年%m月%d日')}工作总结"
        else:
            title = f"{start_time.strftime('%Y年%m月%d日')} 至 {end_time.strftime('%Y年%m月%d日')}工作总结"
        return title, range_text

    def _format_content_summary(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        content_summary = analysis_results.get("content_summary", {})
        summary = content_summary.get("daily_summary", "今日没有收集到可分析的具体工作内容。")
        # 根据新的模板要求，将摘要转换为更自然、更流畅的描述
        if summary == "今日没有收集到可分析的具体工作内容。":
            return "🧭 **今日工作摘要**\n----------------------------------------\n今日暂无具体工作内容记录。"
        # 尝试将摘要转换为更自然的语言
        natural_summary = summary.replace("。", "。\n").replace("；", "；\n")
        return f"🧭 **今日工作摘要**\n----------------------------------------\n{natural_summary}"

    def _format_project_work(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        project_groups = analysis_results.get("content_summary", {}).get("project_groups", [])
        if not project_groups:
            return ""

        lines = [
            "🗂️ **按项目看**",
            "----------------------------------------"
        ]

        for group in project_groups[:4]:
            name = group.get("name", "未识别项目")
            count = group.get("count", 0)

            # 提取主要工作内容
            work_items = []
            for item in group.get("items", [])[:2]:
                title = item.get("title", "")
                if title:
                    # 简化标题，提取核心内容
                    simplified_title = self._simplify_work_title(title)
                    work_items.append(simplified_title)

            # 如果没有提取到具体工作，使用主题
            if not work_items:
                primary_topics = group.get("primary_topics", [])[:2]
                if primary_topics:
                    work_items.extend(primary_topics)
                else:
                    work_items.append("相关工作")

            # 生成自然语言描述
            work_desc = "、".join(work_items)
            lines.append(f"• **{name}**：今日主要推进{name}相关工作，完成了{work_desc}等{count}项工作，为项目发展提供了有力支持。")

        return "\n".join(lines[:2]) + "\n\n" + "\n\n".join(lines[2:])

    def _simplify_work_title(self, title: str) -> str:
        """简化工作标题，提取核心内容"""
        # 移除常见的技术术语和冗余信息
        simplifications = {
            "Trae Work CN编辑文件: ": "文件编辑",
            "Codex会话: 项目：": "项目分析",
            "项目：headroom 工作目录：": "工作目录分析",
            "模式：analysis；sandbox: read-only": "分析模式",
            "模式：change；sandbox: w": "修改模式",
            "Trae CN工作项: ": "工作记录",
            "从Trae CN收集到": "数据收集",
            "从Trae Work CN收集到": "工作记录收集",
            "从Codex收集到": "会话分析",
            "从OpenClaw收集到": "消息收集",
            "从Hermes收集到": "会话记录"
        }

        simplified = title
        for old, new in simplifications.items():
            simplified = simplified.replace(old, new)

        # 处理时间戳格式，如"[Thu 2026-06-18 10:36 GMT+8..."
        import re
        timestamp_pattern = r'\[\w+ \d{4}-\d{2}-\d{2} \d{2}:\d{2} GMT\+\d+\.\.\.'
        if re.match(timestamp_pattern, simplified):
            simplified = "时间记录"

        # 如果标题仍然太长，截断
        if len(simplified) > 30:
            simplified = simplified[:27] + "..."

        return simplified if simplified else "相关工作"

    def _format_concrete_work(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        content_summary = analysis_results.get("content_summary", {})
        human_summary_items = content_summary.get("human_summary_items", [])
        activity_groups = content_summary.get("activity_groups", [])
        if not activity_groups and not human_summary_items:
            return "📝 **按主题看**\n----------------------------------------\n今日暂无可展示的具体工作事项。"

        lines = [
            "📝 **按主题看**",
            "----------------------------------------"
        ]

        # 优先使用人工总结项
        if human_summary_items:
            for item in human_summary_items[:5]:
                group = item.get("group", "工作事项")
                summary = item.get("summary", "")
                count = item.get("count", 0)

                # 解析summary，提取关键信息
                parsed_info = self._parse_summary(summary, group, count)

                # 生成自然语言描述
                lines.append(f"• **{group}**：{parsed_info}")
        else:
            # 使用活动组
            for group in activity_groups[:5]:
                group_name = group.get("name", "未分类工作")
                count = group.get("count", 0)

                # 提取主要工作内容
                work_items = []
                for item in group.get("items", [])[:2]:
                    title = item.get("title", "")
                    if title:
                        simplified_title = self._simplify_work_title(title)
                        work_items.append(simplified_title)

                # 生成自然语言描述
                if work_items:
                    work_desc = "、".join(work_items)
                    lines.append(f"• **{group_name}**：今日主要推进{group_name}相关工作，完成了{work_desc}等{count}项工作，为相关领域提供了有力支持。")
                else:
                    lines.append(f"• **{group_name}**：今日主要处理{group_name}相关工作，完成了{count}项具体工作，为项目发展提供了支持。")

        return "\n".join(lines[:2]) + "\n\n" + "\n\n".join(lines[2:])

    def _parse_summary(self, summary: str, group: str, count: int) -> str:
        """解析summary，生成自然语言描述"""
        if not summary:
            return f"今日主要推进{group}相关工作，完成了{count}项具体工作，为项目发展奠定了基础。"

        import re

        # 尝试解析常见格式
        # 格式1: "处理XXX相关工作，共 X 项，重点是YYY"
        pattern1 = r'^处理([^，]+)相关工作，共 (\d+) 项，重点是([^。]+)'
        match1 = re.search(pattern1, summary)
        if match1:
            purpose = match1.group(1)
            item_count = match1.group(2)
            key_points = match1.group(3)
            # 简化key_points
            key_points = self._simplify_key_points(key_points)
            return f"今日主要进行{purpose}相关工作，重点完成了{key_points}等{item_count}项工作，为相关领域提供了支持。"

        # 格式2: "推进XXX，共 X 项，重点是YYY"
        pattern2 = r'^推进([^，]+)，共 (\d+) 项，重点是([^。]+)'
        match2 = re.search(pattern2, summary)
        if match2:
            purpose = match2.group(1)
            item_count = match2.group(2)
            key_points = match2.group(3)
            key_points = self._simplify_key_points(key_points)
            return f"今日主要推进{purpose}，重点完成了{key_points}等{item_count}项工作，为相关领域提供了支持。"

        # 格式3: "整理XXX，共 X 项，重点是YYY"
        pattern3 = r'^整理([^，]+)，共 (\d+) 项，重点是([^。]+)'
        match3 = re.search(pattern3, summary)
        if match3:
            purpose = match3.group(1)
            item_count = match3.group(2)
            key_points = match3.group(3)
            key_points = self._simplify_key_points(key_points)
            return f"今日主要整理{purpose}，重点完成了{key_points}等{item_count}项工作，为相关领域提供了支持。"

        # 格式4: "优化XXX，共 X 项，重点是YYY"
        pattern4 = r'^优化([^，]+)，共 (\d+) 项，重点是([^。]+)'
        match4 = re.search(pattern4, summary)
        if match4:
            purpose = match4.group(1)
            item_count = match4.group(2)
            key_points = match4.group(3)
            key_points = self._simplify_key_points(key_points)
            return f"今日主要优化{purpose}，重点完成了{key_points}等{item_count}项工作，为相关领域提供了支持。"

        # 格式5: "维护XXX，共 X 项，重点是YYY"
        pattern5 = r'^维护([^，]+)，共 (\d+) 项，重点是([^。]+)'
        match5 = re.search(pattern5, summary)
        if match5:
            purpose = match5.group(1)
            item_count = match5.group(2)
            key_points = match5.group(3)
            key_points = self._simplify_key_points(key_points)
            return f"今日主要维护{purpose}，重点完成了{key_points}等{item_count}项工作，为相关领域提供了支持。"

        # 格式6: "进行XXX，共 X 项，重点是YYY"
        pattern6 = r'^进行([^，]+)，共 (\d+) 项，重点是([^。]+)'
        match6 = re.search(pattern6, summary)
        if match6:
            purpose = match6.group(1)
            item_count = match6.group(2)
            key_points = match6.group(3)
            key_points = self._simplify_key_points(key_points)
            return f"今日主要进行{purpose}，重点完成了{key_points}等{item_count}项工作，为相关领域提供了支持。"

        # 如果无法解析，检查是否包含"共 X 项，重点是"格式
        fallback_pattern = r'共 (\d+) 项，重点是([^。]+)'
        fallback_match = re.search(fallback_pattern, summary)
        if fallback_match:
            item_count = fallback_match.group(1)
            key_points = fallback_match.group(2)
            key_points = self._simplify_key_points(key_points)
            # 尝试从开头提取目的
            purpose_match = re.search(r'^([^，]+)', summary)
            purpose = purpose_match.group(1) if purpose_match else group
            return f"今日主要{purpose}，重点完成了{key_points}等{item_count}项工作，为相关领域提供了支持。"

        # 如果无法解析，使用简化版本
        simplified = self._simplify_summary(summary)
        if len(simplified) > 150:
            simplified = simplified[:147] + "..."
        # 确保有动词
        if not any(verb in simplified for verb in ["进行", "推进", "处理", "整理", "优化", "维护", "完成"]):
            return f"今日主要进行{simplified}"
        return f"今日主要{simplified}"

    def _simplify_key_points(self, key_points: str) -> str:
        """简化重点事项"""
        # 分割多个重点事项
        items = key_points.split('、')
        if len(items) > 2:
            # 只取前两个
            return f"{items[0]}、{items[1]}"
        return key_points

    def _simplify_summary(self, summary: str) -> str:
        """简化摘要，使其更自然"""
        # 移除技术术语和冗余信息
        simplifications = {
            "重点完成了": "主要完成了",
            "共": "",
            "项": "项工作",
            "，重点是": "，主要包括",
            "。": "。",
            "；": "、"
        }

        simplified = summary
        for old, new in simplifications.items():
            simplified = simplified.replace(old, new)

        # 限制长度
        if len(simplified) > 100:
            simplified = simplified[:97] + "..."

        return simplified if simplified else "相关工作"

    def _format_content_key_outputs(self, analysis_results: Dict[str, Any], report_format: ReportFormat) -> str:
        outputs = analysis_results.get("content_summary", {}).get("key_outputs", [])
        if not outputs:
            return ""

        lines = [
            "✅ **关键产出解读**",
            "----------------------------------------"
        ]

        item_lines = []
        for output in outputs:
            summary = output.get("summary") or output.get("title", "")
            title = self._simplify_output_title(summary)
            description = self._compact_text(output.get("description", ""), 120)
            title = self._build_readable_output_title(title, description)
            if self._is_low_information_output(title, description):
                continue
            project = output.get("project") or "未识别项目"
            source = output.get("source") or "unknown"
            output_type = output.get("output_type", "progress")
            type_label = self._format_output_type_label(output_type)
            detail = description if description and description != title else title
            index = len(item_lines) + 1
            item_lines.append(
                f"{index}. **{title}**\n"
                f"   - 项目：{project}\n"
                f"   - 类型：{type_label}\n"
                f"   - 来源：{source}\n"
                f"   - 说明：{detail}"
            )
            if len(item_lines) >= 5:
                break
        if not item_lines:
            return ""
        lines.extend(item_lines)

        return "\n\n".join(lines)

    def _simplify_output_title(self, title: str) -> str:
        """简化产出标题"""
        # 移除技术术语
        simplifications = {
            "Codex会话: ": "项目分析",
            "项目：headroom 工作目录：": "工作目录",
            "模式：analysis；sandbox: read-only": "分析模式",
            "模式：change；sandbox: w": "修改模式",
            "Trae Work CN编辑文件: ": "文件编辑",
            "Trae CN工作项: ": "工作记录"
        }

        simplified = title
        for old, new in simplifications.items():
            simplified = simplified.replace(old, new)

        # 限制长度
        if len(simplified) > 50:
            simplified = simplified[:47] + "..."

        return simplified if simplified else "相关工作"

    def _format_output_type_label(self, output_type: str) -> str:
        labels = {
            "output": "可交付产出",
            "decision": "决策/方向确认",
            "progress": "阶段性进展"
        }
        return labels.get(output_type, "工作进展")

    def _build_readable_output_title(self, title: str, description: str = "") -> str:
        compact_title = "".join(str(title or "").split())
        if len(compact_title) > 2 or not description:
            return title
        candidates = [part.strip() for part in description.replace("；", "、").split("、") if part.strip()]
        if not candidates:
            return title
        return self._compact_text("、".join(candidates[:2]), 50)

    def _is_low_information_output(self, title: str, description: str = "") -> bool:
        text = f"{title} {description}".strip()
        compact = "".join(text.split())
        if len(compact) <= 1:
            return True
        if len(compact) <= 2 and compact.isascii():
            return True
        low_value_titles = {"相关工作", "工作记录", "项目分析", "分析模式", "修改模式"}
        return title.strip() in low_value_titles and not description.strip()

    def _analyze_output_value(self, summary: str, output_type: str) -> str:
        """分析产出价值"""
        # 根据产出类型和内容推断价值
        value_mapping = {
            "output": {
                "修复": "问题修复",
                "实现": "功能实现",
                "完成": "任务完成",
                "提交": "代码提交",
                "更新": "版本更新",
                "优化": "性能优化"
            },
            "decision": {
                "确认": "方向确认",
                "决定": "方案确定",
                "规划": "方案规划",
                "设计": "架构设计",
                "评审": "方案评审"
            },
            "progress": {
                "推进": "工作推进",
                "分析": "问题分析",
                "检查": "系统检查",
                "整理": "文档整理",
                "收集": "数据收集"
            }
        }

        summary_lower = summary.lower()
        if output_type in value_mapping:
            for keyword, value in value_mapping[output_type].items():
                if keyword in summary_lower:
                    return value

        # 默认值
        default_values = {
            "output": "实际价值",
            "decision": "明确方向",
            "progress": "坚实基础"
        }

        return default_values.get(output_type, "有效支持")

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

    def _escape_table_cell(self, value: Any) -> str:
        return str(value or "").replace("|", "\\|").replace("\n", " ").strip()

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
        return "\n\n".join(lines)

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
            return f"\n---\n📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return f"\n---\n📊 统一工作记录系统 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

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