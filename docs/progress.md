# 项目进度记录

更新时间：2026-06-11

## 当前状态

统一工作记录整理与飞书推送系统已经进入可运行基线阶段。当前主链路可以完成多源数据收集、清洗、分析、日报生成、报告保存和飞书真实推送。

当前 Git 提交历史：

```bash
6725931 fix: enable lark cli report push
e14c95f test: cover daily report pipeline
1e438ab feat: stabilize daily report pipeline
```

当前工作区状态：干净。

## 已完成功能

### 1. 项目 Git 基线

- 已初始化 Git 仓库。
- 已完成稳定基线提交。
- 已配置 `.gitignore`，避免提交运行产物、日志、本地索引和敏感记录。
- 已完成三次阶段性提交：
  - `feat: stabilize daily report pipeline`
  - `test: cover daily report pipeline`
  - `fix: enable lark cli report push`

### 2. 主链路打通

当前入口：

```bash
python3 src/main.py --run-daily --env production --chat-id <oc_xxx>
```

已打通流程：

1. 加载系统配置。
2. 初始化收集器、处理器、格式化器、飞书推送器。
3. 从多数据源收集工作项。
4. 清洗数据并生成分析结果。
5. 生成 Markdown 日报。
6. 保存报告到 `data/reports/backup/`。
7. 推送日报到飞书群聊。
8. 记录运行日志。

### 3. 数据源收集

#### Trae CN

文件：`src/collectors/trae_cn_collector.py`

已支持读取：

- `~/.trae-cn/memory/projects/`
- `.jsonl`
- `.json`
- `.md`
- `.txt`

能力：

- 按时间范围过滤记录。
- 将 JSONL 记忆记录转换为标准 `WorkItem`。
- 将近期更新的文本/Markdown/JSON 文件转换为文件活动工作项。

#### Hermes

文件：`src/collectors/hermes_collector.py`

已支持读取：

- `~/.hermes/sessions/`
- `~/.hermes/memory_evaluation/`

能力：

- 解析会话 JSON 中的用户消息。
- 解析记忆系统健康检查日志。
- 将会话活动和系统健康信息转换为标准 `WorkItem`。

#### OpenClaw

文件：`src/collectors/openclaw_collector.py`

已完成：

- 修复 `~/.openclaw/lcm.db` 路径展开。
- 支持根据 SQLite 实际表结构降级查询。
- 原有 `tasks/sessions` 查询保留。
- 新增 `messages` 表查询兼容。
- 表不存在时不再导致主链路失败。

当前真实验证中，OpenClaw 最近 24 小时没有符合条件的用户消息，因此收集结果为 0，但链路正常。

### 4. 标准工作项模型

文件：`src/collectors/base_collector.py`

已补齐：

- `duration_minutes`
- `tool`
- `category`
- `to_dict()`
- `test_connection()`
- 基础统计方法

这些字段用于兼容处理器、报告生成器和测试。

### 5. 收集器管理器

文件：`src/collectors/collector_manager.py`

已完成：

- `collect_all()` 返回标准结构：
  - `success`
  - `work_items`
  - `collector_results`
  - `collection_time_ms`
  - `start_time`
  - `end_time`
- `collect()` 保留旧接口，返回工作项列表。
- 单个收集器失败时不会中断全部收集。

### 6. 数据处理与分析

文件：`src/processors/data_analyzer.py`

已补齐基础分析：

- 时长分析
- 关键词分析
- 优先级分析
- 汇总统计
- 基础洞察生成

文件：`src/managers/report_manager.py`

已完成：

- 处理空数据时生成空分析报告，不再直接失败。
- 将分析结果规范化为报告格式化器需要的结构。
- 增加系统健康状态字段：
  - `status`
  - `successful_collectors`
  - `failed_collectors`
  - `collection_time_ms`
  - `processing_success`

### 7. 日报内容增强

文件：`src/formatters/simple_report_formatter.py`

当前日报包含：

- 工作概览
- 关键指标
- 主要活动与分布
- 关键洞察
- 今日工作亮点
- 系统健康状态
- 明日建议
- 报告尾部

已兼容真实分析结果中的不同数据结构，例如 `tool_analysis.tools` 和 `category_analysis.categories` 中的统计对象。

### 8. 飞书推送

文件：`src/pushers/feishu_pusher.py`

已解决真实推送问题。

当前推送策略：

1. 非测试模式优先使用已授权的 `lark-cli`。
2. 如果 lark-cli 失败，并且存在 `app_id/app_secret`，再尝试 OpenAPI 回退。
3. 缺少 `chat_id` 时返回明确错误。
4. lark-cli 错误输出会压缩为可读错误信息。

支持目标群聊配置方式：

```bash
python3 src/main.py --run-daily --env production --chat-id <oc_xxx>
```

或环境变量：

```bash
export FEISHU_DEFAULT_CHAT_ID="oc_xxx"
export LARK_DEFAULT_CHAT_ID="oc_xxx"
export DAILY_REPORT_CHAT_ID="oc_xxx"
```

已完成真实验证：

- lark-cli 最小测试消息发送成功。
- `python3 src/main.py --test-feishu --env production --chat-id <oc_xxx>` 发送成功。
- `python3 src/main.py --run-daily --env production --chat-id <oc_xxx>` 完整日报发送成功。

### 9. 自动测试

当前测试目录：`tests/`

已覆盖：

- `WorkItem` 兼容字段和字典转换。
- `CollectorManager` 标准结果结构。
- `CollectorManager.collect()` 旧接口兼容。
- `ReportManager` 日报生成和推送主链路。
- 日报格式化器核心章节。
- 飞书推送器 lark-cli 优先发送、缺少群聊 ID 错误、CLI 错误透传。

当前测试结果：

```bash
python3 -m pytest
```

结果：

```text
8 passed
```

### 10. 验证与质量检查

已通过：

```bash
python3 -m pytest
python3 -m flake8 src tests
python3 -m compileall src tests
```

敏感信息扫描已通过，源码和测试中无历史飞书密钥残留。

## 当前使用方式

### 测试模式运行日报

```bash
python3 src/main.py --run-daily --env test --test
```

### 真实推送日报

```bash
python3 src/main.py --run-daily --env production --chat-id <oc_xxx>
```

### 测试飞书连接

```bash
python3 src/main.py --test-feishu --env production --chat-id <oc_xxx>
```

### 使用环境变量免传 chat_id

```bash
export FEISHU_DEFAULT_CHAT_ID="oc_xxx"
python3 src/main.py --run-daily --env production
```

## 已知问题和技术债

### 1. mypy 类型治理尚未完成

当前项目可以通过语法编译、lint 和运行测试，但 `mypy src` 仍有历史类型债务，主要集中在：

- 旧 formatter 文件和保留片段文件。
- 部分类属性未显式声明。
- 部分处理器返回结构和基类类型定义不完全一致。
- 历史实验脚本未纳入类型治理范围。

建议后续单独做一轮类型治理，不与功能开发混在一起。

### 2. `*_part2.py` 保留片段

以下文件是历史片段文件，当前已保留但不参与运行和 lint：

- `src/formatters/base_formatter_part2.py`
- `src/formatters/work_report_formatter_part2.py`
- `src/managers/report_manager_part2.py`

后续可以选择归档到 `docs/archive/` 或合并进正式实现。

### 3. OpenClaw 数据当前偏少

OpenClaw 真实库最近 24 小时没有符合条件的用户消息，当前收集结果为 0。后续可以进一步确认 OpenClaw 的实际业务表和消息记录规则。

### 4. 旧实验脚本较多

根目录和 `scripts/` 下仍有较多历史实验脚本。当前主链路已经集中在 `src/main.py`，建议后续整理：

- 保留仍有用的脚本到 `scripts/`。
- 删除或归档一次性实验脚本。
- 更新 README 中的运行命令，避免旧命令误导。

## 后续待办

### 高优先级

1. 配置定时任务真实运行
   - 确认 macOS LaunchAgent 配置。
   - 将运行命令改为当前主入口。
   - 确认 `chat_id` 通过环境变量或配置文件注入。
   - 验证每天 19:00 自动推送。

2. 更新 README
   - 修正旧命令 `python src/main.py --collect --generate --push`。
   - 补充当前真实命令：
     - `--run-daily`
     - `--test-feishu`
     - `--chat-id`
   - 说明 lark-cli 授权和目标群聊配置方式。

3. 整理历史脚本
   - 区分正式脚本和实验脚本。
   - 删除或归档不再使用的脚本。
   - 避免后续维护时误用旧入口。

4. 飞书卡片消息
   - 当前推送为文本消息。
   - 后续可以扩展为 interactive card，提高群内阅读体验。

### 中优先级

1. 增强 OpenClaw 收集
   - 检查真实库表结构。
   - 补充更多字段映射。
   - 增加 OpenClaw 收集器测试样例库。

2. 增强日报内容
   - 增加项目维度汇总。
   - 增加具体工作项列表。
   - 增加重要事项/风险/阻塞项识别。
   - 增加周报和趋势分析能力。

3. 补充调度器测试
   - 验证 LaunchAgent 配置生成。
   - 验证手动触发脚本。
   - 验证日志路径和失败告警。

4. 类型治理
   - 分阶段修复 mypy 问题。
   - 为核心数据结构增加更严格类型定义。
   - 清理历史兼容分支。

### 低优先级

1. 多推送渠道支持
   - 支持邮件、Webhook 或其他 IM 平台。

2. 报告历史索引
   - 为 `data/reports/backup/` 增加索引文件。
   - 支持快速查询历史日报。

3. Web 可视化
   - 增加本地报告预览页面。
   - 展示每日/每周趋势图。

## 下一轮建议

建议下一轮优先做：

1. 更新 README 和部署文档。
2. 整理 LaunchAgent 定时任务，确保每天 19:00 自动真实推送。
3. 清理历史脚本，减少维护噪音。

完成后，项目就可以从“可手动运行”进入“可长期无人值守运行”阶段。
