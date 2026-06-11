#!/usr/bin/env python3
"""
直接授权脚本
帮你完成飞书授权流程
"""

import subprocess
import json
import time
import sys
import os

print("🔐 直接授权脚本")
print("=" * 60)

def run_simple_auth():
    """运行简单的授权流程"""
    print("1. 🚀 启动交互式授权...")
    
    # 尝试直接运行 lark-cli auth
    try:
        print("正在运行: lark-cli auth")
        print("=" * 40)
        
        # 使用 subprocess.Popen 来保持交互
        process = subprocess.Popen(
            ["lark-cli", "auth"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 等待一段时间
        time.sleep(3)
        
        # 尝试读取输出
        try:
            stdout, stderr = process.communicate(timeout=10)
            print("输出:", stdout[:500])
            if stderr:
                print("错误:", stderr)
        except subprocess.TimeoutExpired:
            print("授权流程已启动，请在浏览器中继续...")
            process.terminate()
        
        return True
        
    except Exception as e:
        print(f"❌ 授权失败: {e}")
        return False

def create_auth_url():
    """创建授权URL"""
    print("\n2. 🔗 生成授权URL...")
    
    # 应用信息
    app_id = "${FEISHU_APP_ID}"
    redirect_uri = "http://localhost:3000/auth/callback"
    
    # 构建授权URL
    auth_url = f"https://open.feishu.cn/open-apis/authen/v1/index?app_id={app_id}&redirect_uri={redirect_uri}"
    
    print(f"📱 授权URL: {auth_url}")
    print()
    print("📋 授权步骤:")
    print("1. 复制上面的URL到浏览器")
    print("2. 登录你的飞书账号")
    print("3. 授权应用访问权限")
    print("4. 获取授权码")
    
    # 保存到文件
    with open("auth_url.txt", "w", encoding="utf-8") as f:
        f.write(f"授权URL: {auth_url}\n")
        f.write(f"应用ID: {app_id}\n")
        f.write(f"群聊ID: ${FEISHU_DEFAULT_CHAT_ID}\n")
    
    print(f"✅ 授权URL已保存到: auth_url.txt")
    
    return auth_url

def create_auth_complete_script():
    """创建授权完成脚本"""
    print("\n3. 📝 创建授权完成脚本...")
    
    script_content = '''#!/usr/bin/env python3
"""
授权完成脚本
获取授权码后运行此脚本
"""

import subprocess
import json
import sys

print("🔐 授权完成脚本")
print("=" * 50)

# 获取授权码
auth_code = input("请输入浏览器中获取的授权码: ").strip()

if not auth_code:
    print("❌ 授权码不能为空")
    sys.exit(1)

print(f"📋 授权码: {auth_code[:10]}...")

# 使用授权码获取access_token
print("🚀 正在获取access_token...")

try:
    # 构建获取token的命令
    token_cmd = [
        "lark-cli", "api", "post", "/open-apis/auth/v3/app_access_token",
        "--data", json.dumps({
            "app_id": "${FEISHU_APP_ID}",
            "app_secret": "${FEISHU_APP_SECRET}"
        })
    ]
    
    result = subprocess.run(token_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 应用token获取成功")
        print(f"响应: {result.stdout[:200]}")
        
        # 使用授权码获取用户token
        user_token_cmd = [
            "lark-cli", "api", "post", "/open-apis/authen/v1/oidc/access_token",
            "--data", json.dumps({
                "grant_type": "authorization_code",
                "code": auth_code
            })
        ]
        
        user_result = subprocess.run(user_token_cmd, capture_output=True, text=True)
        
        if user_result.returncode == 0:
            print("🎉 用户授权成功！")
            print(f"响应: {user_result.stdout[:200]}")
            
            # 保存授权信息
            with open("auth_success.txt", "w") as f:
                f.write(f"授权时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"授权码: {auth_code[:10]}...\n")
                f.write(f"应用ID: ${FEISHU_APP_ID}\n")
            
            print("✅ 授权信息已保存到 auth_success.txt")
            print("\n🚀 现在可以测试发送消息了:")
            print("python test_authorization.py")
            
        else:
            print(f"❌ 用户token获取失败: {user_result.stderr}")
            
    else:
        print(f"❌ 应用token获取失败: {result.stderr}")
        
except Exception as e:
    print(f"❌ 授权异常: {e}")

print("\n" + "=" * 50)
'''
    
    script_path = "complete_auth.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    print(f"✅ 授权完成脚本已创建: {script_path}")
    
    return script_path

def create_manual_auth_guide():
    """创建手动授权指南"""
    print("\n4. 📖 创建手动授权指南...")
    
    guide = """# 🔐 手动飞书授权指南

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
"""
    
    with open("manual_auth_guide.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("✅ 手动授权指南已创建: manual_auth_guide.md")
    
    return "manual_auth_guide.md"

def main():
    """主函数"""
    print("🔐 直接授权脚本")
    print("=" * 60)
    
    # 1. 尝试交互式授权
    print("\n尝试方法1: 交互式授权")
    print("-" * 40)
    if run_simple_auth():
        print("✅ 交互式授权已启动")
    else:
        print("❌ 交互式授权失败，尝试方法2")
    
    # 2. 创建授权URL
    print("\n尝试方法2: 手动授权")
    print("-" * 40)
    auth_url = create_auth_url()
    
    # 3. 创建授权完成脚本
    complete_script = create_auth_complete_script()
    
    # 4. 创建手动授权指南
    guide = create_manual_auth_guide()
    
    # 5. 显示总结
    print("\n" + "=" * 60)
    print("🎯 授权方案总结")
    print("=" * 60)
    print("方案A: 交互式授权")
    print("  运行: lark-cli auth")
    print("  然后按照提示操作")
    print()
    print("方案B: 手动授权")
    print("  1. 打开浏览器访问授权URL")
    print(f"  2. 授权URL: {auth_url[:50]}...")
    print("  3. 登录并授权应用")
    print("  4. 复制授权码")
    print(f"  5. 运行: python {complete_script}")
    print()
    print("方案C: 使用现有应用")
    print("  应用ID: ${FEISHU_APP_ID}")
    print("  运行: lark-cli config bind --app-id ${FEISHU_APP_ID}")
    print()
    print("📖 详细指南:")
    print(f"  cat {guide}")
    print()
    print("🚀 授权成功后:")
    print("  运行: python test_authorization.py")
    print("  然后: python system_with_lark.py --run-daily --real-push")
    print("=" * 60)
    
    # 6. 提供一键运行命令
    print("\n💡 一键运行命令:")
    print("```bash")
    print("cd /Users/xingan/Documents/software/daily_report_system")
    print("source venv/bin/activate")
    print("python direct_auth.py")
    print("```")
    
    return True

if __name__ == "__main__":
    main()