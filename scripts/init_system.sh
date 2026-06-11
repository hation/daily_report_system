#!/bin/bash
set -euo pipefail

PROJECT_ROOT="/Users/xingan/Documents/software/daily_report_system"

cd "$PROJECT_ROOT"

echo "每日工作报告系统初始化"
echo "================================"

if [ ! -f "pyproject.toml" ]; then
    echo "请在项目根目录运行此脚本"
    exit 1
fi

if ! command -v python3 > /dev/null 2>&1; then
    echo "需要安装 Python3"
    exit 1
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "虚拟环境已创建"
else
    echo "虚拟环境已存在"
fi

source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

mkdir -p data/reports data/cache data/backups logs tests/test_data
touch data/reports/.gitkeep data/cache/.gitkeep data/backups/.gitkeep logs/.gitkeep
chmod +x scripts/run_daily_report.sh

echo ""
echo "数据源路径检查"
echo "--------------------------------"
for path in "$HOME/.trae-cn/memory/projects" "$HOME/.openclaw/lcm.db" "$HOME/.hermes/sessions" "$HOME/.hermes/memory_evaluation"; do
    if [ -e "$path" ]; then
        echo "存在: $path"
    else
        echo "未找到: $path"
    fi
done

echo ""
echo "飞书推送检查"
echo "--------------------------------"
if command -v lark-cli > /dev/null 2>&1; then
    echo "lark-cli 可用: $(command -v lark-cli)"
else
    echo "未找到 lark-cli，请先安装并授权"
fi

if [ -n "${FEISHU_DEFAULT_CHAT_ID:-}" ] || [ -n "${LARK_DEFAULT_CHAT_ID:-}" ] || [ -n "${DAILY_REPORT_CHAT_ID:-}" ]; then
    echo "已检测到默认群聊环境变量"
else
    echo "未检测到默认群聊环境变量，真实推送时请传入 --chat-id oc_xxx 或设置 FEISHU_DEFAULT_CHAT_ID"
fi

echo ""
echo "运行验证"
echo "--------------------------------"
python3 -m pytest
python3 -m flake8 src tests
python3 -m compileall src tests

echo ""
echo "初始化完成"
echo "常用命令："
echo "  python3 src/main.py --run-daily --env test --test"
echo "  python3 src/main.py --test-feishu --env production --chat-id oc_xxx"
echo "  python3 src/main.py --run-daily --env production --chat-id oc_xxx"
echo "  ./scripts/run_daily_report.sh"
