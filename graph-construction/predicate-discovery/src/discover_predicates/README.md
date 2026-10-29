# Predicate Discovery

第三阶段入口：`python -m src.discover_predicates`。从模块所在项目目录执行，参数包括 `--input-dir`、`--output-dir`、可选 `--config`、`--resume`。

完整用法见[项目说明](../../README.md)，字段语义见[谓词协议 v1](../../docs/predicate-definition-v1.md)。

## 流程

1. Discovery 只读取当前窗口，返回 `candidate_predicates`；不读取已有 Registry。
2. Comparison 读取候选与已有库，返回 `existing/new/uncertain`。新候选和待判断候选保持原定义；已有匹配要求语义双向等价，并保持参数数量和有序类型。
3. Review 重新检查当前窗口、全部比较结果和已有库，返回 `accepted_predicates`、`revised_existing_predicates`。
4. Registry 应用新增与修订，保存可重建的记录。
5. 每批窗口后生成审核卡；人工反馈可保留、删除、修订或合并定义。

Review 通过详细证据纠正 Comparison 的分类，细化过粗候选、归纳过细候选。人工 MERGE 的目标必须为 KEEP/REVISE，源和最终目标要求语义双向等价且有序参数类型一致。上位概念包含不构成合并依据。

粒度标准与正反例统一维护在 `prompts/common/granularity_examples.txt`，加载器将其附加到发现、比较、审核和人工反馈四个阶段。当前策略为 `predicate-granularity/v1`，改动见 [记录](../../docs/2026-10-14-granularity-prompt-update.md)。

## 实现位置

| 文件 | 职责 |
| --- | --- |
| `validator.py` | 协议、阶段响应和修订计划校验 |
| `prompts/` | 共享定义契约与四个阶段的 Prompt |
| `discovery.py`、`comparison.py`、`review.py` | 三阶段模型调用 |
| `registry.py`、`registry_revision.py` | 定义库修改和人工反馈 |
| `storage.py` | 原子落盘、审核卡、历史重建 |
| `execution_manager.py` | 进度、批次、暂停和恢复 |
| `window_loader.py` | 加载窗口与输入哈希清单 |

当前输出没有具体谓词实例或规则推导。离线窗口包含的未来摘要只能服务离线定义研究。
