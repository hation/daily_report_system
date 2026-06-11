#!/bin/bash
"""
统一工作记录系统 - 定时任务脚本
每天19:00自动运行，收集工作记录并推送到飞书
"""

# 设置环境
PROJECT_ROOT="/Users/xingan/Documents/software/daily_report_system"
VENV_PATH="$PROJECT_ROOT/venv"
LOG_DIR="$PROJECT_ROOT/logs"
CONFIG_FILE="$PROJECT_ROOT/config/system_config.yaml"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 设置日志文件
LOG_FILE="$LOG_DIR/cron.log"
ERROR_LOG="$LOG_DIR/cron_error.log"

# 记录执行时间
echo "============================================================" >> "$LOG_FILE"
echo "🕒 定时任务执行时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "============================================================" >> "$LOG_FILE"

# 检查虚拟环境
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "❌ 虚拟环境不存在: $VENV_PATH" | tee -a "$LOG_FILE" "$ERROR_LOG"
    exit 1
fi

# 激活虚拟环境
source "$VENV_PATH/bin/activate"

# 检查Python环境
if ! python --version > /dev/null 2>&1; then
    echo "❌ Python环境检查失败" | tee -a "$LOG_FILE" "$ERROR_LOG"
    exit 1
fi

# 运行每日工作报告
echo "🚀 开始运行每日工作报告..." >> "$LOG_FILE"

cd "$PROJECT_ROOT" && \
python src/main.py --run-daily --env production >> "$LOG_FILE" 2>> "$ERROR_LOG"

EXIT_CODE=$?

# 记录执行结果
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 每日工作报告执行成功" >> "$LOG_FILE"
    echo "📅 执行时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
else
    echo "❌ 每日工作报告执行失败 (退出码: $EXIT_CODE)" >> "$LOG_FILE"
    echo "🔍 查看错误日志: $ERROR_LOG" >> "$LOG_FILE"
fi

echo "============================================================" >> "$LOG_FILE"

# 退出虚拟环境
deactivate

exit $EXIT_CODE