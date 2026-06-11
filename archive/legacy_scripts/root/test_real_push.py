#!/usr/bin/env python3
"""
实际飞书推送测试
使用 lark-cli 发送测试消息
"""

import subprocess
import json
import sys

def test_real_push():
    """测试实际推送"""
    print("🚀 测试实际飞书推送")
    print("=" * 60)
    
    # 测试消息
    test_message = {
        "receive_id": "${FEISHU_DEFAULT_CHAT_ID}",
        "msg_type": "text",
        "content": json.dumps({
            "text": "🚀 统一工作记录系统测试\n\n✅ 这是通过 lark-cli 发送的实际测试消息！\n\n系统状态: 正常\n测试时间: 2026-06-11 09:30:00\n版本: v1.0"
        }, ensure_ascii=False)
    }
    
    # 构建命令
    command = [
        'lark-cli', 'api', 'post', '/open-apis/im/v1/messages',
        '--params', json.dumps({"receive_id_type": "chat_id"}),
        '--data', json.dumps(test_message)
    ]
    
    print(f"执行命令: {' '.join(command[:6])} ...")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 命令执行成功")
            try:
                response = json.loads(result.stdout)
                print(f"响应: {json.dumps(response, indent=2)}")
                
                if response.get("code") == 0:
                    print("🎉 实际推送测试成功！")
                    print(f"消息ID: {response.get('data', {}).get('message_id')}")
                    return True
                else:
                    print(f"❌ API返回错误: {response.get('msg')}")
                    return False
            except json.JSONDecodeError:
                print(f"响应: {result.stdout[:500]}")
                return False
        else:
            print(f"❌ 命令执行失败")
            print(f"错误: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 执行超时")
        return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

if __name__ == "__main__":
    success = test_real_push()
    sys.exit(0 if success else 1)
