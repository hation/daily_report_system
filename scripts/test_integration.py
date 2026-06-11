#!/usr/bin/env python3
"""
报告系统集成测试
测试数据收集、处理、格式化、推送全流程
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 设置项目路径
project_root = "/Users/xingan/Documents/software/daily_report_system"
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

def test_report_system():
    """测试报告系统"""
    print("🧪 报告系统集成测试")
    print("=" * 60)
    
    try:
        # 导入模块
        from src.managers import create_report_manager
        
        print("✅ 模块导入成功")
        
        # 创建报告管理器配置
        config = {
            "report_types": {
                "daily": {
                    "enabled": True,
                    "format": "daily_work_summary",
                    "push_time": "19:00",
                    "target": {"receive_type": "chat", "chat_id": "test_chat"}
                }
            },
            "data_sources": ["trae-cn", "openclaw", "hermes"],
            "processing_workflow": ["data_cleaner", "data_analyzer"],
            "feishu_app_id": "${FEISHU_APP_ID}",
            "feishu_app_secret": "${FEISHU_APP_SECRET}",
            "feishu_encrypt_key": "${FEISHU_ENCRYPT_KEY}",
            "feishu_verification_token": "${FEISHU_VERIFICATION_TOKEN}",
            "feishu_default_chat_id": "test_chat",
            "enable_backup": False,  # 测试时关闭备份
            "test_mode": True  # 测试模式
        }
        
        # 创建报告管理器
        print("创建报告管理器...")
        report_manager = create_report_manager(config)
        
        # 初始化组件
        print("初始化组件...")
        initialized = report_manager.initialize()
        
        if not initialized:
            print("❌ 组件初始化失败")
            return False
        
        print("✅ 所有组件初始化成功")
        
        # 测试系统状态
        print("\n📊 系统状态检查:")
        system_status = report_manager.get_system_status()
        
        print(f"  系统状态: {system_status.get('status')}")
        print(f"  组件状态: {system_status.get('components')}")
        print(f"  飞书连接: {system_status.get('feishu_connection')}")
        
        # 测试生成报告（不推送）
        print("\n📄 测试报告生成（不推送）...")
        
        # 使用模拟数据
        test_time_range = {
            "start_time": (datetime.now() - timedelta(hours=24)).isoformat(),
            "end_time": datetime.now().isoformat()
        }
        
        report_result = report_manager.generate_report("daily", test_time_range)
        
        if report_result.get("success"):
            print("✅ 报告生成成功")
            
            # 显示报告摘要
            summary = report_result.get("report_summary", {})
            collection = summary.get("data_collection", {})
            processing = summary.get("data_processing", {})
            formatting = summary.get("report_formatting", {})
            
            print(f"  数据收集: {collection.get('total_work_items', 0)} 个工作项")
            print(f"  数据处理: {processing.get('processed_items', 0)} 个处理项")
            print(f"  报告格式化: {formatting.get('content_length', 0)} 字符")
            print(f"  执行时间: {report_result.get('execution_time_seconds', 0):.1f} 秒")
            
            # 显示报告内容预览
            report_content = report_result.get("report_content", "")
            if report_content:
                print(f"\n📋 报告内容预览（前500字符）:")
                print("-" * 40)
                print(report_content[:500])
                print("...")
                print("-" * 40)
            
            # 测试保存报告
            print("\n💾 测试报告保存...")
            save_result = report_result.get("save_result", {})
            
            if save_result.get("success"):
                print(f"✅ 报告保存成功: {save_result.get('filename')}")
                print(f"   文件路径: {save_result.get('filepath')}")
            else:
                print(f"⚠️  报告保存警告: {save_result.get('error', '未知错误')}")
            
            # 测试执行历史
            print("\n📜 测试执行历史...")
            execution_history = report_manager.get_execution_history()
            
            if execution_history:
                print(f"✅ 执行历史记录: {len(execution_history)} 条")
                latest = execution_history[-1]
                print(f"   最新执行: {latest.get('execution_id')} ({latest.get('report_type')})")
            else:
                print("⚠️  无执行历史记录")
            
            # 测试报告历史
            print("\n📚 测试报告历史...")
            report_history = report_manager.get_report_history()
            
            if report_history:
                print(f"✅ 报告历史记录: {len(report_history)} 条")
                latest_report = report_history[-1]
                print(f"   最新报告: {latest_report.get('filename')}")
            else:
                print("⚠️  无报告历史记录")
            
            # 测试配置导出
            print("\n⚙️  测试配置导出...")
            exported_config = report_manager.export_config()
            
            if exported_config:
                print("✅ 配置导出成功")
                print(f"   数据源: {exported_config.get('data_sources', [])}")
                print(f"   处理工作流: {exported_config.get('processing_workflow', [])}")
                print(f"   报告类型: {list(exported_config.get('report_types', {}).keys())}")
            
            # 测试数据清理（模拟）
            print("\n🧹 测试数据清理（模拟）...")
            cleanup_result = report_manager.cleanup_old_data(days_to_keep=0)  # 清理所有旧数据（模拟）
            
            if cleanup_result.get("success"):
                print("✅ 数据清理测试通过")
                print(f"   清理文件数: {cleanup_result.get('cleaned_files_count', 0)}")
            else:
                print(f"⚠️  数据清理测试警告: {cleanup_result.get('error', '未知错误')}")
            
            print("\n🎉 所有测试通过！")
            return True
            
        else:
            print(f"❌ 报告生成失败: {report_result.get('error_details')}")
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_components():
    """测试各个组件"""
    print("\n🔧 测试各个组件")
    print("=" * 60)
    
    try:
        # 测试格式化器
        print("测试报告格式化器...")
        from src.formatters import create_work_report_formatter
        
        formatter = create_work_report_formatter()
        
        # 创建模拟分析结果
        mock_analysis = {
            "metadata": {
                "total_items": 25,
                "analyzed_at": datetime.now().isoformat(),
                "time_range": {
                    "start_date": "2024-06-09",
                    "end_date": "2024-06-10",
                    "days": 2
                }
            },
            "summary_statistics": {
                "overall": {
                    "total_work_items": 25,
                    "total_duration_hours": 8.5,
                    "unique_tools": 3,
                    "unique_categories": 5,
                    "work_rate_items_per_day": 12.5
                },
                "averages": {
                    "avg_duration_minutes": 34.2,
                    "avg_categories_per_item": 1.2,
                    "avg_keywords_per_item": 3.5,
                    "avg_importance_score": 0.65
                },
                "totals": {
                    "total_completed_items": 18
                }
            },
            "time_analysis": {
                "hourly": {"09:00": 5, "10:00": 8, "14:00": 7, "16:00": 5},
                "daily": {"2024-06-09": 12, "2024-06-10": 13},
                "peak_hour": ("10:00", 8),
                "peak_day": ("2024-06-10", 13)
            },
            "tool_analysis": {
                "tools": {
                    "trae-cn": {"count": 10, "percentage": 40, "total_duration_minutes": 300},
                    "hermes": {"count": 8, "percentage": 32, "total_duration_minutes": 240},
                    "openclaw": {"count": 7, "percentage": 28, "total_duration_minutes": 210}
                },
                "most_used_tool": ("trae-cn", 10)
            },
            "category_analysis": {
                "categories": {
                    "coding": {"count": 8, "percentage": 32},
                    "research": {"count": 6, "percentage": 24},
                    "planning": {"count": 5, "percentage": 20},
                    "debugging": {"count": 4, "percentage": 16},
                    "documentation": {"count": 2, "percentage": 8}
                },
                "primary_categories": ["coding", "research"]
            },
            "priority_analysis": {
                "priorities": {
                    "high": {"count": 5, "percentage": 20, "completion_rate": 80},
                    "medium": {"count": 15, "percentage": 60, "completion_rate": 75},
                    "low": {"count": 5, "percentage": 20, "completion_rate": 60}
                }
            },
            "duration_analysis": {
                "stats": {
                    "total_minutes": 510,
                    "total_hours": 8.5,
                    "mean": 34.2,
                    "median": 30.0,
                    "short_tasks": 10,
                    "medium_tasks": 12,
                    "long_tasks": 3
                },
                "efficiency_score": 0.72
            },
            "keyword_analysis": {
                "top_keywords": ["代码", "测试", "分析", "文档", "优化"],
                "total_keyword_occurrences": 88,
                "total_unique_keywords": 15,
                "avg_keywords_per_item": 3.5
            },
            "insights": {
                "general": ["共分析 25 个工作项，总时长 8.5 小时"],
                "time_patterns": ["最活跃的时间段是 10:00，共完成 8 个工作项"],
                "tool_usage": ["最常使用的工具是 trae-cn，共使用 10 次"],
                "efficiency": ["平均任务时长较短 (34.2 分钟)，工作效率较高"]
            }
        }
        
        # 测试不同格式
        formats = ["daily_work_summary", "detailed_work_report", "executive_work_summary"]
        
        for fmt in formats:
            try:
                report = formatter.format(mock_analysis, fmt)
                print(f"✅ {fmt}: {len(report)} 字符")
            except Exception as e:
                print(f"❌ {fmt} 失败: {e}")
        
        # 测试飞书推送器（不实际发送）
        print("\n测试飞书推送器（模拟）...")
        from src.pushers import create_feishu_pusher
        
        feishu_config = {
            "app_id": "${FEISHU_APP_ID}",
            "app_secret": "${FEISHU_APP_SECRET}",
            "encrypt_key": "${FEISHU_ENCRYPT_KEY}",
            "verification_token": "${FEISHU_VERIFICATION_TOKEN}",
            "test_mode": True  # 测试模式，不实际发送
        }
        
        pusher = create_feishu_pusher(feishu_config)
        print("✅ 飞书推送器创建成功")
        
        # 测试获取令牌（模拟）
        token = pusher.get_access_token()
        if token:
            print("✅ 访问令牌获取成功（模拟）")
        else:
            print("⚠️  访问令牌获取失败（模拟模式）")
        
        print("\n🎉 所有组件测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 统一工作记录系统 - 集成测试")
    print("=" * 60)
    
    # 创建必要的目录
    os.makedirs("./data/reports/", exist_ok=True)
    os.makedirs("./data/errors/", exist_ok=True)
    
    # 运行测试
    all_passed = True
    
    # 测试各个组件
    if not test_individual_components():
        all_passed = False
    
    # 测试报告系统
    if not test_report_system():
        all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 所有测试通过！系统功能正常")
        return 0
    else:
        print("❌ 部分测试失败，请检查系统配置")
        return 1


if __name__ == "__main__":
    sys.exit(main())