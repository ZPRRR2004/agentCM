# 谓词发现 Prompt 粒度调整

日期：2026-10-14。粒度策略：`predicate-granularity/v1`；定义协议继续使用 `predicate-definition/v1`。

## 改动目标

让谓词表达可区分的语义机制。相同机制跨工具和资源泛化，输入使用、决策依据、验收标准等不同作用分别表达。

## 五处核心改动

| 文件 | 调整 |
| --- | --- |
| [共享规则](../src/discover_predicates/prompts/common/granularity_examples.txt) | 将完整示例由 USES 改为 USES_AS_INPUT；增加过粗、合适、过细的对照；补充输入/决策/验收、诊断/修复/验证和必要作用域等例子 |
| [发现](../src/discover_predicates/prompts/discovery/system.txt) | 要求先识别具体机制及区分证据，再跨资源泛化；证据不足的候选直接省略 |
| [比较](../src/discover_predicates/prompts/comparison/system.txt) | existing 要求双向语义等价；精确机制被宽泛概念包含时保留为 new；过粗或边界模糊的候选进入 uncertain |
| [审核](../src/discover_predicates/prompts/review/system.txt) | 根据窗口证据细化过粗候选、归纳过细候选、纠正误判的 existing；每个拆分机制分别需要证据 |
| [人工反馈](../src/discover_predicates/prompts/registry_revision/system.txt) | MERGE 对照源定义与最终目标，要求双向等价；防止通过拓宽目标或删除细定义掩盖语义差异 |

共享规则由现有加载器附加到四个阶段。用户消息的变量与输出字段保持兼容。

## 关键判断标准

1. **资源替换**：把路径换成数据库 ID，或更换工具后，如果机制和条件一致，就归为同一谓词。
2. **区分情形**：对齐角色后，如果存在一个因机制、条件或作用域差异而让两个谓词判断不同的情形，就保留区别。
3. **包含与等价**：精确谓词可能蕴含宽泛概念；合并要求双向语义等价。
4. **多谓词共存**：同一事件可满足多个有证据的谓词。一个阈值可同时作为检查器输入和验收标准。
5. **开放发现**：示例校准粒度，实际谓词由轨迹决定。

## 用于模型对照的场景

| 输入情形 | 期望处理 |
| --- | --- |
| 路径、ID、URL 分别作为操作输入 | 泛化为同一输入使用机制 |
| 信息用于选择行动，但没有供应操作输入 | 表达决策依据关系 |
| 两个定义同为 action/information 参数，却分别描述输入与验收标准 | 保留两个机制 |
| 候选为 USES_AS_INPUT，已有库只有泛化的 USES | new |
| 候选为泛化的 USES，已有库包含 USES_AS_INPUT | uncertain，Review 根据窗口证据校准 |
| Registry 为空 | 候选全部进入 new，Review 负责粒度校准 |
| 要将 USES_AS_INPUT 合并进宽泛 USES | 保留具体机制；包含关系不满足 MERGE |
| 同义定义具有等价条件与有序角色 | 可匹配 existing，或在反馈阶段 MERGE |

## 配套更新与验证

协议说明、人工示例、模块说明、TODO 和项目总文件同步更新。人工 JSON 示例采用 USES_AS_INPUT。

- 11 项现有流程测试通过，测试使用确定的模拟模型响应。
- 四阶段消息渲染通过，均包含一份共享粒度策略，模板变量全部解析。
- Prompt 版本快照与恢复内容逐项一致。
- Prompt 内完整 JSON 示例、协议示例及五个人工示例通过 schema 校验；中文协议示例与示例文件一致。

在模块目录执行 `python -m unittest discover -s tests -v` 可复验流程测试。

## 使用新 Prompt

新运行从源码加载本版 Prompt 并保存快照。`--resume` 读取原运行的 Prompt 快照。要对照两版粒度策略，可为相同输入窗口分别创建新的输出目录，再比较候选与审核结果；原运行保留原快照以便复现。

当前人工反馈输出使用 KEEP / DELETE / REVISE / MERGE。带证据的拆分由发现和审核阶段处理，概念分组写入说明，运行输出继续采用五字段定义列表。
