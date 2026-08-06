# CUMCM 章节技能链契约

## 目标

把论文写作拆成可验收的职责链。每一节只消费已经落盘的证据，只输出本节应承担的内容，
并用结构化门禁向下一节交接。语言流畅不能替代题意闭环、数值证据或独立验证。

## 论文页序与执行顺序

论文页序通常为：摘要 → 问题重述 → 问题分析 → 模型假设 → 符号说明 → 各问建模、
求解、结果与验证 → 评价、改进与推广 → 参考文献 → 附录。

实际执行顺序为：

1. `cumcm-outline` 建立标题树和章节清单；
2. `cumcm-restatement`、`cumcm-analysis`、`cumcm-assumptions`、`cumcm-notation` 完成前置章节；
3. `cumcm-model-writing` 与 `cumcm-results-validation` 逐问闭环；
4. `cumcm-evaluation`、`cumcm-references`、`cumcm-appendix` 收束全文；
5. 结论与数值冻结后由 `cumcm-abstract` 定稿摘要；
6. `cumcm-language-audit` 扫描全文，`cumcm-paper` 编译并交给 `cumcm-review`。

`cumcm-figures` 与 `cumcm-diagrams` 是跨阶段技能：有相应图形时，在图进入正文前完成验收。
数据图写入 `审查/figure-registry.json`，关系图、机理图、几何图与流程图写入
`审查/diagram-registry.json`；注册表不是图表目录的重复，而是把命题、来源、生成方式、最终尺寸、
风格和整页复核绑定到每一幅正式图。

## 章节清单

由 `cumcm-outline` 创建 `审查/section-chain/manifest.json`。允许单文件或多文件 LaTeX，
但必须列出各阶段实际写入的源文件。最低结构为：

```json
{
  "schema_version": 1,
  "question_ids": ["q1"],
  "paper_source": "论文/论文.tex",
  "stages": {
    "restatement": {
      "required": true,
      "source_files": ["论文/论文.tex"],
      "gate": "审查/section-chain/gates/restatement.json"
    }
  },
  "cross_cutting": {
    "figures_used": true,
    "diagrams_used": false,
    "figure_registry": "审查/figure-registry.json",
    "diagram_registry": null
  }
}
```

完整阶段键为 `outline`、`restatement`、`analysis`、`assumptions`、`notation`、
`model-writing`、`results-validation`、`evaluation`、`references`、`appendix`、`abstract`、
`language-audit`。评价或推广不适合独立设章时仍保留门禁，记录其合并位置与理由。

## 阶段门禁

每个子技能写入 `审查/section-chain/gates/<stage>.json`：

```json
{
  "schema_version": 1,
  "stage": "analysis",
  "status": "pass",
  "source_files": ["论文/论文.tex"],
  "claim_ids": ["C-Q1-01"],
  "checks": [
    {"id": "separate_from_restatement", "pass": true, "evidence": "一级标题独立"}
  ],
  "blocking_issues": [],
  "handoff": "assumptions"
}
```

- `status` 只能在全部硬检查通过时写 `pass`。
- `claim_ids` 必须能回到 `求解/证据矩阵.csv`；无结论职责的前置节可为空。
- `evidence` 写可核对的文件、表图编号、公式编号或具体位置，不写“已检查”。
- 任何 `blocking_issues` 非空时停止交接，回到求解或本节修订。

## 全文不变量

1. 问题重述与问题分析必须是两个独立一级章节。
2. 默认顺序固定为“模型假设 → 符号说明”；符号理解若确为假设前提，记录例外理由。
3. 标题采用最少充分层级。每问通常只保留 2--4 个二级标题；三级标题仅在并列论证无法由段首短语承载时使用。
4. 分问连续排版，不因“问题一”“问题二”强制换页。
5. 摘要粗体只强调核心方法与最终结论；普通参数、中间值和过程动作不加粗。
6. 正文只写数学对象、方法、推导、结果、验证和边界，不写生产过程、审查过程或读者导航。
7. 正文不得暴露附件名、文件名、路径、代码、脚本、CSV、JSON、运行命令、支撑材料清单或生成方式。
8. 未经实际运行的候选模型不得写入论文；模型选择只保留真正影响答案且有比较证据的取舍。
9. 图表必须承担唯一主要证据职责。数值图从结果文件生成；结构图只表达真实依赖、机理或算法分支。
10. 正文结论必须能追溯到公式、结果表或图以及独立验证；无法追溯的判断删除或补算。
11. `figures_used=true` 时，`figure-style-audit.json` 必须晚于注册表且为 PASS；
    `diagrams_used=true` 时同理要求 `diagram-style-audit.json`。正式关系图、流程图、机理图和
    几何图的最终风格族只允许 TikZ 或 Visio，最终成品必须为 PDF/SVG 矢量图。
12. 图形自动报告只证明字段与显式检查已完成，不能替代最终 PDF 的原尺寸、缩略图、灰度和整页复核。

## 硬禁表达

下列表达及其近义改写不得进入摘要或正文：

- “本文的回答”“本问回答”；
- “计算口径”“满足问题一对模型建立和可计算性的要求”；
- “前者回答……后者回答……”“不因……预设结论”；
- “在表中列出的……在首次出现处定义”“首次出现处定义”“见下文定义”；
- “完整程序见附录”“详见附件”“代码实现如下”；
- “本文采用 AI/人工智能工具”“提示词”“生成过程”“审查流程”；
- 只用于评价写作本身的“便于读者理解”“使论文结构更加清晰”“体现了模型的有效性”。

需要表达相同事实时，直接陈述物理条件、数学关系、数值结果、误差、边界或模型局限。

## 50 篇语料的使用边界

语料只校准职责、密度和常见组织方式，不复制标题、句式、段落骨架、图形布局或模型链。
统计频率不是配额：摘要字数、章节数、图数、公式数和附录页数均由当前题目的证据决定。

## 改动传播

结果、符号、假设或模型变化后，至少重开以下门禁：

- 数值变化：`results-validation`、`abstract`、`language-audit`；
- 符号或单位变化：`notation`、`model-writing`、`results-validation`、`abstract`；
- 假设变化：`assumptions` 及全部下游阶段；
- 标题树变化：`outline` 及受影响章节；
- 图形变化：对应 `figures` 或 `diagrams` 门禁以及引用该图的章节。
- 图源、尺寸、字体、配色、连接或画布变化：更新注册表，重跑对应风格审计，并重新打开引用章节与视觉审查门禁。
