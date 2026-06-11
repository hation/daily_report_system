"""
系统配置
统一工作记录系统的配置文件
"""

import os
from datetime import datetime

# 基础配置
BASE_CONFIG = {
    # 系统信息
    "system": {
        "name": "统一工作记录系统",
        "version": "1.0.0",
        "description": "从多个工具收集工作记录，统一整理后自动推送到飞书",
        "author": "xingan",
        "created_at": "2024-06-10"
    },
    
    # 数据源配置
    "data_sources": {
        "enabled": ["trae-cn", "openclaw", "hermes"],
        "trae-cn": {
            "name": "Trae CN",
            "data_path": "~/.trae-cn/memory/projects/",
            "enabled": True,
            "description": "Trae CN 项目记忆数据"
        },
        "openclaw": {
            "name": "OpenClaw",
            "db_path": "~/.openclaw/lcm.db",
            "enabled": True,
            "description": "OpenClaw 任务数据库"
        },
        "hermes": {
            "name": "Hermes Agent",
            "sessions_path": "~/.hermes/sessions/",
            "memory_path": "~/.hermes/memory_evaluation/",
            "enabled": True,
            "description": "Hermes Agent 会话和记忆数据"
        },
        "trae-work-cn": {
            "name": "Trae Work CN",
            "enabled": False,
            "description": "Trae Work CN 工作数据（待确认格式）"
        },
        "codex": {
            "name": "Codex",
            "enabled": False,
            "description": "Codex 工作数据（待确认格式）"
        }
    },
    
    # 数据处理配置
    "processing": {
        "workflow": ["data_cleaner", "data_analyzer"],
        "data_cleaner": {
            "min_duration": 1,      # 最小持续时间（分钟）
            "max_duration": 480,    # 最大持续时间（分钟）
            "remove_duplicates": True,
            "normalize_timestamps": True,
            "fill_missing_fields": True
        },
        "data_analyzer": {
            "time_bucket_size": 60,     # 时间分桶大小（分钟）
            "top_n_categories": 10,     # 显示前N个分类
            "top_n_keywords": 20,       # 显示前N个关键词
            "min_insight_confidence": 0.7
        }
    },
    
    # 报告配置
    "reporting": {
        "formats": {
            "daily_work_summary": {
                "name": "每日工作摘要",
                "sections": ["header", "overview", "time_analysis", "tool_analysis", 
                           "category_analysis", "priority_analysis", "key_insights", "footer"],
                "max_length": 4000,
                "enabled": True
            },
            "detailed_work_report": {
                "name": "详细工作报告",
                "sections": ["header", "metadata", "overview", "time_analysis", 
                           "tool_analysis", "category_analysis", "priority_analysis",
                           "duration_analysis", "keyword_analysis", "key_insights", "footer"],
                "max_length": 6000,
                "enabled": True
            },
            "executive_work_summary": {
                "name": "执行工作摘要",
                "sections": ["header", "key_metrics", "top_insights", "footer"],
                "max_length": 2000,
                "enabled": True
            }
        },
        "default_format": "daily_work_summary",
        "save_reports": True,
        "backup_reports": True,
        "backup_path": "./data/reports/backup/",
        "max_report_history": 30
    },
    
    # 飞书推送配置（密钥通过环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET / FEISHU_ENCRYPT_KEY / FEISHU_VERIFICATION_TOKEN / FEISHU_DEFAULT_CHAT_ID 注入）
    "feishu": {
        "app_id": "",
        "app_secret": "",
        "encrypt_key": "",
        "verification_token": "",
        
        # 推送目标
        "targets": {
            "daily_report": {
                "receive_type": "chat",
                "chat_id": "",
                "enabled": True,
                "description": "每日工作报告推送群"
            },
            "error_alerts": {
                "receive_type": "chat",
                "chat_id": "",
                "enabled": True,
                "description": "错误告警推送"
            },
            "test": {
                "receive_type": "chat",
                "chat_id": "",
                "enabled": True,
                "description": "测试消息推送"
            }
        },
        
        # 推送配置
        "push_config": {
            "max_retries": 3,
            "retry_delay": 2,
            "timeout": 30,
            "test_mode": False,
            "prefer_lark_cli": True
        },
        
        # 消息模板
        "message_templates": {
            "daily_work_report": {
                "title": "📊 每日工作分析报告",
                "template": "daily",
                "color": "blue"
            },
            "detailed_work_report": {
                "title": "📈 详细工作分析报告",
                "template": "detailed",
                "color": "green"
            },
            "executive_summary": {
                "title": "👔 工作执行摘要",
                "template": "executive",
                "color": "purple"
            },
            "error_alert": {
                "title": "⚠️ 系统错误告警",
                "template": "error",
                "color": "red"
            }
        }
    },
    
    # 调度配置（每天19:00运行）
    "scheduling": {
        "daily_report": {
            "enabled": True,
            "schedule": "0 19 * * *",  # 每天19:00
            "report_type": "daily",
            "push_enabled": True,
            "time_range_hours": 24,  # 收集最近24小时数据
            "retry_on_failure": True,
            "max_retries": 3
        },
        "weekly_report": {
            "enabled": False,
            "schedule": "0 18 * * 0",  # 每周日18:00
            "report_type": "detailed",
            "push_enabled": True,
            "time_range_hours": 168,  # 收集最近7天数据
            "retry_on_failure": True
        }
    },
    
    # 系统管理
    "system_management": {
        "log_level": "INFO",
        "log_file": "./logs/system.log",
        "max_log_size_mb": 10,
        "max_log_files": 5,
        
        "data_retention": {
            "reports_days": 30,
            "errors_days": 7,
            "logs_days": 14,
            "cleanup_schedule": "0 2 * * *"  # 每天2:00清理
        },
        
        "monitoring": {
            "health_check_interval": 3600,  # 每小时检查一次
            "alert_on_failure": True,
            "performance_monitoring": True
        }
    },
    
    # 路径配置
    "paths": {
        "project_root": "/Users/xingan/Documents/software/daily_report_system",
        "data_dir": "./data/",
        "reports_dir": "./data/reports/",
        "logs_dir": "./logs/",
        "errors_dir": "./data/errors/",
        "config_dir": "./config/",
        "scripts_dir": "./scripts/"
    }
}

# 开发环境配置（覆盖生产配置）
DEV_CONFIG = {
    "feishu": {
        "push_config": {
            "test_mode": True  # 开发环境使用测试模式
        }
    },
    "system_management": {
        "log_level": "DEBUG"
    }
}

# 测试环境配置
TEST_CONFIG = {
    "feishu": {
        "push_config": {
            "test_mode": True
        }
    },
    "reporting": {
        "save_reports": True,
        "backup_reports": False
    }
}


def get_config(environment="production"):
    """
    获取配置
    
    Args:
        environment: 环境类型 (production, development, test)
        
    Returns:
        配置字典
    """
    config = _copy_config(BASE_CONFIG)
    
    if environment == "development":
        _deep_update(config, DEV_CONFIG)
    elif environment == "test":
        _deep_update(config, TEST_CONFIG)
    
    _apply_environment_overrides(config)
    _ensure_directories(config)
    
    return config


def _copy_config(config):
    """复制配置字典"""
    import copy
    return copy.deepcopy(config)


def _deep_update(original, update):
    """深度更新字典"""
    for key, value in update.items():
        if key in original and isinstance(original[key], dict) and isinstance(value, dict):
            _deep_update(original[key], value)
        else:
            original[key] = value


def _apply_environment_overrides(config):
    """从环境变量补齐敏感配置"""
    feishu = config.get("feishu", {})
    feishu["app_id"] = os.getenv("FEISHU_APP_ID", feishu.get("app_id", ""))
    feishu["app_secret"] = os.getenv("FEISHU_APP_SECRET", feishu.get("app_secret", ""))
    feishu["encrypt_key"] = os.getenv("FEISHU_ENCRYPT_KEY", feishu.get("encrypt_key", ""))
    feishu["verification_token"] = os.getenv("FEISHU_VERIFICATION_TOKEN", feishu.get("verification_token", ""))
    default_chat_id = (
        os.getenv("FEISHU_DEFAULT_CHAT_ID", "")
        or os.getenv("LARK_DEFAULT_CHAT_ID", "")
        or os.getenv("DAILY_REPORT_CHAT_ID", "")
    )
    if default_chat_id:
        for target in feishu.get("targets", {}).values():
            if not target.get("chat_id"):
                target["chat_id"] = default_chat_id


def _ensure_directories(config):
    """确保所有必要的目录存在"""
    paths = config.get("paths", {})
    
    for key, path in paths.items():
        if key.endswith("_dir"):
            # 解析路径
            if path.startswith("./"):
                # 相对路径，基于项目根目录
                base_dir = paths.get("project_root", ".")
                full_path = os.path.join(base_dir, path[2:])
            else:
                full_path = path
            
            # 创建目录
            os.makedirs(full_path, exist_ok=True)


def save_config(config, filepath="config/system_config.yaml"):
    """保存配置到文件"""
    import yaml
    
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"✅ 配置已保存到: {filepath}")


def load_config(filepath="config/system_config.yaml"):
    """从文件加载配置"""
    import yaml
    
    if not os.path.exists(filepath):
        print(f"⚠️  配置文件不存在: {filepath}")
        return get_config()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"✅ 配置已从文件加载: {filepath}")
    return config


# 导出默认配置
DEFAULT_CONFIG = get_config()


if __name__ == "__main__":
    # 测试配置
    config = get_config("development")
    print("✅ 配置系统测试通过")
    print(f"系统名称: {config['system']['name']}")
    print(f"飞书群聊ID: {config['feishu']['targets']['daily_report']['chat_id']}")
    print(f"调度时间: {config['scheduling']['daily_report']['schedule']}")
    
    # 保存配置
    save_config(config, "config/system_config.yaml")