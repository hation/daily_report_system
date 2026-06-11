#!/bin/bash
# 一键复制工作报告内容到剪贴板

echo "🚀 正在复制工作报告内容到剪贴板..."
cat "./data/reports/manual_copy_report_20260611_141227.md" | pbcopy

# 检查是否复制成功
if [ $? -eq 0 ]; then
    echo "✅ 工作报告内容已成功复制到剪贴板！"
    echo ""
    echo "📱 现在可以："
    echo "1. 打开飞书应用"
    echo "2. 进入群聊: ${FEISHU_DEFAULT_CHAT_ID}"
    echo "3. 粘贴报告内容 (Command+V)"
    echo "4. 发送完成每日工作汇报"
    echo ""
    echo "📊 报告包含："
    echo "   • OpenClaw的实际工作内容"
    echo "   • 用户任务和要求"
    echo "   • 已完成的工作"
    echo "   • 解决方案调整"
    echo "   • 对话内容摘要"
else
    echo "❌ 复制失败，请手动复制文件内容"
    echo "文件位置: ./data/reports/manual_copy_report_20260611_141227.md"
fi
