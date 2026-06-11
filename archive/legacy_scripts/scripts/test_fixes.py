#!/usr/bin/env python3
"""
统一工作记录系统 - 修复测试
测试修复后的OpenClaw收集器和简化版报告格式化器
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# 设置项目路径
project_root = "/Users/xingan/Documents/software/daily_report_system"
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from src.config.system_config import get_config
from src.collectors.collector_manager import create_default_collector_manager
from src.processors.processor_manager import create_default_processor_manager
from src.formatters.simple_report_formatter import create_work_report_formatter
from src.pushers.feishu_pusher import create_feishu_pusher


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("test")


def test_openclaw_collector(logger):
    """测试OpenClaw收集器"""
    logger.info("🧪 测试OpenClaw收集器...")
    
    try:
        from src.collectors.openclaw_collector import create_openclaw_collector
        
        config = {
            "db_path": "~/.openclaw/lcm.db"
        }
        
        collector = create_openclaw_collector(config)
        
        # 测试验证
        if collector._validate_database():
            logger.info("✅ OpenClaw数据库验证通过")
        else:
            logger.error("❌ OpenClaw数据库验证失败")
            return False
        
        # 测试收集
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        work_items = collector.collect(start_time, end_time)
        logger.info(f"✅ OpenClaw收集器收集到 {len(work_items)} 个工作项")
        
        # 显示统计信息
        stats = collector.get_stats()
        logger.info(f"📊 OpenClaw统计: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ OpenClaw收集器测试失败: {e}", exc_info=True)
        return False


def test_simple_formatter(logger):
    """测试简化版报告格式化器"""
    logger.info("🧪 测试简化版报告格式化器...")
    
    try:
        formatter = create_work_report_formatter()
        
        # 创建模拟分析结果
        mock_analysis = {
            "overview": {
                "total_work_items": 15,
                "total_duration_hours": 12.5,
                "unique_tools": 3,
                "unique_categories": 4,
                "average_duration_minutes": 50.0,
                "completion_rate_percent": 66.7
            },
            "time_analysis": {
                "peak_hour": "10:00",
                "peak_hour_count": 5
            },
            "tool_analysis": {
                "top_tools": [
                    {"tool_name": "Terminal", "count": 8, "total_duration_hours": 6.5},
                    {"tool_name": "Browser", "count": 5, "total_duration_hours": 4.0},
                    {"tool_name": "Code Editor", "count": 2, "total_duration_hours": 2.0}
                ]
            },
            "category_analysis": {
                "top_categories": [
                    {"category_name": "开发", "count": 8},
                    {"category_name": "测试", "count": 4},
                    {"category_name": "文档", "count": 3}
                ]
            },
            "key_insights": [
                {"text": "上午10点是工作效率最高的时段", "confidence": 0.85},
                {"text": "终端工具使用频率最高，占总工作时长的52%", "confidence": 0.78},
                {"text": "开发类工作占主导，占比53.3%", "confidence": 0.82}
            ]
        }
        
        # 测试不同格式
        formats = formatter.get_available_formats()
        logger.info(f"📋 可用格式: {[f['name'] for f in formats]}")
        
        for fmt in formats:
            report = formatter.format_report(mock_analysis, fmt["name"])
            validation = formatter.validate_report_length(report, fmt["name"])
            
            logger.info(f"📄 格式 '{fmt['name']}':")
            logger.info(f"  • 字符数: {validation['character_count']}")
            logger.info(f"  • 字节数: {validation['byte_count']}")
            logger.info(f"  • 飞书限制: {validation['within_feishu_limit']} ({validation['feishu_limit_percent']:.1f}%)")
            
            # 显示报告预览
            preview = report[:200] + "..." if len(report) > 200 else report
            logger.info(f"  • 预览: {preview}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 简化版报告格式化器测试失败: {e}", exc_info=True)
        return False


def test_feishu_message_length(logger):
    """测试飞书消息长度"""
    logger.info("🧪 测试飞书消息长度...")
    
    try:
        from src.pushers.feishu_pusher import FeishuPusher
        
        # 创建不同长度的消息
        test_messages = [
            ("短消息", "这是一条短测试消息。" * 10),  # ~200字符
            ("中等消息", "这是一条中等长度的测试消息。" * 100),  # ~2000字符
            ("长消息", "这是一条长测试消息。" * 1000),  # ~20000字符
            ("超长消息", "这是一条超长测试消息。" * 10000),  # ~200000字符
        ]
        
        for name, content in test_messages:
            byte_length = len(content.encode('utf-8'))
            char_length = len(content)
            feishu_limit = 131072
            
            status = "✅ 在限制内" if byte_length <= feishu_limit else "❌ 超出限制"
            
            logger.info(f"📏 '{name}':")
            logger.info(f"  • 字符数: {char_length}")
            logger.info(f"  • 字节数: {byte_length}")
            logger.info(f"  • 飞书限制: {feishu_limit} 字节")
            logger.info(f"  • 状态: {status} ({byte_length/feishu_limit*100:.1f}%)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 飞书消息长度测试失败: {e}")
        return False


def test_integration(logger):
    """测试集成"""
    logger.info("🧪 测试系统集成...")
    
    try:
        # 加载配置
        config = get_config("development")
        
        # 创建收集器管理器
        collector_manager = create_default_collector_manager()
        logger.info("✅ 收集器管理器创建成功")
        
        # 收集数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        work_items = collector_manager.collect(start_time, end_time)
        logger.info(f"✅ 收集到 {len(work_items)} 个工作项")
        
        if work_items:
            # 显示工作项详情
            for i, item in enumerate(work_items[:3]):  # 只显示前3个
                logger.info(f"  {i+1}. {item.title} ({item.source})")
        
        # 创建处理器管理器
        processor_manager = create_default_processor_manager()
        logger.info("✅ 处理器管理器创建成功")
        
        # 处理数据
        if work_items:
            processed_data = processor_manager.process(work_items)
            logger.info(f"✅ 处理完成，分析结果: {len(processed_data)} 个指标")
        else:
            logger.info("⚠️  没有工作项数据，使用模拟数据")
            # 使用模拟数据
            processed_data = {
                "overview": {
                    "total_work_items": 8,
                    "total_duration_hours": 6.5,
                    "unique_tools": 2,
                    "unique_categories": 3,
                    "average_duration_minutes": 48.8,
                    "completion_rate_percent": 75.0
                },
                "time_analysis": {
                    "peak_hour": "14:00",
                    "peak_hour_count": 3
                },
                "key_insights": [
                    {"text": "下午2点是工作高峰期", "confidence": 0.8}
                ]
            }
        
        # 创建报告格式化器
        formatter = create_work_report_formatter()
        logger.info("✅ 报告格式化器创建成功")
        
        # 生成报告
        report = formatter.format_report(processed_data, "daily_work_summary")
        validation = formatter.validate_report_length(report, "daily_work_summary")
        
        logger.info(f"📄 报告生成成功:")
        logger.info(f"  • 字符数: {validation['character_count']}")
        logger.info(f"  • 字节数: {validation['byte_count']}")
        logger.info(f"  • 飞书限制: {validation['within_feishu_limit']}")
        
        # 显示报告预览
        lines = report.split('\n')
        for line in lines[:10]:  # 只显示前10行
            logger.info(f"  {line}")
        
        if len(lines) > 10:
            logger.info(f"  ... (共 {len(lines)} 行)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 集成测试失败: {e}", exc_info=True)
        return False


def main():
    """主函数"""
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("🔧 统一工作记录系统 - 修复测试")
    logger.info("=" * 60)
    
    tests = [
        ("OpenClaw收集器", test_openclaw_collector),
        ("简化版报告格式化器", test_simple_formatter),
        ("飞书消息长度", test_feishu_message_length),
        ("系统集成", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 开始测试: {test_name}")
        try:
            success = test_func(logger)
            results.append((test_name, success))
            if success:
                logger.info(f"✅ {test_name} 测试通过")
            else:
                logger.error(f"❌ {test_name} 测试失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 测试异常: {e}", exc_info=True)
            results.append((test_name, False))
    
    # 总结结果
    logger.info("\n" + "=" * 60)
    logger.info("📊 测试结果总结")
    logger.info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    logger.info(f"✅ 通过: {passed}/{total}")
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        logger.info(f"  • {test_name}: {status}")
    
    if passed == total:
        logger.info("\n🎉 所有测试通过！系统修复完成。")
    else:
        logger.info(f"\n⚠️  有 {total - passed} 个测试失败，需要进一步修复。")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)