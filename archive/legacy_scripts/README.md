# 历史脚本归档

本目录保存项目早期的一次性实验、授权、发送、修复和测试脚本。

当前正式入口为：

```bash
python3 src/main.py --run-daily --env production
./scripts/run_daily_report.sh
```

当前正式测试入口为：

```bash
python3 -m pytest
python3 -m flake8 src tests
python3 -m compileall src tests
```

## 目录说明

- `root/`：原项目根目录下的历史实验脚本。
- `scripts/`：原 `scripts/` 目录下的历史测试和修复脚本。

这些脚本仅用于追溯历史实现思路，不应作为新功能开发基础。后续维护请优先修改 `src/`、`tests/`、`scripts/run_daily_report.sh` 和 `scripts/init_system.sh`。
