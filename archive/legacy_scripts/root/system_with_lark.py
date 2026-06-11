#!/usr/bin/env python3
"""
统一工作记录系统 - 集成 lark-cli 版本
使用 lark-cli 发送飞书消息
"""

import sys
import os
import logging
import json
from datetime import datetime, timedelta
import argparse

print("🚀 统一工作记录系统 - 集成 lark-cli 版本")
print("=" * 60)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/system.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("main")

# 导入 lark-cli 推送器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lark_cli_pusher import LarkCliPusher, create_lark_cli_pusher


class MockCollector:
    """模拟收集器"""
    
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"collector.{name}")
    
    def collect_work_items(self, start_time, end_time):
        """收集模拟工作项"""
        self.logger.info(f"收集 {self.name} 工作项: {start_time} - {end_time}")
        
        # 返回模拟数据
        mock_items = [
            {
                "id": f"{self.name}_001",
                "source": self.name,
                "source_type": "task",
                "title": f"{self.name} 任务1",
                "description": f"来自 {self.name} 的测试任务",
                "start_time": start_time,
                "end_time": end_time,
                "duration_hours": 1.5,
                "status": "completed",
                "priority": "high",
                "tags": ["test", self.name],
                "metadata": {"test": True, "collector": self.name}
            },
            {
                "id": f"{self.name}_002",
                "source": self.name,
                "source_type": "task",
                "title": f"{self.name} 任务2",
                "description": f"来自 {self.name} 的另一个测试任务",
                "start_time": start_time - timedelta(hours=2),
                "end_time": end_time - timedelta(hours=1),
                "duration_hours": 2.0,
                "status": "in_progress",
                "priority": "medium",
                "tags": ["test"],
                "metadata": {"test": True, "collector": self.name}
            }
        ]
        
        self.logger.info(f"返回 {len(mock_items)} 个模拟工作项")
        return mock_items


class SimpleReportFormatter:
    """简单报告格式化器"""
    
    def __init__(self, name="report_formatter"):
        self.name = name
        self.logger = logging.getLogger(f"formatter.{name}")
    
    def format_report(self, work_items, report_type="daily_work_summary"):
        """格式化报告"""
        self.logger.info(f"格式化报告: {report_type}, 工作项数量: {len(work_items)}")
        
        # 生成简单报告
        report = "📊 每日工作报告\n"
        report += f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"📋 工作项总数: {len(work_items)}\n\n"
        
        # 按来源统计
        sources = {}
        for item in work_items:
            source = item.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        if sources:
            report += "📂 数据来源统计:\n"
            for source, count in sources.items():
                report += f"  • {source}: {count}个\n"
        
        # 显示工作项详情
        if work_items:
            report += "\n📝 工作项详情:\n"
            for i, item in enumerate(work_items[:5]):  # 只显示前5个
                report += f"  {i+1}. [{item.get('source')}] {item.get('title')} ({item.get('status')})\n"
            
            if len(work_items) > 5:
                report += f"  ... 还有 {len(work_items) - 5} 个工作项\n"
        
        report += "\n✅ 报告生成完成\n"
        report += f"🔧 系统版本: 统一工作记录系统 v1.0\n"
        report += "=" * 40
        
        return report


def run_daily_report(test_mode=True):
    """运行每日报告"""
    logger.info("开始运行每日工作报告")
    
    try:
        # 创建模拟收集器
        collectors = {
            "trae-cn": MockCollector("trae-cn"),
            "openclaw": MockCollector("openclaw"),
            "hermes": MockCollector("hermes")
        }
        
        # 收集工作项
        start_time = datetime.now() - timedelta(days=1)
        end_time = datetime.now()
        
        all_work_items = []
        for name, collector in collectors.items():
            logger.info(f"收集 {name} 数据...")
            items = collector.collect_work_items(start_time, end_time)
            all_work_items.extend(items)
            logger.info(f"  ✓ {name}: 收集到 {len(items)} 个工作项")
        
        logger.info(f"总共收集到 {len(all_work_items)} 个工作项")
        
        if not all_work_items:
            logger.warning("没有工作项数据")
            return False
        
        # 格式化报告
        formatter = SimpleReportFormatter()
        report = formatter.format_report(all_work_items)
        
        logger.info(f"报告生成完成，长度: {len(report)} 字符")
        
        # 保存报告到文件
        report_dir = "./data/reports/"
        os.makedirs(report_dir, exist_ok=True)
        
        report_filename = f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(report_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"报告保存到: {report_path}")
        
        # 创建 lark-cli 推送器
        pusher_config = {
            "app_id": "${FEISHU_APP_ID}",
            "app_secret": "${FEISHU_APP_SECRET}",
            "default_chat_id": "${FEISHU_DEFAULT_CHAT_ID}",
            "test_mode": test_mode
        }
        
        pusher = create_lark_cli_pusher(pusher_config)
        
        # 测试连接
        connection_test = pusher.test_connection()
        if not connection_test.get("success"):
            logger.error("飞书连接测试失败")
            return False
        
        logger.info("飞书连接测试成功")
        
        # 发送报告
        push_result = pusher.send_message(report, "daily_work_report")
        
        if push_result.get("success"):
            logger.info("✅ 每日工作报告运行成功")
            logger.info(f"   报告长度: {len(report)} 字符")
            logger.info(f"   推送状态: 成功 (测试模式: {test_mode})")
            logger.info(f"   报告文件: {report_path}")
            
            # 显示报告摘要
            print("\n📋 报告摘要:")
            print(f"   工作项总数: {len(all_work_items)}")
            print(f"   报告长度: {len(report)} 字符")
            print(f"   保存位置: {report_path}")
            print(f"   推送状态: {'测试模式' if test_mode else '实际发送'}")
            
            return True
        else:
            logger.error(f"❌ 报告推送失败: {push_result.get('error')}")
            return False
        
    except Exception as e:
        logger.error(f"运行每日报告时出现异常: {e}", exc_info=True)
        return False


def test_feishu_connection(test_mode=True):
    """测试飞书连接"""
    logger.info("测试飞书连接...")
    
    pusher_config = {
        "app_id": "${FEISHU_APP_ID}",
        "app_secret": "${FEISHU_APP_SECRET}",
        "default_chat_id": "${FEISHU_DEFAULT_CHAT_ID}",
        "test_mode": test_mode
    }
    
    pusher = create_lark_cli_pusher(pusher_config)
    
    result = pusher.test_connection()
    
    if result.get("success"):
        logger.info("✅ 飞书连接测试成功")
        logger.info(f"   测试模式: {result.get('test_mode', False)}")
        logger.info(f"   消息ID: {result.get('message_id', 'N/A')}")
        return True
    else:
        logger.error(f"❌ 飞书连接测试失败: {result.get('error')}")
        return False


def show_system_info():
    """显示系统信息"""
    logger.info("=" * 60)
    logger.info("📊 统一工作记录系统 v1.0.0")
    logger.info("📝 从多个工具收集工作记录，统一整理后自动推送到飞书")
    logger.info("=" * 60)
    
    logger.info("📂 数据源配置:")
    logger.info("  • Trae CN: ✅ 启用")
    logger.info("  • OpenClaw: ✅ 启用")
    logger.info("  • Hermes Agent: ✅ 启用")
    
    logger.info("\n📱 飞书配置:")
    logger.info("  • 应用ID: ${FEISHU_APP_ID}")
    logger.info("  • 目标群聊: ${FEISHU_DEFAULT_CHAT_ID}")
    logger.info("  • 推送工具: lark-cli")
    
    logger.info("\n⏰ 调度配置:")
    logger.info("  • daily_report: 每天19:00自动运行")
    
    logger.info("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="统一工作记录系统")
    parser.add_argument("--test", action="store_true", help="测试模式（不实际推送）")
    parser.add_argument("--test-feishu", action="store_true", help="测试飞书连接")
    parser.add_argument("--run-daily", action="store_true", help="运行每日报告")
    parser.add_argument("--show-config", action="store_true", help="显示配置信息")
    parser.add_argument("--real-push", action="store_true", help="启用实际推送（关闭测试模式）")
    
    args = parser.parse_args()
    
    # 显示系统信息
    show_system_info()
    
    # 确定是否测试模式
    test_mode = not args.real_push  # 默认测试模式，除非指定 --real-push
    
    # 测试飞书连接
    if args.test_feishu:
        success = test_feishu_connection(test_mode)
        sys.exit(0 if success else 1)
    
    # 运行每日报告
    if args.run_daily:
        success = run_daily_report(test_mode)
        sys.exit(0 if success else 1)
    
    # 显示帮助信息
    if not any([args.test_feishu, args.run_daily, args.show_config, args.real_push]):
        logger.info("\n📋 可用命令:")
        logger.info("  --run-daily     运行每日工作报告")
        logger.info("  --test-feishu   测试飞书连接")
        logger.info("  --real-push     启用实际推送（关闭测试模式）")
        logger.info("  --show-config   显示配置信息")
        logger.info("\n💡 示例:")
        logger.info("  python system_with_lark.py --run-daily --test")
        logger.info("  python system_with_lark.py --test-feishu --real-push")
        logger.info("\n⚠️  注意:")
        logger.info("  默认使用测试模式，添加 --real-push 启用实际飞书推送")


if __name__ == "__main__":
    main()