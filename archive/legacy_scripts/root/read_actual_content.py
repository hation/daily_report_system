#!/usr/bin/env python3
"""
读取实际工作内容脚本
从各个工具读取具体的工作内容，而不仅仅是统计
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
import sys

print("🔍 读取实际工作内容")
print("=" * 60)

def read_trae_cn_content():
    """读取Trae CN实际工作内容"""
    print("1. 📂 读取Trae CN实际工作内容...")
    
    trae_cn_path = '/Users/xingan/.trae-cn/memory/projects/'
    work_contents = []
    
    if os.path.exists(trae_cn_path):
        projects = os.listdir(trae_cn_path)
        
        for project in projects[:3]:  # 只读取前3个项目
            project_path = os.path.join(trae_cn_path, project)
            if os.path.isdir(project_path):
                print(f"   📁 项目: {project}")
                
                # 查找项目描述文件
                description_files = []
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        if file.endswith(('.md', '.txt')) and any(keyword in file.lower() for keyword in ['readme', 'description', 'notes', 'plan', 'todo']):
                            description_files.append(os.path.join(root, file))
                
                if description_files:
                    # 读取最近的文件
                    latest_file = max(description_files, key=lambda x: os.path.getmtime(x))
                    try:
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # 提取关键内容（前200字符）
                        preview = content[:200].replace('\n', ' ').strip()
                        if len(content) > 200:
                            preview += "..."
                        
                        work_contents.append({
                            'source': 'Trae CN',
                            'project': project,
                            'file': os.path.basename(latest_file),
                            'content_preview': preview,
                            'full_content': content[:500]  # 保存前500字符
                        })
                        
                        print(f"   📄 文件: {os.path.basename(latest_file)}")
                        print(f"   📝 内容: {preview}")
                        
                    except Exception as e:
                        print(f"   ❌ 读取文件失败: {e}")
                else:
                    print(f"   ℹ️ 未找到描述文件")
                
                print()
    
    print(f"   ✅ 从Trae CN读取到 {len(work_contents)} 个工作内容")
    return work_contents

def read_openclaw_content():
    """读取OpenClaw实际工作内容"""
    print("\n2. 📂 读取OpenClaw实际工作内容...")
    
    openclaw_db = '/Users/xingan/.openclaw/lcm.db'
    work_contents = []
    
    if os.path.exists(openclaw_db):
        try:
            conn = sqlite3.connect(openclaw_db)
            cursor = conn.cursor()
            
            # 获取表结构
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"   📊 数据库表: {[t[0] for t in tables]}")
            
            # 尝试读取消息表
            for table in ['messages', 'conversations', 'summaries']:
                if table in [t[0] for t in tables]:
                    try:
                        cursor.execute(f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT 3")
                        rows = cursor.fetchall()
                        
                        # 获取列名
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [col[1] for col in cursor.fetchall()]
                        
                        print(f"   📋 表 {table} 列: {columns}")
                        
                        for i, row in enumerate(rows):
                            # 构建内容预览
                            content_dict = {}
                            for col_idx, col_name in enumerate(columns):
                                if col_idx < len(row):
                                    value = row[col_idx]
                                    if value and isinstance(value, str) and len(value) > 0:
                                        # 只记录有内容的字段
                                        content_dict[col_name] = str(value)[:100]
                            
                            if content_dict:
                                work_contents.append({
                                    'source': 'OpenClaw',
                                    'table': table,
                                    'row_id': i + 1,
                                    'content': json.dumps(content_dict, ensure_ascii=False, indent=2)
                                })
                                
                                print(f"   📄 {table} 行{i+1}: {len(content_dict)}个字段")
                        
                    except Exception as e:
                        print(f"   ⚠️ 读取表 {table} 失败: {e}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ 连接数据库失败: {e}")
    else:
        print("   ❌ OpenClaw数据库不存在")
    
    print(f"   ✅ 从OpenClaw读取到 {len(work_contents)} 个工作内容")
    return work_contents

def read_hermes_content():
    """读取Hermes实际工作内容"""
    print("\n3. 📂 读取Hermes实际工作内容...")
    
    hermes_sessions = '/Users/xingan/.hermes/sessions/'
    work_contents = []
    
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
        
        # 按修改时间排序，取最近2个
        recent_sessions = sorted(sessions, key=lambda x: x['modified'], reverse=True)[:2]
        
        for session in recent_sessions:
            print(f"   🗂️ 会话: {session['name']}")
            
            # 查找会话文件
            session_files = []
            for root, dirs, files in os.walk(session['path']):
                for file in files:
                    if file.endswith(('.md', '.txt', '.json')):
                        session_files.append(os.path.join(root, file))
            
            if session_files:
                # 读取最近的文件
                latest_file = max(session_files, key=lambda x: os.path.getmtime(x))
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取关键内容
                    lines = content.split('\n')
                    preview_lines = []
                    for line in lines[:10]:  # 取前10行
                        line = line.strip()
                        if line and len(line) > 10:  # 只取有内容的行
                            preview_lines.append(line[:100])
                    
                    preview = ' | '.join(preview_lines[:3])  # 取前3行
                    if len(preview_lines) > 3:
                        preview += "..."
                    
                    work_contents.append({
                        'source': 'Hermes',
                        'session': session['name'],
                        'file': os.path.basename(latest_file),
                        'content_preview': preview,
                        'full_content': content[:500]  # 保存前500字符
                    })
                    
                    print(f"   📄 文件: {os.path.basename(latest_file)}")
                    print(f"   📝 内容: {preview}")
                    
                except Exception as e:
                    print(f"   ❌ 读取文件失败: {e}")
            else:
                print(f"   ℹ️ 未找到内容文件")
            
            print()
    
    print(f"   ✅ 从Hermes读取到 {len(work_contents)} 个工作内容")
    return work_contents

def generate_detailed_report(work_contents):
    """生成详细工作报告"""
    print("\n" + "=" * 60)
    print("📊 生成详细工作报告")
    print("=" * 60)
    
    if not work_contents:
        return "❌ 没有读取到任何工作内容"
    
    report = f"""📊 统一工作记录系统 - 详细工作报告
📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📋 工作内容总数: {len(work_contents)}

"""
    
    # 按来源分组
    sources = {}
    for content in work_contents:
        source = content['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(content)
    
    for source, contents in sources.items():
        report += f"🔹 {source} ({len(contents)}个):\n\n"
        
        for i, content in enumerate(contents):
            report += f"{i+1}. "
            
            if source == 'Trae CN':
                report += f"📁 项目: {content['project']}\n"
                report += f"   文件: {content['file']}\n"
                report += f"   内容: {content['content_preview']}\n"
            
            elif source == 'OpenClaw':
                report += f"📋 表: {content['table']} (行{content['row_id']})\n"
                # 解析JSON内容
                try:
                    data = json.loads(content['content'])
                    for key, value in list(data.items())[:3]:  # 显示前3个字段
                        report += f"   {key}: {value}\n"
                except:
                    report += f"   内容: {content['content'][:100]}...\n"
            
            elif source == 'Hermes':
                report += f"🗂️ 会话: {content['session']}\n"
                report += f"   文件: {content['file']}\n"
                report += f"   内容: {content['content_preview']}\n"
            
            report += "\n"
    
    report += f"""✅ 详细报告生成完成
🔍 实际工作内容已读取
📊 内容来源: {', '.join(sources.keys())}
⏰ 下次读取: 今天19:00自动运行
========================================
"""
    
    return report

def save_detailed_report(report_content):
    """保存详细报告"""
    report_dir = "./data/reports/"
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"detailed_work_report_{timestamp}.md"
    filepath = os.path.join(report_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # 保存最新版本
    latest_path = os.path.join(report_dir, "latest_detailed_report.md")
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 详细报告已保存到: {filepath}")
    print(f"📋 最新版本: {latest_path}")
    
    return filepath

def main():
    """主函数"""
    print("🔍 读取实际工作内容")
    print("=" * 60)
    
    # 读取各个工具的实际工作内容
    trae_cn_contents = read_trae_cn_content()
    openclaw_contents = read_openclaw_content()
    hermes_contents = read_hermes_content()
    
    # 合并所有工作内容
    all_contents = trae_cn_contents + openclaw_contents + hermes_contents
    
    if not all_contents:
        print("\n❌ 没有读取到任何工作内容")
        return False
    
    print(f"\n📊 总共读取到 {len(all_contents)} 个工作内容")
    print(f"   • Trae CN: {len(trae_cn_contents)} 个")
    print(f"   • OpenClaw: {len(openclaw_contents)} 个")
    print(f"   • Hermes: {len(hermes_contents)} 个")
    
    # 生成详细工作报告
    report = generate_detailed_report(all_contents)
    
    print("\n📄 详细工作报告内容:")
    print("-" * 40)
    print(report[:800] + "..." if len(report) > 800 else report)
    print("-" * 40)
    
    # 保存报告
    report_path = save_detailed_report(report)
    
    print(f"\n📋 报告统计:")
    print(f"   总字数: {len(report)} 字符")
    print(f"   工作内容: {len(all_contents)} 个")
    print(f"   数据源: {len(set(item['source'] for item in all_contents))} 个")
    
    return True

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("✅ 实际工作内容读取完成")
        print("📊 现在可以看到各个工具的实际工作内容了！")
    else:
        print("❌ 读取失败")
    sys.exit(0 if success else 1)