#!/usr/bin/env python3
"""
实际收集工作内容脚本
从各个工具收集真实的工作记录
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
import sys

print("🔍 实际收集工作内容")
print("=" * 60)

def collect_trae_cn_work():
    """收集Trae CN工作内容"""
    print("1. 📂 收集Trae CN工作内容...")
    
    trae_cn_path = '/Users/xingan/.trae-cn/memory/projects/'
    work_items = []
    
    if os.path.exists(trae_cn_path):
        projects = os.listdir(trae_cn_path)
        
        for project in projects:
            project_path = os.path.join(trae_cn_path, project)
            if os.path.isdir(project_path):
                # 检查项目文件
                project_files = []
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        if file.endswith(('.md', '.txt', '.json', '.yaml', '.yml')):
                            file_path = os.path.join(root, file)
                            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                            project_files.append({
                                'file': file,
                                'path': file_path,
                                'modified': mtime.strftime('%Y-%m-%d %H:%M:%S')
                            })
                
                if project_files:
                    # 找到最近修改的文件
                    recent_files = sorted(project_files, key=lambda x: x['modified'], reverse=True)[:3]
                    
                    work_items.append({
                        'source': 'Trae CN',
                        'project': project.replace('-', '/').replace('Users/xingan/', '~/'),
                        'file_count': len(project_files),
                        'recent_activity': recent_files[0]['modified'] if recent_files else '未知',
                        'description': f'Trae CN项目: {project}，包含{len(project_files)}个文件'
                    })
        
        print(f"   ✅ 从Trae CN收集到 {len(work_items)} 个工作项")
        for item in work_items[:2]:  # 显示前2个
            print(f"   • {item['project']} ({item['file_count']}文件，最近: {item['recent_activity']})")
    else:
        print("   ❌ Trae CN目录不存在")
    
    return work_items

def collect_openclaw_work():
    """收集OpenClaw工作内容"""
    print("\n2. 📂 收集OpenClaw工作内容...")
    
    openclaw_db = '/Users/xingan/.openclaw/lcm.db'
    work_items = []
    
    if os.path.exists(openclaw_db):
        try:
            conn = sqlite3.connect(openclaw_db)
            cursor = conn.cursor()
            
            # 获取最近的对话
            cursor.execute("""
                SELECT id, created_at, summary, model 
                FROM conversations 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            conversations = cursor.fetchall()
            
            for conv in conversations:
                conv_id, created_at, summary, model = conv
                
                # 获取对话中的消息数量
                cursor.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = ?", (conv_id,))
                message_count = cursor.fetchone()[0]
                
                work_items.append({
                    'source': 'OpenClaw',
                    'conversation_id': conv_id,
                    'created_at': created_at,
                    'message_count': message_count,
                    'model': model,
                    'summary': (summary[:100] + '...') if summary else '无摘要',
                    'description': f'OpenClaw对话: {model}，{message_count}条消息'
                })
            
            conn.close()
            
            print(f"   ✅ 从OpenClaw收集到 {len(work_items)} 个工作项")
            for item in work_items[:2]:  # 显示前2个
                print(f"   • {item['model']} ({item['message_count']}消息，{item['created_at'][:10]})")
                
        except Exception as e:
            print(f"   ❌ 读取OpenClaw数据库失败: {e}")
    else:
        print("   ❌ OpenClaw数据库不存在")
    
    return work_items

def collect_hermes_work():
    """收集Hermes工作内容"""
    print("\n3. 📂 收集Hermes工作内容...")
    
    hermes_sessions = '/Users/xingan/.hermes/sessions/'
    work_items = []
    
    if os.path.exists(hermes_sessions):
        # 获取最近修改的会话
        sessions = []
        for session in os.listdir(hermes_sessions):
            session_path = os.path.join(hermes_sessions, session)
            if os.path.isdir(session_path):
                mtime = os.path.getmtime(session_path)
                sessions.append({
                    'name': session,
                    'path': session_path,
                    'modified': datetime.fromtimestamp(mtime)
                })
        
        # 按修改时间排序
        recent_sessions = sorted(sessions, key=lambda x: x['modified'], reverse=True)[:5]
        
        for session in recent_sessions:
            # 检查会话中的文件
            session_files = []
            for root, dirs, files in os.walk(session['path']):
                for file in files:
                    if file.endswith(('.md', '.txt', '.json', '.log')):
                        file_path = os.path.join(root, file)
                        session_files.append(file)
            
            work_items.append({
                'source': 'Hermes',
                'session': session['name'],
                'modified': session['modified'].strftime('%Y-%m-%d %H:%M:%S'),
                'file_count': len(session_files),
                'description': f'Hermes会话: {session["name"]}，{len(session_files)}个文件'
            })
        
        print(f"   ✅ 从Hermes收集到 {len(work_items)} 个工作项")
        for item in work_items[:2]:  # 显示前2个
            print(f"   • {item['session']} ({item['file_count']}文件，修改: {item['modified'][:16]})")
    else:
        print("   ❌ Hermes会话目录不存在")
    
    return work_items

def generate_actual_report(work_items):
    """生成实际工作报告"""
    print("\n" + "=" * 60)
    print("📊 生成实际工作报告")
    print("=" * 60)
    
    # 按来源统计
    sources = {}
    for item in work_items:
        source = item['source']
        sources[source] = sources.get(source, 0) + 1
    
    # 生成报告
    report = f"""📊 统一工作记录系统 - 实际工作报告
📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📋 工作项总数: {len(work_items)}

📂 数据来源统计:
"""
    
    for source, count in sources.items():
        report += f"  • {source}: {count}个\n"
    
    report += "\n📝 工作项详情:\n"
    
    # 按来源分组显示
    grouped_items = {}
    for item in work_items:
        source = item['source']
        if source not in grouped_items:
            grouped_items[source] = []
        grouped_items[source].append(item)
    
    item_count = 0
    for source, items in grouped_items.items():
        report += f"\n🔹 {source}:\n"
        for i, item in enumerate(items[:3]):  # 每个来源显示前3个
            item_count += 1
            if 'project' in item:
                report += f"   {item_count}. 📁 {item['project']}\n"
                report += f"      文件数: {item['file_count']}，最近活动: {item['recent_activity']}\n"
            elif 'conversation_id' in item:
                report += f"   {item_count}. 💬 {item['model']}\n"
                report += f"      消息数: {item['message_count']}，创建时间: {item['created_at'][:10]}\n"
            elif 'session' in item:
                report += f"   {item_count}. 🗂️ {item['session']}\n"
                report += f"      文件数: {item['file_count']}，修改时间: {item['modified'][:16]}\n"
        
        if len(items) > 3:
            report += f"      ... 还有 {len(items) - 3} 个工作项\n"
    
    report += f"""
✅ 报告生成完成
🔍 数据来源: Trae CN, OpenClaw, Hermes
📊 实际工作项: {len(work_items)} 个
⏰ 下次收集: 今天19:00自动运行
========================================
"""
    
    return report

def save_report(report_content):
    """保存报告"""
    report_dir = "./data/reports/"
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"actual_work_report_{timestamp}.md"
    filepath = os.path.join(report_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # 保存最新版本
    latest_path = os.path.join(report_dir, "latest_actual_report.md")
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 报告已保存到: {filepath}")
    print(f"📋 最新版本: {latest_path}")
    
    return filepath

def main():
    """主函数"""
    print("🔍 实际收集工作内容")
    print("=" * 60)
    
    # 收集各个工具的工作内容
    trae_cn_items = collect_trae_cn_work()
    openclaw_items = collect_openclaw_work()
    hermes_items = collect_hermes_work()
    
    # 合并所有工作项
    all_work_items = trae_cn_items + openclaw_items + hermes_items
    
    if not all_work_items:
        print("\n❌ 没有收集到任何工作内容")
        return False
    
    print(f"\n📊 总共收集到 {len(all_work_items)} 个工作项")
    print(f"   • Trae CN: {len(trae_cn_items)} 个")
    print(f"   • OpenClaw: {len(openclaw_items)} 个")
    print(f"   • Hermes: {len(hermes_items)} 个")
    
    # 生成实际工作报告
    report = generate_actual_report(all_work_items)
    
    print("\n📄 实际工作报告内容:")
    print("-" * 40)
    print(report[:500] + "..." if len(report) > 500 else report)
    print("-" * 40)
    
    # 保存报告
    report_path = save_report(report)
    
    print(f"\n📋 报告统计:")
    print(f"   总字数: {len(report)} 字符")
    print(f"   工作项: {len(all_work_items)} 个")
    print(f"   数据源: {len(set(item['source'] for item in all_work_items))} 个")
    
    return True

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("✅ 实际工作内容收集完成")
        print("📊 现在可以看到从各个工具收集的真实工作记录了！")
    else:
        print("❌ 收集失败")
    sys.exit(0 if success else 1)