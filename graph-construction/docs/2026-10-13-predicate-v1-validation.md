# 2026-10-13：目录迁移与谓词定义 v1 验证

## 来源与范围

- 父仓库基线：`da378721e25fce85c27dd26da5b2f7c906285d54`。
- RZP：重新克隆上游并检出 `cb32e964d262854ec5a0fe135f6a05505aa8c532`，转为父仓库普通源码。
- Traceview：保留子模块，版本 `4b55f40efb495b9f7801ce9d25f473ed5ee2dffb`。
- 本轮范围：整理建图代码目录；改造谓词定义与发现流程。实例抽取、规则执行和与建图模块的接合待实现。

## 实际检查结果

| 检查 | 结果 | 证明范围 |
| --- | --- | --- |
| 谓词测试 | 11 项通过 | 元数、集合参数、旧结构拒绝、候选保持、已有匹配及合并的参数兼容、审核卡、三阶段流程、人工反馈、历史重建、恢复隔离 |
| 轨迹建图测试 | 34 项通过 | 原有两个适配器及模拟模型流程在新目录下通过 |
| 动画构建与状态检查 | 通过 | 63 个事件，14 个回合、18 条依赖的展开恢复，高层归并、时序可见性与几何检查 |
| 示例输入检查 | 通过 | 14 个 agent event、28 个 tool call，原始哈希一致 |
| 五个手写谓词示例 | 通过校验 | 仅证明格式有效，未做语义质量评测 |
| Python 静态解析 | 53 个文件通过 | 两模块源码与新增测试的语法 |
| 迁移文件清单 | 1,833 项无缺失 | 1,806 项字节一致；27 项为明确改动的源码、Prompt、文档或生成播放数据 |
| 受保护材料 | 1,706 项哈希完全一致 | 原始轨迹、历史输出、作者材料、分镜和分享文件 |
| Git 结构 | 通过 | 仅保留 Traceview gitlink；新谓词目录无嵌套 Git，源码与 AGENT.md 未被忽略 |
| Git diff 空白检查 | 通过 | 已跟踪变更无空白格式错误 |

源轨迹 SHA-256：`b4a29783e2c20c4140b116eb5b8ee5e5c13e24d28ad1e99519eda08c7dff4208`。

## 复验命令

在代码仓库根目录执行，下列命令不调用真实模型：

```bash
(cd graph-construction/predicate-discovery && python -m unittest discover -s tests -v)
(cd graph-construction/trajectory-graph && PYTHONPATH=src python -m unittest discover -s tests -v)
(cd graph-construction/predicate-discovery && python -m src.discover_predicates --help)
(cd graph-construction/trajectory-graph && python run.py inspect --adapter terminal-bench-2.0 --input ../examples/trajectory.json)
python graph-construction/demos/trajectory-animation/build_data.py
node graph-construction/demos/trajectory-animation/tests/state.cjs
```

本机系统命令受 Xcode 许可状态影响，实际使用 Codex 内置 Python、Node 与 Git 完成上述检查。迁移哈希清单位于本机父仓库 `.git/local-imports/2026-10-13-rzp/migration-manifest.json`，原子模块工作目录备份位于同目录。

## 仍待验证

测试使用确定的模拟模型响应，没有调用真实模型，也没有执行轨迹中的工具命令。尚未验证谓词发现质量、下游建图收益、在线上下文管理或 Shapley 干预效果。旧 19 类关系继续按原协议保存；五个示例定义不构成正式冻结的谓词库。

本轮变更保留在本地工作区，未提交、推送或发布。
