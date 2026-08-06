---
name: cumcm-paper
description: 数学建模国赛优秀论文导向的撰写、章节编排与编译总控技能。用于把已完成的求解证据包通过摘要、重述、分析、假设、符号、建模求解、结果验证、评价、参考文献、附录和语言审计子技能链写成 CUMCM LaTeX 论文，并执行原创性、格式和 PDF 视觉验收。
---

# CUMCM 论文阶段

只从证据写论文。证据不足就回 `cumcm-solve` 补算，不编造数值、文献、图表或验证。

## 先决条件

- `求解/求解计划.md`
- 每问可运行脚本、`结果/metrics.json` 和结果表
- `求解/证据矩阵.csv`
- `求解/图表清单.md`
- `求解/证据审计.md` 为 PASS

## 章节子技能链

先完整读取 [references/section-chain-contract.md](references/section-chain-contract.md)，再按论证生成顺序调用：

```text
cumcm-outline
  → cumcm-restatement → cumcm-analysis
  → cumcm-assumptions → cumcm-notation
  → cumcm-model-writing → cumcm-results-validation
  → cumcm-evaluation → cumcm-references → cumcm-appendix
  → cumcm-abstract → cumcm-language-audit
  → 编译与 cumcm-review
```

`cumcm-figures` 与 `cumcm-diagrams` 贯穿各阶段：图进入正文前必须通过对应门禁。不得跳过子技能后用总控技能一次性自由生成全文。
上一阶段门禁不通过时回退修订或补算，禁止用说明性文字遮盖证据缺口。

前置章节同时读 [references/front-section-content-standard.md](references/front-section-content-standard.md)，
逐问主体同时读 [references/model-result-content-standard.md](references/model-result-content-standard.md)，
收束章节同时读 [references/closing-section-content-standard.md](references/closing-section-content-standard.md)。
这些统计只用于发现职责缺口和冗余，不能成为字数、标题数、图数或文献数配额。

同时读 [references/official-rules.md](references/official-rules.md) 与
[references/sections.md](references/sections.md)。LaTeX 细节见
[references/latex-template.md](references/latex-template.md)。本工作区的人工写作与排版硬规则见
[references/style-profile.md](references/style-profile.md)。若本地有优秀论文语料，同时读
[../cumcm/references/benchmarking.md](../cumcm/references/benchmarking.md) 和
[../cumcm/references/full-paper-census.md](../cumcm/references/full-paper-census.md)，
按全文职责链使用普查，不把显式标题率解释为内容缺失。
图形编排同时遵守
[../cumcm/references/figure-routing.md](../cumcm/references/figure-routing.md)。
工作区启用 `paper-figure-router`、`paper-visio`、`paper-tikz` 和 `paper-matlab` 时，同时完整读取
[../cumcm/references/figure-mcp-routing.md](../cumcm/references/figure-mcp-routing.md)，按“命题—路由—生成—
注册—最终页面复核—插入”的顺序调动，不允许在章节写完后批量补装饰图。
流程图编排同时遵守
[../cumcm/references/flowchart-routing.md](../cumcm/references/flowchart-routing.md)。
摘要写作同时遵守
[../cumcm/references/abstract-writing.md](../cumcm/references/abstract-writing.md)。
标题层级与章节路由同时遵守
[../cumcm/references/title-structure.md](../cumcm/references/title-structure.md)。
前置功能、独立符号章、跨问题验证职责、标题信息密度和篇幅路由同时遵守
[../cumcm/references/paper-architecture.md](../cumcm/references/paper-architecture.md)。
封面总标题同时遵守
[../cumcm/references/paper-title.md](../cumcm/references/paper-title.md)，方法词必须由模型、
实现与验证共同支撑。
几何图与流程图布局同时遵守
[../cumcm/references/diagram-layout.md](../cumcm/references/diagram-layout.md)，使用内嵌节点
文字、对象锚定标注、固定画布和同名布局审计文件。
几何机理图还须遵守
[../cumcm/references/geometry-diagram-routing.md](../cumcm/references/geometry-diagram-routing.md)，
锁定 Office 文本坐标，检查实际字形与轨迹、轮廓和实体的碰撞。
所有几何图、关系图和流程图还须遵守
[../cumcm/references/diagram-connection-audit.md](../cumcm/references/diagram-connection-audit.md)，
逐条验收引线、箭头、判断分支和反馈回路，核对有向/无向属性、箭头朝向与物理/算法含义，
再独立验收整图构图。
数据图还须完整读取
[../cumcm-figures/references/aesthetic-standard.md](../cumcm-figures/references/aesthetic-standard.md)。国一/国奖候选同时读取
[../cumcm-figures/references/signature-figure-standard.md](../cumcm-figures/references/signature-figure-standard.md)，
并完整读取 [../cumcm-figures/references/visual-identity-and-archetypes.md](../cumcm-figures/references/visual-identity-and-archetypes.md)，
复制规划模板，在标题树与图形职责预算阶段规划特色主视觉图，而不是正文完成后临时美化普通图。
特色图前后必须承担核心命题、关键读数、机制解释和答案影响；若只是多张常规图拼接或仅换配色，
则不得计为特色图。确实不适合时允许经独立审查的有理由豁免，不为满足数量强制拼图。
结构图、机理图、几何图和流程图还须完整读取
[../cumcm-diagrams/references/tikz-visio-standard.md](../cumcm-diagrams/references/tikz-visio-standard.md)。
二者分别建立 `审查/figure-registry.json` 与 `审查/diagram-registry.json`，不能仅凭正文截图验收。
附录编排同时遵守
[../cumcm/references/appendix-structure.md](../cumcm/references/appendix-structure.md)。
全文内容、摘要语义强调、默认前置顺序和标题压缩同时遵守
[../cumcm/references/content-quality.md](../cumcm/references/content-quality.md)。
数学写作（变量引入、公式动机、推导叙事、数值精度）同时遵守
[../cumcm/references/mathematical-writing.md](../cumcm/references/mathematical-writing.md)。
论证叙事（段落职责、证据密度、连接词、跨问衔接）同时遵守
[../cumcm/references/argumentation-patterns.md](../cumcm/references/argumentation-patterns.md)。
表格设计（类型选择、列结构、排序、数值格式、图表分工）同时遵守
[../cumcm/references/table-design.md](../cumcm/references/table-design.md)。
模型选择与答案结论同时遵守
[../cumcm/references/model-selection-and-answer-quality.md](../cumcm/references/model-selection-and-answer-quality.md)，
只写真实试算过的候选与冻结后的选择证据。

## 原创性约束

- 优秀论文只用于质量校准，不复用标题、摘要句式、段落结构、专属模型链、图号、数值或代码。
- 同题常用术语可以一致，但推导组织、解释和结论必须来自本项目证据。
- 禁止把参考论文的“首先—接着—然后—最后”段落替换少量词后使用。
- 成稿后必须运行相似度审计；高风险时重写相关段落，而不是机械同义替换。

## 去 AI 化

成稿后调用 `humanizer-zh` 的检查框架逐章复核，写 `审查/去AI化审查.json`。目标是让文字具体、自然、可辩护，不是迎合检测器：

- 删除无逻辑作用的“此外、值得注意的是、综上所述”和机械“首先—其次—最后”；
- 把“显著、卓越、具有重要意义、应用前景广阔”等空泛判断改成可观察结果、适用范围或局限；
- 删除“便于、有助于、本文报告、不声明、不构成证明、不能据此宣称”等自我评价或元叙事，
  只保留模型结构、数值事实和客观不确定性；
- 避免每段同构、强凑三点、重复小结和同义词轮换，允许长短句自然变化；
- 保留技术术语、公式、数值、单位、引用和 `claim_id` 口径，不为“更像人”改动事实；
- 审查结果必须 `pass: true`，并列出已修改模式与仍保留表达的技术理由。

## 论文组织

总标题在证据稳定后确定，优先采用“对象 + 核心动作”或“基于核心机理的对象 + 核心动作”。
对象与动作必须出现；方法词是可选项，不为增加学术感堆叠算法，也不使用正文未严格兑现的
“非线性、智能、AI、深度学习”等升格词。

模板资产位于：

```text
.agents/skills/cumcm-paper/assets/latex-template/format.cls
.agents/skills/cumcm-paper/assets/latex-template/fonts/
.agents/skills/cumcm-paper/assets/latex-template/restatement.tex
.agents/skills/cumcm-paper/assets/latex-template/analysis.tex
.agents/skills/cumcm-paper/assets/latex-template/assumptions.tex
.agents/skills/cumcm-paper/assets/latex-template/notation.tex
.agents/skills/cumcm-paper/assets/latex-template/model-establishment-solution.tex
```

论文前五个一级章固定如下；第五章内部再按问题依赖选择共享模型或逐问展开，后续结果验证、
评价与附录结构按真实证据量调整：

```text
摘要
一、问题重述
二、问题分析
三、模型假设
四、符号说明
五、模型的建立与求解
综合验证与稳健性（按跨问题证据量决定独立设章或合并）
模型评价、改进与推广
参考文献
工具使用声明（仅在当年规则要求且用户授权时单列）
附录与支撑材料清单
```

问题重述与问题分析必须使用两个独立一级章。问题重述固定采用“一、问题重述—1.1 问题背景—
1.2 问题提出”的标题结构：背景只用一个紧凑段落交代对象与场景；问题提出先概括共同条件，
再以段内加粗的“问题一：”“问题二：”逐问重述对象、输入、约束、任务和输出。各分问不得升为
三级标题。重述必须用自己的话重新组织，不得照抄题面，也不得写问题分析、模型、求解、结果、
验证、评价、改进或推广。问题分析另行说明数据特征、难点、问题依赖和模型路线。
不得使用“问题重述与分析”合并章，也不得在模型假设
标题中加入“计算口径、说明、若干问题”等解释性词。默认先写模型假设、再写符号说明；
只有符号定义是理解假设不可缺少的前提时例外并记录理由。符号说明不得
埋入其他章节；第四章标题后直接放“符号—物理或数学含义—单位或量纲”三列表，必要说明
只陈述共同约定或适用范围且保持一至两句，不作评价。具体公式推导、参数求取和数值求解过程
集中放入第五章；问题分析只保留高层思路与路线。综合验证有两类以上跨问题证据时独立设章，
否则在逐问验证后用一节完成汇总。
一级标题由模板显示为中文序数，目录深度控制在三级。每问默认 2--4 个二级
标题，超过 5 个先合并同一论证链；语料中的标题数和分问页数不是填充目标。

每问必须闭环：

1. 界定口径、变量、目标和约束；
2. 说明方法为何适配；
   当候选路线实质影响答案时，给出决定性比较和取舍；
3. 给出必要且连续的数学表达；
4. 说明求解过程与参数来源；
5. 展示关键结果及不确定性；
6. 用独立验证支撑可信度；
7. 用具体结论直接回答原问，不设置“本问回答”“本文的回答”等模板标签。

不按固定公式数、图数或字数填充。公式服务于可复现推导，图表服务于关键结论；正文仍须以真实论证达到 20--30 页硬区间。

模型选择跨越多问时放在问题分析；只影响单问时放在该问模型小节。两条路线优先用一段话，
三条以上且需要同时比较信息利用、验证表现、稳健性或代价时再使用表格。不得把未运行的算法
列成“备选”，也不得展示内部试错、文件名或审查门禁。若基本规律唯一，用一句话说明主模型
和独立复算路线，不为凑内容制作方法对比表。

## 增量成文纪律

- 先落盘 `论文.tex` 与摘要并完成首次编译，再写正文；不得长时间只在内存中组织整篇稿件。
- 每新增 1--2 个章节文件立即保存并编译，及时修复语法、引用、字体、图片和越界问题。
- 每轮编译记录 `references:start - 1` 的正文页数；低于 20 页时只补缺失推导、验证和解释，不补重复题面或装饰内容。
- 正文、参考文献、按要求授权的独立声明和附录全部完成后再做两遍收敛编译与逐页视觉验收。

## 摘要

摘要不得超过官方规定的一页。先写每问的四元组，再压缩成自然段：

```text
问题目标 + 方法及选择理由 + 关键定量结果（含单位） + 验证/稳健性结论
```

首段交代总问题和统一思路，末段只总结最重要的决策与适用边界。禁止主观自夸、公式、引用、
未在 `metrics.json` 中出现的数字和参考论文句式。字数由模板实排决定，不设脱离版式的固定配额。

关键词标签按模板加粗，关键词内容保持常规字重。摘要正文粗体只标记核心方法与最终结论；最终结论可包含决定答案的数值、
单位和不确定性。优先使用 `\keymethod{...}` 与 `\keyresult{...}`，每问原则上各突出一个。
普通参数、中间数值、过程动作和验证细节不加粗，禁止整段或连续粗体。摘要不得出现 AI、
人工智能、提示词、prompt、工具名、辅助过程、审查过程或写作策略。

## 正文密度

- 正文必须为 20--30 页；机器口径为摘要首页至参考文献开始前一页，即 `references:start - 1`。
- 20 页是完整论证的质量下限，30 页及当年更低的官方上限是合规上限；不得用重复题面、放大图表或稀疏排版凑页。
- 参考文献必须另起一页并标记 `\label{references:start}`；参考文献、按规则单列的声明和附录不计入上述区间。
- 各分问章节连续排版；问题一、问题二等章节之间不使用 `\newpage`、`\clearpage` 或章节末尾
  `\FloatBarrier` 强制换页。页尾空间足够容纳标题和至少两行正文时，下一问直接接排。
- 从附录首页起不设页数上限；附录页数按完整代码和支撑材料自然形成，仅受文件大小、完整性和可读性约束。
- 语料页数、图表数只作校准，不追求达到中位数或上四分位数。
- 前置重述、分析、假设和符号通常控制在约 4 页以内；这是密度检查，不得以缩小字号或
  删除必要定义实现。
- 每张核心图表在正文说明：观察到什么、关键数值、为何出现、如何回答问题。
- 删除重复题面、教科书式算法介绍、无数据评价、重复流程图和不参与结论的装饰图。
- 摘要和正文不得出现附件文件名、工作表名、代码、程序、脚本、CSV、JSON、文件路径、
  生成过程、运行命令或“完整程序见附录”等制作痕迹。必要的数据指代改写为材料、角度、
  时段、区域或实验条件；实现与文件信息只放附录。
- 删除“满足问题一对模型建立和可计算性的要求”“由此证明本文写法正确”等面向任务清单
  或评审的解释句。结论只保留模型事实、定量结果、验证和边界。
- 删除“前者回答……后者回答……”“不因……预设结论”等替读者解释论证意图的元叙事；
  物理条件、数据判据和结果直接陈述，不再补一句说明它们分别“回答什么”。
- 符号和参数应在符号表或首次使用处直接定义，但正文不得写“首次出现处定义”“见下文定义”
  “未在表中列出的量另行定义”等阅读指引或写作安排。
- 对关键假设、参数和约束给出来源、范围或敏感性影响。
- 各问最终答案和结论性数值使用克制的粗体强调，中间参数和普通计算值保持常规字重。
- 中文 LaTeX 使用宋体正文时，先确认 `\textbf` 在最终 PDF 中确实产生可见粗体；若字体无粗体
  字形，应对关键词、核心方法和关键结果切换黑体或启用模板已有的伪粗体，不能只在源码中形式加粗。
- 先区分问题关系、分题求解、算法迭代、数值计算和状态决策，再决定是否画图；只有真实
  复杂依赖、三个以上不可合并步骤、判断或回退才使用流程图。禁止把任务契约、结果文件、
  Excel、支撑材料和结果交付拼成论文流程图。
- 三个以上相互依赖的对象、变量或问题若用图能明显缩短说明，优先制作关系图、结构图或
  机理图；表格仍用于精确比较，公式仍用于定义和推导。图形必须替代一段真实说明，不能
  与正文重复，也不能为增加图数而可视化简单列表。
- 问题关系复杂时至少规划一幅关系图、结构图或机理图；复杂算法再增加流程图。不得把
  “1--2 幅流程图”机械设为每篇配额。
- 保留 `.drawio`、TikZ、Python 或 `.pptx` 等可编辑源文件和 PDF/SVG 矢量输出；禁止渐变、
  阴影、圆角卡片、装饰图标和模板化彩色流程图；流程图默认使用白底黑灰线和基础几何。
- 节点文字必须内嵌在矩形或菱形自身，不得用独立文本框覆盖空框；示意图标注使用对象锚线。
  源图留白在生成器中解决，LaTeX 不得用 `trim`、`clip` 或非等比缩放修图。
- 按 `style-profile.md` 的 A/B 制图路由做漏图检查：全篇插图数量**硬性限定为 16 ~ 22 幅**（保持正文 0.65~0.85 幅/页的高密度区间）。
- 对显示不同演化过程、多时间节点（如 $t=0\,\text{s}, 10\,\text{s}, 20\,\text{s}, 40\,\text{s}$）或多临界状态（参考 **2024A 板凳龙** 舞龙队轨迹、运动演化与碰撞切点），**必须采用多面板子图拼图（Subfigures：含 (a)(b)(c)(d) 联排子图）**。单图包含 3-4 个子面板，提高信息密度。
- 正文（摘要至参考文献前一页）**硬性控制在 20 ~ 30 页**；既不少于 20 页（保证论证充分），也不超过 30 页（遵守官方硬上限）。借鉴国一优秀论文安排特色版面（模型决策流程图、多阶段演化拼图、临界切点碰撞图、机理-结果三联主图）。
- 几何机理和流程图优先 TikZ、draw.io 或 Visio；PowerPoint 仅在能保持真实边界锚点并通过
  逐连接审计时使用。工程三维与动态曲线优先 MATLAB，统计诊断和批量图优先 Python；
  数值图不得在演示软件中手工调整数据位置。

## 公式排版硬规则

- 行内公式不编号；所有独立展示公式必须编号，禁止 `\[...\]` 和带星号的无编号环境。
- 引出展示公式的最后一句必须以中文冒号“：”结束。
- 公式末尾不得保留句号、逗号、分号或中文标点；编号后不追加标点。
- 正文引用统一写“式（1）”；多行推导用一个编号环境包裹 `aligned` 或 `split`。
- 同组并列坐标、约束、状态方程或分段条件使用左大括号和 `aligned`，整组共用一个编号；
  连续推导不机械添加大括号。
- 段内 `\paragraph{...}` 或列表项加粗短语用于引出说明时，末尾统一使用中文冒号。

## 参考文献与附录

- 只引用实际阅读并在正文使用的真实来源；逐条核对作者、题名、年份和引用位置。
- 文献数量由方法与背景需要决定，不设为凑数目标。
- 附录列出支撑材料，并收录建模实际使用的完整可运行源程序；不得使用省略号占位。
- 正文不暴露附录文件名、代码入口、程序路径或运行过程。附录可以自成复现体系，但不得让
  “完整程序见附录”成为每问结尾的机械收口。
- 摘要和正文永不展示 AI 提示词、工具名、辅助脚注或生成过程。只有当年官方规则明确要求且用户授权时，
  才在参考文献后单列工具使用声明并准备匿名支撑记录；用户明确暂不加入时不得擅自创建或插入。
- 论文数值表不得手抄。由结果 CSV/JSON 生成 LaTeX 表，或由构建脚本写出表格片段；结果重跑后必须重新生成并核对。

## 编译与视觉验收

编译前运行：

```bash
python .agents/skills/cumcm-language-audit/scripts/audit_language.py --root .
python .agents/skills/cumcm-figures/scripts/audit_figure_style.py --root .
python .agents/skills/cumcm-diagrams/scripts/audit_diagram_style.py --root .
python .agents/skills/cumcm-paper/scripts/audit_section_chain.py --root .
```

只运行项目实际使用的图形审计；所有适用项与章节链都通过后再编译。自动扫描通过仍不能替代逐章、
最终尺寸与整页人工复核。

```bash
cd 论文
xelatex -interaction=nonstopmode 论文.tex
xelatex -interaction=nonstopmode 论文.tex
```

验收：

- `论文.log` 无 LaTeX Error，引用与编号已收敛；
- 摘要不超过一页，正文为 20--30 页且不超过当年官方上限；
- PDF 非空且满足文件大小限制；
- 逐页检查空白页、越界、重叠、缺字、低清图、表头断裂和异常留白；
- 数值、单位、有效数字与证据矩阵一致；
- 逐节执行内容审查，确认段落职责、标题必要性、方法兑现、结论证据和适用边界；
- 运行优秀论文相似度审计并通过。

缺少编译环境时，保留完整源码和资产，在审查报告记录未完成的视觉与编译检查。
