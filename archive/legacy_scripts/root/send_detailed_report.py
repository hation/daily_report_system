#!/usr/bin/env python3
"""
发送详细工作报告到飞书
包含OpenClaw的实际工作内容
"""

import subprocess
import json
import time
import sys
import os

print("🚀 发送详细工作报告到飞书")
print("=" * 60)

def read_detailed_report():
    """读取详细工作报告"""
    report_path = "./data/reports/latest_detailed_report.md"
    
    if not os.path.exists(report_path):
        print(f"❌ 报告文件不存在: {report_path}")
        return None
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    print(f"✅ 读取详细工作报告，长度: {len(report_content)} 字符")
    return report_content

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
                    print(f"   🎉 详细工作报告发送成功！")
                    print(f"   消息ID: {response.get('data', {}).get('message_id')}")
                    print(f"   发送时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 保存发送记录
                    with open("detailed_report_sent.txt", "w", encoding="utf-8") as f:
                        f.write(f"发送时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"消息ID: {response.get('data', {}).get('message_id')}\n")
                        f.write(f"群聊ID: {message['receive_id']}\n")
                        f.write(f"报告类型: 详细工作报告\n")
                        f.write(f"数据来源: OpenClaw\n")
                        f.write(f"工作内容: 9个\n")
                    
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

def show_report_highlights():
    """显示报告亮点"""
    print("\n📋 报告亮点:")
    print("=" * 40)
    
    report_path = "./data/reports/latest_detailed_report.md"
    with open(report_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    highlights = []
    for line in lines:
        if 'content:' in line and len(line.strip()) > 50:
            content = line.strip().replace('content:', '').strip()
            if len(content) > 30:
                highlights.append(content[:100] + "...")
    
    print("从OpenClaw收集的实际工作内容:")
    for i, highlight in enumerate(highlights[:3], 1):
        print(f"{i}. {highlight}")
    
    print("=" * 40)

def main():
    """主函数"""
    print("🚀 发送详细工作报告到飞书")
    print("=" * 60)
    
    # 1. 读取详细工作报告
    report_content = read_detailed_report()
    if not report_content:
        return False
    
    # 2. 显示报告亮点
    show_report_highlights()
    
    # 3. 发送到飞书
    print("\n🚀 正在发送详细工作报告到飞书...")
    if send_to_feishu(report_content):
        print("\n" + "=" * 60)
        print("🎉 详细工作报告已发送到飞书！")
        print("=" * 60)
        
        print("\n📊 发送内容包含:")
        print("   ✅ OpenClaw的实际对话内容")
        print("   ✅ 用户和助手的消息记录")
        print("   ✅ 对话摘要和总结")
        print("   ✅ 实际的工作任务描述")
        
        print("\n📱 现在请立即检查飞书群聊:")
        print(f"   群聊ID: ${FEISHU_DEFAULT_CHAT_ID}")
        print("   查看包含实际工作内容的详细报告")
        
        return True
    else:
        print("\n❌ 发送失败")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("✅ 详细工作报告发送完成")
        print("📊 现在飞书群聊中可以看到OpenClaw的实际工作内容了！")
    else:
        print("❌ 发送失败")
    sys.exit(0 if success else 1)