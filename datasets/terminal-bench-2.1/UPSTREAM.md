# Terminal-Bench 2.1 官方数据来源

| 项目 | 记录 |
| --- | --- |
| 官方仓库 | https://github.com/harbor-framework/terminal-bench-2-1 |
| 固定 commit | `7131e4375048a0e408a8fb404b5f499d726b695b` |
| 下载日期 | 2026-10-16 |
| 任务数 | 89 |
| 仓库原版文件数 | 1,101 |
| 原版文件字节数 | 59,252,655 |
| 本地原版目录 | `source/` |
| 许可文件 | `source/LICENSE`，与上游原文一起保留 |
| 本地文件改动 | 上游文件逐字节保留；通过官方 Git 树 blob 摘要验证 |

官方发布说明：[Terminal-Bench 2.1](https://www.tbench.ai/news/terminal-bench-2-1)。

下载使用固定 commit 的完整归档，保留任务说明、配置、环境、参考解法、验证脚本、附属数据，以及仓库根目录文件。每个任务的 `instruction.md` 和 `task.toml` 随原版目录保留；执行任务后生成的 Agent 轨迹属于实验产物。

下载归档 SHA-256 和逐文件 Git blob SHA-1 见 [source-manifest.json](source-manifest.json)。从仓库根目录运行 `python3 datasets/download.py --verify-only` 可重新校验。

2026-10-16 按用户要求，数据集集中到代码仓库根目录的 `datasets/`，原先导入的 20 任务子集及其 19 条规范化轨迹已移出仓库。工作台唯一注册项为 `terminal-bench-2.1` 的完整官方任务包。
