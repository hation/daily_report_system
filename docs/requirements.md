# 📋 **统一工作记录整理与定时推送系统**需求文档（V1.1）

**版本**: 1.1  
**最后更新**: 2026-06-10  
**项目状态**: 实施中  
**项目目录**: `/Users/xingan/Documents/software/daily_report_system/`

## 🎯 **项目概述**

### **项目名称**
统一工作记录整理与定时推送系统

### **项目目标**
开发一个自动化系统，从用户的所有工作工具中收集每日工作记录，统一整理后于每晚7点推送到飞书。

### **核心价值**
- 统一视图：整合分散在各个工具中的工作记录
- 自动整理：智能分类、统计和分析
- 定时推送：无需手动操作，自动生成和发送报告
- 历史追溯：保留完整的工作历史记录

## 📊 **数据源需求**

### **1. Trae CN**（已确认）
- **数据位置**：`~/.trae-cn/memory/projects/`
- **数据格式**：JSONL文件（`session_memory_*.jsonl`）
- **收集内容**：
  - 项目名称（从目录结构解析）
  - 工作意图（intent字段）
  - 执行行动（actions字段）
  - 工作成果（outcome字段）
  - 学习总结（learned字段）
  - 时间戳（message_summary_time字段）

### **2. Trae Work CN**（待确认）
- **数据位置**：需要用户提供
- **数据格式**：待确认
- **状态**：等待用户提供详细信息

### **3. OpenClaw**（已确认）
- **数据位置**：`~/.openclaw/lcm.db`
- **数据格式**：SQLite数据库
- **收集内容**：
  - 用户对话记录（messages表）
  - 对话时间（created_at字段）
  - 对话内容（content字段）
  - 过滤条件：排除"梦想日记"等自动生成内容

### **4. Hermes Agent**（已确认）
- **数据位置**：
  - 会话记录：`~/.hermes/sessions/*.json`
  - 系统状态：`~/.hermes/memory_evaluation/daily_check_*.log`
- **收集内容**：
  - 用户请求（session文件中的user消息）
  - 系统健康状态（从评估日志解析）
  - 时间戳（session_start字段）

### **5. Codex**（待确认）
- **数据位置**：需要用户提供
- **数据格式**：待确认
- **状态**：等待用户提供详细信息

## 🔄 **数据处理需求**

### **数据收集策略**
1. **时间范围**：收集当日（00:00-23:59）的工作记录
2. **去重处理**：相同内容跨系统只保留一次
3. **时间标准化**：统一转换为ISO 8601格式
4. **内容清洗**：
   - 移除无意义的系统消息
   - 截断过长的内容（保留前200字符+...）
   - 过滤敏感信息（API密钥等）

### **分类与标记**
1. **按项目分类**：
   - 金融科技（fintech-mentor）
   - 视频分析（video-anlalyer）
   - AI赚钱（aitoearn）
   - 股票分析（stock）
   - 新创项目（new-venture-creation）
   - 其他项目

2. **按工作类型分类**：
   - 代码开发
   - 数据分析
   - 系统维护
   - 学习研究
   - 文档编写
   - 会议讨论

3. **按重要性分级**：
   - 关键成果（完成重要功能/解决重大问题）
   - 常规工作（日常开发/维护）
   - 系统通知（状态更新/日志记录）

## 📈 **报告生成需求**

### **报告结构**
```
📊 每日工作汇总报告 - YYYY-MM-DD
========================================

📈 统计概览
----------------------------------------
• 总工作记录: XX条
• 工作时间分布: 上午XX条, 下午XX条, 晚上XX条
• 系统来源: Trae CN(XX), Trae Work CN(XX), OpenClaw(XX), Hermes(XX), Codex(XX)

🏷️ 项目工作量分布
----------------------------------------
• 项目A: XX条 (XX%)
• 项目B: XX条 (XX%)
• 项目C: XX条 (XX%)
• 其他项目: XX条 (XX%)

🔄 详细工作记录（按时间排序）
----------------------------------------
[时间段] 系统/项目: 工作内容摘要
[时间段] 系统/项目: 工作内容摘要
...

🎯 今日工作亮点
----------------------------------------
1. ✅ 重要成果1
2. ✅ 重要成果2
3. ⚠️ 需要注意的问题

📊 系统健康状态
----------------------------------------
• Hermes记忆系统: XX/100
• 磁盘使用率: XX%
• 其他系统状态...

💡 明日建议
----------------------------------------
1. 建议1（基于今日工作）
2. 建议2（基于系统状态）
3. 建议3（基于项目进度）

📁 原始数据参考
----------------------------------------
• Trae CN: [路径]
• Trae Work CN: [路径]
• OpenClaw: [路径]
• Hermes: [路径]
• Codex: [路径]
```

## 📱 **飞书推送需求**

### **推送配置**
1. **使用Hermes的飞书配置**：
   - 配置路径：`~/.hermes/config.yaml`
   - 配置项：`feishu`部分
   - 认证方式：使用Hermes已有的飞书认证

2. **推送时间**：
   - 主推送：每天19:00（晚上7点）
   - 重试机制：失败后5分钟重试，最多3次
   - 手动触发：支持随时手动推送

## ⚙️ **系统配置需求**

### **配置文件结构**
```yaml
# /Users/xingan/Documents/software/daily_report_system/config/system_config.yaml
system:
  name: "每日工作报告系统"
  version: "1.0.0"
  
schedule:
  push_time: "19:00"
  timezone: "Asia/Shanghai"
  retry_times: 3
  retry_interval: "5m"

data_sources:
  trae_cn:
    enabled: true
    path: "~/.trae-cn/memory/projects/"
    
  trae_work_cn:
    enabled: false  # 待确认后启用
    path: "待确认"
    
  openclaw:
    enabled: true
    db_path: "~/.openclaw/lcm.db"
    
  hermes:
    enabled: true
    sessions_path: "~/.hermes/sessions/"
    memory_eval_path: "~/.hermes/memory_evaluation/"
    
  codex:
    enabled: false  # 待确认后启用
    path: "待确认"

feishu:
  enabled: true
  use_hermes_config: true
  hermes_config_path: "~/.hermes/config.yaml"
```

## 📅 **实施计划**

### **阶段一：项目初始化与基础框架（2026-06-10）**
- [ ] 创建项目目录结构
- [ ] 初始化Python项目
- [ ] 创建配置文件系统
- [ ] 实现日志系统
- [ ] 创建基础收集器框架

### **阶段二：核心数据收集器开发（2026-06-11）**
- [ ] Trae CN收集器
- [ ] OpenClaw收集器
- [ ] Hermes收集器
- [ ] 数据处理器流水线

### **阶段三：飞书推送集成（2026-06-12）**
- [ ] 飞书消息格式化器
- [ ] 飞书推送器（使用Hermes配置）
- [ ] 推送错误处理
- [ ] 推送状态监控

### **阶段四：定时任务与部署（2026-06-13）**
- [ ] macOS定时任务配置
- [ ] 安装脚本和配置向导
- [ ] 系统测试和验证
- [ ] 用户文档编写

### **阶段五：Trae Work CN和Codex集成（待信息确认后）**
- [ ] 调研Trae Work CN数据格式
- [ ] 调研Codex数据格式
- [ ] 实现相应收集器
- [ ] 集成测试

## 🚀 **当前状态**

### **已完成**
- [x] 需求文档整理和确认
- [x] 项目目录规划
- [x] 技术方案设计
- [x] **阶段一：项目初始化与基础框架**
  - [x] 创建项目目录结构（20个目录）
  - [x] 创建项目配置文件（pyproject.toml, requirements.txt）
  - [x] 创建Git忽略文件和README
  - [x] 创建配置模板文件（system_config.yaml.template, data_sources.yaml.template）
  - [x] 创建初始化脚本（init_system.sh）
  - [x] 创建主程序入口文件（main.py）
  - [x] 运行初始化脚本并验证数据源路径
  - [x] 创建虚拟环境和安装基础依赖

- [x] **阶段二：核心数据收集器开发**
  - [x] 创建基础收集器框架（BaseCollector, WorkItem, CollectorFactory）
  - [x] 实现Trae CN收集器（基于 `~/.trae-cn/memory/projects/`）
  - [x] 实现OpenClaw收集器（基于 `~/.openclaw/lcm.db`）
  - [x] 实现Hermes收集器（基于 `~/.hermes/sessions/` 和 `~/.hermes/memory_evaluation/`）
  - [x] 创建收集器管理器（CollectorManager）
  - [x] 创建测试脚本并验证功能
  - [x] **✅ 测试结果**：所有收集器连接成功，框架功能正常

- [x] **阶段三：数据处理与报告生成**
  - [x] 创建基础处理器框架（BaseProcessor, ProcessedWorkItem, ProcessorFactory）
  - [x] 实现数据清洗处理器（DataCleaner） - 数据清洗、去重、标准化
  - [x] 实现数据分析处理器（DataAnalyzer） - 统计分析和洞察生成
  - [x] 创建处理器管理器（ProcessorManager） - 工作流协调和执行
  - [x] 创建测试脚本并验证功能
  - [x] **✅ 测试结果**：所有处理器功能正常，模块集成成功

### **进行中**
- [ ] 阶段四：报告格式化与飞书推送
  - [ ] 创建报告格式化器
  - [ ] 实现飞书推送器
  - [ ] 集成报告生成和推送流程

### **发现的问题**
1. **飞书配置**：Hermes配置文件中未找到飞书设置，需要确认飞书配置状态
2. **数据源验证**：Trae CN、OpenClaw、Hermes数据源路径验证通过
3. **OpenClaw数据库结构**：数据库表结构可能与预期不同（缺少tasks/sessions/projects表）
4. **待确认信息**：Trae Work CN和Codex数据位置仍需确认
5. **实际数据收集**：测试期间未收集到实际工作项，需要进一步分析数据格式

### **待处理**
- [ ] Trae Work CN数据格式确认
  - [ ] 安装路径
  - [ ] 数据存储方式
  - [ ] 数据结构
- [ ] Codex数据格式确认
  - [ ] 安装路径
  - [ ] 数据存储方式
  - [ ] 数据结构
- [ ] 飞书配置验证
  - [ ] Hermes飞书配置可用性（当前未找到）
  - [ ] 推送目标确认
  - [ ] Webhook URL配置
- [ ] OpenClaw数据库分析
  - [ ] 实际表结构分析
  - [ ] 数据格式适配

## 🔧 **技术实现详情**

### **项目目录结构**
```
/Users/xingan/Documents/software/daily_report_system/
├── src/                          # 源代码
├── tests/                        # 测试文件
├── scripts/                      # 可执行脚本
├── config/                       # 运行时配置
├── data/                         # 数据目录
├── logs/                         # 系统日志
├── docs/                         # 文档
├── requirements.txt              # Python依赖
├── pyproject.toml                # 项目配置
├── README.md                     # 项目说明
└── .gitignore                    # Git忽略文件
```

### **依赖技术栈**
- **语言**: Python 3.11+
- **数据库**: SQLite (只读访问)
- **定时任务**: macOS LaunchAgent
- **推送**: 飞书Webhook API
- **配置**: YAML格式
- **日志**: 结构化日志记录

## 📝 **更新记录**

### **2026-06-10 V1.1**
- 更新项目目录到 `/Users/xingan/Documents/software/daily_report_system/`
- 细化实施计划为5个阶段
- 明确待确认信息清单
- 开始阶段一实施

### **2026-06-10 V1.0**
- 初始需求文档创建
- 包含所有5个数据源需求
- 设计完整的系统架构
- 制定初步实施计划

## 🤝 **联系方式**

**项目负责人**: Hermes Agent  
**最后更新**: 2026-06-10  
**文档状态**: 实施中