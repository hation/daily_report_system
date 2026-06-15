# 统一工作记录整理与定时推送系统

用于从 Trae CN、Trae Work CN、Codex、PilotDeck、OpenClaw、Hermes 等工作工具中收集每日工作记录，自动清洗分析、生成日报，并推送到飞书群聊。

## 当前状态

项目已经具备可运行基线：

- 多源工作记录收集
- 数据清洗与基础分析
- Markdown 日报生成
- 报告本地保存到 `data/reports/`
- 基于已授权 `lark-cli` 的飞书真实推送
- macOS LaunchAgent 每天 19:00 自动执行，并支持登录/每小时检查补跑
- pytest 自动测试覆盖核心链路
- 上线前敏感信息保护：本地配置、日志、报告、真实 plist、旧归档脚本默认忽略

最新进度见：[docs/progress.md](docs/progress.md)

## 核心功能

- 多源数据收集：Trae CN、Trae Work CN、Codex、PilotDeck、OpenClaw、Hermes
- 标准工作项模型：统一不同来源的数据结构
- 日报生成：今日摘要、按项目看、按主题看、关键产出（支持更长文本显示）、后续关注、数据概览（优化Markdown格式，每个指标独立成行）
- 飞书推送：优先使用 `lark-cli`，不强依赖项目内保存 app secret
- 历史报告：生成结果保存到 `data/reports/`，备份目录为 `data/reports/backup/`
- 自动测试：覆盖收集器、报告管理、数据分析、格式化器、飞书推送器和调度配置

## 项目结构

```text
daily_report_system/
├── src/                         # 正式源码
│   ├── collectors/              # 数据收集器
│   ├── processors/              # 数据处理器
│   ├── formatters/              # 报告格式化器
│   ├── pushers/                 # 飞书推送器
│   ├── managers/                # 报告主链路管理
│   └── config/                  # 默认配置
├── tests/                       # pytest 自动测试
├── scripts/                     # 正式运行和 LaunchAgent 安装脚本
├── config/                      # 配置模板和 LaunchAgent 模板
├── docs/                        # 项目文档
├── data/                        # 运行数据目录，本地产物默认忽略
└── logs/                        # 日志目录，本地产物默认忽略
```

## 架构与执行链路

当前 CodeGraph 索引显示正式源码共 39 个 Python 文件。主链路如下：

```text
src/main.py
  └── ReportManager
      ├── CollectorManager
      │   ├── TraeCNCollector
      │   ├── TraeWorkCNCollector
      │   ├── CodexCollector
      │   ├── PilotDeckCollector
      │   ├── OpenClawCollector
      │   └── HermesCollector
      ├── ProcessorManager
      │   ├── DataCleaner
      │   └── DataAnalyzer
      ├── WorkReportFormatter / SimpleReportFormatter
      └── FeishuPusher
          ├── lark-cli 优先发送
          └── OpenAPI 可选回退
```

日报执行流程：

```text
加载配置 → 初始化组件 → 收集多源工作项 → 清洗去重 → 分析项目/主题/产出 → 格式化 Markdown → 保存报告 → 推送飞书
```

每天 19:00 的自动运行链路：

```text
macOS LaunchAgent → scripts/run_daily_report.sh → src/main.py --run-daily --env production
```

## 快速开始

### 1. 安装依赖

```bash
cd <project_root>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 确认 lark-cli 已授权

```bash
lark-cli --version
```

飞书推送默认优先使用已授权的 `lark-cli`。如果授权失效，请重新执行你的 lark-cli 登录流程。

### 3. 配置目标群聊

推荐使用环境变量：

```bash
export FEISHU_DEFAULT_CHAT_ID="oc_xxx"
```

也支持以下变量名：

```bash
export FEISHU_DAILY_REPORT_CHAT_ID="oc_xxx"
export LARK_DEFAULT_CHAT_ID="oc_xxx"
export DAILY_REPORT_CHAT_ID="oc_xxx"
```

定时脚本会自动读取本地忽略文件 `config/local.env`，可以写入：

```bash
FEISHU_DEFAULT_CHAT_ID=oc_xxx
```

也可以每次运行时通过命令行传入：

```bash
python3 src/main.py --run-daily --env production --chat-id oc_xxx
```

配置模板：

```text
config/system_config.yaml.template
config/data_sources.yaml.template
```

如果需要生成本地配置文件，请复制模板为 `.yaml` 文件；本地 `.yaml` 已被 `.gitignore` 忽略，避免上传真实路径或群聊 ID。

### 4. 运行测试

```bash
python3 -m pytest
python3 -m flake8 src tests
python3 -m compileall src tests
```

当前基线结果：

```text
19 passed
```

## 使用手册

### 日常使用

正常部署后无需手动操作：系统每天 19:00 尝试生成并推送日报；如果当时电脑休眠或错过触发，登录时和每小时检查会在 19:00 后自动补跑一次。

生成的报告保存在：

```text
data/reports/
```

主要日志保存在：

```text
logs/system.log
logs/cron.log
logs/cron_error.log
logs/launchd.log
logs/launchd_error.log
```

### 安装或更新定时任务

修改模板或脚本后，运行安装脚本即可重新生成、卸载旧任务并加载新任务：

```bash
./scripts/install_launch_agent.sh
```

### 手动强制补发

如果今天已经发过但仍要再发一次：

```bash
./scripts/run_daily_report.sh --force
```

### 防重复规则

定时脚本默认最多每天成功发送一次：

- 19:00 前执行：只记录检查日志并跳过
- 19:00 后执行：如果今天没成功发过则补发
- 今天已成功发送：直接跳过
- `--force` 或 `FORCE_RUN_DAILY_REPORT=1`：跳过防重复检查，强制执行

## 常用命令

### 测试模式生成日报

不会真实推送到飞书：

```bash
python3 src/main.py --run-daily --env test --test
```

### 测试飞书连接

会向目标群聊发送测试消息：

```bash
python3 src/main.py --test-feishu --env production --chat-id oc_xxx
```

如果已经设置 `FEISHU_DEFAULT_CHAT_ID`：

```bash
python3 src/main.py --test-feishu --env production
```

### 真实生成并推送日报

```bash
python3 src/main.py --run-daily --env production --chat-id oc_xxx
```

如果已经设置 `FEISHU_DEFAULT_CHAT_ID`：

```bash
python3 src/main.py --run-daily --env production
```

### 生成固定时间范围工作总结

使用快捷关键词，只生成文件、不真实推送：

```bash
python3 src/main.py --run-daily --env production --test --range 昨日
python3 src/main.py --run-daily --env production --test --range 最近7天
python3 src/main.py --run-daily --env production --test --range 最近一个月
```

使用明确日期范围：

```bash
python3 src/main.py --run-daily --env production --test --start 2026-06-01 --end 2026-06-07
```

指定到具体时间：

```bash
python3 src/main.py --run-daily --env production --test --start "2026-06-01 09:00:00" --end "2026-06-07 18:30:00"
```

快捷关键词：

| 关键词 | 时间范围 |
|---|---|
| `today` / `今日` / `今天` | 今天 00:00:00 到当前时间 |
| `yesterday` / `昨日` / `昨天` | 昨天 00:00:00 到 23:59:59 |
| `last-7-days` / `最近7天` / `近7天` | 最近 7 个自然日，含今天 |
| `last-30-days` / `最近30天` / `最近一个月` / `近30天` | 最近 30 个自然日，含今天 |

日期简写规则：

- `--start 2026-06-01` 等价于 `2026-06-01 00:00:00`
- `--end 2026-06-07` 等价于 `2026-06-07 23:59:59`
- `--range` 不能和 `--start/--end` 同时使用

### 通过脚本运行

```bash
./scripts/run_daily_report.sh
```

脚本会读取 `config/local.env`，补齐 launchd 环境下的飞书群聊 ID 和 PATH；然后使用项目虚拟环境，并调用当前正式入口：

```bash
python3 src/main.py --run-daily --env production
```

### 查看或保存配置

```bash
python3 src/main.py --show-config --env production
python3 src/main.py --save-config --env production
python3 src/main.py --run-daily --config config/system_config.yaml --test
```

主要参数：

| 参数 | 说明 |
|---|---|
| `--run-daily` | 生成日报并按配置推送 |
| `--test` | 测试模式，不真实推送 |
| `--test-feishu` | 测试飞书连接 |
| `--env production/development/test` | 选择运行环境 |
| `--chat-id oc_xxx` | 指定飞书目标群，优先级最高 |
| `--range` | 快捷时间范围，如 `今日`、`昨日`、`最近7天`、`最近一个月` |
| `--start` | 固定时间范围开始时间，需和 `--end` 一起使用 |
| `--end` | 固定时间范围结束时间，需和 `--start` 一起使用 |
| `--config path` | 从指定配置文件加载配置 |
| `--show-config` | 显示当前配置 |
| `--save-config` | 保存当前配置到 `config/system_config.yaml` |

## 数据源说明

### Trae CN

默认路径：

```text
~/.trae-cn/memory/projects/
```

支持 `.jsonl`、`.json`、`.md`、`.txt`。

### Trae Work CN

默认路径：

```text
~/Library/Application Support/TRAE SOLO CN/User/History/
```

支持读取 Trae Work CN / TRAE SOLO CN 的本地编辑历史 `entries.json`，用于识别项目文件编辑活动。

### Codex

默认路径：

```text
~/.codex/state_5.sqlite
```

支持读取 Codex 本地 `threads` 表，识别会话标题、首条用户消息、工作目录、模型来源和 token 使用量；会自动过滤模型问答和简单 OK 测试类噪音会话。

### PilotDeck

默认路径：

```text
~/.pilotdeck
```

支持读取 PilotDeck 项目会话、项目记忆、路由统计和工作区控制库：

- `projects/*/chats/*.jsonl`
- `projects/*/memory/MEMORY.md`
- `router/stats.jsonl`
- `memory/workspaces/*/control.sqlite`

会自动跳过 `auth.db`、`server-token` 等认证敏感文件。

### OpenClaw

默认路径：

```text
~/.openclaw/lcm.db
```

支持 `tasks`、`sessions` 和 `messages` 表结构兼容查询。

### Hermes

默认路径：

```text
~/.hermes/sessions/
~/.hermes/memory_evaluation/
```

支持会话 JSON 和记忆系统健康检查日志。

## 飞书推送策略

文件：`src/pushers/feishu_pusher.py`

当前策略：

1. 非测试模式优先调用 `lark-cli im +messages-send`。
2. 如果 lark-cli 失败，并且配置了 `FEISHU_APP_ID` 与 `FEISHU_APP_SECRET`，再尝试 OpenAPI 回退。
3. 如果缺少群聊 ID，会返回明确错误。
4. lark-cli 错误会被整理成可读信息。

可选 OpenAPI 环境变量：

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
export FEISHU_ENCRYPT_KEY="xxx"
export FEISHU_VERIFICATION_TOKEN="xxx"
```

## 定时任务

macOS LaunchAgent 使用模板生成本地真实配置：

```text
config/com.xingan.daily_report_system.plist.template
```

当前触发策略：

- `StartCalendarInterval`：每天 19:00 准点触发
- `RunAtLoad`：登录或任务加载时检查一次
- `StartInterval`：每小时检查一次
- 脚本防重复：当天已经成功发送则跳过

安装方式：

```bash
./scripts/install_launch_agent.sh
```

部署方式见：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

飞书/lark-cli 授权与排障见：[docs/lark_cli_troubleshooting.md](docs/lark_cli_troubleshooting.md)

## 上线前安全说明

以下内容默认不会上传：

```text
config/local.env
config/*.yaml
config/com.xingan.daily_report_system.plist
archive/legacy_scripts/
data/reports/*
logs/*
.trae/
.codegraph/
.mypy_cache/
```

上线仓库只保留模板和安装脚本：

```text
config/system_config.yaml.template
config/data_sources.yaml.template
config/com.xingan.daily_report_system.plist.template
scripts/install_launch_agent.sh
```

真实飞书群聊 ID、日志、日报产物和本机 LaunchAgent plist 都应只保留在本地。

## 报告内容

当前日报模板见：[docs/daily_report_template.md](docs/daily_report_template.md)。

日报当前包含：

1. 今日工作摘要
2. 按项目看
3. 按主题看
4. 关键产出
5. 需要关注的事项
6. 后续关注与建议
7. 数据概览
8. 报告尾部

后续如果要优化日报内容，请先更新模板文档，再同步修改分析和格式化代码。

## 历史脚本归档

历史实验脚本保留在本地归档目录：

```text
archive/legacy_scripts/
```

该目录已加入 `.gitignore`，不会上传到线上仓库。正式入口以 `src/main.py`、`scripts/run_daily_report.sh` 和 `scripts/install_launch_agent.sh` 为准。

## 已知技术债

- `mypy src` 仍有历史类型债务，后续建议单独治理。
- `*_part2.py` 是历史片段文件，当前保留但不参与运行和 lint。
- OpenClaw 当前真实数据较少，后续可继续增强表结构适配。

## 后续建议

1. 等待下一次 19:00 自动真实推送并检查日志。
2. 增加飞书卡片消息格式。
3. 增强 OpenClaw 数据收集。
4. 做类型治理和历史片段清理。
