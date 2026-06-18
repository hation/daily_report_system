#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.xingan.daily_report_system"
TEMPLATE_PATH="$PROJECT_ROOT/config/$LABEL.plist.template"
GENERATED_PATH="$PROJECT_ROOT/config/$LABEL.plist"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PATH="$TARGET_DIR/$LABEL.plist"
LAUNCHCTL_DOMAIN="gui/$(id -u)"

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

mkdir -p "$PROJECT_ROOT/logs" "$TARGET_DIR"

python3 - "$TEMPLATE_PATH" "$GENERATED_PATH" "$PROJECT_ROOT" "$LAUNCHD_PATH" <<'PY'
import sys
from pathlib import Path

template_path, generated_path, project_root, launchd_path = sys.argv[1:]
content = Path(template_path).read_text(encoding="utf-8")
content = content.replace("{{PROJECT_ROOT}}", project_root)
content = content.replace("{{LAUNCHD_PATH}}", launchd_path)
Path(generated_path).write_text(content, encoding="utf-8")
PY

plutil -lint "$GENERATED_PATH" >/dev/null

if launchctl print "$LAUNCHCTL_DOMAIN/$LABEL" >/dev/null 2>&1; then
    launchctl bootout "$LAUNCHCTL_DOMAIN/$LABEL" 2>/dev/null || launchctl unload "$TARGET_PATH" 2>/dev/null || true
elif [ -f "$TARGET_PATH" ]; then
    launchctl unload "$TARGET_PATH" 2>/dev/null || true
fi

cp "$GENERATED_PATH" "$TARGET_PATH"
chmod 644 "$TARGET_PATH"

if ! launchctl bootstrap "$LAUNCHCTL_DOMAIN" "$TARGET_PATH" 2>/dev/null; then
    launchctl load "$TARGET_PATH"
fi

launchctl enable "$LAUNCHCTL_DOMAIN/$LABEL" 2>/dev/null || true

if launchctl print "$LAUNCHCTL_DOMAIN/$LABEL" >/dev/null 2>&1 || launchctl list | grep -q "$LABEL"; then
    echo "LaunchAgent 已重新安装并加载: $TARGET_PATH"
    echo "每天 19:00 自动执行，并在登录时检查补跑: $PROJECT_ROOT/scripts/run_daily_report.sh"
else
    echo "LaunchAgent 安装后未检测到加载状态: $LABEL" >&2
    exit 1
fi
