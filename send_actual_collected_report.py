#!/usr/bin/env python3
"""
发送实际收集的工作报告到飞书
包含从各个工具收集的真实工作内容
"""

import subprocess
import json
import time
import sys
import os

print("🚀 发送实际收集的工作报告到飞书")
print("=" * 60)

def read_actual_report():
    """读取实际工作报告"""
    report_path = "./data/reports/latest_actual_report.md"
    
    if not os.path.exists(report_path):
        print(f"❌ 报告文件不存在: {report_path}")
        return None
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    print(f"✅ 读取实际工作报告，长度: {len(report_content)} 字符")
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
                    print(f"   🎉 实际工作报告发送成功！")
                    print(f"   消息ID: {response.get('data', {}).get('message_id')}")
                    print(f"   发送时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 保存发送记录
                    with open("actual_report_sent.txt", "w", encoding="utf-8") as f:
                        f.write(f"发送时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"消息ID: {response.get('data', {}).get('message_id')}\n")
                        f.write(f"群聊ID: {message['receive_id']}\n")
                        f.write(f"报告类型: 实际收集的工作报告\n")
                        f.write(f"数据来源: Trae CN, OpenClaw, Hermes\n")
                    
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

def show_report_summary(report_content):
    """显示报告摘要"""
    print("\n📋 报告摘要:")
    print("=" * 40)
    
    lines = report_content.split('\n')
    
    # 提取关键信息
    for line in lines:
        if '报告时间:' in line:
            print(f"📅 {line}")
        elif '工作项总数:' in line:
            print(f"📋 {line}")
        elif '数据来源统计:' in line:
            print(f"📂 {line}")
            # 显示下一行的数据来源
            idx = lines.index(line)
            if idx + 1 < len(lines):
                print(f"   {lines[idx + 1]}")
    
    # 显示工作项详情
    print("\n📝 工作项详情:")
    for i, line in enumerate(lines):
        if '🔹 Trae CN:' in line:
            # 显示Trae CN的工作项
            for j in range(i+1, min(i+5, len(lines))):
                if lines[j].strip() and '...' not in lines[j]:
                    print(f"   {lines[j]}")
            break
    
    print("=" * 40)

def main():
    """主函数"""
    print("🚀 发送实际收集的工作报告到飞书")
    print("=" * 60)
    
    # 1. 读取实际工作报告
    report_content = read_actual_report()
    if not report_content:
        return False
    
    # 2. 显示报告摘要
    show_report_summary(report_content)
    
    # 3. 发送到飞书
    print("\n🚀 正在发送实际工作报告到飞书...")
    if send_to_feishu(report_content):
        print("\n" + "=" * 60)
        print("🎉 实际收集的工作报告已发送到飞书！")
        print("=" * 60)
        
        print("\n📊 发送内容包含:")
        print("   ✅ 从Trae CN收集的实际项目")
        print("   ✅ 各个项目的文件数量和活动时间")
        print("   ✅ 真实的工作记录统计")
        print("   ✅ 下次自动运行时间")
        
        print("\n📱 现在请立即检查飞书群聊:")
        print(f"   群聊ID: ${FEISHU_DEFAULT_CHAT_ID}")
        print("   查看实际收集的工作报告")
        
        return True
    else:
        print("\n❌ 发送失败")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("✅ 实际工作报告发送完成")
        print("📊 现在飞书群聊中可以看到从各个工具收集的真实工作记录了！")
    else:
        print("❌ 发送失败")
    sys.exit(0 if success else 1)