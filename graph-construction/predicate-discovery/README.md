# 离线谓词发现

基于 [RZP 的迭代发现流程](UPSTREAM.md)，从轨迹窗口发现可复用的谓词定义，经过比较、模型审核和人工反馈形成 Registry。当前协议为 `predicate-definition/v2`，详细定义见 [三类节点与谓词协议](docs/predicate-definition-v2.md)。

## 本轮实现范围

- 支持一元、二元、多元谓词，以及 `observation[]` 等集合参数。
- 每个参数显式记录名称、对象类型和角色；每个谓词记录成立条件和排除条件。
- 保留独立发现 → 与已有库比较 → 审核 → 批量人工反馈的流程。
- 粒度按可区分的语义机制校准；共享 Prompt 提供过粗、合适、过细的对照，比较和合并要求语义双向等价，见 [2026-10-14 改动记录](docs/2026-10-14-granularity-prompt-update.md)。
- 保存模型请求与响应、Prompt 版本、审核卡、Registry 历史和恢复状态。
- 将 event 中的文本、调用和返回分别保存为 reasoning、action、observation 节点，固定调用与返回的结构边。发现输入使用节点 ID 与内容；输出为谓词定义库，语义实例绑定是后续实验。

## 目录

```text
predicate-discovery/
├── UPSTREAM.md
├── docs/predicate-definition-v2.md
├── examples/predicate_definitions.json  # 人工协议示例，无自动加载行为
├── run.py                              # 全流程：预处理、切窗、发现
├── src/
│   ├── trajectory_nodes.py             # 三类节点、稳定 ID 与调用返回边
│   ├── preprocess/                     # 轨迹格式归一化
│   ├── split/                          # Core/Overlap 与前后摘要
│   └── discover_predicates/            # 定义发现、比较、审核、反馈
├── tests/
├── codex prompt/                       # 作者原始材料，保留旧术语
└── runs/                               # 新生成的处理与谓词实验输出，Git 忽略
```

官方原版数据统一放在仓库级 [datasets](../../datasets/README.md)。当前注册官方完整 89 个任务；轨迹由后续 Agent 执行产生。发现流程使用已生成的轨迹和切分窗口。

## 运行

需要 Python 3.10+，程序使用标准库。测试不调用模型；实际发现需要 DeepSeek 兼容接口配置。将密钥放入 `src/.env` 或环境变量：

```dotenv
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_MODEL=deepseek-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

在本模块目录运行：

```bash
python run.py --input-dir /absolute/path/to/agent-runs
```

全流程从显式指定的运行目录读取 `*/agent/trajectory.json`，创建新的日期序号运行目录，依次生成 `processed_trajectory/`、`split_windows/` 和 `discover_predicates/`。该命令会调用真实模型。预处理与切窗配置见 [预处理说明](src/preprocess/README.md) 和 [切窗说明](src/split/README.md)。

已有窗口可直接用于新定义发现：

```bash
python -m src.discover_predicates \
  --input-dir /absolute/path/to/completed-split/windows \
  --output-dir runs/predicate-v2-pilot
```

输出目录必须为空。同一协议的新运行中断后，可在相同命令末尾加 `--resume`；输入窗口集合、顺序和内容必须保持一致。新版本拒绝恢复旧 `build_edges` 或 v1 谓词运行；旧结果可继续查阅。

默认每 10 个窗口暂停一次，用户输入自然语言反馈，模型生成 KEEP / DELETE / REVISE / MERGE 计划。交互以单独一行 `END` 结束输入；空反馈保留现有库。反馈间隔、重试次数和模式见 `src/discover_predicates/config.yaml`。

## 输出与 review

- `predicate_registry.json`：当前定义列表。
- `node_windows/*.json`：每个窗口实际使用的节点和结构边。
- `execution_state.json`：协议版本、进度和恢复状态。
- `runs/*/`：逐窗口的三阶段请求、响应、定义修改记录。
- `batches/*/review_packet.md`：签名、参数角色、成立条件、排除条件。
- `batches/*/registry_revision_plan.json`：人工反馈对应的修改计划。
- `prompt_versions/`：实际使用过的 Prompt 快照。

Schema 校验只检查结构与部分兼容约束。对象角色是否等价、条件是否充分、定义是否有用，需要结合轨迹证据审核。模型审核通过的候选也不等于人工已确认的语义标准。

## 测试与历史兼容

```bash
python -m unittest discover -s tests -v
python -m src.discover_predicates --help
```

2026-10-16 按用户要求清除旧子集及预处理副本，统一下载官方完整 89 个任务到仓库级 `datasets/`；生成的轨迹与窗口按实验管理。旧关系类型结果保持清理状态。协议兼容校验与来源记录见 [UPSTREAM.md](UPSTREAM.md)。
