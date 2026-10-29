# 建图模块

这里集中管理与轨迹建图有关的源码、发现流程、演示和小型示例。研究笔记、论文与项目总文件保留在代码仓库外。

| 目录 | 职责 | 当前入口 |
| --- | --- | --- |
| [workbench](workbench/README.md) | 本地实验编排、任务看板、谓词/轨迹审核、批次反馈与 Prompt 编辑 | `python3 run.py` → `127.0.0.1:8765` |
| [仓库级 datasets](../datasets/README.md) | 官方原版任务、数据集注册、下载与校验 | `python3 datasets/download.py`，从仓库根目录运行 |
| [predicate-discovery](predicate-discovery/README.md) | 从离线轨迹归纳可复用谓词定义；保留 RZP 的迭代审核机制 | `run.py`、`python -m src.discover_predicates` |
| [trajectory-graph](trajectory-graph/README.md) | 轨迹规范化、任务组织、依赖证据和离线图页面 | `python run.py inspect/build/render` |
| [demos/trajectory-animation](demos/trajectory-animation/README.md) | 讨论图生长与压缩交互的演示 | `index.html` |
| [examples](examples/) | 共享的原始示例输入 | `trajectory.json` |

## 当前流程与待接合部分

```text
离线轨迹 → 预处理 → 切窗 → reasoning/action/observation 节点 → 谓词候选 → 比较/审核 → 谓词定义 Registry
轨迹输入 → 规范化 → 语义标注 → 任务树 → 信息依赖 → 图页面
```

上面第一条是当前工作台使用的流程。`predicate-discovery/src/trajectory_nodes.py` 负责三类节点和调用返回结构边；第二条是独立的历史任务树原型。后续需要把谓词定义绑定到具体 action、observation、reasoning 节点，保存事实证据，再让建图模块消费这些实例。规则应用、混合归并和在线管理需要各自验收。

工作台提供预处理、切分与谓词发现三类实验。预处理固定输入和字段规则并提供前后对照，切分与谓词实验固定输入、参数及对应 Prompt。算法、定义校验和阶段恢复由 `predicate-discovery` 维护；界面、任务与人工意见由 `workbench` 维护。

## 目录约定

- 每个可运行模块保留自己的配置、源码和测试；暂不引入共享抽象或单一启动器。
- `runs/` 保存本地生成产物，Git 忽略；原始输入与运行结果分开放置。
- 数据集统一保存在仓库根目录 `datasets/`，当前为官方完整 `terminal-bench-2.1`。任务执行后产生轨迹，切分参数由用户填写，窗口与统计进入工作台独立实验的 `runs/experiments/<id>/output/`。
- 动画与模型程序分开维护；动画中的人工分组和压缩事件不作为算法测量结果。
- 数据集迁移校验轨迹和窗口字节；用户要求清理的旧结果从仓库移出。
