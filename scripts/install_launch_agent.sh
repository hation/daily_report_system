#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_PATH="$PROJECT_ROOT/config/com.xingan.daily_report_system.plist.template"
GENERATED_PATH="$PROJECT_ROOT/config/com.xingan.daily_report_system.plist"
TARGET_PATH="$HOME/Library/LaunchAgents/com.xingan.daily_report_system.plist"

if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "LaunchAgent 模板不存在: $TEMPLATE_PATH" >&2
    exit 1
fi

LARK_CLI_BIN=""
if command -v lark-cli >/dev/null 2>&1; then
    LARK_CLI_BIN="$(dirname "$(command -v lark-cli)")"
fi

LAUNCHD_PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
if [ -n "$LARK_CLI_BIN" ]; then
    LAUNCHD_PATH="$LARK_CLI_BIN:$LAUNCHD_PATH"
fi

mkdir -p "$PROJECT_ROOT/logs" "$HOME/Library/LaunchAgents"

python3 - "$TEMPLATE_PATH" "$GENERATED_PATH" "$PROJECT_ROOT" "$LAUNCHD_PATH" <<'PY'
import sys
from pathlib import Path

template_path, generated_path, project_root, launchd_path = sys.argv[1:]
content = Path(template_path).read_text(encoding="utf-8")
content = content.replace("{{PROJECT_ROOT}}", project_root)
content = content.replace("{{LAUNCHD_PATH}}", launchd_path)
Path(generated_path).write_text(content, encoding="utf-8")
PY

cp "$GENERATED_PATH" "$TARGET_PATH"
launchctl unload "$TARGET_PATH" 2>/dev/null || true
launchctl load "$TARGET_PATH"
launchctl list | grep daily_report_system || true

echo "LaunchAgent 已安装: $TARGET_PATH"
echo "每天 19:00 自动执行: $PROJECT_ROOT/scripts/run_daily_report.sh"
