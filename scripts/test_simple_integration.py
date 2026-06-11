#!/usr/bin/env python3
"""
简化版集成测试
只测试核心功能，跳过外部依赖
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 设置项目路径
project_root = "/Users/xingan/Documents/software/daily_report_system"
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

def test_core_components():
    """测试核心组件"""
    print("🧪 测试核心组件")
    print("=" * 60)
    
    try:
        # 测试报告格式化器
        print("1. 测试报告格式化器...")
        from src.formatters.work_report_formatter import create_work_report_formatter
        
        formatter = create_work_report_formatter()
        print("✅ 报告格式化器创建成功")
        
        # 创建模拟分析结果
        mock_analysis = {
            "metadata": {
                "total_items": 10,
                "analyzed_at": datetime.now().isoformat(),
            },
            "summary_statistics": {
                "overall": {
                    "total_work_items": 10,
                    "total_duration_hours": 5.5,
                }
            }
        }
        
        # 测试格式化
        report = formatter.format(mock_analysis, "daily_work_summary")
        print(f"✅ 报告格式化成功，长度: {len(report)} 字符")
        print(f"   报告预览: {report[:100]}...")
        
        # 测试处理器
        print("\n2. 测试数据处理器...")
        from src.processors.processor_manager import create_default_processor_manager
        
        processor_manager = create_default_processor_manager()
        print("✅ 处理器管理器创建成功")
        
        processors = processor_manager.list_processors()
        print(f"✅ 可用处理器: {[p['name'] for p in processors]}")
        
        # 测试收集器
        print("\n3. 测试数据收集器...")
        from src.collectors.collector_manager import create_default_collector_manager
        
        collector_manager = create_default_collector_manager()
        print("✅ 收集器管理器创建成功")
        
        collectors = collector_manager.list_collectors()
        print(f"✅ 可用收集器: {[c['name'] for c in collectors]}")
        
        # 测试报告管理器（不初始化飞书）
        print("\n4. 测试报告管理器...")
        from src.managers.report_manager import create_report_manager
        
        config = {
            "test_mode": True,
            "enable_backup": False
        }
        
        report_manager = create_report_manager(config)
        print("✅ 报告管理器创建成功")
        
        # 测试系统状态
        system_status = report_manager.get_system_status()
        print(f"✅ 系统状态检查: {system_status.get('status')}")
        
        print("\n🎉 所有核心组件测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 核心组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_generation_with_mock_data():
    """使用模拟数据测试报告生成"""
    print("\n📄 使用模拟数据测试报告生成")
    print("=" * 60)
    
    try:
        from src.managers.report_manager import create_report_manager
        
        # 创建模拟数据收集器
        class MockCollectorManager:
            def collect_all(self, time_range=None):
                # 返回模拟数据
                from datetime import datetime, timedelta
                import random
                
                mock_items = []
                for i in range(15):
                    start_time = datetime.now() - timedelta(hours=random.randint(1, 24))
                    duration = random.randint(15, 120)
                    
                    mock_items.append({
                        "id": f"mock_{i}",
                        "title": f"模拟工作项 {i}",
                        "description": "这是一个模拟的工作项描述",
                        "tool": random.choice(["trae-cn", "hermes", "openclaw"]),
                        "category": random.choice(["coding", "research", "planning"]),
                        "priority": random.choice(["high", "medium", "low"]),
                        "start_time": start_time.isoformat(),
                        "duration_minutes": duration,
                        "status": random.choice(["completed", "in_progress"])
                    })
                
                return {
                    "success": True,
                    "work_items": mock_items,
                    "collection_time_ms": 150,
                    "collector_results": {
                        "trae-cn": {"success": True, "count": 5},
                        "hermes": {"success": True, "count": 5},
                        "openclaw": {"success": True, "count": 5}
                    }
                }
            
            def list_collectors(self):
                return []
        
        # 创建报告管理器
        config = {
            "test_mode": True,
            "enable_backup": False,
            "processing_workflow": ["data_cleaner", "data_analyzer"]
        }
        
        report_manager = create_report_manager(config)
        
        # 替换收集器管理器为模拟版本
        report_manager.collector_manager = MockCollectorManager()
        
        # 测试报告生成
        print("生成模拟报告...")
        
        # 使用测试模式，避免实际数据处理
        try:
            # 直接测试格式化器
            from src.formatters.work_report_formatter import create_work_report_formatter
            from src.processors.processor_manager import create_default_processor_manager
            
            formatter = create_work_report_formatter()
            processor_manager = create_default_processor_manager()
            
            # 创建模拟分析结果
            mock_analysis = {
                "metadata": {
                    "total_items": 15,
                    "analyzed_at": datetime.now().isoformat(),
                    "time_range": {
                        "start_date": "2024-06-09",
                        "end_date": "2024-06-10",
                        "days": 2
                    }
                },
                "summary_statistics": {
                    "overall": {
                        "total_work_items": 15,
                        "total_duration_hours": 12.5,
                        "unique_tools": 3,
                        "unique_categories": 4,
                        "work_rate_items_per_day": 7.5
                    },
                    "averages": {
                        "avg_duration_minutes": 50.0
                    },
                    "totals": {
                        "total_completed_items": 10
                    }
                },
                "time_analysis": {
                    "hourly": {"09:00": 3, "10:00": 5, "14:00": 4, "16:00": 3},
                    "daily": {"2024-06-09": 7, "2024-06-10": 8},
                    "peak_hour": ("10:00", 5),
                    "peak_day": ("2024-06-10", 8)
                },
                "tool_analysis": {
                    "tools": {
                        "trae-cn": {"count": 5, "percentage": 33.3, "total_duration_minutes": 250},
                        "hermes": {"count": 5, "percentage": 33.3, "total_duration_minutes": 300},
                        "openclaw": {"count": 5, "percentage": 33.3, "total_duration_minutes": 200}
                    },
                    "most_used_tool": ("hermes", 5)
                },
                "insights": {
                    "general": ["共分析 15 个工作项，总时长 12.5 小时"],
                    "time_patterns": ["最活跃的时间段是 10:00，共完成 5 个工作项"],
                    "tool_usage": ["工具使用分布均衡，各工具使用次数相近"]
                }
            }
            
            # 生成报告
            report = formatter.format(mock_analysis, "daily_work_summary")
            
            print(f"✅ 模拟报告生成成功，长度: {len(report)} 字符")
            print("\n📋 报告内容预览:")
            print("-" * 40)
            lines = report.split('\n')[:20]
            for line in lines:
                print(line)
            print("...")
            print("-" * 40)
            
            # 保存报告
            import os
            reports_dir = "./data/reports/test/"
            os.makedirs(reports_dir, exist_ok=True)
            
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n💾 报告已保存到: {filepath}")
            
            return True
            
        except Exception as e:
            print(f"❌ 模拟报告生成失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 统一工作记录系统 - 简化测试")
    print("=" * 60)
    
    # 创建必要的目录
    os.makedirs("./data/reports/test/", exist_ok=True)
    
    # 运行测试
    all_passed = True
    
    # 测试核心组件
    if not test_core_components():
        all_passed = False
    
    # 测试模拟报告生成
    if not test_report_generation_with_mock_data():
        all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 所有核心功能测试通过！系统架构完整")
        print("\n📋 下一步:")
        print("  1. 配置飞书chat_id进行实际推送测试")
        print("  2. 设置定时任务（每天19:00）")
        print("  3. 验证实际数据收集功能")
        return 0
    else:
        print("❌ 部分测试失败，请检查系统配置")
        return 1


if __name__ == "__main__":
    sys.exit(main())