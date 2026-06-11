#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/cron.log"
ERROR_LOG="$LOG_DIR/cron_error.log"
LOCAL_ENV_FILE="$PROJECT_ROOT/config/local.env"

mkdir -p "$LOG_DIR"

if [ -f "$LOCAL_ENV_FILE" ]; then
    set -a
    source "$LOCAL_ENV_FILE"
    set +a
fi

BASE_PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PATH="$BASE_PATH:$PATH"

if command -v lark-cli >/dev/null 2>&1; then
    LARK_CLI_BIN="$(dirname "$(command -v lark-cli)")"
elif [ -n "${LARK_CLI_BIN:-}" ]; then
    LARK_CLI_BIN="$LARK_CLI_BIN"
else
    LARK_CLI_BIN=""
fi

if [ -n "$LARK_CLI_BIN" ]; then
    export PATH="$LARK_CLI_BIN:$BASE_PATH:$PATH"
fi
export PYTHONPATH="$PROJECT_ROOT"

{
    echo "============================================================"
    echo "定时任务执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================================"
} >> "$LOG_FILE"

if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "虚拟环境不存在: $VENV_PATH" | tee -a "$LOG_FILE" "$ERROR_LOG"
    exit 1
fi

source "$VENV_PATH/bin/activate"

if ! command -v python3 > /dev/null 2>&1; then
    echo "Python3 环境检查失败" | tee -a "$LOG_FILE" "$ERROR_LOG"
    exit 1
fi

cd "$PROJECT_ROOT"

echo "开始运行每日工作报告..." >> "$LOG_FILE"

if [ "$#" -eq 0 ]; then
    python3 src/main.py --run-daily --env production >> "$LOG_FILE" 2>> "$ERROR_LOG"
else
    python3 src/main.py "$@" >> "$LOG_FILE" 2>> "$ERROR_LOG"
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "每日工作报告执行成功" >> "$LOG_FILE"
else
    echo "每日工作报告执行失败，退出码: $EXIT_CODE" >> "$LOG_FILE"
    echo "查看错误日志: $ERROR_LOG" >> "$LOG_FILE"
fi

echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "============================================================" >> "$LOG_FILE"

deactivate
exit $EXIT_CODE
