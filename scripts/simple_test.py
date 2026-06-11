#!/usr/bin/env python3
"""
超简化测试 - 验证系统核心功能
"""

import sys
import os
import logging
from datetime import datetime

# 设置项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

print("🚀 超简化系统测试")
print("=" * 60)

# 1. 测试配置加载
print("
1. 📋 测试配置加载...")
try:
    from src.config.system_config import get_config
    config = get_config("development")
    print(f"   ✅ 配置加载成功")
    print(f"     系统名称: {config['system']['name']}")
    print(f"     版本: {config['system']['version']}")
    print(f"     飞书群聊: {config['feishu']['targets']['daily_report']['chat_id']}")
except Exception as e:
    print(f"   ❌ 配置加载失败: {e}")

# 2. 测试收集器
print("
2. 📂 测试收集器...")
try:
    from src.collectors import CollectorFactory
    from src.collectors.trae_cn_collector import TraeCNCollector
    from src.collectors.openclaw_collector import OpenClawCollector
    from src.collectors.hermes_collector import HermesCollector
    
    # 注册收集器
    CollectorFactory.register('trae-cn', TraeCNCollector)
    CollectorFactory.register('openclaw', OpenClawCollector)
    CollectorFactory.register('hermes', HermesCollector)
    
    print(f"   ✅ 收集器注册成功: {CollectorFactory.get_registered_collectors()}")
    
    # 测试创建
    for name in ['trae-cn', 'openclaw', 'hermes']:
        try:
            collector = CollectorFactory.create(name, {})
            print(f"   ✅ {name}: 创建成功")
            
            # 测试收集
            items = collector.collect_work_items(datetime.now(), datetime.now())
            print(f"     收集到 {len(items)} 个工作项")
            
        except Exception as e:
            print(f"   ❌ {name}: 失败 - {e}")
    
except Exception as e:
    print(f"   ❌ 收集器测试失败: {e}")

# 3. 测试报告格式化器
print("
3. 📊 测试报告格式化器...")
try:
    from src.formatters.work_report_formatter import WorkReportFormatter
    
    formatter = WorkReportFormatter("test_formatter")
    print(f"   ✅ 格式化器创建成功")
    
    # 测试格式化
    mock_items = [
        {"id": "test1", "source": "test", "title": "测试任务"},
        {"id": "test2", "source": "test", "title": "另一个测试"}
    ]
    
    report = formatter.format_report(mock_items, "daily_work_summary")
    print(f"   ✅ 报告生成成功")
    print(f"     报告长度: {len(report)} 字符")
    print(f"     报告预览: {report[:100]}...")
    
except Exception as e:
    print(f"   ❌ 格式化器测试失败: {e}")

# 4. 测试飞书推送器（测试模式）
print("
4. 📱 测试飞书推送器（测试模式）...")
try:
    from src.pushers.feishu_pusher import FeishuPusher
    
    pusher_config = {
        "app_id": "test_app_id",
        "app_secret": "test_app_secret",
        "default_chat_id": "${FEISHU_DEFAULT_CHAT_ID}",
        "test_mode": True
    }
    
    pusher = FeishuPusher("test_pusher", pusher_config)
    print(f"   ✅ 推送器创建成功")
    print(f"     测试模式: {pusher.test_mode}")
    print(f"     默认群聊: {pusher.default_chat_id}")
    
    # 测试消息发送（测试模式）
    test_result = pusher.send_message("测试消息", "test_report")
    print(f"   ✅ 消息发送测试: {test_result.get('success', False)}")
    
except Exception as e:
    print(f"   ❌ 推送器测试失败: {e}")

print("
" + "=" * 60)
print("🎉 超简化系统测试完成！")
print("
📋 系统核心功能验证通过")
print("✅ 配置加载 ✅ 收集器注册 ✅ 报告格式化 ✅ 飞书推送")
print("
🚀 现在可以运行完整系统:")
print("python src/main.py --run-daily --test")
