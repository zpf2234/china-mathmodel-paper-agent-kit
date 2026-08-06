---
name: cumcm-figures
description: 规划、生成和审查 CUMCM 数据图形。用于依据待证明命题、数据维度和不确定性选择图型，以本地 50 篇优秀论文的图形密度作漏图或冗余检查，并统一出版级配色、标注、分辨率和正文解释。
---

# CUMCM 数据图形

先读 [../cumcm/references/figure-routing.md](../cumcm/references/figure-routing.md) 与
[../cumcm-paper/references/section-chain-contract.md](../cumcm-paper/references/section-chain-contract.md)，
再完整读取 [references/aesthetic-standard.md](references/aesthetic-standard.md)。国一/国奖候选还必须读取
[references/visual-identity-and-archetypes.md](references/visual-identity-and-archetypes.md) 与
[references/signature-figure-standard.md](references/signature-figure-standard.md)，并复制
[templates/signature-figure-plan.md](templates/signature-figure-plan.md) 在普通图批量生成前规划特色主视觉；
特色必须来自真实模型和结果，不得用装饰性信息图替代科学证据。工作区启用论文绘图 MCP 时完整读取
[../cumcm/references/figure-mcp-routing.md](../cumcm/references/figure-mcp-routing.md)，并调用项目级
`cumcm-figure-router` 判断是否插图、图型、后端与正文位置。若独立 `paper-figure-router` MCP 可用则优先
调用；不可用时运行 `cumcm-figure-router/scripts/route_figures.py` 并登记
`router_mode: deterministic_fallback`。工程动态、轨迹、曲面和参数结果优先交给 `paper-matlab`。
结构图、机理图和流程图转交 `cumcm-diagrams`。

涉及临界构型、切点、垂足、碰撞或策略切换边界时，除非主图在最终宽度已经足够清楚，否则向
`cumcm-diagrams` 传递 `detail_inset` 契约，由同一结构化几何重绘局部，不得裁图放大。涉及单主轴、
判断和反馈的算法证据时，优先传递 `visual_preset: editorial-spine` 与 `focus_node`；它是跨题型视觉
语法，不是某道题的固定流程模板。

## 先定义证据职责

每张图先写一句内部命题：它要证明趋势、差异、空间结构、分布、拟合、残差、收敛、敏感性、
方案结构还是不确定性。无法写出唯一主要命题的图先合并、拆分或删除。
路由返回 `should_insert=false` 时不再调用绘图工具；返回 true 时把 `insertion_point`、
`before_sentence_contract` 和 `after_paragraph_contract` 写入图形注册表，约束正文落点和解释顺序。

## 图型路由

- 时间演化或迭代：折线图，必要时加置信带或事件标记；
- 两变量关系与拟合：散点图加模型曲线，残差另设诊断面板；
- 分布与组间差异：箱线图、小提琴图、直方图或经验分布；
- 参数扫描与敏感性：响应曲线、等高线或热力图；
- 空间路线与覆盖：真实坐标系中的路线、覆盖带、方向或误差图；
- 多方案精确比较：排序条形图、点图或小型多面板；
- 收敛与稳健性：目标轨迹、多起点分布、扰动箱线图或区间图；
- 三维曲面仅在第三维本身有解释价值时使用，能用等高线表达时优先二维。

## 50 篇普查校准与硬性数量约束

760 个正式图形中，机理/几何、动态、空间路线、算法框架和参数曲线最常见；诊断、比较、敏感性与热图按题目需要出现。

### 核心硬性要求与特色安排

1. **图形数量硬性约束（16 ~ 22 幅）**：全篇正文中，正式注册的图号数量必须**硬性限制在 16 ~ 22 幅之间**。密度在 20-30 页正文中维持在 0.65~0.85 幅/页的高学术密度区间。
2. **多阶段演化过程采用多面板拼图 (Subfigures)**：
   - 对涉及多时间节点（如 $t=0\,\text{s}, 10\,\text{s}, 20\,\text{s}, 40\,\text{s}$）、多阶段运动演化、临界状态对比（如 **2024A 板凳龙** 舞龙队运动轨迹、碰撞临界切点、多阶段调头过程）的题目，**必须采用多面板子图拼图（Subfigures：含 (a)、(b)、(c)、(d) 子图）** 呈现。
   - 单张大图下拼合 3~4 个子面板，既避免占用过多图号，又集中展现动态演化过程，极大增强版面学术冲击力。
3. **20 ~ 30 页正文的特色版面安排**：
   - 正文页数（摘要至参考文献前一页）**严格限制在 20 ~ 30 页**。
   - 借鉴 2024A 板凳龙优秀论文，打造特色排版：包含前置模型选择决策图、多阶段临界演化拼图、板凳节点轨迹与碰撞边界图、机理-结果三联特色主图。

按“正文图数 ÷ 正文页数”做二次审计：

- 机理或优化证据占主导时，0.55 / 0.71 / 0.88 可作下四分位、中位数、上四分位参照；
- 数据分析或决策证据占主导时，0.41 / 0.60 / 0.80 可作相应参照；
- **全篇硬性控制：正文插图数在 16 ~ 22 幅，正文页数严格控制在 20 ~ 30 页。**

## 审美与真实性

- 白底或极浅底，黑灰文字，使用一套克制主色和一套强调色；
- 同类变量颜色、线型、点型全篇一致；颜色不能成为唯一区分手段；
- 坐标轴写变量和单位，图例命名与正文一致，字号在最终插入尺寸可读；
- 误差条、置信带和样本量在适用时明确；不截断坐标轴制造差异；
- 数值点必须由结果文件生成，不在 PowerPoint 或绘图软件中手动移动；
- 优先 PDF/SVG 矢量输出；位图按最终尺寸确保清晰，避免截图和插值放大。

最终字号、线宽、插入宽度、色觉安全配色和各图型专属检查严格按 `aesthetic-standard.md` 执行。
默认软件主题、彩虹色、图内大标题、三维柱、无单位坐标或只展示最好一次的随机优化曲线不得放行。

## 正文解释

图前提出命题，图后依次写观察、关键数值、机制解释和对答案的影响。不得逐点念图，
也不得只写“由图可知模型效果良好”。同一结果不再用一张图和一张表完整重复。

## 门禁

为每张图记录数据来源、生成命令、主要命题、正文定位和可编辑源文件，并建立
`审查/figure-registry.json`。schema v3 在根级登记全局视觉身份与 signature policy，在逐图登记
`signature_figure/core_claim/ten_second_takeaway/read_order/data_linkage/signature_checks`。字段结构可复制
[assets/figure-registry.example.json](assets/figure-registry.example.json) 后替换为本项目真实路径和检查证据。运行：

```bash
python .agents/skills/cumcm-figures/scripts/audit_figure_style.py --root .
# 国一/国奖候选必须显式开启特色图门禁
python .agents/skills/cumcm-figures/scripts/audit_figure_style.py --root . --track national-first
```

每次正文 figure、源数据、生成脚本或矢量输出变化后先运行
`python .agents/skills/cumcm-review/scripts/sync_review_artifacts.py --root .`。该命令生成
provenance v2 的逐文件 SHA-256；哈希仅证明文件身份和链路，不替代图型适配、审美和科学性人工复核。

自动报告与人工整页复核均通过后写 `gates/figures.json`。检查图型适配、数值可追溯、标注单位、
色觉与灰度可辨、最终尺寸清晰、密度审计和正文解释。国一模式至少一张特色图，确实不适合时允许
记录具体科学理由、关联证据和独立审查批准的豁免；豁免不降低任何科学、provenance 或最终页面门禁，
也不得为满足数量强制拼图。仅换配色、装饰增强或无共享事件/阈值的数据拼接一律拒绝。
