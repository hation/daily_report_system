#!/usr/bin/env python3
"""
统一工作记录系统 - 主程序入口
从多个工具收集工作记录，统一整理后自动推送到飞书
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import argparse

# 设置项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from src.config.system_config import get_config, save_config, load_config
from src.managers import create_report_manager


def setup_logging(config):
    """设置日志"""
    log_config = config.get("system_management", {})
    log_level = log_config.get("log_level", "INFO")
    log_file = log_config.get("log_file", "./logs/system.log")
    
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("main")
    logger.info(f"日志系统已初始化，级别: {log_level}")
    logger.info(f"日志文件: {log_file}")
    
    return logger


def run_daily_report(config, logger, test_mode=False):
    """运行每日报告"""
    logger.info("开始运行每日工作报告")
    
    try:
        # 创建报告管理器
        feishu_config = config.get("feishu", {})
        reporting_config = config.get("reporting", {})
        daily_target = feishu_config.get("targets", {}).get("daily_report", {})
        manager_config = {
            "feishu_app_id": feishu_config.get("app_id", ""),
            "feishu_app_secret": feishu_config.get("app_secret", ""),
            "feishu_encrypt_key": feishu_config.get("encrypt_key", ""),
            "feishu_verification_token": feishu_config.get("verification_token", ""),
            "feishu_default_chat_id": daily_target.get("chat_id", ""),
            "data_sources": config.get("data_sources", {}).get("enabled", []),
            "processing_workflow": config.get("processing", {}).get("workflow", ["data_cleaner", "data_analyzer"]),
            "report_types": {
                "daily": {
                    "enabled": True,
                    "format": reporting_config.get("default_format", "daily_work_summary"),
                    "push_time": "19:00",
                    "target": daily_target
                }
            },
            "enable_backup": reporting_config.get("backup_reports", True),
            "backup_path": reporting_config.get("backup_path", "./data/reports/backup/"),
            "max_report_history": reporting_config.get("max_report_history", 30),
            "test_mode": test_mode or feishu_config.get("push_config", {}).get("test_mode", True)
        }
        
        report_manager = create_report_manager(manager_config)
        
        # 初始化组件
        logger.info("初始化系统组件...")
        if not report_manager.initialize():
            logger.error("系统组件初始化失败")
            return False
        
        # 检查系统状态
        system_status = report_manager.get_system_status()
        logger.info(f"系统状态: {system_status.get('status')}")
        logger.info(f"飞书连接: {system_status.get('feishu_connection')}")
        
        # 运行每日报告
        result = report_manager.run_daily_report()
        
        if result.get("success"):
            logger.info("✅ 每日工作报告运行成功")
            
            # 显示执行摘要
            summary = result.get("summary", {})
            logger.info(f"分析工作项: {summary.get('work_items_analyzed', 0)} 个")
            logger.info(f"报告长度: {summary.get('report_content_length', 0)} 字符")
            logger.info(f"推送状态: {'成功' if summary.get('push_success') else '失败'}")
            logger.info(f"执行时间: {summary.get('total_execution_time', 0):.1f} 秒")
            
            # 显示报告历史
            report_history = report_manager.get_report_history(limit=3)
            if report_history:
                latest_report = report_history[-1]
                logger.info(f"最新报告: {latest_report.get('filename')}")
            
            return True
        else:
            logger.error("❌ 每日工作报告运行失败")
            
            # 显示错误详情
            report_gen = result.get("report_generation", {})
            report_push = result.get("report_push", {})
            
            if report_gen and not report_gen.get("success"):
                logger.error(f"报告生成错误: {report_gen.get('error_details')}")
            
            if report_push and not report_push.get("success"):
                logger.error(f"报告推送错误: {report_push.get('error')}")
            
            return False
        
    except Exception as e:
        logger.error(f"运行每日报告时出现异常: {e}", exc_info=True)
        return False


def test_feishu_connection(config, logger):
    """测试飞书连接"""
    logger.info("测试飞书连接...")
    
    try:
        from src.pushers import create_feishu_pusher
        
        feishu = config.get("feishu", {})
        daily_target = feishu.get("targets", {}).get("daily_report", {})
        feishu_config = {
            "app_id": feishu.get("app_id", ""),
            "app_secret": feishu.get("app_secret", ""),
            "encrypt_key": feishu.get("encrypt_key", ""),
            "verification_token": feishu.get("verification_token", ""),
            "default_chat_id": daily_target.get("chat_id", ""),
            "test_mode": feishu.get("push_config", {}).get("test_mode", True)
        }
        
        pusher = create_feishu_pusher(feishu_config)
        
        if not feishu_config["test_mode"]:
            token = pusher.get_access_token()
            if not token:
                logger.error("❌ 无法获取飞书访问令牌")
                return False
            logger.info("✅ 飞书访问令牌获取成功")
        else:
            logger.info("✅ 飞书测试模式已启用，跳过真实令牌请求")
        
        # 测试发送消息
        test_content = (
            "🔧 **飞书连接测试**\n\n"
            "✅ 统一工作记录系统连接测试成功！\n\n"
            "系统状态: 正常\n"
            "测试时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
            "版本: " + config["system"]["version"] + "\n"
            "配置群聊ID: " + daily_target.get("chat_id", "未设置")
        )
        
        test_result = pusher.send_message(
            content=test_content,
            message_type="daily_work_report",
            target=daily_target
        )
        
        if test_result.get("success"):
            logger.info("✅ 飞书消息发送测试成功")
            logger.info(f"消息ID: {test_result.get('message_id')}")
            return True
        else:
            logger.error(f"❌ 飞书消息发送测试失败: {test_result.get('error')}")
            return False
        
    except Exception as e:
        logger.error(f"飞书连接测试异常: {e}", exc_info=True)
        return False


def show_system_info(config, logger):
    """显示系统信息"""
    logger.info("=" * 60)
    logger.info(f"📊 {config['system']['name']} v{config['system']['version']}")
    logger.info(f"📝 {config['system']['description']}")
    logger.info("=" * 60)
    
    # 数据源信息
    logger.info("📂 数据源配置:")
    for source_name in config["data_sources"]["enabled"]:
        source_config = config["data_sources"].get(source_name, {})
        status = "✅ 启用" if source_config.get("enabled") else "❌ 禁用"
        logger.info(f"  • {source_config.get('name', source_name)}: {status}")
    
    # 飞书配置
    logger.info("\n📱 飞书配置:")
    feishu_targets = config["feishu"]["targets"]
    for target_name, target_config in feishu_targets.items():
        if target_config.get("enabled"):
            chat_id = target_config.get("chat_id", "未设置")
            logger.info(f"  • {target_config.get('description', target_name)}: {chat_id}")
    
    # 调度配置
    logger.info("\n⏰ 调度配置:")
    scheduling = config["scheduling"]
    for job_name, job_config in scheduling.items():
        if job_config.get("enabled"):
            schedule = job_config.get("schedule", "未设置")
            report_type = job_config.get("report_type", "未知")
            logger.info(f"  • {job_name}: {schedule} ({report_type}报告)")
    
    logger.info("=" * 60)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="统一工作记录系统")
    parser.add_argument("--env", choices=["production", "development", "test"], 
                       default="development", help="运行环境")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--test", action="store_true", help="测试模式（不实际推送）")
    parser.add_argument("--test-feishu", action="store_true", help="测试飞书连接")
    parser.add_argument("--show-config", action="store_true", help="显示配置信息")
    parser.add_argument("--run-daily", action="store_true", help="运行每日报告")
    parser.add_argument("--save-config", action="store_true", help="保存配置到文件")
    
    args = parser.parse_args()
    
    # 加载配置
    if args.config and os.path.exists(args.config):
        config = load_config(args.config)
    else:
        config = get_config(args.env)
    
    # 设置日志
    logger = setup_logging(config)
    
    # 显示系统信息
    show_system_info(config, logger)
    
    # 保存配置（如果需要）
    if args.save_config:
        save_config(config, "config/system_config.yaml")
    
    # 测试飞书连接
    if args.test_feishu:
        success = test_feishu_connection(config, logger)
        sys.exit(0 if success else 1)
    
    # 运行每日报告
    if args.run_daily:
        success = run_daily_report(config, logger, args.test)
        sys.exit(0 if success else 1)
    
    # 显示帮助信息
    if not any([args.test_feishu, args.run_daily, args.show_config, args.save_config]):
        logger.info("\n📋 可用命令:")
        logger.info("  --run-daily     运行每日工作报告")
        logger.info("  --test-feishu   测试飞书连接")
        logger.info("  --test          测试模式（不实际推送）")
        logger.info("  --show-config   显示配置信息")
        logger.info("  --save-config   保存配置到文件")
        logger.info("  --env <env>     运行环境 (production/development/test)")
        logger.info("  --config <path> 指定配置文件")
        logger.info("\n💡 示例:")
        logger.info("  python main.py --run-daily --test")
        logger.info("  python main.py --test-feishu")
        logger.info("  python main.py --show-config")


if __name__ == "__main__":
    main()