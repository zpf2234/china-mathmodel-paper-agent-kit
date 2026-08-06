---
name: cumcm
description: 数学建模国赛（CUMCM）优秀论文导向的全流程总控技能。用于用户提供赛题与附件、要求开始求解、完成国赛论文、冲击国奖或用历年优秀论文校准质量时；串联 cumcm-solve、cumcm-paper、cumcm-review，完成语料对标、独立建模、证据落盘、LaTeX 成文、原创性与提交审查。
---

# CUMCM 优秀论文总控

当前稳定适用范围聚焦 CUMCM **A/B 题**：A 类侧重机理、几何、物理和高精度数值闭合；B 类侧重统计、决策、优化、生产过程和不确定性证据链。C/D/E 题不自动宣称同等稳定性，除非另行完成对应回归语料与门禁。

目标是产出具备优秀论文竞争力的完整候选稿，不承诺奖项。评价顺序固定为：
题意正确 > 模型适配 > 结果可信 > 回答完整 > 原创可复现 > 表达与排版。

## 核心原则

1. 参考优秀论文的质量分布，不复制其文字、模型链、参数、结果、代码或图形。
2. 不按 A/B 字母预设方法。先识别机理、预测、评价、优化、仿真或决策本质，再选方法。
3. 正文必须落在 20--30 页；区间内不用页数、图数、表数和公式数灌水。官方规则与该项目质量下限都是硬约束，语料统计是软校准。
4. 每个关键结论必须有可运行脚本、结构化指标和图/表证据；论文只写已落盘证据。
5. 采用“独立求解—独立审查”闭环。审查不得替求解阶段发明结果。
6. 最多回退修复 3 轮；仍未通过时交付当前最佳版本并列出剩余风险。
7. 图型由数据结构和待证明结论决定，不由 A/B 题号决定；全文完成后执行中文去 AI 化审查，保留事实、公式、数值和证据口径。
8. 使用 [../cumcm-paper/references/style-profile.md](../cumcm-paper/references/style-profile.md)
   统一摘要强调、客观表达、公式编号、流程图和标题层级；正文不展示 AI 提示词或辅助脚注。
9. 摘要使用 [references/abstract-writing.md](references/abstract-writing.md)：从逐问证据
   五元组写作，以一页成品、定量答案、清晰分段和口径一致性放行，不把经验字数写成硬规则。
10. A/B 题制图使用 [references/figure-routing.md](references/figure-routing.md)：先判图的论证
   职责和变量维度，再用 50 篇优秀论文的分布做漏图检查；经验先验不得变成固定图数或套图。
11. 流程图使用 [references/flowchart-routing.md](references/flowchart-routing.md)：区分问题关系、
    分题求解、算法迭代、数值计算和状态决策，禁止用文件生产或交付流水线替代数学逻辑。
12. 论文标题树使用 [references/title-structure.md](references/title-structure.md)：先判断各问
    的共享关系，再选择分问题一级章、总章统领、问题嵌入或模块驱动，不套固定获奖目录。
13. 附录使用 [references/appendix-structure.md](references/appendix-structure.md)：建立正文到
    逐问代码的索引，写明真实环境与命令，完整代码可超过语料均值但不得用原始数据灌页。
14. 论文架构使用 [references/paper-architecture.md](references/paper-architecture.md)：
    前置功能、独立符号章、三级标题上限、结构流派、跨问题验证职责和附录反向引用按证据层级执行；
    十章模板、标题数、流程图数和分问页数只作校准。
15. 封面总标题使用 [references/paper-title.md](references/paper-title.md)：先验证标题普查的
    OCR 与文件名，再按“对象 + 动作 + 可选核心机理”生成；不把方法词数量或未经清洗的字数
    均值设为硬规则。
15A. 用户目标为国一、国奖或一等奖时，必须完整执行
    [references/national-first-precision-and-visual-gates.md](references/national-first-precision-and-visual-gates.md)。
    此规则将结果精度、复杂思路流程图、逐问直观证据、动态图密度和 MCP 最终图质量升级为阻断门禁，
    并覆盖本文件中“图数/流程图只作软校准”的旧措辞。低于门槛只能标记
    `REVISE_NATIONAL_FIRST_CANDIDATE`，不得 PASS。
15B. 国一模式不得直接从读题跳入单题求解。依次调用 `cumcm-contest-operations` 建立限时检查点、
    `cumcm-problem-selection` 完成候选题同口径最小试算和止损冻结，再由 `cumcm-model-tournament`
    对关键问题执行基线—主候选—异构挑战竞技。答案冻结后调用 `cumcm-blind-benchmark`，成文后调用
    `cumcm-adversarial-review`，最终仅由 `cumcm-national-first-gate` 签发国一竞争候选状态。
16. 几何图与流程图使用 [references/diagram-layout.md](references/diagram-layout.md)：框与
    框内文字必须为单一对象，标注锚定几何对象，固定画布导出，并生成同名布局审计文件；
    不用 LaTeX 裁边修复源图。
17. 几何机理图同时使用
    [references/geometry-diagram-routing.md](references/geometry-diagram-routing.md)：按对象、
    轨迹、判据和注释分层，锁定 Office 文本坐标，执行字形—线段和标签—实体碰撞检查。
18. 所有几何图、关系图和流程图还须使用
    [references/diagram-connection-audit.md](references/diagram-connection-audit.md)：先对每条
    引线、箭头、判断分支和反馈回路做连接级审计，核对每条线的方向与含义，再做整图级审计；
    任一连接或线语义失败不得入正文。
19. 全文内容使用 [references/content-quality.md](references/content-quality.md)：默认先模型
    假设、后符号说明；摘要只突出核心方法与最终结论；标题采用最少充分层级；逐段检查定义、
    推导、证据、结论与边界职责。
20. 使用本地 50 篇语料时先读
    [references/full-paper-census.md](references/full-paper-census.md)：按全文职责解释摘要、
    前置章节、逐问闭环、验证、评价、引用与附录；标题和关键词命中只作显式下限，不把
    频率转成固定目录或配额。
21. 模型选择与答案充分性使用
    [references/model-selection-and-answer-quality.md](references/model-selection-and-answer-quality.md)：
    在同题答案不可见时建立基线、主候选和异构挑战，先做科学硬淘汰，再用独立验证、稳健性、
    可识别性或最优性证据择优；答案冻结后才允许隐藏参考评估。
22. 论文成文使用 [../cumcm-paper/references/section-chain-contract.md](../cumcm-paper/references/section-chain-contract.md)：
    由 `cumcm-outline` 建立清单，依次调用重述、分析、假设、符号、建模求解、结果验证、评价、引用、附录、摘要与语言审计子技能；
    `cumcm-figures` 和 `cumcm-diagrams` 作为跨阶段图形门禁。不得跳过章节门禁后一次性自由生成全文。
23. 章节具体内容同时使用 `cumcm-paper/references/front-section-content-standard.md`、
    `model-result-content-standard.md` 和 `closing-section-content-standard.md`；语料字符量与命中率只触发
    漏项或冗余复核，真正放行依据仍是当前题目的证据职责。
24. 数据图审美使用 `cumcm-figures/references/aesthetic-standard.md`，结构图、流程图、机理图和
    几何图使用 `cumcm-diagrams/references/tikz-visio-standard.md`。正式结构图最终只允许 TikZ
    或 Visio 风格族；两类图均须注册、自动审计并在最终 PDF 中复核，不能把“美观”留作主观承诺。
24A. 国一/国奖候选还须执行 `cumcm-figures/references/signature-figure-standard.md`：在题目证据允许时，
    规划通常 2--3 张具有论文辨识度的特色主视觉图，至少一张将核心机理/模型结构与最终结论放在
    同一阅读链中。特色图必须来自真实数据、临界关系、策略景观、时空演化或不确定性联动；不得把
    渐变、图标、装饰性三维或商业仪表盘当成特色。若题目不适合复合主视觉，必须记录豁免理由，
    不为满足数量强制拼图。
24B. 同时执行 `cumcm-figures/references/visual-identity-and-archetypes.md` 并复制规划模板：全篇先冻结
    变量—颜色/线型语义，再从 A 类机理—结果、临界构型、时空演化，或 B 类策略景观、策略指纹、
    不确定性—决策联动等原型中按证据结构选择。国一 registry 使用 schema v3；特色图门禁必须显式
    `--track national-first`，仅换配色或装饰性拼图不得通过，有理由豁免也不降低科学与 provenance 门禁。
25. 工作区存在 `paper-visio`、`paper-tikz` 与 `paper-matlab` MCP 时，完整读取
    [references/figure-mcp-routing.md](references/figure-mcp-routing.md)，并先调用项目级
    `cumcm-figure-router`；若独立 `paper-figure-router` MCP 可用则优先使用，不可用时运行确定性回退脚本并
    如实登记。路由器先判断插图必要性、后端和正文位置，再生成、注册和审查；路由拒绝的候选图不得
    因装饰需要保留。
26. 数学写作使用 [references/mathematical-writing.md](references/mathematical-writing.md)：统一变量
    引入顺序、公式动机、推导叙事、边界条件表达、参数来源和数值精度报告，使正文读起来像连贯
    的数学论证而不是代码注释；语料建模段定义信号 92.9%、数值词密度 60.46/千字是校准标准。
27. 论证叙事使用 [references/argumentation-patterns.md](references/argumentation-patterns.md)：每段
    只承担一个职责（定义/推导/求解/证据/结论/边界），每个结论性断言在 ±2 段内有证据支持，
    跨问衔接写在后问开头，连接词承载因果而非装饰。
28. 表格设计使用 [references/table-design.md](references/table-design.md)：区分结果表、参数表、
    对比表、敏感性表、验证表和数据描述表，各有标准列结构；同列同精度、单位在列头、表图不
    重复同一信息。
29. **A/B 题多假设试算与精准精选**：在求解探索阶段显式设计与测试多组合理假设及异构候选模型；
    成文时仅精选最合理、最准确的假设与最正确的模型作为正文主解，彻底剔除废弃假设与试算冗余。
30. **模型选择克制表达与以图概括**：正文中对模型选择思考、假设衍生与算法淘汰的描述保持极度克制
    （控制在 1-2 句/一小段内）；复杂的选择逻辑、架构比较与机理拆解，优先使用结构图、决策树流程图
    或模型对比图替代，实现“一图胜千言”。
31. **图形数量硬性锁定（16 ~ 22 幅）**：全篇正文中，正式注册的插图数量硬性限制在 **16 ~ 22 幅**。
    30. **多阶段演化与子图拼图 (Subfigures)**：对涉及多时间点、状态演化或对比的题目，使用多面板子图拼图 (Subfigures)。**子图面板数量完全按数据逻辑灵活选择（如 (a)(b) 2 面板、(a)(b)(c) 3 面板、(a)(b)(c)(d) 4 面板）**，严禁为凑格式而机械凑图。
32. **正文 20 ~ 30 页特色版面安排**：正文页数（摘要至参考文献前一页）**严格限制在 20 ~ 30 页**。
    借鉴国一优秀论文的特色排版：包含前置模型决策流程图、多阶段演化联排拼图、临界切点与碰撞边界图、
    及机理-结果三联主图，使论文具备顶尖优秀论文的视觉张力与版面质感。

## 标准目录

```bash
python .agents/skills/cumcm/scripts/init_project.py --root .
```

```text
工作目录/
├── 题目/
├── 数据/
├── 求解/
├── 论文/
├── 审查/
└── 最终效果/高教杯优秀论文/   可选的本地基准语料
```

## 阶段 0：优秀论文校准

若本地语料存在，先读
[references/benchmarking.md](references/benchmarking.md)，再运行：

```bash
python .agents/skills/cumcm/scripts/benchmark_corpus.py --root .
python .agents/skills/cumcm/scripts/build_section_content_profiles.py --corpus 最终效果/高教杯优秀论文
```

从报告中形成当前题目的质量预算：需要回答的关键问题、必须出现的验证类型、适合的图表职责、
正文密度和附录规模。不得把邻近论文的专属内容写进求解计划。
同时按 [references/figure-routing.md](references/figure-routing.md) 建立图形职责预算：
模型解释图、方案结果图和诊断验证图分别需要证明什么，以及哪些候选图应删除。
若计划关系图或流程图，再按 [references/flowchart-routing.md](references/flowchart-routing.md)
逐图指定唯一主要职责、对应脚本步骤、判断条件、回退路径和可编辑源文件。
所有几何图、关系图和流程图同时按
[references/diagram-layout.md](references/diagram-layout.md) 执行源端包含检查和最终插入
尺寸验收。
几何图另按 [references/geometry-diagram-routing.md](references/geometry-diagram-routing.md)
建立对象—标签锚点表，并在导出前完成碰撞检查。
所有连接按 [references/diagram-connection-audit.md](references/diagram-connection-audit.md)
建立逐连接清单；移动任一节点、标签或画布后必须全量重审，不只复查被修改位置。
再按 [references/title-structure.md](references/title-structure.md) 画出当前题目的标题树草案，
标明共享模型放置位置与每问的最终回答、结果和验证归属。
同时用 [references/paper-architecture.md](references/paper-architecture.md) 检查前置四项功能、
独立符号章、跨问题验证职责、编号层级和标题信息密度。
再用 [references/content-quality.md](references/content-quality.md) 压缩标题树、确定符号与
假设顺序，并建立逐段内容审查表。
本地 50 篇语料存在时，再用
[references/full-paper-census.md](references/full-paper-census.md) 核对全文职责链、统计口径
和 OCR/自动识别边界；冲突时以官方规则、题目结构和项目证据优先。
同时读取 `最终效果/高教杯优秀论文/内容职责普查/section_content_profiles.json`，按章节检查输入、
输出、方法、证据与边界信号；不得复制报告来源段落或把字符分位数变成写作配额。
求解证据稳定后按 [references/paper-title.md](references/paper-title.md) 拟定总标题，逐个核对
标题方法词能否在摘要、公式、代码和验证中兑现。
摘要成稿前按 [references/abstract-writing.md](references/abstract-writing.md) 抽取逐问证据；
附录生成前按 [references/appendix-structure.md](references/appendix-structure.md) 建立正文引用、
代码模块、环境和支撑材料索引。

修改或评估本套 skills 时，同时读取
[references/regression-suite.md](references/regression-suite.md)，不得用单题表现证明跨题型能力。

## 阶段 1：独立求解

调用 `cumcm-solve`，完成：

- 题面、附件和提交要求的全量读取；
- 赛题地图、歧义清单、变量/单位/约束字典；
- `求解/任务契约.json`，锁定题面问题、附件角色、官方输出和逐问验证；
- 候选方法比较、主模型和可执行降级方案；
- 冻结的候选模型比较、淘汰依据和异构挑战路线；
- 逐问可复现代码、结果表、图形、`metrics.json`；
- `求解/运行环境.json`：实际验证的 Python 与依赖版本、逐问命令和验证状态；
- `求解/证据矩阵.csv`：题目要求—结论—指标—图表—脚本的映射；
- 至少一种与题型匹配的独立验证，而不是笼统写“效果良好”。
- 每问通过题面闭环、可行性、独立验证、数值分辨率、替代路线挑战和不确定性/最优性六项答案门禁。

运行：

```bash
python .agents/skills/cumcm-solve/scripts/audit_evidence.py --root .
```

只有题目每一问都有明确答案、证据矩阵无断链、关键指标可解析时才交接论文阶段。

## 阶段 2：证据成文

调用 `cumcm-paper`，并按其章节子技能链逐门禁成文。只从证据矩阵和结果文件写作：

- 第一页为摘要专用页，摘要覆盖每问的方法理由、关键结果和验证信息；
- 摘要粗体只标记核心方法和最终结论，不突出普通数字、过程动作或验证细节；
- 正文按真实论证需要组织，在不灌水的前提下形成 20--30 页完整论证；
- 默认先写模型假设、再写独立符号说明；每问二级标题优先控制在 2--4 个；
- 每个问题形成“对象与变量—建立模型—求解—验证—结论”的闭环；
- 对真正影响答案的模型选择，在问题分析或对应问题中用紧凑段落/表格展示决定性证据；
- 正文（摘要首页至参考文献开始前一页）必须为 20--30 页，并同时服从当年官方上限；参考文献、AI 声明和附录不计入该区间，从附录首页起不设页数上限，附录包含支撑材料清单和完整可运行代码；
- XeLaTeX 两遍编译，修复错误、越界、缺字、引用和大面积异常空白。
- 编译前运行 `cumcm-language-audit/scripts/audit_language.py` 和
  `cumcm-paper/scripts/audit_section_chain.py`，硬禁表达、生产痕迹或任一章节门禁失败时不得进入候选审查。

## 阶段 3：优秀论文候选审查

调用 `cumcm-review`，运行：

```bash
python .agents/skills/cumcm-solve/scripts/audit_evidence.py --root .
python .agents/skills/cumcm/scripts/benchmark_corpus.py --root . --fail-on-similarity
python .agents/skills/cumcm-figures/scripts/audit_figure_style.py --root .
python .agents/skills/cumcm-diagrams/scripts/audit_diagram_style.py --root .
python .agents/skills/cumcm-paper/scripts/audit_section_chain.py --root .
python .agents/skills/cumcm-review/scripts/audit_artifacts.py --root .
```

两项图形审计只在项目实际使用相应图类时运行；使用却缺注册表、风格报告或最终页面复核即失败。

审查四类门槛：

- 合规门槛：匿名、格式、正文 20--30 页、文件大小、AI 使用声明与支撑材料；
- 科学门槛：假设、推导、验证、稳健性、约束与结论有效；
- 答案门槛：主模型经异构路线挑战，数值误差小于报告精度，优化有界差或诚实的近优声明；
- 证据门槛：数值、图表、代码和论文可双向追溯；
- 原创门槛：无参考论文复刻和高相似长句。
- 内容门槛：逐节阅读正文，标题最少充分，段落职责明确，摘要—正文—证据同口径。

任一硬门槛失败或优秀论文评分未达标，按整改清单回退对应阶段。

## 最终交付

- `论文/论文.pdf` 与完整 LaTeX 源码；
- `求解/` 下可从原始数据重跑的代码、结果、图表、运行环境契约和证据矩阵；
- `审查/审查报告.md`、自动审查与优秀论文对标报告；
- 支撑材料压缩包，满足当年官方格式和大小限制。

缺少编译器或依赖时，仍交付完整源码、可运行说明和已验证产物，并在审查报告中明确阻塞点。

## Skill 发布门槛

只有 [references/regression-suite.md](references/regression-suite.md) 中六案例路由、三类证据包、
留出题全流程和冻结后盲测答案门槛全部通过，才能声称该版本具有稳定的优秀论文级产出能力。

对已完成的独立项目运行：

```bash
python .agents/skills/cumcm/scripts/evaluate_skill_suite.py --projects <机理题项目> <统计或决策题项目> <优化题项目> --min-projects 3
```
