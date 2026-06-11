# 📊 统一工作记录整理与定时推送系统

## 🎯 项目简介

这是一个自动化系统，用于从多个工作工具中收集每日工作记录，统一整理后于每晚7点自动推送到飞书。

## ✨ 核心功能

- **多源数据收集**：从 Trae CN、OpenClaw、Hermes Agent 等工具收集工作记录
- **智能整理分析**：自动分类、统计、分析工作内容
- **定时自动推送**：每天19:00自动生成并推送报告
- **飞书集成**：使用 Hermes 的飞书配置进行推送
- **历史追溯**：完整保存每日工作报告

## 📁 项目结构

```
daily_report_system/
├── src/                          # 源代码
│   ├── config/                   # 配置管理
│   ├── collectors/               # 数据收集器
│   ├── processors/               # 数据处理器
│   ├── formatters/               # 报告格式化器
│   ├── pushers/                  # 推送器
│   ├── schedulers/               # 任务调度器
│   └── utils/                    # 工具函数
├── tests/                        # 测试文件
├── scripts/                      # 可执行脚本
├── config/                       # 运行时配置
├── data/                         # 数据目录
├── logs/                         # 系统日志
└── docs/                         # 文档
```

## 🚀 快速开始

### 安装依赖
```bash
cd /Users/xingan/Documents/software/daily_report_system
pip install -r requirements.txt
```

### 配置系统
1. 复制配置文件模板：
```bash
cp config/system_config.yaml.template config/system_config.yaml
```

2. 编辑配置文件，设置数据源路径和推送时间

### 运行测试
```bash
python -m pytest tests/
```

### 手动运行
```bash
python src/main.py --collect --generate --push
```

## ⚙️ 配置说明

### 数据源配置
系统支持以下数据源：
- **Trae CN**: `~/.trae-cn/memory/projects/`
- **OpenClaw**: `~/.openclaw/lcm.db`
- **Hermes Agent**: `~/.hermes/sessions/` 和 `~/.hermes/memory_evaluation/`
- **Trae Work CN**: 待确认
- **Codex**: 待确认

### 飞书配置
系统使用 Hermes Agent 的飞书配置，无需重复配置。

## 📅 定时任务

系统配置为每天19:00自动运行，使用 macOS LaunchAgent。

### 查看任务状态
```bash
launchctl list | grep daily-report
```

### 手动控制
```bash
# 立即运行
launchctl start ai.xingan.daily-report

# 停止任务
launchctl stop ai.xingan.daily-report
```

## 📊 报告格式

报告包含以下部分：
1. **统计概览**：工作记录数量、时间分布、系统来源
2. **项目分布**：各项目工作量占比
3. **详细记录**：按时间排序的工作内容
4. **工作亮点**：重要成果和需要注意的问题
5. **系统健康**：Hermes记忆系统状态
6. **明日建议**：基于今日工作的建议

## 🔧 开发指南

### 添加新的数据源
1. 在 `src/collectors/` 中创建新的收集器类
2. 继承 `BaseCollector` 类
3. 实现 `collect()` 方法
4. 在配置文件中启用新数据源

### 添加新的推送渠道
1. 在 `src/pushers/` 中创建新的推送器类
2. 继承 `BasePusher` 类
3. 实现 `send()` 方法
4. 在配置文件中配置新渠道

## 📝 文档

- [需求文档](docs/requirements.md) - 项目需求和设计
- [用户指南](docs/user_guide.md) - 使用说明
- [API参考](docs/api_reference.md) - 开发接口说明
- [故障排除](docs/troubleshooting.md) - 常见问题解决

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

如有问题或建议，请：
1. 查看 [故障排除指南](docs/troubleshooting.md)
2. 检查日志文件 `logs/system.log`
3. 提交 Issue

---

**版本**: 1.0.0  
**最后更新**: 2026-06-10  
**状态**: 开发中