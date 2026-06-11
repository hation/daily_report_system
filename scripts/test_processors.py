#!/usr/bin/env python3
"""
数据处理器测试脚本
测试数据清洗、分析和管理的功能
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, project_root)

from src.processors import (
    BaseProcessor,
    ProcessedWorkItem,
    ProcessorFactory,
    DataCleaner,
    DataAnalyzer,
    ProcessorManager,
    create_default_processor_manager
)


def generate_sample_work_items(count: int = 20) -> list:
    """生成示例工作项数据"""
    sample_items = []
    
    tools = ['trae-cn', 'openclaw', 'hermes', 'codex', 'trae-work-cn']
    categories = ['coding', 'research', 'planning', 'debugging', 'documentation', 'meeting']
    priorities = ['high', 'medium', 'low']
    statuses = ['completed', 'in_progress', 'pending', 'cancelled']
    
    for i in range(count):
        # 随机生成时间
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        start_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        duration = random.randint(15, 180)  # 15-180分钟
        
        item = {
            "id": f"item_{i+1:03d}",
            "title": f"测试工作项 {i+1}",
            "description": f"这是第 {i+1} 个测试工作项的详细描述，包含一些关键词如：代码、测试、分析等。",
            "tool": random.choice(tools),
            "category": random.choice(categories),
            "priority": random.choice(priorities),
            "status": random.choice(statuses),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(minutes=duration)).isoformat(),
            "duration_minutes": duration,
            "tags": [f"标签{i+1}", "测试", "示例"],
            "importance": random.uniform(0.3, 0.9),
            "created_at": start_time.isoformat(),
            "updated_at": (start_time + timedelta(minutes=random.randint(0, duration))).isoformat()
        }
        
        # 添加一些重复项用于测试去重
        if i % 5 == 0 and i > 0:
            item["title"] = f"重复工作项 {i//5}"
        
        sample_items.append(item)
    
    return sample_items


def test_base_processor():
    """测试基础处理器"""
    print("🧪 测试基础处理器...")
    
    processor = BaseProcessor(name="test_processor")
    
    # 测试文本清理
    test_text = "  这是一段 测试  文本，包含多余空格 和特殊字符！@#$%^&*()  "
    cleaned_text = processor._clean_text(test_text)
    print(f"  文本清理: '{test_text[:30]}...' -> '{cleaned_text[:30]}...'")
    
    # 测试时间标准化
    test_time = "2024-06-10T14:30:00"
    normalized_time = processor._normalize_time(test_time)
    print(f"  时间标准化: '{test_time}' -> '{normalized_time}'")
    
    # 测试分类
    test_item = {
        "title": "修复代码bug",
        "description": "修复Python代码中的错误",
        "tool": "hermes",
        "priority": "high",
        "status": "completed",
        "duration_minutes": 45
    }
    categories = processor._categorize_item(test_item)
    print(f"  分类测试: {categories}")
    
    # 测试关键词提取
    keywords = processor._extract_keywords(test_item)
    print(f"  关键词提取: {keywords}")
    
    # 测试情感分析
    sentiment = processor._analyze_sentiment(test_item)
    print(f"  情感分析: {sentiment}")
    
    # 测试重要性评分
    importance = processor._calculate_importance(test_item, categories)
    print(f"  重要性评分: {importance:.2f}")
    
    print("✅ 基础处理器测试完成\n")


def test_data_cleaner():
    """测试数据清洗器"""
    print("🧪 测试数据清洗器...")
    
    # 生成测试数据
    sample_items = generate_sample_work_items(15)
    print(f"  生成 {len(sample_items)} 个测试工作项")
    
    # 创建数据清洗器
    cleaner_config = {
        "min_duration": 5,
        "max_duration": 240,
        "remove_duplicates": True,
        "normalize_timestamps": True,
        "fill_missing_fields": True
    }
    cleaner = DataCleaner(config=cleaner_config)
    
    # 执行清洗
    processed_items = cleaner.process(sample_items)
    
    print(f"  清洗前: {len(sample_items)} 个工作项")
    print(f"  清洗后: {len(processed_items)} 个工作项")
    
    if processed_items:
        # 检查清洗结果
        sample_item = processed_items[0]
        print(f"  清洗示例:")
        print(f"    原始ID: {sample_item.original_item.get('id')}")
        print(f"    清洗后ID: {sample_item.cleaned_item.get('id')}")
        print(f"    分类: {sample_item.categories}")
        print(f"    关键词: {sample_item.keywords}")
        print(f"    情感: {sample_item.sentiment}")
        print(f"    重要性评分: {sample_item.importance_score:.2f}")
    
    print("✅ 数据清洗器测试完成\n")


def test_data_analyzer():
    """测试数据分析器"""
    print("🧪 测试数据分析器...")
    
    # 生成测试数据
    sample_items = generate_sample_work_items(25)
    print(f"  生成 {len(sample_items)} 个测试工作项")
    
    # 创建数据清洗器
    cleaner = DataCleaner()
    cleaned_items = cleaner.process(sample_items)
    print(f"  清洗后: {len(cleaned_items)} 个工作项")
    
    if cleaned_items:
        # 创建数据分析器
        analyzer_config = {
            "time_bucket_size": 30,
            "top_n_categories": 5,
            "top_n_keywords": 10,
            "min_insight_confidence": 0.6
        }
        analyzer = DataAnalyzer(config=analyzer_config)
        
        # 执行分析
        analysis_results = analyzer.process(cleaned_items)
        
        print(f"  分析完成，包含以下部分:")
        print(f"    元数据: {analysis_results['metadata']['total_items']} 个工作项")
        print(f"    时间分析: {len(analysis_results['time_analysis']['hourly'])} 个时间段")
        print(f"    工具分析: {len(analysis_results['tool_analysis']['tools'])} 个工具")
        print(f"    分类分析: {len(analysis_results['category_analysis']['categories'])} 个分类")
        print(f"    优先级分析: {len(analysis_results['priority_analysis']['priorities'])} 个优先级")
        print(f"    情感分析: {len(analysis_results['sentiment_analysis']['sentiments'])} 种情感")
        
        # 显示洞察
        insights = analysis_results.get('insights', {})
        if insights.get('general'):
            print(f"  通用洞察: {insights['general'][0]}")
        
        if insights.get('time_patterns'):
            print(f"  时间模式: {insights['time_patterns'][0]}")
        
        if insights.get('tool_usage'):
            print(f"  工具使用: {insights['tool_usage'][0]}")
        
        # 显示汇总统计
        summary = analysis_results.get('summary_statistics', {})
        overall = summary.get('overall', {})
        print(f"  汇总统计:")
        print(f"    总时长: {overall.get('total_duration_hours', 0):.1f} 小时")
        print(f"    平均时长: {summary.get('averages', {}).get('avg_duration_minutes', 0):.1f} 分钟")
        print(f"    唯一工具: {overall.get('unique_tools', 0)} 个")
        print(f"    唯一分类: {overall.get('unique_categories', 0)} 个")
    
    print("✅ 数据分析器测试完成\n")


def test_processor_manager():
    """测试处理器管理器"""
    print("🧪 测试处理器管理器...")
    
    # 生成测试数据
    sample_items = generate_sample_work_items(30)
    print(f"  生成 {len(sample_items)} 个测试工作项")
    
    # 创建处理器管理器
    manager = create_default_processor_manager()
    
    # 列出处理器
    processors = manager.list_processors()
    print(f"  可用处理器: {[p['name'] for p in processors]}")
    
    # 执行工作流
    print("  执行工作流: data_cleaner -> data_analyzer")
    results = manager.process_workflow(sample_items)
    
    if results.get('success'):
        print(f"  工作流执行成功，耗时 {results.get('execution_time_ms', 0):.1f}ms")
        
        # 显示摘要
        summary = results.get('summary', {})
        print(f"  处理摘要:")
        print(f"    处理工作项: {summary.get('total_items', 0)} 个")
        print(f"    处理阶段: {summary.get('successful_stages', 0)}/{summary.get('processing_stages', 0)} 成功")
        
        # 显示时间范围
        time_range = summary.get('time_range', {})
        if time_range.get('start_date'):
            print(f"    时间范围: {time_range.get('start_date')} 到 {time_range.get('end_date')}")
        
        # 导出结果
        try:
            json_output = manager.export_results(results, format="json")
            print(f"  JSON输出长度: {len(json_output)} 字符")
            
            text_output = manager.export_results(results, format="text")
            print(f"  文本输出预览:")
            for line in text_output.split('\n')[:10]:
                if line.strip():
                    print(f"    {line}")
            
        except Exception as e:
            print(f"  导出结果时出错: {e}")
        
        # 获取执行历史
        history = manager.get_execution_history()
        print(f"  执行历史: {len(history)} 条记录")
    
    else:
        print(f"  工作流执行失败: {results.get('error', '未知错误')}")
    
    print("✅ 处理器管理器测试完成\n")


def test_processor_factory():
    """测试处理器工厂"""
    print("🧪 测试处理器工厂...")
    
    # 列出可用的处理器类型
    available_processors = ProcessorFactory.list_available()
    print(f"  可用处理器类型: {available_processors}")
    
    # 测试创建处理器
    for processor_type in available_processors:
        try:
            processor = ProcessorFactory.create(processor_type)
            print(f"  ✅ 成功创建处理器: {processor_type} ({processor.__class__.__name__})")
        except Exception as e:
            print(f"  ❌ 创建处理器失败 {processor_type}: {e}")
    
    # 测试自定义配置
    try:
        custom_config = {"min_duration": 10, "max_duration": 300}
        cleaner = ProcessorFactory.create("data_cleaner", config=custom_config)
        print(f"  ✅ 成功创建带配置的数据清洗器")
    except Exception as e:
        print(f"  ❌ 创建带配置的处理器失败: {e}")
    
    print("✅ 处理器工厂测试完成\n")


def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 数据处理器测试套件")
    print("=" * 60)
    
    try:
        # 测试基础处理器
        test_base_processor()
        
        # 测试数据清洗器
        test_data_cleaner()
        
        # 测试数据分析器
        test_data_analyzer()
        
        # 测试处理器工厂
        test_processor_factory()
        
        # 测试处理器管理器
        test_processor_manager()
        
        print("=" * 60)
        print("✅ 所有测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())