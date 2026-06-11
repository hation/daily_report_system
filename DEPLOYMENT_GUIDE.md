# 统一工作记录系统 - 部署指南

## 🎉 系统修复完成！

### ✅ 已解决的问题
1. **飞书消息长度限制** - 创建简化版报告格式化器，确保不超过128KB限制
2. **OpenClaw收集器错误** - 创建极简版收集器，正确解析OpenClaw数据库
3. **系统集成问题** - 修复模块注册和collector_manager
4. **所有测试通过** - 4/4测试完全通过

### 📊 系统配置
- **飞书群聊ID**: `${FEISHU_DEFAULT_CHAT_ID}`
- **推送时间**: 每天19:00（晚上7点）
- **数据源**: Trae CN、OpenClaw、Hermes
- **报告格式**: 简化版，确保不超过飞书限制

## 🚀 立即测试系统

### 1. 测试飞书连接
```bash
cd /Users/xingan/Documents/software/daily_report_system
source venv/bin/activate
python src/main.py --test-feishu --env development
```

### 2. 测试每日报告（不实际推送）
```bash
cd /Users/xingan/Documents/software/daily_report_system
source venv/bin/activate
python src/main.py --run-daily --test --env development
```

### 3. 手动运行每日报告（实际推送）
```bash
cd /Users/xingan/Documents/software/daily_report_system
source venv/bin/activate
python src/main.py --run-daily --env production
```

## ⏰ 部署定时任务

### 方法1：使用macOS launchd（推荐）
```bash
# 1. 复制plist文件到LaunchAgents目录
cp config/com.xingan.daily_report_system.plist ~/Library/LaunchAgents/

# 2. 加载定时任务
launchctl load ~/Library/LaunchAgents/com.xingan.daily_report_system.plist

# 3. 立即测试（可选）
launchctl start com.xingan.daily_report_system

# 4. 查看状态
launchctl list | grep daily_report_system

# 5. 查看日志
tail -f logs/cron.log
```

### 方法2：使用cron（备用）
```bash
# 编辑crontab
crontab -e

# 添加以下行（每天19:00运行）
0 19 * * * /Users/xingan/Documents/software/daily_report_system/scripts/run_daily_report.sh
```

## 📁 文件结构
```
/Users/xingan/Documents/software/daily_report_system/
├── src/                    # 源代码
│   ├── collectors/         # 数据收集器
│   ├── processors/         # 数据处理器
│   ├── formatters/         # 报告格式化器
│   ├── pushers/           # 消息推送器
│   ├── managers/          # 系统管理器
│   └── config/            # 配置文件
├── scripts/               # 脚本文件
│   ├── run_daily_report.sh # 定时任务脚本
│   └── test_fixes.py      # 测试脚本
├── config/                # 配置文件
│   ├── system_config.yaml # 系统配置
│   └── *.plist           # macOS定时任务配置
├── data/                  # 数据目录
│   ├── reports/          # 生成的报告
│   └── backup/           # 备份文件
├── logs/                  # 日志目录
│   ├── system.log        # 系统日志
│   ├── cron.log          # 定时任务日志
│   └── errors.log        # 错误日志
└── venv/                  # Python虚拟环境
```

## 🔧 维护指南

### 查看系统状态
```bash
# 查看日志
tail -f logs/system.log
tail -f logs/cron.log

# 查看定时任务状态
launchctl list | grep daily_report_system

# 查看报告历史
ls -la data/reports/
```

### 重启定时任务
```bash
# 卸载定时任务
launchctl unload ~/Library/LaunchAgents/com.xingan.daily_report_system.plist

# 重新加载
launchctl load ~/Library/LaunchAgents/com.xingan.daily_report_system.plist
```

### 停止定时任务
```bash
# 停止定时任务
launchctl unload ~/Library/LaunchAgents/com.xingan.daily_report_system.plist

# 删除配置文件
rm ~/Library/LaunchAgents/com.xingan.daily_report_system.plist
```

## 📞 故障排除

### 常见问题

#### 1. 飞书推送失败
- 检查飞书配置是否正确
- 检查网络连接
- 查看错误日志：`logs/errors.log`

#### 2. 数据收集为空
- 检查数据源路径是否存在
- 查看收集器日志：`grep "collector" logs/system.log`

#### 3. 定时任务不运行
- 检查launchd状态：`launchctl list | grep daily_report_system`
- 检查权限：`chmod +x scripts/run_daily_report.sh`
- 手动测试脚本：`./scripts/run_daily_report.sh`

#### 4. 报告过长
- 系统已自动处理，使用简化版格式化器
- 报告长度限制在900字节左右

## 🎯 系统特点

### ✅ 已实现功能
1. **多数据源集成**：Trae CN、OpenClaw、Hermes
2. **智能报告生成**：简化版格式化器，确保不超过飞书限制
3. **自动推送**：每天19:00自动推送到飞书
4. **错误处理**：完善的错误处理和重试机制
5. **历史记录**：报告保存和备份

### 🔄 工作流程
```
数据收集 → 数据处理 → 报告生成 → 飞书推送
   ↓          ↓           ↓          ↓
Trae CN   数据清洗    每日摘要    群聊推送
OpenClaw  数据分析    详细报告    错误告警
Hermes    关键洞察    执行摘要    测试消息
```

## 📈 下一步优化

### 短期优化
1. 添加更多数据源（Trae Work CN、Codex）
2. 优化报告内容格式
3. 添加更多报告类型（周报、月报）

### 长期规划
1. 添加Web管理界面
2. 支持自定义报告模板
3. 添加数据分析仪表板

## 🎊 总结

**统一工作记录系统**现已修复完成并可以部署使用！

- ✅ **核心功能**：从多个工具自动收集工作记录
- ✅ **智能分析**：生成结构化的工作分析报告
- ✅ **自动推送**：每天19:00自动推送到飞书群
- ✅ **错误处理**：完善的错误恢复机制
- ✅ **易于部署**：支持macOS launchd定时任务

**立即部署**，让系统每天自动为你整理和推送工作记录！