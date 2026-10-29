# Agent 轨迹生长与子图压缩动画

这是 AgentCM 的预期成果演示。案例来自 `../../examples/trajectory.json`：主 Agent 处理 17 份文件，经过 14 个 agent event、28 次工具调用完成文档分类和发票汇总。动画从空图开始，逐个显示 reasoning、action、observation，再展示子图压缩、两层归并和后续执行。

## 打开与操作

双击本目录的 **`index.html`** 即可播放。也可以单独复制并打开 **`share-with-chatgpt/animation-standalone.html`**。两种方式都在浏览器内运行，所需数据已包含在文件中。

- **播放 / 暂停 / 继续、速度、上一步 / 下一步**：逐步查看节点出现、压缩和归并。
- **拖动进度条、点击章节或跳到完成**：定位到指定阶段。
- **点击节点**：查看它的原文、调用参数或工具返回；展开“查看连接、参数和证据”可检查谓词如何绑定节点。
- **展开子图 / 恢复压缩**：检查摘要覆盖的原始节点。高层摘要先展开为 PDF 与 JPG 两个子摘要，再展开到三类节点。
- **重播**：回到空图。恢复播放或重新定位会恢复该时刻的预设压缩状态。

图区域可以单独滚动。播放时跟随当前节点；暂停后可自行浏览。实线表示调用与反馈的对应，虚线表示分镜中标注的语义谓词。点击节点后，与它有关的连线会突出显示。

## 节点、谓词和压缩

| 类型 | 内容 | 本案例数量 |
| --- | --- | --- |
| reasoning | 一条非空 agent 文本；与工具调用同轮出现时也独立保留 | 14 |
| action | 一次工具调用，包含工具名与完整参数 | 28 |
| observation | 原轨迹记录的一块工具返回 | 14 |

共 **56 个原始节点**。event 继续用于标明来源与组织播放顺序。节点 ID 由轨迹 ID、step、类型和位置确定。

这份 ATIF 轨迹每个 event 只有一块返回记录，多次调用的输出保存在一起。因此，同一轮的多个 action 共同指向一个 observation，使用 `batch_feedback` 记录整批对应。只有一次调用时使用 `returns`；若输入提供明确调用编号，构建器按编号配对。仅有 reasoning 的 event 也可生成独立节点。

分镜定义了 7 个语义谓词，人工标注了 57 条实例。每个实例保存英文谓词名、按角色排列的节点参数及证据。例如 `ATTEMPTS_REPAIR(repair: action, failure: observation)` 中，第一个参数是修复操作，图上的信息流方向则从失败 observation 指向后续 action。绘图端点和参数顺序分别保存。

动画包含 6 个子图、4 次叶子压缩和 1 次高层归并。完成 step 12 后，PDF 与 JPG 子图合并成“全部文档判定结果”，覆盖 28 个原始节点，并保存 10 份发票的文件名、总额、VAT 和 7 份其他文档的文件名。随后 step 13 执行归档和 CSV 汇总。

压缩后，对外连线显示在摘要上，每条谓词的原始节点参数继续保存。演示结束时显示 **3 个摘要 + 12 个独立节点**；全部展开后恢复 56 个节点、28 条反馈对应和 57 条语义谓词实例。

## 源文件与修改方式

| 文件 | 职责 |
| --- | --- |
| `storyboard.json` | 文案、子图、谓词定义与节点参数、证据、压缩和归并时点 |
| `node_model.py` | 将原始 ATIF 记录拆成三类节点，校验反馈配对和谓词参数 |
| `build_data.py` | 合并原始记录与分镜，校验覆盖范围和时序 |
| `data.js` | 构建生成的播放数据 |
| `app.js` | 时间轴、图布局、摘要展开与节点查看 |
| `styles.css`、`index.html` | 页面样式、布局与固定文字 |
| `export_for_chatgpt.cjs` | 导出独立 HTML、完整事件说明和关键帧时间表 |
| `tests/` | 数据、播放状态和隔离浏览器检查 |

修改分镜或节点适配器后，在本目录重新生成数据：

```sh
python3 build_data.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/state.cjs
```

构建器读取原轨迹与分镜，只写入 `data.js`。检查包括：节点内容与来源、参数类型、依赖时序、子图覆盖、压缩时点、归并成员与逐文件证据。`higherGroups` 保存高层摘要和 `records`；`merges` 设置归并时点。播放顺序为本轮节点出现、叶子压缩、高层归并，时长由 `app.js` 顶部的 `TIMING` 计算。

如系统 Python 提示 Xcode 许可问题，当前电脑也可使用：

```sh
"/Users/tianyu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" build_data.py
```

## 来源与验证

原文、调用参数与反馈来自原始轨迹；子图、摘要、语义谓词和压缩时点来自人工分镜。动画用于 review 目标设计。自动建图质量与上下文卸载效果需要通过相应实验评价；页面计数统计的是图中节点。

当前验证包括 12 项数据测试、63 个播放阶段检查，以及桌面和窄屏的实际浏览器检查。检查覆盖：reasoning 独立出现、反馈出现时序、批量对应、谓词参数、两层展开、拖动回退、真实播放、独立 HTML 和九张关键帧。

逐文件分类和金额依据 step 6～12 当时已有的返回。动画采用文件清单中的 **11 份 JPG + 6 份 PDF**。原始文件 SHA-256：

```text
b4a29783e2c20c4140b116eb5b8ee5e5c13e24d28ad1e99519eda08c7dff4208
```

## 分享材料

`share-with-chatgpt/` 保存 9 张浏览器关键帧、完整的 `execution-events.txt`、独立 HTML 和 ZIP。`使用说明.txt` 说明如何组合使用这些材料。

修改动画后先运行 `node export_for_chatgpt.cjs`，再运行 `node tests/browser.cjs` 更新截图与概览图。后者使用 Playwright 和隔离的无界面 Chrome；可通过 `CHROME_BIN` 指定浏览器路径，通过 `NODE_PATH` 指定 Playwright 所在目录。导出文件更新后重新生成 ZIP。网页支持 `?t=78.9` 这样的秒数链接，打开时暂停在指定位置。

历史发布地址是 [GitHub Pages](https://tychenn.github.io/agentCM/)。本次三类节点更新保存在本地源码与分享材料中。发布工作流 `.github/workflows/trajectory-pages.yml` 在 `main` 上相关文件更新后检查数据、节点与播放状态，再发布静态文件。
