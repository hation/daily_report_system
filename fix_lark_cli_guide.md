# 🔧 修复 lark-cli keychain 问题

## 📋 问题描述
lark-cli 出现 keychain 错误：
```
keychain Get failed: keychain not initialized
```

## 🚀 解决方案

### 方案A: 重新初始化配置
```bash
# 1. 重新初始化配置
lark-cli config init

# 2. 重新绑定应用
lark-cli config bind --app-id ${FEISHU_APP_ID} --source openclaw

# 3. 重新授权
lark-cli auth login --recommend
```

### 方案B: 更新 lark-cli
```bash
# 更新到最新版本
lark-cli update

# 当前版本: 1.0.27
# 最新版本: 1.0.51
```

### 方案C: 手动复制（立即可用）
```bash
# 1. 生成报告
python manual_solution.py

# 2. 复制到剪贴板
bash copy_to_clipboard.sh

# 3. 手动粘贴到飞书
```

## 📱 飞书群聊信息
- 群聊ID: `${FEISHU_DEFAULT_CHAT_ID}`
- 应用ID: `${FEISHU_APP_ID}` (OpenClaw应用)

## ⏰ 系统状态
- ✅ 工作记录收集功能正常
- ✅ 报告生成功能正常
- ⚠️ 自动推送需要修复lark-cli
- ✅ 手动复制方案立即可用
