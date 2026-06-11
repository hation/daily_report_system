#!/bin/bash
# 统一工作记录系统 - 每日定时任务
# 每天19:00自动运行

cd "/Users/xingan/Documents/software/daily_report_system"
source venv/bin/activate

echo "[$(date)] 开始运行每日工作报告" >> /tmp/daily_report.log

# 运行系统
python system_with_lark.py --run-daily --real-push

echo "[$(date)] 每日工作报告完成" >> /tmp/daily_report.log
