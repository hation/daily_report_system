#!/bin/bash

# 数据收集器测试脚本
# 测试Trae CN、OpenClaw、Hermes收集器的功能

set -e  # 遇到错误退出

echo "=================================================="
echo "🧪 数据收集器测试套件"
echo "=================================================="

# 进入项目目录
cd "$(dirname "$0")/.."

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    echo "🔧 激活虚拟环境..."
    source venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行 ./scripts/init_system.sh"
    exit 1
fi

# 检查Python依赖
echo "🔍 检查Python依赖..."
python -c "import yaml, json, sqlite3" 2>/dev/null || {
    echo "❌ 缺少Python依赖，正在安装..."
    pip install -r requirements.txt
}

# 运行测试
echo "🚀 运行数据收集器测试..."
python scripts/test_collectors.py

# 检查测试输出
TEST_OUTPUT_DIR="data/test_output"
if [ -d "$TEST_OUTPUT_DIR" ]; then
    echo ""
    echo "📁 测试输出目录内容:"
    ls -la "$TEST_OUTPUT_DIR/"
    
    echo ""
    echo "📊 测试输出统计:"
    for file in "$TEST_OUTPUT_DIR"/*.json; do
        if [ -f "$file" ]; then
            file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            item_count=$(python -c "
import json
try:
    with open('$file', 'r') as f:
        data = json.load(f)
    print(len(data))
except:
    print(0)
")
            echo "  📄 $(basename "$file"): ${file_size}字节, ${item_count}个工作项"
        fi
    done
fi

echo ""
echo "=================================================="
echo "✅ 测试脚本执行完成"
echo "=================================================="