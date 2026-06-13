# lark-cli 授权与排障指南

本文档用于排查飞书推送相关问题。当前系统优先使用已授权的 `lark-cli` 发送消息，通常只需要配置目标群聊 ID，不需要在项目中保存 app secret。

## 当前推送链路

```text
scripts/run_daily_report.sh
  → src/main.py --run-daily --env production
  → FeishuPusher
  → lark-cli im +messages-send
```

如果 `lark-cli` 不可用，且配置了 `FEISHU_APP_ID` 与 `FEISHU_APP_SECRET`，系统才会尝试 OpenAPI 回退。

## 基础检查

### 检查 lark-cli 是否可用

```bash
lark-cli --version
```

如果命令不存在，先安装或修复本机 `lark-cli`。

### 检查目标群聊 ID

推荐写入本地忽略配置：

```bash
cat config/local.env
```

应包含：

```bash
FEISHU_DEFAULT_CHAT_ID=oc_xxx
```

也支持以下变量名：

```bash
FEISHU_DAILY_REPORT_CHAT_ID=oc_xxx
LARK_DEFAULT_CHAT_ID=oc_xxx
DAILY_REPORT_CHAT_ID=oc_xxx
```

## 重新授权

如果飞书推送失败，先重新登录或授权：

```bash
lark-cli auth login --recommend
```

如果当前版本使用的是旧命令，也可以尝试：

```bash
lark-cli auth
```

授权完成后测试：

```bash
python3 src/main.py --test-feishu --env production
```

## keychain 问题

如果出现类似错误：

```text
keychain Get failed: keychain not initialized
```

可以按顺序尝试：

```bash
lark-cli config init
lark-cli auth login --recommend
```

如果仍然失败，更新 `lark-cli`：

```bash
lark-cli update
```

然后重新授权：

```bash
lark-cli auth login --recommend
```

## 发送测试消息

如果已经配置 `config/local.env`：

```bash
python3 src/main.py --test-feishu --env production
```

也可以临时指定群聊：

```bash
python3 src/main.py --test-feishu --env production --chat-id oc_xxx
```

## 运行日报

正常运行：

```bash
./scripts/run_daily_report.sh
```

如果今天已经成功发过，但需要强制再发一次：

```bash
./scripts/run_daily_report.sh --force
```

## 查看日志

优先查看：

```bash
tail -80 logs/system.log
tail -80 logs/cron.log
tail -80 logs/cron_error.log
```

如果是 LaunchAgent 触发失败，查看：

```bash
tail -80 logs/launchd.log
tail -80 logs/launchd_error.log
```

## 常见现象

### 日报生成成功但没有收到飞书消息

检查：

1. `lark-cli --version` 是否可用。
2. `config/local.env` 是否有正确的 `FEISHU_DEFAULT_CHAT_ID`。
3. 当前授权用户或机器人是否有目标群发送权限。
4. `logs/system.log` 中是否有 `lark-cli 消息发送成功`。
5. `logs/cron_error.log` 是否有 lark-cli 错误。

### 定时任务触发但没有重复发送

如果日志显示：

```text
今日日报已成功发送，跳过重复执行
```

说明防重复机制正常生效。需要重复发送时使用：

```bash
./scripts/run_daily_report.sh --force
```

### 修改脚本后定时任务仍旧执行老逻辑

重新安装 LaunchAgent：

```bash
./scripts/install_launch_agent.sh
```

安装脚本会重新生成 plist、卸载旧任务、复制新配置并重新加载。