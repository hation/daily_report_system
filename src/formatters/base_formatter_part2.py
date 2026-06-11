if False:
    def _format_tool_analysis(self, analysis_results: Dict[str, Any],
                             report_format: ReportFormat) -> str:
        """格式化工具分析"""
        tool_analysis = analysis_results.get("tool_analysis", {})
        tools = tool_analysis.get("tools", {})
        
        lines = [
            "🛠️ 工具使用分析",
            "-" * 40
        ]
        
        if not tools:
            lines.append("📭 未收集到工具使用数据")
            return "\n".join(lines)
        
        # 最常用工具
        most_used_tool = tool_analysis.get("most_used_tool")
        if most_used_tool:
            tool_name, count = most_used_tool
            lines.append(f"🏆 最常用工具: {tool_name} ({count} 次)")
        
        # 最长使用工具
        longest_duration_tool = tool_analysis.get("longest_duration_tool")
        if longest_duration_tool:
            tool_name, duration = longest_duration_tool
            lines.append(f"⏱️  最长使用: {tool_name} ({duration:.1f} 分钟)")
        
        # 工具使用统计
        lines.append("\n📊 工具使用统计:")
        sorted_tools = sorted(tools.items(), key=lambda x: x[1].get("total_duration_minutes", 0), reverse=True)
        
        for tool_name, stats in sorted_tools[:5]:  # 显示前5个工具
            count = stats.get("count", 0)
            total_minutes = stats.get("total_duration_minutes", 0)
            percentage = stats.get("percentage", 0)
            
            lines.append(f"  {tool_name}:")
            lines.append(f"    📋 使用次数: {count} 次 ({percentage:.1f}%)")
            lines.append(f"    ⏱️  总时长: {total_minutes:.1f} 分钟 ({total_minutes/60:.1f} 小时)")
            
            avg_duration = stats.get("avg_duration_minutes", 0)
            if avg_duration > 0:
                lines.append(f"    📊 平均时长: {avg_duration:.1f} 分钟")
        
        # 工具多样性
        tool_diversity = tool_analysis.get("tool_diversity", 0)
        if tool_diversity > 0:
            lines.append(f"\n🎯 工具多样性: {tool_diversity:.2f}")
        
        return "\n".join(lines)
    
    def _format_category_analysis(self, analysis_results: Dict[str, Any],
                                 report_format: ReportFormat) -> str:
        """格式化分类分析"""
        category_analysis = analysis_results.get("category_analysis", {})
        categories = category_analysis.get("categories", {})
        
        lines = [
            "🏷️ 工作分类分析",
            "-" * 40
        ]
        
        if not categories:
            lines.append("📭 未收集到分类数据")
            return "\n".join(lines)
        
        # 主要分类
        primary_categories = category_analysis.get("primary_categories", [])
        if primary_categories:
            lines.append(f"🎯 主要工作分类: {', '.join(primary_categories)}")
        
        # 最常见分类
        most_common_category = category_analysis.get("most_common_category")
        if most_common_category:
            category_name, count = most_common_category
            lines.append(f"🏆 最常见分类: {category_name} ({count} 次)")
        
        # 分类统计
        lines.append("\n📊 分类分布:")
        sorted_categories = sorted(categories.items(), key=lambda x: x[1].get("count", 0), reverse=True)
        
        for category_name, stats in sorted_categories[:8]:  # 显示前8个分类
            count = stats.get("count", 0)
            percentage = stats.get("percentage", 0)
            total_minutes = stats.get("total_duration_minutes", 0)
            
            lines.append(f"  {category_name}:")
            lines.append(f"    📋 工作项数: {count} 个 ({percentage:.1f}%)")
            lines.append(f"    ⏱️  总时长: {total_minutes:.1f} 分钟")
            
            # 相关工具
            tools = stats.get("tools", [])
            if tools:
                lines.append(f"    🛠️  相关工具: {', '.join(tools[:3])}")
        
        # 分类多样性
        category_diversity = category_analysis.get("category_diversity", 0)
        total_categories = category_analysis.get("total_categories", 0)
        
        lines.append(f"\n🎯 分类多样性: {category_diversity:.2f}")
        lines.append(f"📊 总分类数: {total_categories} 个")
        
        return "\n".join(lines)
    
    def _format_priority_analysis(self, analysis_results: Dict[str, Any],
                                 report_format: ReportFormat) -> str:
        """格式化优先级分析"""
        priority_analysis = analysis_results.get("priority_analysis", {})
        priorities = priority_analysis.get("priorities", {})
        
        lines = [
            "⚡ 优先级分析",
            "-" * 40
        ]
        
        if not priorities:
            lines.append("📭 未收集到优先级数据")
            return "\n".join(lines)
        
        # 优先级分布
        lines.append("📊 优先级分布:")
        
        for priority_level in ['high', 'medium', 'low']:
            if priority_level in priorities:
                stats = priorities[priority_level]
                count = stats.get("count", 0)
                percentage = stats.get("percentage", 0)
                completion_rate = stats.get("completion_rate", 0)
                
                priority_icon = {
                    'high': '🔴',
                    'medium': '🟡', 
                    'low': '🟢'
                }.get(priority_level, '⚪')
                
                lines.append(f"  {priority_icon} {priority_level.upper()}优先级:")
                lines.append(f"    📋 任务数量: {count} 个 ({percentage:.1f}%)")
                lines.append(f"    ✅ 完成率: {completion_rate:.1f}%")
                
                total_duration = stats.get("total_duration_minutes", 0)
                if total_duration > 0:
                    lines.append(f"    ⏱️  总时长: {total_duration:.1f} 分钟")
        
        # 高优先级效率
        high_priority_efficiency = priority_analysis.get("high_priority_efficiency", 0)
        if high_priority_efficiency > 0:
            lines.append(f"\n🎯 高优先级任务效率: {high_priority_efficiency:.1f}%")
        
        # 最常见优先级
        most_common_priority = priority_analysis.get("most_common_priority")
        if most_common_priority:
            priority_name, count = most_common_priority
            lines.append(f"📈 最常见优先级: {priority_name.upper()} ({count} 个任务)")
        
        return "\n".join(lines)