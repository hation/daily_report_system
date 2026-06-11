# 统一工作记录系统部署指南

本文档说明如何在本机部署每日 19:00 自动运行的工作日报系统。

## 部署前提

### 1. Python 环境

```bash
cd /Users/xingan/Documents/software/daily_report_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. lark-cli 已授权

系统真实推送优先使用 `lark-cli`。

```bash
lark-cli --version
```

如授权失效，请先重新完成 lark-cli 登录授权。

### 3. 配置目标飞书群聊

推荐写入 shell 环境变量或 LaunchAgent 环境变量：

```bash
export FEISHU_DEFAULT_CHAT_ID="oc_xxx"
```

系统也支持：

```bash
export LARK_DEFAULT_CHAT_ID="oc_xxx"
export DAILY_REPORT_CHAT_ID="oc_xxx"
```

也可以手动运行时通过 `--chat-id` 指定。

## 手动验证

### 测试模式运行日报

不会真实推送：

```bash
python3 src/main.py --run-daily --env test --test
```

### 测试飞书连接

会向飞书发送一条测试消息：

```bash
python3 src/main.py --test-feishu --env production --chat-id oc_xxx
```

如果已配置 `FEISHU_DEFAULT_CHAT_ID`：

```bash
python3 src/main.py --test-feishu --env production
```

### 真实推送日报

```bash
python3 src/main.py --run-daily --env production --chat-id oc_xxx
```

如果已配置 `FEISHU_DEFAULT_CHAT_ID`：

```bash
python3 src/main.py --run-daily --env production
```

### 使用脚本运行

```bash
./scripts/run_daily_report.sh
```

脚本会：

1. 进入项目目录。
2. 激活 `venv`。
3. 执行 `python3 src/main.py --run-daily --env production`。
4. 写入 `logs/cron.log` 和 `logs/cron_error.log`。

## macOS LaunchAgent 定时任务

配置文件：

```text
config/com.xingan.daily_report_system.plist
```

### 1. 检查 plist 中的环境变量

如果不希望依赖 shell 环境变量，可以在 plist 的 `EnvironmentVariables` 中加入：

```xml
<key>FEISHU_DEFAULT_CHAT_ID</key>
<string>oc_xxx</string>
```

注意不要把 app secret 写入仓库。当前系统优先使用已授权的 `lark-cli`，通常只需要群聊 ID。

### 2. 安装 LaunchAgent

```bash
cp config/com.xingan.daily_report_system.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/com.xingan.daily_report_system.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.xingan.daily_report_system.plist
```

### 3. 立即触发一次

```bash
launchctl start com.xingan.daily_report_system
```

### 4. 查看状态

```bash
launchctl list | grep daily_report_system
```

### 5. 查看日志

```bash
tail -f logs/cron.log
tail -f logs/cron_error.log
tail -f logs/launchd.log
tail -f logs/launchd_error.log
```

### 6. 卸载定时任务

```bash
launchctl unload ~/Library/LaunchAgents/com.xingan.daily_report_system.plist
rm ~/Library/LaunchAgents/com.xingan.daily_report_system.plist
```

## cron 备用方案

如果不用 LaunchAgent，可使用 cron：

```bash
crontab -e
```

加入：

```cron
0 19 * * * FEISHU_DEFAULT_CHAT_ID=oc_xxx /Users/xingan/Documents/software/daily_report_system/scripts/run_daily_report.sh
```

## 质量检查

部署前建议运行：

```bash
python3 -m pytest
python3 -m flake8 src tests
python3 -m compileall src tests
```

当前基线：

```text
8 passed
```

## 数据目录和日志

```text
data/reports/backup/    # 日报备份
logs/system.log         # 系统日志
logs/cron.log           # 定时脚本标准日志
logs/cron_error.log     # 定时脚本错误日志
logs/launchd.log        # LaunchAgent 标准输出
logs/launchd_error.log  # LaunchAgent 错误输出
```

## 常见问题

### 飞书推送失败

优先检查：

1. `lark-cli` 是否可用。
2. `FEISHU_DEFAULT_CHAT_ID` 或 `--chat-id` 是否正确。
3. 机器人或当前授权身份是否有目标群聊发送权限。
4. `logs/cron_error.log` 或 `logs/system.log` 中的错误信息。

可单独测试：

```bash
python3 src/main.py --test-feishu --env production --chat-id oc_xxx
```

### 定时任务不运行

检查：

```bash
launchctl list | grep daily_report_system
chmod +x scripts/run_daily_report.sh
./scripts/run_daily_report.sh
```

### 数据收集为空

检查数据源路径：

```bash
ls ~/.trae-cn/memory/projects/
ls ~/.openclaw/lcm.db
ls ~/.hermes/sessions/
ls ~/.hermes/memory_evaluation/
```

OpenClaw 最近 24 小时没有符合条件消息时，收集为 0 属于正常情况。

## 正式入口

当前正式入口只有两个：

```bash
python3 src/main.py --run-daily --env production
./scripts/run_daily_report.sh
```

历史实验脚本已归档到：

```text
archive/legacy_scripts/
```

后续维护请优先修改 `src/`、`tests/` 和正式脚本，不要再基于归档脚本扩展功能。
