# 统一工作记录整理与定时推送系统

用于从 Trae CN、OpenClaw、Hermes 等工作工具中收集每日工作记录，自动清洗分析、生成日报，并推送到飞书群聊。

## 当前状态

项目已经具备可运行基线：

- 多源工作记录收集
- 数据清洗与基础分析
- Markdown 日报生成
- 报告本地保存
- 基于已授权 `lark-cli` 的飞书真实推送
- pytest 自动测试覆盖核心链路

最新进度见：[docs/progress.md](docs/progress.md)

## 核心功能

- 多源数据收集：Trae CN、OpenClaw、Hermes
- 标准工作项模型：统一不同来源的数据结构
- 日报生成：工作概览、关键指标、主要活动、洞察、系统健康、明日建议
- 飞书推送：优先使用 `lark-cli`，不强依赖项目内保存 app secret
- 历史报告：生成结果保存到 `data/reports/backup/`
- 自动测试：覆盖收集器、报告管理、格式化器和飞书推送器

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
├── scripts/                     # 正式运行脚本
├── config/                      # 配置模板和 LaunchAgent 配置
├── docs/                        # 项目文档
├── archive/legacy_scripts/      # 历史实验脚本归档
├── data/                        # 运行数据目录
└── logs/                        # 日志目录
```

## 快速开始

### 1. 安装依赖

```bash
cd /Users/xingan/Documents/software/daily_report_system
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
export LARK_DEFAULT_CHAT_ID="oc_xxx"
export DAILY_REPORT_CHAT_ID="oc_xxx"
```

也可以每次运行时通过命令行传入：

```bash
python3 src/main.py --run-daily --env production --chat-id oc_xxx
```

### 4. 运行测试

```bash
python3 -m pytest
python3 -m flake8 src tests
python3 -m compileall src tests
```

当前基线结果：

```text
8 passed
```

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

### 通过脚本运行

```bash
./scripts/run_daily_report.sh
```

脚本会使用项目虚拟环境，并调用当前正式入口：

```bash
python3 src/main.py --run-daily --env production
```

## 数据源说明

### Trae CN

默认路径：

```text
~/.trae-cn/memory/projects/
```

支持 `.jsonl`、`.json`、`.md`、`.txt`。

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

macOS LaunchAgent 配置文件：

```text
config/com.xingan.daily_report_system.plist
```

部署方式见：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 报告内容

日报当前包含：

1. 工作概览
2. 关键指标
3. 主要活动与分布
4. 关键洞察
5. 今日工作亮点
6. 系统健康状态
7. 明日建议
8. 报告尾部

## 历史脚本归档

历史实验脚本已归档到：

```text
archive/legacy_scripts/
```

正式入口以 `src/main.py` 和 `scripts/run_daily_report.sh` 为准。

## 已知技术债

- `mypy src` 仍有历史类型债务，后续建议单独治理。
- `*_part2.py` 是历史片段文件，当前保留但不参与运行和 lint。
- OpenClaw 当前真实数据较少，后续可继续增强表结构适配。

## 后续建议

1. 部署并验证每天 19:00 自动真实推送。
2. 增加飞书卡片消息格式。
3. 增强 OpenClaw 数据收集。
4. 做类型治理和历史片段归档。
