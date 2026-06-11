#!/usr/bin/env python3
"""
测试数据收集器
验证Trae CN、OpenClaw、Hermes收集器的功能
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.collectors import create_default_collector_manager


def test_collector_connections():
    """测试收集器连接"""
    print("🔌 测试收集器连接...")
    
    manager = create_default_collector_manager()
    results = manager.test_all_connections()
    
    print("\n📊 连接测试结果:")
    for name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {name}: {status}")
    
    return all(results.values())


def test_collector_data_collection():
    """测试数据收集"""
    print("\n📥 测试数据收集...")
    
    manager = create_default_collector_manager()
    
    # 收集今天的数据
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)  # 收集过去24小时的数据
    
    print(f"收集时间范围: {start_time} - {end_time}")
    
    try:
        results = manager.collect_all(start_time, end_time)
        
        print("\n📊 数据收集结果:")
        total_items = 0
        
        for collector_name, items in results.items():
            print(f"  {collector_name}: {len(items)} 个工作项")
            total_items += len(items)
            
            # 显示前3个工作项
            for i, item in enumerate(items[:3]):
                print(f"    {i+1}. {item.title} ({item.duration_minutes}分钟)")
        
        print(f"\n总计: {total_items} 个工作项")
        
        # 获取统计信息
        stats = manager.get_combined_statistics(results)
        print(f"\n📈 统计信息:")
        print(f"  总时长: {stats['total_duration_hours']:.1f} 小时")
        print(f"  平均时长: {stats['average_duration_minutes']:.1f} 分钟")
        
        print(f"\n🛠️  工具分布:")
        for tool, count in stats['tools'].items():
            print(f"  {tool}: {count} 项")
        
        print(f"\n📁 分类分布:")
        for category, count in stats['categories'].items():
            print(f"  {category}: {count} 项")
        
        return results
        
    except Exception as e:
        print(f"❌ 数据收集失败: {e}")
        return None


def test_data_export(results):
    """测试数据导出"""
    if not results:
        print("❌ 没有数据可以导出")
        return False
    
    print("\n💾 测试数据导出...")
    
    manager = create_default_collector_manager()
    
    # 创建测试输出目录
    test_output_dir = project_root / "data" / "test_output"
    test_output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        exported_files = manager.export_results(
            results, 
            str(test_output_dir),
            format='json'
        )
        
        print(f"✅ 导出成功，文件保存在: {test_output_dir}")
        for filepath in exported_files:
            print(f"  📄 {Path(filepath).name}")
        
        # 显示导出的文件大小
        for filepath in exported_files:
            size = Path(filepath).stat().st_size
            print(f"    {Path(filepath).name}: {size:,} 字节")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据导出失败: {e}")
        return False


def test_collector_details():
    """测试收集器详细信息"""
    print("\n🔍 测试收集器详细信息...")
    
    manager = create_default_collector_manager()
    
    print("已注册的收集器:")
    for name in manager.list_collectors():
        info = manager.get_collector_info(name)
        print(f"\n  {name}:")
        print(f"    配置路径: {info.get('config', {})}")
        print(f"    必要配置: {info.get('required_config_keys', [])}")


def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 数据收集器测试套件")
    print("=" * 60)
    
    # 测试连接
    if not test_collector_connections():
        print("\n⚠️  部分收集器连接失败，继续测试数据收集...")
    
    # 测试数据收集
    results = test_collector_data_collection()
    
    if results:
        # 测试数据导出
        test_data_export(results)
    
    # 测试收集器详细信息
    test_collector_details()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()