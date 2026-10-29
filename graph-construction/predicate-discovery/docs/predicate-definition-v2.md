# 谓词定义协议 v2：参数指向轨迹节点

2026-10-21，用户确认使用三种节点：`action`、`observation`、`reasoning`。带工具调用的 event 中，reasoning 也单独建节点。协议为 `predicate-definition/v2`；节点格式为 `trajectory-nodes/v1`。

## 一个 event 怎样展开

| 内容 | 生成的节点 | 保存内容 |
| --- | --- | --- |
| 非空 agent 文本 | 一个 `reasoning` | 原始 `thought` 全文，包括计划、决策、结论和最终回答 |
| 一次工具调用 | 一个 `action` | 工具名和原始参数 |
| 一次已记录的工具返回 | 一个 `observation` | 返回正文及错误状态等返回字段 |

例如，先写“查看文件”，再调用两次工具、收到两份返回，会得到 1 个 reasoning、2 个 action、2 个 observation。只含文本的 agent event 得到一个 reasoning 节点；空文本不生成节点。缺失返回不生成 observation，明确记录的空返回仍生成 observation。

文件内容完整保存在读取文件所得的 observation 中。文件路径、资源、规则和目标保留为节点内容或断言条件。用户、系统及其他来源的消息保存为上下文，不标成 agent reasoning。reasoning 指记录中能看到的 agent 文本。

`src/trajectory_nodes.py` 负责确定性转换。ID 由转义后的轨迹 ID、event ID、类型和调用位置组成，例如 `trace/event-0001/action-1`。调用短编号替换和窗口重叠不改变节点身份。每个节点保存原 event 与字段来源，`event_groups` 记录原分组。

代码为匹配的调用和返回建立 `returns(action → observation)`，存入 `structural_edges`。并行调用分别保留，不根据列表顺序推断依赖。reasoning 和 action 之间的语义关系由证据决定；同属一个 event 不自动表示“指导”。

## 谓词参数

定义继续使用五字段：`name`、`definition`、`parameters`、`assertion_conditions`、`exclusion_conditions`。字段结构和有序参数要求沿用 v1。

参数类型只能是 `action`、`observation`、`reasoning` 或各自的一层数组类型，例如 `observation[]`。旧版的 `information/artifact/goal/scope/rule`、混合类型和嵌套数组会被校验拒绝。名称、定义、参数说明及条件使用英文。

例子：

- `IS_PLAN(reasoning)`：一元断言，描述一个节点。
- `USES_OBSERVATION_AS_INPUT(action, observation)`：二元断言，参数角色分别为接收输入的调用、提供输入的返回。
- `GUIDES_ACTION_CHOICE(observation, action)`：返回内容为后续调用的选择提供依据。
- `DERIVES_CONCLUSION(observation[], reasoning)`：多条返回支撑一条明确结论。
- `CONFIRMS_REPAIR(action, observation, observation)`：分别保存修复动作、失败返回和复查返回三个角色。

二元断言按参数角色表达节点连接；多元或集合断言保留全部角色。一元属性和多元关系不被压成普通两端边。`returns` 是已有结构关系，发现模型无需重复命名它。

机制粒度继续按“供应输入、指导选择、诊断、尝试修复、验证结果”等可区分作用划分。工具名或文件类型变化不单独产生一个谓词。时间相邻、同时可见、文字相似不构成语义连接的充分证据；自身返回不能成为已发出调用的决策依据。

## 实验输入与历史

窗口继续按 agent event 切分。现有切分结果可直接用于创建 v2 谓词实验，创建时展开成节点并保存 `nodes/<窗口>.json`。同一节点在 Core 与 Overlap 中沿用相同 ID。发现与审核读取 `[CORE NODES]`、`[OVERLAP NODES]`、已有结构边和上下文，实际使用的节点另存 `output/node_windows/`。

工作台运行前核验输入与节点快照，证据页显示已保存节点。工作副本 Prompt 首次升级时备份到 `runs/prompt_migrations/`，旧实验内的 Prompt、定义和审核记录保持原版本。v1 实验可查阅；新发现从已有切分结果新建 v2 实验。

本阶段输出三类节点、调用返回边与谓词定义库。语义谓词实例将使用这些节点 ID、参数顺序和证据进行绑定；节点出现本身不代表已经建立某条语义边。

新建预处理实验使用 `execution-record/v5`：有工具调用或非空 agent reasoning 的轨迹均可纳入；环境故障中断以及两种内容都为空的轨迹排除。同任务不同尝试保留，相同记录的重复导入去重。历史实验继续按其创建时的规则复现。
