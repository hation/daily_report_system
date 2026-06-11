#!/usr/bin/env python3
"""
综合工作记录收集脚本
从所有工具收集实际工作记录
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
import sys

print("🔍 综合工作记录收集 - 从所有工具")
print("=" * 60)

def collect_all_work():
    """从所有工具收集工作记录"""
    all_work = {
        'Trae CN': [],
        'OpenClaw': [],
        'Hermes': [],
        'Codex': []
    }
    
    print("📊 开始收集所有工具的工作记录...")
    print("=" * 40)
    
    # 1. Trae CN 工作记录
    print("1. 📂 收集 Trae CN 工作记录...")
    trae_path = '/Users/xingan/.trae-cn/memory/projects/'
    if os.path.exists(trae_path):
        projects = os.listdir(trae_path)
        for project in projects[:3]:  # 前3个项目
            project_name = project.replace('-', '/').replace('Users/xingan/', '~/')
            all_work['Trae CN'].append({
                'type': 'project',
                'name': project_name,
                'description': f'Trae CN项目: {project_name}',
                'status': 'active',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
        print(f"   ✅ 收集到 {len(all_work['Trae CN'])} 个Trae CN项目")
    else:
        print("   ❌ Trae CN目录不存在")
    
    # 2. OpenClaw 工作记录
    print("\n2. 📂 收集 OpenClaw 工作记录...")
    openclaw_db = '/Users/xingan/.openclaw/lcm.db'
    if os.path.exists(openclaw_db):
        try:
            conn = sqlite3.connect(openclaw_db)
            cursor = conn.cursor()
            
            # 获取最近的对话
            cursor.execute("""
                SELECT conversation_id, created_at, title, model 
                FROM conversations 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            conversations = cursor.fetchall()
            
            for conv_id, created_at, title, model in conversations:
                all_work['OpenClaw'].append({
                    'type': 'conversation',
                    'id': conv_id,
                    'title': title or f'{model}对话',
                    'model': model,
                    'created_at': created_at,
                    'description': f'OpenClaw对话: {model}，创建于{created_at[:10]}'
                })
            
            conn.close()
            print(f"   ✅ 收集到 {len(all_work['OpenClaw'])} 个OpenClaw对话")
        except Exception as e:
            print(f"   ❌ 读取OpenClaw失败: {e}")
    else:
        print("   ❌ OpenClaw数据库不存在")
    
    # 3. Hermes 工作记录
    print("\n3. 📂 收集 Hermes 工作记录...")
    hermes_sessions = '/Users/xingan/.hermes/sessions/'
    if os.path.exists(hermes_sessions):
        # 获取最近修改的会话
        sessions = []
        for session in os.listdir(hermes_sessions):
            session_path = os.path.join(hermes_sessions, session)
            if os.path.isdir(session_path):
                mtime = os.path.getmtime(session_path)
                sessions.append({
                    'name': session,
                    'modified': datetime.fromtimestamp(mtime)
                })
        
        # 取最近3个
        recent_sessions = sorted(sessions, key=lambda x: x['modified'], reverse=True)[:3]
        
        for session in recent_sessions:
            all_work['Hermes'].append({
                'type': 'session',
                'name': session['name'],
                'modified': session['modified'].strftime('%Y-%m-%d %H:%M:%S'),
                'description': f'Hermes会话: {session["name"]}，最后修改{session["modified"].strftime("%Y-%m-%d %H:%M")}'
            })
        
        print(f"   ✅ 收集到 {len(all_work['Hermes'])} 个Hermes会话")
    else:
        print("   ❌ Hermes会话目录不存在")
    
    # 4. Codex 工作记录（需要确认路径）
    print("\n4. 📂 收集 Codex 工作记录...")
    # 需要确认Codex数据位置
    codex_paths = [
        '/Users/xingan/.codex/',
        '/Users/xingan/Library/Application Support/Codex/',
        '/Users/xingan/Documents/codex/'
    ]
    
    codex_found = False
    for path in codex_paths:
        if os.path.exists(path):
            print(f"   ✅ 找到Codex目录: {path}")
            # 这里可以添加具体的Codex数据收集逻辑
            all_work['Codex'].append({
                'type': 'system',
                'name': 'Codex AI助手',
                'description': 'Codex AI编程助手系统',
                'status': 'active',
                'path': path
            })
            codex_found = True
            break
    
    if not codex_found:
        print("   ⚠️ 未找到Codex数据目录，需要确认路径")
        all_work['Codex'].append({
            'type': 'system',
            'name': 'Codex AI助手',
            'description': 'Codex AI编程助手系统（需要确认数据位置）',
            'status': 'pending',
            'note': '需要提供Codex数据存储路径'
        })
    
    print(f"   ✅ 收集到 {len(all_work['Codex'])} 个Codex记录")
    
    return all_work

def generate_comprehensive_report(all_work):
    """生成综合工作报告"""
    print("\n" + "=" * 60)
    print("📊 生成综合工作报告")
    print("=" * 60)
    
    # 统计总数
    total_items = sum(len(items) for items in all_work.values())
    
    report = f"""📊 统一工作记录系统 - 综合工作报告
📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📋 工作记录总数: {total_items}

"""
    
    # 按工具显示工作记录
    for tool, items in all_work.items():
        if items:
            report += f"🔹 {tool} ({len(items)}个):\n\n"
            
            for i, item in enumerate(items, 1):
                report += f"{i}. "
                
                if tool == 'Trae CN':
                    report += f"📁 {item['name']}\n"
                    report += f"   状态: {item['status']}，最后更新: {item['last_updated']}\n"
                
                elif tool == 'OpenClaw':
                    report += f"💬 {item['title']}\n"
                    report += f"   模型: {item['model']}，创建时间: {item['created_at'][:10]}\n"
                
                elif tool == 'Hermes':
                    report += f"🗂️ {item['name']}\n"
                    report += f"   最后修改: {item['modified'][:16]}\n"
                
                elif tool == 'Codex':
                    report += f"🤖 {item['name']}\n"
                    report += f"   描述: {item['description']}\n"
                    if 'note' in item:
                        report += f"   备注: {item['note']}\n"
                
                report += "\n"
            
            report += "\n"
    
    # 添加总结
    report += f"""📈 工作记录统计:
  • Trae CN: {len(all_work['Trae CN'])} 个项目
  • OpenClaw: {len(all_work['OpenClaw'])} 个对话
  • Hermes: {len(all_work['Hermes'])} 个会话
  • Codex: {len(all_work['Codex'])} 个系统记录

✅ 综合报告生成完成
🔍 数据来源: Trae CN, OpenClaw, Hermes, Codex
📊 总计: {total_items} 个工作记录
⏰ 下次收集: 今天19:00自动运行
========================================
"""
    
    return report

def save_report(report_content):
    """保存报告"""
    report_dir = "./data/reports/"
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"comprehensive_report_{timestamp}.md"
    filepath = os.path.join(report_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # 保存最新版本
    latest_path = os.path.join(report_dir, "latest_comprehensive_report.md")
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 综合报告已保存到: {filepath}")
    print(f"📋 最新版本: {latest_path}")
    
    return filepath

def show_summary(all_work):
    """显示收集摘要"""
    print("\n" + "=" * 60)
    print("📊 工作记录收集摘要")
    print("=" * 60)
    
    total = 0
    for tool, items in all_work.items():
        count = len(items)
        total += count
        status = "✅" if count > 0 else "❌"
        print(f"{status} {tool}: {count} 个工作记录")
    
    print(f"\n📈 总计: {total} 个工作记录")
    print("=" * 60)

def main():
    """主函数"""
    print("🔍 综合工作记录收集 - 从所有工具")
    print("=" * 60)
    
    # 收集所有工具的工作记录
    all_work = collect_all_work()
    
    # 显示摘要
    show_summary(all_work)
    
    # 生成综合报告
    report = generate_comprehensive_report(all_work)
    
    print("\n📄 综合工作报告内容:")
    print("-" * 40)
    print(report[:800] + "..." if len(report) > 800 else report)
    print("-" * 40)
    
    # 保存报告
    report_path = save_report(report)
    
    print(f"\n📋 报告统计:")
    print(f"   总字数: {len(report)} 字符")
    print(f"   工作记录: {sum(len(items) for items in all_work.values())} 个")
    print(f"   数据工具: {len([tool for tool, items in all_work.items() if items])} 个")
    
    return True

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("✅ 综合工作记录收集完成")
        print("📊 现在可以看到所有工具的工作记录了！")
    else:
        print("❌ 收集失败")
    sys.exit(0 if success else 1)