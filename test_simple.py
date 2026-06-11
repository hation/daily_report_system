#!/usr/bin/env python3
"""
最简单的测试 - 直接运行模块
"""

import sys
import os

# 直接执行模块
os.chdir("/Users/xingan/Documents/software/daily_report_system/src/processors")

print("当前目录:", os.getcwd())
print("目录内容:", os.listdir('.'))

# 直接导入
sys.path.insert(0, '/Users/xingan/Documents/software/daily_report_system/src')
sys.path.insert(0, '/Users/xingan/Documents/software/daily_report_system')

try:
    # 尝试导入
    import processors
    print("✅ 成功导入 processors 模块")
    
    # 检查模块内容
    print("模块内容:", dir(processors)[:10])
    
    # 尝试创建实例
    if hasattr(processors, 'DataCleaner'):
        cleaner = processors.DataCleaner()
        print(f"✅ 创建 DataCleaner: {cleaner}")
    
    if hasattr(processors, 'DataAnalyzer'):
        analyzer = processors.DataAnalyzer()
        print(f"✅ 创建 DataAnalyzer: {analyzer}")
    
    if hasattr(processors, 'create_default_processor_manager'):
        manager = processors.create_default_processor_manager()
        print(f"✅ 创建 ProcessorManager: {manager}")
        
        # 列出处理器
        processors_list = manager.list_processors()
        print(f"✅ 处理器列表: {[p['name'] for p in processors_list]}")
    
    print("\n🎉 测试成功！")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()