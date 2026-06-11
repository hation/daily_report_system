#!/usr/bin/env python3
"""
简化版数据处理器测试
"""

import sys
import os

# 设置Python路径
project_root = "/Users/xingan/Documents/software/daily_report_system"
sys.path.insert(0, os.path.join(project_root, "src"))

# 直接导入
import importlib.util

# 动态导入模块
def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# 导入各个模块
base_processor = import_module_from_path(
    "base_processor", 
    os.path.join(project_root, "src/processors/base_processor.py")
)

data_cleaner = import_module_from_path(
    "data_cleaner",
    os.path.join(project_root, "src/processors/data_cleaner.py")
)

data_analyzer = import_module_from_path(
    "data_analyzer",
    os.path.join(project_root, "src/processors/data_analyzer.py")
)

processor_manager = import_module_from_path(
    "processor_manager",
    os.path.join(project_root, "src/processors/processor_manager.py")
)

print("✅ 成功导入所有处理器模块")
print(f"基础处理器: {base_processor.BaseProcessor.__name__}")
print(f"数据清洗器: {data_cleaner.DataCleaner.__name__}")
print(f"数据分析器: {data_analyzer.DataAnalyzer.__name__}")
print(f"处理器管理器: {processor_manager.ProcessorManager.__name__}")

# 测试创建实例
print("\n🧪 测试创建处理器实例...")
try:
    cleaner = data_cleaner.DataCleaner()
    print(f"✅ 成功创建数据清洗器: {cleaner.__class__.__name__}")
    
    analyzer = data_analyzer.DataAnalyzer()
    print(f"✅ 成功创建数据分析器: {analyzer.__class__.__name__}")
    
    manager = processor_manager.create_default_processor_manager()
    print(f"✅ 成功创建处理器管理器: {manager.__class__.__name__}")
    
    # 列出处理器
    processors = manager.list_processors()
    print(f"✅ 处理器管理器包含 {len(processors)} 个处理器:")
    for p in processors:
        print(f"  - {p['name']} ({p['type']})")
    
    print("\n🎉 所有测试通过！")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()