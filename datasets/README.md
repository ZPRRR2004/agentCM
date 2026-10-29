# 数据集

本目录统一保存项目使用的数据集、来源记录、下载与校验工具。当前只注册官方完整的 `terminal-bench-2.1`。

| 数据集 | 官方任务 | 原版文件 | 固定 commit |
| --- | --- | --- | --- |
| terminal-bench-2.1 | 89 | 1,101 | `7131e4375048a0e408a8fb404b5f499d726b695b` |

## 目录

```text
datasets/
├── README.md
├── catalog.json                     # 工作台唯一的数据集注册入口
├── download.py                      # 下载固定官方版本、逐文件校验
├── public_trajectories.py            # 固定公开完整运行的下载与转换
├── adapters/omp.py                  # OMP 原文到完整事件轨迹
├── tests/                           # 原版完整性与事件保真测试
└── terminal-bench-2.1/
    ├── UPSTREAM.md                  # 官方来源、版本、清理记录
    ├── source-manifest.json         # 归档 SHA-256、逐文件 Git blob 摘要
    └── source/                      # 官方仓库完整内容，Git 忽略
        ├── LICENSE
        ├── README.md
        ├── configs/
        ├── leaderboard/
        └── tasks/
            └── <89 个官方任务>/
                ├── instruction.md
                ├── task.toml
                ├── environment/
                ├── solution/
                └── tests/
```

上游文件逐字节保留；项目自己的配置、清单和说明放在 `source/` 外。源码快照不包含嵌套 Git 仓库。脚本执行需要 Python 3.12+。

## 下载与校验

在代码仓库根目录执行：

```bash
python3 datasets/download.py
python3 datasets/download.py --verify-only
python3 -m unittest discover -s datasets/tests -v
```

下载器使用官方仓库的固定 commit 获取完整归档和 Git 树，核对每个文件的 Git blob SHA-1、完整文件清单、89 个任务数量，以及每个任务的说明、配置、环境、参考解法和测试目录。额外记录下载归档的 SHA-256。

数据集注册格式为 `agentcm-datasets/v2`。工作台通过 `format: harbor-tasks` 读取原版任务，在“数据集”页面展示说明、配置、文件清单、类别与难度。任务脚本按文本读取。

## 与实验的连接

官方数据集提供任务说明、运行环境、参考解法和验证脚本。Agent 执行任务产生轨迹；已有轨迹进入规范化与切分流程，切分参数由用户填写，并作为独立实验保存，再选择其结果开展谓词发现。

## 子集清理：2026-10-16

按用户要求移除原有 20 任务执行记录、19 条规范化轨迹及旧数据集配置。旧目录 `graph-construction/datasets/` 移至系统废纸篓 `AgentCM-subset-datasets-20261016/`。当前数据源统一为本目录中的官方完整 89 任务版本。

## 公开执行轨迹：2026-10-16

同一数据集已接入 [Lottolabs 的 Qwen3.8-27B 公开运行](https://huggingface.co/datasets/Lottolabs/terminal-bench-2.1-qwen3.8-27b-traces)：完整主轮 89 条轨迹与两条基础设施重跑，共 91 条、8,139 个事件。任务集合与每条任务说明均和本地官方版本匹配。保留全部成功和失败记录。

文件集中在 `terminal-bench-2.1/trajectories/qwen3.8-27b-xhigh/`，其中 `source/` 存放 1,013 个原版文件，`normalized/` 存放完整事件轨迹，两个 manifest 和 [UPSTREAM.md](terminal-bench-2.1/trajectories/qwen3.8-27b-xhigh/UPSTREAM.md) 记录来源与逐文件摘要。公开运行作为该数据集的轨迹来源，数据集选择仍为单个 `terminal-bench-2.1`。

```bash
python3 datasets/public_trajectories.py
```

下载按固定 revision 的 Git blob / LFS SHA-256 验证；转换保留工具调用与返回对应关系，并记录原文行号。窗口由用户填写参数后，在独立切分实验中生成。
