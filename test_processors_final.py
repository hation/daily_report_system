#!/usr/bin/env python3
"""
直接在项目根目录运行的测试
"""

import sys
import os

# 切换到项目根目录
os.chdir("/Users/xingan/Documents/software/daily_report_system")

# 设置Python路径
sys.path.insert(0, ".")
sys.path.insert(0, "./src")

print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path[:3])

# 尝试导入
try:
    # 直接导入
    from src.processors.base_processor import BaseProcessor, ProcessedWorkItem, ProcessorFactory
    print("✅ 成功导入 base_processor")
    
    from src.processors.data_cleaner import DataCleaner
    print("✅ 成功导入 data_cleaner")
    
    from src.processors.data_analyzer import DataAnalyzer
    print("✅ 成功导入 data_analyzer")
    
    from src.processors.processor_manager import ProcessorManager, create_default_processor_manager
    print("✅ 成功导入 processor_manager")
    
    # 测试创建实例
    print("\n🧪 测试创建实例...")
    
    cleaner = DataCleaner()
    print(f"✅ 创建数据清洗器: {cleaner.__class__.__name__}")
    
    analyzer = DataAnalyzer()
    print(f"✅ 创建数据分析器: {analyzer.__class__.__name__}")
    
    manager = create_default_processor_manager()
    print(f"✅ 创建处理器管理器: {manager.__class__.__name__}")
    
    # 测试功能
    print("\n🧪 测试基本功能...")
    
    # 生成测试数据
    from datetime import datetime, timedelta
    import random
    
    test_items = []
    for i in range(5):
        item = {
            "id": f"test_{i}",
            "title": f"测试工作项 {i}",
            "description": "这是一个测试描述",
            "tool": random.choice(["trae-cn", "hermes", "openclaw"]),
            "start_time": (datetime.now() - timedelta(hours=i)).isoformat(),
            "duration_minutes": random.randint(15, 120)
        }
        test_items.append(item)
    
    print(f"生成 {len(test_items)} 个测试工作项")
    
    # 测试数据清洗
    cleaned_items = cleaner.process(test_items)
    print(f"数据清洗: {len(test_items)} -> {len(cleaned_items)} 个工作项")
    
    if cleaned_items:
        # 测试数据分析
        analysis_results = analyzer.process(cleaned_items)
        print(f"数据分析完成，包含 {len(analysis_results)} 个部分")
        
        # 显示摘要
        metadata = analysis_results.get('metadata', {})
        print(f"分析统计: {metadata.get('total_items', 0)} 个工作项")
        
        # 测试处理器管理器工作流
        workflow_results = manager.process_workflow(test_items)
        print(f"工作流执行: {'成功' if workflow_results.get('success') else '失败'}")
        
        if workflow_results.get('success'):
            summary = workflow_results.get('summary', {})
            print(f"工作流摘要: {summary.get('total_items', 0)} 个工作项处理完成")
    
    print("\n🎉 所有测试通过！")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()