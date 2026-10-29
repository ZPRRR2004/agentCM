# 公开执行轨迹：Qwen3.8-27B / xhigh

- 发布者：Lottolabs（公开社区运行）。
- 来源：https://huggingface.co/datasets/Lottolabs/terminal-bench-2.1-qwen3.8-27b-traces
- 固定 revision：`dbf15f8e97ec7510c55f97fd66748888b2a27ad5`。
- 上游标注许可：MIT，见原版 `source/README.md`。
- 模型：`btbtyler09/Qwen3.8-27B-GPTQ-4bit`；OMP Agent；推理级别 xhigh。
- 导入完整 `xhigh` 主轮的 89 项任务，及 `xhigh-rerun-prove`、`xhigh-rerun-regex` 两项基础设施重跑。保留全部 91 次执行记录及其成功、失败和基础设施错误结果。
- 任务集合与本地官方 89 项任务完全一致；91 次执行的任务说明逐项核对一致（比较时仅忽略首尾空白）。
- 原版文件共 1,013 个，下载时按 Hugging Face Git blob / LFS SHA-256 校验，另保存每个文件 SHA-256。

## 目录与复现

- `source/`：原版 README、说明、轨迹、运行配置和结果；按上游相对目录保留。
- `source-manifest.json`：下载范围、revision、原版逐文件摘要。
- `normalized/`：91 条完整事件轨迹；共 8,139 个事件、7,817 个工具调用。这里保存完整轨迹，窗口由用户配置实验后生成。
- `normalization-manifest.json`：任务与轨迹覆盖、说明一致性、事件计数、每条轨迹摘要。

在仓库根目录执行 `python3 datasets/public_trajectories.py`；`--download-only` 只下载并校验，`--normalize-only` 复核本地原文后重新转换。

转换器位于 `datasets/adapters/omp.py`：从完整 `message_end` 记录保留文本、思考与工具参数，以调用 ID 对齐返回值；工具执行结束记录补齐被中断回合的返回值。保留压缩、错误和通知事件，避免重复加入流式增量和最终消息转储。原始 JSONL、行号、文件摘要、初始提示词及每次运行结果可追溯。转换在本地进行。

工作台仍只有一个 `terminal-bench-2.1` 数据集选项；其官方任务包与公开执行轨迹分别记录来源。两次重跑在轨迹名称中显式标记。实验创建时保存所选轨迹快照及公开来源版本。
