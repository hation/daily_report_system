if False:
    def _format_priority_analysis(self, analysis_results: Dict[str, Any],
                                 report_format: ReportFormat) -> str:
        """格式化优先级分析"""
        priority_analysis = analysis_results.get("priority_analysis", {})
        priorities = priority_analysis.get("priorities", {})
        
        lines = [
            "⚡ 任务优先级分析",
            "-" * 40
        ]
        
        if not priorities:
            lines.append("📭 未收集到优先级数据")
            return "\n".join(lines)
        
        # 优先级分布
        lines.append("📊 优先级分布:")
        
        priority_icons = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '🟢',
            'unknown': '⚪'
        }
        
        total_tasks = sum(stats.get("count", 0) for stats in priorities.values())
        
        for priority_level in ['high', 'medium', 'low']:
            if priority_level in priorities:
                stats = priorities[priority_level]
                count = stats.get("count", 0)
                percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                completion_rate = stats.get("completion_rate", 0)
                
                icon = priority_icons.get(priority_level, '⚪')
                priority_name = {
                    'high': '高优先级',
                    'medium': '中优先级',
                    'low': '低优先级'
                }.get(priority_level, priority_level)
                
                lines.append(f"  {icon} {priority_name}:")
                lines.append(f"    📋 任务数量: {count} 个 ({percentage:.1f}%)")
                lines.append(f"    ✅ 完成率: {completion_rate:.1f}%")
        
        # 高优先级效率
        high_priority_efficiency = priority_analysis.get("high_priority_efficiency", 0)
        if high_priority_efficiency > 0:
            lines.append(f"\n🎯 高优先级任务完成率: {high_priority_efficiency:.1f}%")
        
        return "\n".join(lines)
    
    def _format_duration_analysis(self, analysis_results: Dict[str, Any],
                                 report_format: ReportFormat) -> str:
        """格式化持续时间分析"""
        duration_analysis = analysis_results.get("duration_analysis", {})
        stats = duration_analysis.get("stats", {})
        
        lines = [
            "⏱️ 任务时长分析",
            "-" * 40
        ]
        
        if not stats:
            lines.append("📭 未收集到时长数据")
            return "\n".join(lines)
        
        # 基本统计
        total_minutes = stats.get("total_minutes", 0)
        total_hours = stats.get("total_hours", 0)
        avg_duration = stats.get("mean", 0)
        median_duration = stats.get("median", 0)
        
        lines.append(f"⏱️  总工作时长: {total_minutes:.0f} 分钟 ({total_hours:.1f} 小时)")
        lines.append(f"📊 平均任务时长: {avg_duration:.1f} 分钟")
        lines.append(f"📈 中位数时长: {median_duration:.1f} 分钟")
        
        # 任务分类
        short_tasks = stats.get("short_tasks", 0)
        medium_tasks = stats.get("medium_tasks", 0)
        long_tasks = stats.get("long_tasks", 0)
        total_tasks = stats.get("count", 0)
        
        if total_tasks > 0:
            lines.append("\n📋 任务时长分类:")
            lines.append(f"  🟢 短任务 (<30分钟): {short_tasks} 个 ({(short_tasks/total_tasks*100):.1f}%)")
            lines.append(f"  🟡 中任务 (30-120分钟): {medium_tasks} 个 ({(medium_tasks/total_tasks*100):.1f}%)")
            lines.append(f"  🔴 长任务 (>120分钟): {long_tasks} 个 ({(long_tasks/total_tasks*100):.1f}%)")
        
        # 效率评分
        efficiency_score = duration_analysis.get("efficiency_score", 0)
        if efficiency_score > 0:
            lines.append(f"\n⭐ 工作效率评分: {efficiency_score:.2f}/1.0")
        
        return "\n".join(lines)
    
    def _format_keyword_analysis(self, analysis_results: Dict[str, Any],
                                report_format: ReportFormat) -> str:
        """格式化关键词分析"""
        keyword_analysis = analysis_results.get("keyword_analysis", {})
        keywords = keyword_analysis.get("keywords", {})
        
        lines = [
            "🔑 工作关键词分析",
            "-" * 40
        ]
        
        if not keywords:
            lines.append("📭 未提取到关键词")
            return "\n".join(lines)
        
        # 热门关键词
        top_keywords = keyword_analysis.get("top_keywords", [])
        if top_keywords:
            lines.append("🏆 热门工作关键词:")
            for i, keyword in enumerate(top_keywords[:10], 1):
                lines.append(f"  {i}. {keyword}")
        
        # 关键词统计
        total_keywords = keyword_analysis.get("total_keyword_occurrences", 0)
        unique_keywords = keyword_analysis.get("total_unique_keywords", 0)
        avg_keywords = keyword_analysis.get("avg_keywords_per_item", 0)
        
        if total_keywords > 0:
            lines.append(f"\n📊 关键词统计:")
            lines.append(f"  📋 关键词出现次数: {total_keywords} 次")
            lines.append(f"  🎯 唯一关键词数: {unique_keywords} 个")
            lines.append(f"  📈 平均关键词/任务: {avg_keywords:.1f} 个")
        
        return "\n".join(lines)
    
    def _format_key_insights(self, analysis_results: Dict[str, Any],
                            report_format: ReportFormat) -> str:
        """格式化关键洞察"""
        insights = analysis_results.get("insights", {})
        
        lines = [
            "💡 关键工作洞察",
            "-" * 40
        ]
        
        if not insights:
            lines.append("📭 未生成工作洞察")
            return "\n".join(lines)
        
        # 通用洞察
        general_insights = insights.get("general", [])
        if general_insights:
            lines.append("📈 总体洞察:")
            for insight in general_insights[:3]:
                lines.append(f"  • {insight}")
        
        # 时间模式
        time_patterns = insights.get("time_patterns", [])
        if time_patterns:
            lines.append("\n⏰ 工作时间模式:")
            for pattern in time_patterns[:2]:
                lines.append(f"  • {pattern}")
        
        # 工具使用
        tool_usage = insights.get("tool_usage", [])
        if tool_usage:
            lines.append("\n🛠️ 工具使用模式:")
            for usage in tool_usage[:2]:
                lines.append(f"  • {usage}")
        
        # 效率洞察
        efficiency_insights = insights.get("efficiency", [])
        if efficiency_insights:
            lines.append("\n⚡ 工作效率洞察:")
            for insight in efficiency_insights[:2]:
                lines.append(f"  • {insight}")
        
        return "\n".join(lines)
    
    def _format_top_insights(self, analysis_results: Dict[str, Any],
                            report_format: ReportFormat) -> str:
        """格式化顶部洞察（用于执行摘要）"""
        insights = analysis_results.get("insights", {})
        
        lines = [
            "💡 核心工作洞察",
            "-" * 40
        ]
        
        all_insights = []
        for category in ["general", "time_patterns", "tool_usage", "efficiency"]:
            all_insights.extend(insights.get(category, []))
        
        if not all_insights:
            lines.append("📭 未生成工作洞察")
            return "\n".join(lines)
        
        # 显示最重要的3个洞察
        for i, insight in enumerate(all_insights[:3], 1):
            lines.append(f"{i}. {insight}")
        
        return "\n".join(lines)
    
    def _format_key_metrics(self, analysis_results: Dict[str, Any],
                           report_format: ReportFormat) -> str:
        """格式化关键指标（用于执行摘要）"""
        summary_stats = analysis_results.get("summary_statistics", {})
        overall = summary_stats.get("overall", {})
        averages = summary_stats.get("averages", {})
        
        lines = [
            "📊 关键工作指标",
            "-" * 40
        ]
        
        # 关键指标
        total_duration_hours = overall.get("total_duration_hours", 0)
        total_items = overall.get("total_work_items", 0)
        avg_duration = averages.get("avg_duration_minutes", 0)
        work_rate = overall.get("work_rate_items_per_day", 0)
        
        lines.append(f"⏱️  总工作时长: {total_duration_hours:.1f} 小时")
        lines.append(f"📋 总工作项数: {total_items} 个")
        lines.append(f"📊 平均任务时长: {avg_duration:.1f} 分钟")
        lines.append(f"⚡ 日均工作项: {work_rate:.1f} 个/天")
        
        # 完成率
        total_completed = summary_stats.get("totals", {}).get("total_completed_items", 0)
        if total_items > 0:
            completion_rate = (total_completed / total_items) * 100
            lines.append(f"✅ 任务完成率: {completion_rate:.1f}%")
        
        return "\n".join(lines)
    
    def _format_footer(self, analysis_results: Dict[str, Any],
                      report_format: ReportFormat) -> str:
        """格式化报告页脚"""
        metadata = analysis_results.get("metadata", {})
        analyzed_at = metadata.get("analyzed_at", datetime.now().isoformat())
        
        try:
            analyzed_dt = datetime.fromisoformat(analyzed_at.replace('Z', '+00:00'))
            generated_time = analyzed_dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            generated_time = "未知时间"
        
        footer_lines = [
            "=" * 60,
            f"📋 报告生成时间: {generated_time}",
            f"🔧 系统版本: 统一工作记录系统 v1.0",
            f"📧 如有问题，请联系系统管理员",
            "=" * 60
        ]
        
        return "\n".join(footer_lines)
    
    def _apply_style(self, report: str, style: Dict[str, Any]) -> str:
        """应用报告样式"""
        # 简化样式处理
        if style.get("compact"):
            # 压缩多余空行
            lines = report.split('\n')
            compressed_lines = []
            prev_empty = False
            
            for line in lines:
                is_empty = not line.strip()
                if not (prev_empty and is_empty):
                    compressed_lines.append(line)
                prev_empty = is_empty
            
            report = '\n'.join(compressed_lines)
        
        return report


def create_work_report_formatter() -> WorkReportFormatter:
    """创建工作报告格式化器"""
    return WorkReportFormatter()