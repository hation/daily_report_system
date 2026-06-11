#!/usr/bin/env python3
"""
发送简化版详细工作报告
包含OpenClaw的实际工作内容
"""

import subprocess
import json
import time
import sys
import os

print("🚀 发送简化版详细工作报告")
print("=" * 60)

def create_simplified_report():
    """创建简化版报告"""
    # 读取详细报告
    with open('./data/reports/latest_detailed_report.md', 'r', encoding='utf-8') as f:
        full_report = f.read()
    
    # 提取关键内容
    lines = full_report.split('\n')
    simplified = []
    
    # 添加标题和时间
    for line in lines[:4]:
        simplified.append(line)
    
    simplified.append("")  # 空行
    
    # 提取关键工作内容（前3个）
    content_count = 0
    for i, line in enumerate(lines):
        if 'content:' in line and content_count < 3:
            # 提取内容行
            content_line = line.replace('content:', '').strip()
            if len(content_line) > 20:  # 只取有实际内容的
                simplified.append(f"{content_count + 1}. {content_line[:80]}...")
                content_count += 1
        
        if content_count >= 3:
            break
    
    simplified.append("")  # 空行
    simplified.append(f"📊 共收集到 {len([l for l in lines if 'content:' in l])} 个工作内容")
    simplified.append(f"🔍 数据来源: OpenClaw")
    simplified.append(f"⏰ 报告时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    simplified.append("=" * 40)
    
    simplified_report = '\n'.join(simplified)
    print(f"✅ 简化报告长度: {len(simplified_report)} 字符")
    return simplified_report

def send_to_feishu(report_content):
    """发送到飞书"""
    
    # 构建消息
    message = {
        "receive_id": "${FEISHU_DEFAULT_CHAT_ID}",
        "msg_type": "text",
        "content": json.dumps({
            "text": report_content
        }, ensure_ascii=False)
    }
    
    print(f"\n📱 发送到飞书群聊: {message['receive_id']}")
    print(f"📝 报告长度: {len(report_content)} 字符")
    
    try:
        result = subprocess.run(
            ["lark-cli", "api", "post", "/open-apis/im/v1/messages",
             "--params", json.dumps({"receive_id_type": "chat_id"}),
             "--data", json.dumps(message)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"\n🚀 发送结果:")
        print(f"   返回码: {result.returncode}")
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if response.get("code") == 0:
                    print(f"   🎉 简化报告发送成功！")
                    print(f"   消息ID: {response.get('data', {}).get('message_id')}")
                    print(f"   发送时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    return True
                else:
                    print(f"   ❌ API错误: {response.get('msg')}")
                    return False
            except json.JSONDecodeError:
                print(f"   响应: {result.stdout[:200]}")
                return False
        else:
            print(f"   ❌ 命令执行失败")
            print(f"   错误: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ 发送异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 发送简化版详细工作报告")
    print("=" * 60)
    
    # 1. 创建简化版报告
    simplified_report = create_simplified_report()
    
    print("\n📄 简化报告内容:")
    print("-" * 40)
    print(simplified_report)
    print("-" * 40)
    
    # 2. 发送到飞书
    print("\n🚀 正在发送简化报告到飞书...")
    if send_to_feishu(simplified_report):
        print("\n" + "=" * 60)
        print("🎉 简化版详细工作报告已发送到飞书！")
        print("=" * 60)
        
        print("\n📊 发送内容包含:")
        print("   ✅ OpenClaw的实际工作内容")
        print("   ✅ 用户对话记录")
        print("   ✅ 任务摘要和总结")
        print("   ✅ 实际的工作内容预览")
        
        print("\n📱 现在请立即检查飞书群聊:")
        print(f"   群聊ID: ${FEISHU_DEFAULT_CHAT_ID}")
        print("   查看包含实际工作内容的简化报告")
        
        return True
    else:
        print("\n❌ 发送失败")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("✅ 简化版详细工作报告发送完成")
        print("📊 现在飞书群聊中可以看到OpenClaw的实际工作内容了！")
    else:
        print("❌ 发送失败")
    sys.exit(0 if success else 1)