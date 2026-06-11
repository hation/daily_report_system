#!/usr/bin/env python3
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
                f.write(f"授权时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
")
                f.write(f"授权码: {auth_code[:10]}...
")
                f.write(f"应用ID: ${FEISHU_APP_ID}
")
            
            print("✅ 授权信息已保存到 auth_success.txt")
            print("
🚀 现在可以测试发送消息了:")
            print("python test_authorization.py")
            
        else:
            print(f"❌ 用户token获取失败: {user_result.stderr}")
            
    else:
        print(f"❌ 应用token获取失败: {result.stderr}")
        
except Exception as e:
    print(f"❌ 授权异常: {e}")

print("
" + "=" * 50)
