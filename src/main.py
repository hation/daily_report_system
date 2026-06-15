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


def parse_datetime_arg(value, is_end=False):
    """解析命令行时间参数"""
    try:
        if len(value) == 10:
            parsed = datetime.strptime(value, "%Y-%m-%d")
            if is_end:
                return parsed.replace(hour=23, minute=59, second=59)
            return parsed
        return datetime.fromisoformat(value.replace(" ", "T"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"无效时间格式: {value}") from exc


def build_preset_time_range(range_value, now=None):
    """根据快捷关键词构建报告时间范围"""
    current = now or datetime.now()
    today_start = current.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = current.replace(microsecond=0)
    aliases = {
        "today": "today",
        "今日": "today",
        "今天": "today",
        "yesterday": "yesterday",
        "昨日": "yesterday",
        "昨天": "yesterday",
        "last-7-days": "last-7-days",
        "last7days": "last-7-days",
        "最近7天": "last-7-days",
        "近7天": "last-7-days",
        "last-30-days": "last-30-days",
        "last30days": "last-30-days",
        "最近30天": "last-30-days",
        "近30天": "last-30-days",
        "最近一个月": "last-30-days",
        "近一个月": "last-30-days",
    }
    normalized = aliases.get(str(range_value).strip().lower()) or aliases.get(str(range_value).strip())
    if not normalized:
        raise argparse.ArgumentTypeError(f"不支持的时间范围关键词: {range_value}")

    if normalized == "today":
        start_time = today_start
        end_time = today_end
    elif normalized == "yesterday":
        start_time = today_start - timedelta(days=1)
        end_time = today_start - timedelta(seconds=1)
    elif normalized == "last-7-days":
        start_time = today_start - timedelta(days=6)
        end_time = today_end
    else:
        start_time = today_start - timedelta(days=29)
        end_time = today_end

    return {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }


def build_time_range(start_value=None, end_value=None, range_value=None):
    """构建报告时间范围"""
    if range_value and (start_value or end_value):
        raise argparse.ArgumentTypeError("--range 不能和 --start/--end 同时使用")
    if range_value:
        return build_preset_time_range(range_value)
    if not start_value and not end_value:
        return None
    if not start_value or not end_value:
        raise argparse.ArgumentTypeError("--start 和 --end 必须同时提供")

    start_time = parse_datetime_arg(start_value)
    end_time = parse_datetime_arg(end_value, is_end=True)
    if start_time > end_time:
        raise argparse.ArgumentTypeError("--start 不能晚于 --end")

    return {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }


def run_daily_report(config, logger, test_mode=False, time_range=None):
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
            "test_mode": test_mode or feishu_config.get("push_config", {}).get("test_mode", False),
            "prefer_lark_cli": feishu_config.get("push_config", {}).get("prefer_lark_cli", True)
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
        
        if time_range:
            logger.info(f"报告时间范围: {time_range['start_time']} - {time_range['end_time']}")

        # 运行每日报告
        result = report_manager.run_daily_report(time_range=time_range)
        
        if result.get("success"):
            logger.info("✅ 每日工作报告运行成功")
            
            # 显示简要总结（遵循项目规则：聊天框精简版）
            collection_stats = result.get("collection_stats", {})
            processing_stats = result.get("processing_stats", {})
            analysis_results = result.get("analysis_results", {})
            
            logger.info("💡 今日工作简要总结")
            logger.info("------------------")
            
            # 获取分析结果中的关键信息
            content_summary = analysis_results.get("content_summary", {})
            daily_summary = content_summary.get("daily_summary", "今日没有收集到可分析的具体工作内容。")
            
            # 显示一句话结论
            logger.info(f"📝 {daily_summary}")
            
            # 显示关键产出（最多5条）
            key_outputs = content_summary.get("key_outputs", [])
            if key_outputs:
                logger.info("\n✅ 关键产出")
                logger.info("-----------")
                for i, output in enumerate(key_outputs[:5], 1):
                    summary_text = output.get("summary", output.get("title", "未命名产出"))
                    project = output.get("project", "未识别项目")
                    logger.info(f"{i}. {summary_text} ({project})")
            
            # 显示报告文件路径（让用户能够访问）
            report_history = report_manager.get_report_history(limit=1)
            if report_history:
                latest_report = report_history[-1]
                # 显示 Trae 可直接点击的格式
                import os
                absolute_path = os.path.abspath(latest_report.get('filepath'))
                filename = os.path.basename(latest_report.get('filepath'))
                logger.info(f"\n📄 详细报告: [{filename}](file://{absolute_path})")
            
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
            "default_chat_id": daily_target.get("chat_id", "") or os.getenv("FEISHU_DEFAULT_CHAT_ID") or os.getenv("FEISHU_DAILY_REPORT_CHAT_ID") or os.getenv("LARK_DEFAULT_CHAT_ID") or os.getenv("DAILY_REPORT_CHAT_ID", ""),
            "test_mode": feishu.get("push_config", {}).get("test_mode", False),
            "prefer_lark_cli": feishu.get("push_config", {}).get("prefer_lark_cli", True)
        }
        
        pusher = create_feishu_pusher(feishu_config)
        
        if feishu_config["test_mode"]:
            logger.info("✅ 飞书测试模式已启用，跳过真实令牌请求")
        elif feishu_config.get("prefer_lark_cli", True):
            test_result = pusher.test_connection()
            if test_result.get("success"):
                logger.info("✅ 飞书连接测试成功")
                if test_result.get("message_id"):
                    logger.info(f"消息ID: {test_result.get('message_id')}")
                return True
            else:
                logger.error(f"❌ 飞书连接测试失败: {test_result.get('error')}")
                return False
        else:
            token = pusher.get_access_token()
            if not token:
                logger.error("❌ 无法获取飞书访问令牌")
                return False
            logger.info("✅ 飞书访问令牌获取成功")
        
        # 测试发送消息
        test_content = (
            "🔧 **飞书连接测试**\n\n"
            "✅ 统一工作记录系统连接测试成功！\n\n"
            "系统状态: 正常\n"
            "测试时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
            "版本: " + config["system"]["version"] + "\n"
            "配置群聊ID: " + feishu_config.get("default_chat_id", "未设置")
        )
        
        target = daily_target.copy()
        target["chat_id"] = target.get("chat_id") or feishu_config.get("default_chat_id", "")
        test_result = pusher.send_message(
            content=test_content,
            message_type="daily_work_report",
            target=target
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
    parser.add_argument("--range", help="快捷时间范围，支持 today/今日、yesterday/昨日、last-7-days/最近7天、last-30-days/最近一个月")
    parser.add_argument("--start", help="报告开始时间，支持 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS")
    parser.add_argument("--end", help="报告结束时间，支持 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS")
    parser.add_argument("--chat-id", help="飞书目标群聊ID，优先级高于配置和环境变量")
    parser.add_argument("--save-config", action="store_true", help="保存配置到文件")
    
    args = parser.parse_args()
    try:
        time_range = build_time_range(args.start, args.end, args.range)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    
    # 加载配置
    if args.config and os.path.exists(args.config):
        config = load_config(args.config)
    else:
        config = get_config(args.env)
    
    if args.chat_id:
        for target in config.get("feishu", {}).get("targets", {}).values():
            if target.get("enabled"):
                target["chat_id"] = args.chat_id
    
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
        success = run_daily_report(config, logger, args.test, time_range)
        sys.exit(0 if success else 1)
    
    # 显示帮助信息
    if not any([args.test_feishu, args.run_daily, args.show_config, args.save_config]):
        logger.info("\n📋 可用命令:")
        logger.info("  --run-daily     运行每日工作报告")
        logger.info("  --test-feishu   测试飞书连接")
        logger.info("  --test          测试模式（不实际推送）")
        logger.info("  --show-config   显示配置信息")
        logger.info("  --range         快捷时间范围 (今日/昨日/最近7天/最近一个月)")
        logger.info("  --start         报告开始时间 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)")
        logger.info("  --end           报告结束时间 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)")
        logger.info("  --chat-id       指定飞书目标群聊ID")
        logger.info("  --save-config   保存配置到文件")
        logger.info("  --env <env>     运行环境 (production/development/test)")
        logger.info("  --config <path> 指定配置文件")
        logger.info("\n💡 示例:")
        logger.info("  python main.py --run-daily --test")
        logger.info("  python main.py --test-feishu --chat-id oc_xxx")
        logger.info("  python main.py --run-daily --env production --chat-id oc_xxx")
        logger.info("  python main.py --run-daily --range 昨日 --test")
        logger.info("  python main.py --run-daily --start 2026-06-01 --end 2026-06-07 --test")
        logger.info("  python main.py --show-config")


if __name__ == "__main__":
    main()