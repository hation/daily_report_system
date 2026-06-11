#!/usr/bin/env python3
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
        "text": "🎉 授权成功测试消息\n\n✅ 恭喜！飞书授权已成功完成！\n\n📊 统一工作记录系统现在可以:\n• 自动收集工作记录\n• 生成每日报告\n• 自动推送到飞书\n\n发送时间: " + time.strftime('%Y-%m-%d %H:%M:%S')
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
    
    print(f"\n🚀 发送测试消息...")
    
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
                print("\n✅ 授权验证完成！")
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

print("\n" + "=" * 50)
print("测试完成")
