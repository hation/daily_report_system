# 🔐 手动飞书授权指南

## 🚀 授权步骤

### 步骤1: 打开授权页面
打开浏览器访问:
```
https://open.feishu.cn/open-apis/authen/v1/index?app_id=${FEISHU_APP_ID}&redirect_uri=http://localhost:3000/auth/callback
```

### 步骤2: 登录并授权
1. **登录你的飞书账号**
2. **授权应用访问权限**
3. **复制授权码**

### 步骤3: 完成授权
运行授权完成脚本:
```bash
python complete_auth.py
```

然后输入你复制的授权码。

### 步骤4: 测试授权
授权成功后运行:
```bash
python test_authorization.py
```

### 步骤5: 运行完整系统
```bash
python system_with_lark.py --run-daily --real-push
```

## 📋 应用信息
- **应用ID**: `${FEISHU_APP_ID}`
- **应用密钥**: `${FEISHU_APP_SECRET}`
- **目标群聊**: `${FEISHU_DEFAULT_CHAT_ID}`

## 🔧 备用方法
如果上述方法失败，可以:
1. 使用现有应用 `${FEISHU_APP_ID}`
2. 运行 `lark-cli auth` 交互式授权
3. 联系我获取更多帮助

## 📞 需要帮助?
提供:
1. 浏览器截图
2. 错误信息
3. 终端输出
