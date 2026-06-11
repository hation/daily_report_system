#!/usr/bin/env python3
"""
统一工作记录系统 - 最终实用版
使用测试模式生成报告，保存到文件，可手动复制到飞书
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import argparse

print("🚀 统一工作记录系统 - 最终实用版")
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


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger("report_generator")
    
    def generate_daily_report(self, work_items):
        """生成每日报告"""
        self.logger.info(f"生成每日报告，工作项数量: {len(work_items)}")
        
        # 生成报告
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
            for i, item in enumerate(work_items[:10]):  # 显示前10个
                status_emoji = "✅" if item.get('status') == 'completed' else "🔄"
                report += f"  {i+1}. {status_emoji} [{item.get('source')}] {item.get('title')}\n"
                if item.get('description'):
                    report += f"     描述: {item.get('description')[:100]}...\n"
            
            if len(work_items) > 10:
                report += f"  ... 还有 {len(work_items) - 10} 个工作项\n"
        
        report += "\n✅ 报告生成完成\n"
        report += f"🔧 系统版本: 统一工作记录系统 v1.0\n"
        report += f"💾 保存位置: ./data/reports/\n"
        report += "=" * 40
        
        return report
    
    def save_report(self, report_content):
        """保存报告到文件"""
        # 创建报告目录
        report_dir = "./data/reports/"
        os.makedirs(report_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"daily_report_{timestamp}.md"
        filepath = os.path.join(report_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"报告保存到: {filepath}")
        
        # 同时保存一个最新版本
        latest_path = os.path.join(report_dir, "latest_report.md")
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return filepath
    
    def display_report_summary(self, work_items, report_path):
        """显示报告摘要"""
        print("\n" + "=" * 60)
        print("📋 报告摘要:")
        print(f"   工作项总数: {len(work_items)}")
        print(f"   数据来源: {', '.join(set(item.get('source') for item in work_items))}")
        print(f"   报告文件: {report_path}")
        print(f"   最新版本: ./data/reports/latest_report.md")
        print()
        print("📱 使用说明:")
        print("   1. 查看报告: cat ./data/reports/latest_report.md")
        print("   2. 复制到飞书: 复制报告内容到飞书群聊")
        print("   3. 定时运行: 设置cron任务每天19:00自动运行")
        print("=" * 60)


def run_daily_work_report():
    """运行每日工作报告"""
    logger.info("开始运行每日工作报告")
    
    try:
        # 创建模拟收集器
        collectors = {
            "Trae CN": MockCollector("trae-cn"),
            "OpenClaw": MockCollector("openclaw"),
            "Hermes Agent": MockCollector("hermes")
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
        
        # 生成报告
        generator = ReportGenerator()
        report = generator.generate_daily_report(all_work_items)
        
        logger.info(f"报告生成完成，长度: {len(report)} 字符")
        
        # 保存报告
        report_path = generator.save_report(report)
        
        # 显示摘要
        generator.display_report_summary(all_work_items, report_path)
        
        # 显示报告内容预览
        print("\n📄 报告内容预览:")
        print("-" * 40)
        lines = report.split('\n')
        for line in lines[:15]:  # 显示前15行
            print(line)
        if len(lines) > 15:
            print("... (完整内容请查看文件)")
        print("-" * 40)
        
        logger.info("✅ 每日工作报告运行成功")
        return True
        
    except Exception as e:
        logger.error(f"运行每日报告时出现异常: {e}", exc_info=True)
        return False


def show_system_status():
    """显示系统状态"""
    print("\n" + "=" * 60)
    print("📊 统一工作记录系统 - 状态报告")
    print("=" * 60)
    
    # 检查数据目录
    data_dirs = [
        "./data/reports/",
        "./logs/"
    ]
    
    for dir_path in data_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"📁 {dir_path}: {len(files)} 个文件")
            if files:
                latest = max(files, key=lambda f: os.path.getmtime(os.path.join(dir_path, f)))
                print(f"   最新文件: {latest}")
        else:
            print(f"📁 {dir_path}: 目录不存在")
    
    # 检查报告文件
    report_dir = "./data/reports/"
    if os.path.exists(report_dir):
        report_files = [f for f in os.listdir(report_dir) if f.endswith('.md')]
        if report_files:
            print(f"\n📄 可用报告: {len(report_files)} 个")
            for i, file in enumerate(sorted(report_files, reverse=True)[:3]):
                filepath = os.path.join(report_dir, file)
                size = os.path.getsize(filepath)
                print(f"   {i+1}. {file} ({size} 字节)")
    
    print("\n⚙️ 系统配置:")
    print("   数据源: Trae CN, OpenClaw, Hermes Agent")
    print("   报告格式: Markdown")
    print("   保存位置: ./data/reports/")
    print("   日志位置: ./logs/")
    print("=" * 60)


def create_cron_job():
    """创建定时任务"""
    print("\n🔧 创建定时任务（每天19:00运行）")
    print("=" * 60)
    
    cron_script = f'''#!/bin/bash
# 统一工作记录系统定时任务
# 每天19:00自动运行

cd "{os.getcwd()}"
source venv/bin/activate

echo "[$(date)] 开始运行每日工作报告" >> /tmp/daily_report.log
python {__file__} --run-daily
echo "[$(date)] 每日工作报告完成" >> /tmp/daily_report.log
'''
    
    cron_path = "daily_report_cron.sh"
    with open(cron_path, 'w', encoding='utf-8') as f:
        f.write(cron_script)
    
    os.chmod(cron_path, 0o755)
    
    print(f"✅ 定时任务脚本已创建: {cron_path}")
    print("\n📋 添加到 crontab:")
    print(f"crontab -e 添加以下行:")
    print(f"0 19 * * * {os.path.join(os.getcwd(), cron_path)}")
    print("\n💡 测试运行:")
    print(f"bash {cron_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="统一工作记录系统")
    parser.add_argument("--run-daily", action="store_true", help="运行每日工作报告")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--setup-cron", action="store_true", help="设置定时任务")
    parser.add_argument("--view-latest", action="store_true", help="查看最新报告")
    
    args = parser.parse_args()
    
    print("🚀 统一工作记录系统 - 最终实用版")
    print("📝 从 Trae CN、OpenClaw、Hermes 收集工作记录")
    print("💾 生成报告并保存到文件系统")
    print("📱 可手动复制报告内容到飞书")
    print("=" * 60)
    
    # 查看最新报告
    if args.view_latest:
        latest_path = "./data/reports/latest_report.md"
        if os.path.exists(latest_path):
            print(f"\n📄 最新报告内容 ({latest_path}):")
            print("-" * 40)
            with open(latest_path, 'r', encoding='utf-8') as f:
                print(f.read())
            print("-" * 40)
        else:
            print(f"❌ 最新报告不存在，请先运行 --run-daily")
        return
    
    # 显示系统状态
    if args.status:
        show_system_status()
        return
    
    # 设置定时任务
    if args.setup_cron:
        create_cron_job()
        return
    
    # 运行每日报告
    if args.run_daily:
        success = run_daily_work_report()
        sys.exit(0 if success else 1)
    
    # 显示帮助信息
    if not any([args.run_daily, args.status, args.setup_cron, args.view_latest]):
        print("\n📋 可用命令:")
        print("  --run-daily     运行每日工作报告")
        print("  --status        显示系统状态")
        print("  --setup-cron    设置定时任务")
        print("  --view-latest   查看最新报告")
        print("\n💡 示例:")
        print(f"  python {os.path.basename(__file__)} --run-daily")
        print(f"  python {os.path.basename(__file__)} --status")
        print(f"  python {os.path.basename(__file__)} --view-latest")
        print("\n🎯 工作流程:")
        print("  1. 运行 --run-daily 生成报告")
        print("  2. 查看 --view-latest 报告内容")
        print("  3. 复制报告内容到飞书群聊")
        print("  4. 设置 --setup-cron 每天自动运行")


if __name__ == "__main__":
    main()