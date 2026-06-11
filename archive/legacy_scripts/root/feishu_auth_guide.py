#!/usr/bin/env python3
"""
飞书授权引导脚本
引导用户完成 lark-cli 授权流程
"""

import subprocess
import json
import time
import os

print("🔐 飞书授权引导程序")
print("=" * 60)

def check_current_status():
    """检查当前授权状态"""
    print("1. 🔍 检查当前授权状态...")
    try:
        result = subprocess.run(
            ["lark-cli", "config", "show"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            config = json.loads(result.stdout)
            print(f"   ✅ 当前绑定应用: {config.get('appId')}")
            print(f"   👤 绑定用户: {config.get('users', '未授权')}")
            print(f"   🏢 工作空间: {config.get('workspace')}")
            return config
        else:
            print("   ❌ 无法获取配置信息")
            return None
            
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        return None

def create_test_script():
    """创建授权测试脚本"""
    print("\n2. 🧪 创建授权测试脚本...")
    
    test_script = '''#!/usr/bin/env python3
"""
飞书授权测试脚本
授权成功后运行此脚本测试
"""

import subprocess
import json
import time
import sys

print("🧪 飞书授权测试")
print("=" * 50)

# 测试消息
test_message = {
    "receive_id": "${FEISHU_DEFAULT_CHAT_ID}",
    "msg_type": "text",
    "content": json.dumps({
        "text": "🎉 授权成功测试消息\\n\\n✅ 恭喜！飞书授权已成功完成！\\n\\n📊 统一工作记录系统现在可以:\\n• 自动收集工作记录\\n• 生成每日报告\\n• 自动推送到飞书\\n\\n发送时间: " + time.strftime('%Y-%m-%d %H:%M:%S')
    }, ensure_ascii=False)
}

print(f"📱 目标群聊: {test_message['receive_id']}")
print(f"📝 消息类型: {test_message['msg_type']}")

try:
    # 构建命令
    command = [
        "lark-cli", "api", "post", "/open-apis/im/v1/messages",
        "--params", json.dumps({"receive_id_type": "chat_id"}),
        "--data", json.dumps(test_message)
    ]
    
    print(f"\\n🚀 发送测试消息...")
    
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print(f"返回码: {result.returncode}")
    
    if result.returncode == 0:
        try:
            response = json.loads(result.stdout)
            if response.get("code") == 0:
                print("🎉 测试成功！消息已发送到飞书群聊")
                print(f"📨 消息ID: {response.get('data', {}).get('message_id')}")
                print(f"⏰ 发送时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("\\n✅ 授权验证完成！")
                print("📊 现在可以运行完整的工作记录系统了:")
                print("python system_with_lark.py --run-daily --real-push")
            else:
                print(f"❌ API错误: {response.get('msg')}")
                print(f"📋 详细错误: {response.get('error', {}).get('message')}")
        except json.JSONDecodeError:
            print(f"📋 响应: {result.stdout[:300]}")
    else:
        print(f"❌ 命令执行失败")
        print(f"📋 错误输出: {result.stderr[:300]}")
        
except Exception as e:
    print(f"❌ 异常: {e}")
    import traceback
    traceback.print_exc()

print("\\n" + "=" * 50)
print("测试完成")
'''
    
    test_path = "test_authorization.py"
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    os.chmod(test_path, 0o755)
    print(f"   ✅ 测试脚本已创建: {test_path}")
    return test_path

def create_authorization_guide():
    """创建授权指南文件"""
    print("\n3. 📖 创建详细授权指南...")
    
    guide_content = """# 🔐 飞书授权完整指南

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
"""
    
    guide_path = "feishu_authorization_guide.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"   ✅ 授权指南已保存: {guide_path}")
    return guide_path

def main():
    """主函数"""
    print("🔐 飞书授权引导程序")
    print("=" * 60)
    
    # 检查当前状态
    config = check_current_status()
    
    # 创建测试脚本
    test_path = create_test_script()
    
    # 创建授权指南
    guide_path = create_authorization_guide()
    
    # 显示授权步骤
    print("\n" + "=" * 60)
    print("🚀 授权步骤")
    print("=" * 60)
    print("1. 💻 运行授权命令:")
    print("   lark-cli auth")
    print()
    print("2. 🌐 浏览器操作:")
    print("   • 复制URL到浏览器")
    print("   • 登录飞书账号")
    print("   • 授权应用访问")
    print("   • 复制授权码")
    print()
    print("3. 💻 完成授权:")
    print("   • 粘贴授权码到终端")
    print("   • 按回车确认")
    print()
    print("4. 🧪 测试授权:")
    print(f"   python {test_path}")
    print()
    print("5. 🚀 运行完整系统:")
    print("   python system_with_lark.py --run-daily --real-push")
    print("=" * 60)
    
    # 显示重要信息
    print("\n📋 重要信息:")
    print(f"• 应用ID: ${FEISHU_APP_ID} (工作记录系统)")
    print(f"• 群聊ID: ${FEISHU_DEFAULT_CHAT_ID}")
    print(f"• 当前绑定: ${FEISHU_APP_ID} (OpenClaw应用)")
    print()
    print("📖 详细指南:")
    print(f"   查看: cat {guide_path}")
    print()
    print("🎯 授权成功后:")
    print("   系统将自动每天19:00收集工作记录并推送到飞书")
    
    return True

if __name__ == "__main__":
    main()