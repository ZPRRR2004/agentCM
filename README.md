# agentCM

研究如何将 Agent 执行轨迹组织为层级子图，再通过受控续跑与 Shapley 分析评价上下文卸载的影响。项目路线见 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)，协作约定见 [AGENT.md](AGENT.md)，实施顺序见 [TODO.md](TODO.md)。本地研究总文件位于代码仓库外的 `../AgentCM_项目总文件.md`。

## 仓库结构

```text
agentCM/
├── AGENT.md                          # 协作偏好与工作边界
├── AGENTS.md                         # Agent 工具入口
├── PROJECT_OVERVIEW.md               # 研究路线
├── RESEARCH_REVIEW.md                # 待审核的研究建议
├── TODO.md
├── datasets/                         # 官方完整数据集、下载校验、来源与版本
├── graph-construction/               # 建图相关实现
│   ├── README.md                     # 模块职责与数据流
│   ├── workbench/                    # 本地实验、任务、谓词审核与 Prompt 工作台
│   ├── predicate-discovery/          # 基于 RZP 的离线谓词定义发现
│   ├── trajectory-graph/             # 轨迹规范化、任务树、信息依赖图
│   ├── demos/trajectory-animation/   # 可编辑的轨迹生长与压缩演示
│   └── examples/trajectory.json      # 原始示例轨迹
└── reproductions/                    # 外部工作的独立复现
```

`predicate-discovery` 从 RZP 上游 `cb32e964d262854ec5a0fe135f6a05505aa8c532` 引入，已转换为父仓库直接管理的普通源码。后续修改与本仓库一起提交。来源、改动和历史兼容边界见 [UPSTREAM.md](graph-construction/predicate-discovery/UPSTREAM.md)。

## 当前实现

| 模块 | 已有能力 | 边界 |
| --- | --- | --- |
| [实验工作台](graph-construction/workbench/README.md) | 实验创建/运行/恢复、批次反馈、定义与轨迹审核、任务看板、Prompt 工作副本与快照 | 本机服务，接入当前谓词定义发现流程 |
| [谓词发现](graph-construction/predicate-discovery/README.md) | 预处理、窗口划分、三类节点展开、发现/比较/审核、批量人工反馈；参数限定 action/observation/reasoning | 当前输出节点、调用返回边与谓词定义，后续实验绑定语义实例 |
| [轨迹建图](graph-construction/trajectory-graph/README.md) | ATIF 输入、语义标注、有序任务树、依赖证据、离线 HTML | 尚未消费新谓词库；混合归并、在线增量构图待实现 |
| [轨迹动画](graph-construction/demos/trajectory-animation/README.md) | 生长、叶子压缩、高层归并、逐层展开 | 分组、依赖和压缩事件为人工演示设计 |

当前工作台从 event 中分别建立 action、observation 和 reasoning 节点，见[节点与谓词协议 v2](graph-construction/predicate-discovery/docs/predicate-definition-v2.md)。独立的历史任务树原型中，`terminal-bench-2.0` 适配器以 agent event 为原子，`terminal-bench-4.0` 适配器以 tool call 为原子。Shapley 卸载实验、训练及在线效果尚待验证。

## 开始使用

打开本地实验网站：

```bash
python3 graph-construction/workbench/run.py
```

访问 <http://127.0.0.1:8765>，在“数据集”浏览官方完整 89 个任务。已接入完整公开执行轨迹，可先运行字段预处理并对照前后内容，再填写切分参数、发现并逐批审核谓词；步骤见[工作台说明](graph-construction/workbench/README.md)。

保持启动工作台的终端打开，网站就会一直运行。关闭网页不影响实验；关闭该终端或按 Ctrl+C 会停止服务和实验，已保存的进度可在下次打开后继续。macOS 也可以双击上一级项目目录中的 `打开 AgentCM 工作台.command`。

工作台使用 Python 3.11+，数据集下载器使用 Python 3.12+；本地测试使用标准库。实际模型调用需要配置对应模块的 `.env` 或环境变量，密钥文件不会进入 Git。两套程序目前保留各自入口与配置。

检查示例轨迹，无模型调用：

```bash
cd graph-construction/trajectory-graph
python run.py inspect --adapter terminal-bench-2.0 --input ../examples/trajectory.json
```

真实构图与渲染：

```bash
python run.py build --adapter terminal-bench-2.0 \
  --input ../examples/trajectory.json --output runs/terminal-bench-2.0/example
python run.py render --input runs/terminal-bench-2.0/example
```

谓词发现的输入、配置和启动命令见[模块说明](graph-construction/predicate-discovery/README.md)；第一轮优先 review [谓词定义协议](graph-construction/predicate-discovery/docs/predicate-definition-v1.md)。

## 本地验证

在仓库根目录执行：

```bash
(cd graph-construction/trajectory-graph && PYTHONPATH=src python -m unittest discover -s tests -v)
(cd graph-construction/predicate-discovery && python -m unittest discover -s tests -v)
python graph-construction/demos/trajectory-animation/build_data.py
node graph-construction/demos/trajectory-animation/tests/state.cjs
(cd graph-construction/workbench && python3 -m unittest discover -s tests -v)
```

测试使用模拟模型响应；这些检查覆盖结构和流程，不代表真实模型的谓词发现质量。

## 获取代码与本地资产

```bash
git clone --recurse-submodules https://github.com/tychenn/agentCM.git
```

当前仅 [Traceview](reproductions/traceview/README.md) 保留子模块形式，路径为 `reproductions/traceview/source/`，固定版本 `4b55f40efb495b9f7801ce9d25f473ed5ee2dffb`。已有克隆可运行 `git submodule update --init --recursive`。

数据集统一放在 [datasets/](datasets/README.md)，当前只注册官方完整的 `terminal-bench-2.1`：89 个任务、1,101 个原版文件。来源版本和路径登记在 [catalog.json](datasets/catalog.json)，逐文件摘要见 `datasets/terminal-bench-2.1/source-manifest.json`。下载的上游 `source/`、运行产物、缓存和密钥文件由 Git 忽略。

```bash
python3 datasets/download.py
python3 datasets/download.py --verify-only
```

2026-10-16 按用户要求，20 任务子集、19 条预处理轨迹及旧数据目录已移出仓库；原版文件从官方固定 commit 下载并逐文件校验。RZP 旧关系类型实验与仓库内旧导入备份的清理记录保留在来源说明中。

## 演示与复现

[在线播放](https://tychenn.github.io/agentCM/)由 GitHub Pages 工作流发布；本地调整目录不会自动更新线上版本。动画源码和工作流已使用新目录。

外部工作的独立复现放入 [reproductions/](reproductions/README.md)，以其中的模板记录来源、版本、命令和实际结果。

2026-10-16：`terminal-bench-2.1` 已接入覆盖全部 89 任务的 91 条公开执行轨迹（含两项基础设施重跑），共 8,139 个事件。来源与复现见 [datasets/README.md](datasets/README.md)。切分参数由用户填写；工作台支持先保存草稿、后绑定轨迹。
