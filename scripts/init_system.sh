#!/bin/bash
# 每日工作报告系统初始化脚本

set -e

echo "🚀 每日工作报告系统初始化"
echo "================================"

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    echo "项目根目录：/Users/xingan/Documents/software/daily_report_system"
    exit 1
fi

# 检查Python环境
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要安装 Python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python版本: $PYTHON_VERSION"

# 创建虚拟环境
echo "📦 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境并安装依赖
echo "📥 安装依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 创建配置文件
echo "⚙️ 创建配置文件..."
if [ ! -f "config/system_config.yaml" ]; then
    if [ -f "config/system_config.yaml.template" ]; then
        cp config/system_config.yaml.template config/system_config.yaml
        echo "✅ 系统配置文件已创建: config/system_config.yaml"
        echo "   请编辑此文件以配置系统参数"
    else
        echo "⚠️  配置文件模板不存在"
    fi
else
    echo "✅ 系统配置文件已存在"
fi

if [ ! -f "config/data_sources.yaml" ]; then
    if [ -f "config/data_sources.yaml.template" ]; then
        cp config/data_sources.yaml.template config/data_sources.yaml
        echo "✅ 数据源配置文件已创建: config/data_sources.yaml"
    else
        echo "⚠️  数据源配置文件模板不存在"
    fi
else
    echo "✅ 数据源配置文件已存在"
fi

# 创建必要的空文件
echo "📄 创建必要的空文件..."
touch data/reports/.gitkeep
touch data/cache/.gitkeep
touch data/backups/.gitkeep
touch logs/.gitkeep

# 设置文件权限
echo "🔒 设置文件权限..."
chmod +x scripts/*.sh 2>/dev/null || true

# 创建测试数据目录
echo "🧪 创建测试环境..."
mkdir -p tests/test_data

# 检查数据源路径
echo "🔍 检查数据源路径..."
check_path() {
    local path=$1
    local name=$2
    
    expanded_path=$(eval echo "$path")
    if [ -e "$expanded_path" ]; then
        echo "✅ $name: $expanded_path (存在)"
        return 0
    else
        echo "⚠️  $name: $expanded_path (不存在或无法访问)"
        return 1
    fi
}

echo ""
echo "📁 数据源路径检查:"
check_path "~/.trae-cn/memory/projects/" "Trae CN"
check_path "~/.openclaw/lcm.db" "OpenClaw"
check_path "~/.hermes/sessions/" "Hermes Sessions"
check_path "~/.hermes/memory_evaluation/" "Hermes Memory Evaluation"

# 检查Hermes飞书配置
echo ""
echo "📱 检查Hermes飞书配置..."
HERMES_CONFIG="$HOME/.hermes/config.yaml"
if [ -f "$HERMES_CONFIG" ]; then
    echo "✅ Hermes配置文件存在: $HERMES_CONFIG"
    
    # 简单检查是否包含飞书配置
    if grep -q "feishu" "$HERMES_CONFIG"; then
        echo "✅ Hermes配置中包含飞书设置"
    else
        echo "⚠️  Hermes配置中未找到飞书设置"
    fi
else
    echo "⚠️  Hermes配置文件不存在: $HERMES_CONFIG"
    echo "   系统将无法使用Hermes的飞书配置"
fi

# 创建运行脚本
echo ""
echo "📜 创建运行脚本..."
cat > scripts/run_daily_report.sh << 'EOF'
#!/bin/bash
# 每日工作报告运行脚本

cd "$(dirname "$0")/.."
source venv/bin/activate

echo "🚀 启动每日工作报告系统..."
echo "时间: $(date)"
echo "================================"

# 运行主程序
python src/main.py "$@"

exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "✅ 运行成功"
else
    echo "❌ 运行失败，退出码: $exit_code"
fi

echo "================================"
echo "完成时间: $(date)"
EOF

chmod +x scripts/run_daily_report.sh

cat > scripts/test_collectors.sh << 'EOF'
#!/bin/bash
# 测试数据收集器

cd "$(dirname "$0")/.."
source venv/bin/activate

echo "🧪 测试数据收集器..."
echo "================================"

# 运行收集器测试
python -m pytest tests/test_collectors.py -v

echo "================================"
echo "测试完成"
EOF

chmod +x scripts/test_collectors.sh

# 生成初始化报告
echo ""
echo "📊 生成初始化报告..."
INIT_REPORT="logs/init_report_$(date +%Y%m%d_%H%M%S).log"
{
    echo "每日工作报告系统初始化报告"
    echo "生成时间: $(date)"
    echo "================================"
    echo ""
    echo "📁 项目目录: $(pwd)"
    echo "🐍 Python版本: $PYTHON_VERSION"
    echo "📦 虚拟环境: $(which python)"
    echo ""
    echo "✅ 已完成的项目结构:"
    find . -type d -name "__pycache__" -prune -o -type f -name "*.py" -print | head -10
    echo ""
    echo "⚙️  配置文件:"
    ls -la config/*.yaml 2>/dev/null || echo "无配置文件"
    echo ""
    echo "📁 数据目录:"
    ls -la data/
    echo ""
    echo "📜 可用脚本:"
    ls -la scripts/*.sh 2>/dev/null || echo "无脚本文件"
} > "$INIT_REPORT"

echo "✅ 初始化报告已保存: $INIT_REPORT"

# 显示下一步操作指南
echo ""
echo "🎉 初始化完成！"
echo "================================"
echo ""
echo "📋 下一步操作:"
echo ""
echo "1. 📝 编辑配置文件"
echo "   vi config/system_config.yaml"
echo "   vi config/data_sources.yaml"
echo ""
echo "2. 🧪 运行测试"
echo "   ./scripts/test_collectors.sh"
echo ""
echo "3. 🚀 手动运行系统"
echo "   ./scripts/run_daily_report.sh --dry-run"
echo ""
echo "4. ⏰ 设置定时任务（开发完成后）"
echo "   # 编辑 scripts/setup_cron.sh 并运行"
echo ""
echo "5. 📚 查看文档"
echo "   cat docs/requirements.md"
echo ""
echo "📁 重要目录:"
echo "   配置文件: config/"
echo "   数据文件: data/"
echo "   日志文件: logs/"
echo "   源代码: src/"
echo ""
echo "🔧 开发命令:"
echo "   激活虚拟环境: source venv/bin/activate"
echo "   运行测试: python -m pytest"
echo "   代码格式化: black src/"
echo ""
echo "💡 提示: 系统将在每天19:00自动运行"
echo "       首次运行前请确保配置正确"