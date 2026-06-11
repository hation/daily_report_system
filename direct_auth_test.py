#!/usr/bin/env python3
"""
直接授权测试
检查并完成授权流程
"""

import subprocess
import json
import time
import sys

print("🔐 直接授权测试")
print("=" * 50)

def check_auth_status():
    """检查授权状态"""
    print("1. 🔍 检查授权状态...")
    
    try:
        result = subprocess.run(
            ["lark-cli", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"   ✅ 应用ID: {data.get('appId')}")
            print(f"   👤 用户: {data.get('userName')}")
            print(f"   🔑 身份: {data.get('identity')}")
            print(f"   📝 状态: {data.get('note', '未知')}")
            
            if "Token does not exist" in data.get('note', ''):
                print("   ❌ Token不存在，需要重新登录")
                return False
            else:
                print("   ✅ Token存在")
                return True
        else:
            print("   ❌ 无法获取授权状态")
            return False
            
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        return False

def complete_device_flow():
    """完成设备流授权"""
    print("\n2. 🔄 完成设备流授权...")
    
    # 设备码
    device_code = "Oz5H4Tm71XrCraJ0rXg9udvNCHtvzN23GWOOOOOOOOOOsqJKGROOOOOt.fV_Mco6uaHQm9nXb7IjYxZ5yhPPF3z7Uun3QveydifE"
    
    print(f"   使用设备码: {device_code[:20]}...")
    print("   正在等待授权完成...")
    
    try:
        # 启动授权轮询
        process = subprocess.Popen(
            ["lark-cli", "auth", "login", "--device-code", device_code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 等待一段时间
        for i in range(10):
            print(f"   等待中... {i+1}/10")
            
            # 检查进程状态
            return_code = process.poll()
            if return_code is not None:
                stdout, stderr = process.communicate()
                print(f"   进程结束，返回码: {return_code}")
                
                if return_code == 0:
                    print("   ✅ 授权成功完成！")
                    return True
                else:
                    print(f"   ❌ 授权失败: {stderr[:100]}")
                    return False
            
            time.sleep(2)
        
        # 超时
        print("   ⏰ 等待超时")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"   ❌ 授权异常: {e}")
        return False

def test_send_message():
    """测试发送消息"""
    print("\n3. 🧪 测试发送消息...")
    
    test_message = {
        "receive_id": "${FEISHU_DEFAULT_CHAT_ID}",
        "msg_type": "text",
        "content": json.dumps({
            "text": f"🎉 授权测试成功！\\n\\n✅ 飞书授权已完成！\\n\\n⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n📱 来自: 统一工作记录系统"
        }, ensure_ascii=False)
    }
    
    print(f"   目标群聊: {test_message['receive_id']}")
    
    try:
        result = subprocess.run(
            ["lark-cli", "api", "post", "/open-apis/im/v1/messages",
             "--params", json.dumps({"receive_id_type": "chat_id"}),
             "--data", json.dumps(test_message)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"   返回码: {result.returncode}")
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if response.get("code") == 0:
                    print("   🎉 消息发送成功！")
                    print(f"   消息ID: {response.get('data', {}).get('message_id')}")
                    return True
                else:
                    print(f"   ❌ API错误: {response.get('msg')}")
                    return False
            except:
                print(f"   响应: {result.stdout[:200]}")
                return False
        else:
            print(f"   ❌ 命令失败: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ 发送异常: {e}")
        return False

def main():
    """主函数"""
    print("🔐 直接授权测试")
    print("=" * 50)
    
    # 1. 检查授权状态
    if not check_auth_status():
        print("\n🔍 需要完成授权")
        
        # 2. 完成设备流授权
        if complete_device_flow():
            print("\n✅ 授权流程完成")
        else:
            print("\n❌ 授权流程失败")
            return False
    
    # 3. 再次检查授权状态
    print("\n4. 🔍 授权后状态检查...")
    if check_auth_status():
        print("   ✅ 授权状态正常")
    else:
        print("   ❌ 授权状态异常")
        return False
    
    # 4. 测试发送消息
    print("\n5. 🚀 测试发送消息...")
    if test_send_message():
        print("\n🎉 测试成功！系统可以正常工作了！")
        print("\n📊 现在可以运行完整系统:")
        print("python system_with_lark.py --run-daily --real-push")
        return True
    else:
        print("\n❌ 测试失败，需要进一步调试")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 50)
    if success:
        print("✅ 所有测试完成")
    else:
        print("❌ 测试失败")
    sys.exit(0 if success else 1)