# 🔐 飞书授权完整指南

## 📋 当前状态
- 已绑定应用: ${FEISHU_APP_ID} (OpenClaw应用)
- 绑定用户: 甘鑫 (ou_8f9d09920c960f0cc4fc1218f2960ff2)
- 需要完成: 用户授权

## 🚀 授权步骤

### 步骤1: 启动授权流程
```bash
# 运行授权命令
lark-cli auth
```

### 步骤2: 浏览器操作
1. **复制显示的URL**到浏览器
2. **登录你的飞书账号**
3. **授权应用访问权限**
4. **复制授权码**回到终端

### 步骤3: 完成授权
1. **粘贴授权码**到终端
2. **按回车确认**
3. **等待授权完成**

## 🧪 测试授权
授权成功后运行:
```bash
# 测试发送消息
python test_authorization.py
```

## 📱 目标群聊
- 群聊ID: `${FEISHU_DEFAULT_CHAT_ID}`
- 应用ID: `${FEISHU_APP_ID}` (可选)

## 🔧 备用方案
如果遇到问题，尝试:
```bash
# 重新绑定应用
lark-cli config bind --app-id ${FEISHU_APP_ID} --force-init

# 或使用现有应用
lark-cli config bind --app-id ${FEISHU_APP_ID} --force-init
```

## 📞 需要帮助?
如果授权过程中遇到问题，请:
1. 截图错误信息
2. 提供终端输出
3. 我会帮你分析解决
