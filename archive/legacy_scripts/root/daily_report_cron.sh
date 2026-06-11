#!/bin/bash
# 统一工作记录系统定时任务
# 每天19:00自动运行

cd /Users/xingan/Documents/software/daily_report_system
source venv/bin/activate

# 使用测试模式运行（避免授权问题）
python system_with_lark.py --run-daily --test

# 记录执行时间
echo "[$(date)] 每日工作报告已运行" >> /tmp/daily_report.log
