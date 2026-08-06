# LaTeX 模板与排版规范

## 官方硬约束

以 [official-rules.md](official-rules.md) 和当年官网为准：

- A4，页边距至少 2.5 cm；
- 电子版第一页为摘要专用页；
- 摘要原则上不超过一页；
- 正文不要目录，必须达到项目要求的 20--30 页且不超过当年官方页数上限；
- 从附录首页起不设页数上限，只检查文件大小、完整性和可读性；
- 摘要、正文、附录和支撑材料不得出现身份信息；
- 论文与支撑材料满足当年文件格式和大小限制；
- 附录列支撑材料并包含全部建模源程序。

不要把经验性字数、总页数或图表数量写成官方规则。

## 主文件

```latex
\PassOptionsToPackage{quiet}{xeCJK}
\documentclass[withoutpreface,bwprint]{format}
\usepackage{ctex}
\usepackage{booktabs}
\usepackage{array}
\usepackage{tabularx}
\usepackage{longtable}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{siunitx}
\usepackage{url}

\newcolumntype{C}{>{\centering\arraybackslash}X}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\newcolumntype{R}{>{\raggedleft\arraybackslash}X}

\title{论文标题}

\begin{document}
\maketitle
\input{0.摘要.tex}

% 官方规范：不要目录。
\input{1.问题重述.tex}
\input{2.问题分析.tex}
\input{3.模型假设.tex}
\input{4.符号说明.tex}
\input{5.模型的建立与求解.tex}
% 有两类以上实质性跨问题证据时取消下一行注释；否则合并到逐问验证或评价前一节。
% \input{6.综合验证与稳健性.tex}
\input{7.模型评价.tex}
\input{8.模型改进推广.tex}
\clearpage
\label{references:start}
\input{9.参考文献.tex}
\input{10.附录.tex}
\end{document}
```

章节文件可按实际论文合并，但不要保留空章节。参考文献必须另起一页，且保留
`\label{references:start}`；自动审计以该页前一页作为正文末页。

各问题章节连续排版。不得在问题一、问题二或其他分问章节的开头、结尾设置 `\newpage`、
`\clearpage` 或仅为截断章节而添加的 `\FloatBarrier`。若页尾剩余空间足以容纳一级标题及
至少两行正文，下一问应直接接排。只有摘要环境结束、参考文献开始和附录开始允许固定换页。
确需阻止单张图跨越问题边界时，优先调整该图的浮动位置或使用 `[H]`，不得用分问题强制
换页掩盖浮动体布局。

## 标题层级与符号章

- 一级标题显示为中文序数，二级、三级标题分别使用两段和三段编号；
- 编号标题不超过三级；`\paragraph{...}` 只能作为不编号的段内引导语；
- 一级、二级标题必须含研究对象、关键变量、模型/算法或动作中的至少两项，不单独使用
  “模型的建立”“算法的实施”“计算结果”“进一步讨论”等空泛标题；
- 符号说明设置为独立一级章，严格使用“符号｜物理或数学含义｜单位或量纲”三列；
- 标题后默认直接放符号表；必要文字只说明共同约定或适用范围，保持一至两句且不作评价；
- 单位列不得留空，无量纲量统一写“无量纲”或“--”；
- 第五个一级标题固定为“模型的建立与求解”，具体推导、参数求取和数值求解过程均在该章展开。

符号表示例：

```latex
\section{符号说明}

\begin{table}[htbp]
  \centering
  \caption{主要符号及其含义}
  \label{tab:symbols}
  \begin{tabularx}{\textwidth}{C L C}
    \toprule
    \textbf{符号} & \textbf{物理或数学含义} & \textbf{单位或量纲} \\
    \midrule
    $t$ & 任务开始后的时刻 & \si{\second} \\
    $\eta$ & 方案的综合评价指标 & 无量纲 \\
    \bottomrule
  \end{tabularx}
\end{table}
```

可直接复用的章节资产为：

```text
.agents/skills/cumcm-paper/assets/latex-template/notation.tex
.agents/skills/cumcm-paper/assets/latex-template/model-establishment-solution.tex
```

最后一个问题回答之后必须能定位跨问题验证与共同边界。有两类以上实质性跨问题证据时，
设置独立一级章“综合验证与稳健性”或信息等价的标题；否则合并到逐问验证或评价前一节。
不得只用一句“结果合理”代替验证，也不得为保留章名伪造实验。

## 表格选择

- 单页短表：`table` + `tabularx`；
- 需要跨页的结果表：`longtable`；
- 宽表优先重排字段、拆成有逻辑的两表或移入附录，不缩小到不可读；
- 数值列统一小数位并按小数点对齐，单位写在表头；
- `\caption` 在 `\label` 前，正文必须引用并解释表格。

短表示例：

```latex
\begin{table}[htbp]
  \centering
  \caption{模型验证结果}
  \label{tab:validation}
  \begin{tabularx}{\textwidth}{LCCC}
    \toprule
    方法 & 指标 & 结果 & 判定 \\
    \midrule
    步长收敛 & 相对误差（\%） & 0.42 & 通过 \\
    \bottomrule
  \end{tabularx}
\end{table}
```

跨页表示例：

```latex
\begin{longtable}{p{0.18\textwidth}p{0.24\textwidth}p{0.46\textwidth}}
  \caption{完整结果表}\label{tab:full-results}\\
  \toprule
  编号 & 指标 & 结果 \\
  \midrule
  \endfirsthead
  \caption[]{完整结果表（续）}\\
  \toprule
  编号 & 指标 & 结果 \\
  \midrule
  \endhead
  \bottomrule
  \endfoot
  1 & 示例 & 示例结果 \\
\end{longtable}
```

## 图片与公式

- 图片路径相对 `论文/`，优先引用求解阶段生成的 PDF/SVG/PNG；
- 统一图宽和字体尺度，避免在 LaTeX 中拉伸变形；
- 行内公式不编号，所有独立展示公式必须编号；禁止 `\[...\]` 和 `equation*` 等无编号环境；
- 引出展示公式的最后一句以中文冒号“：”结束；
- 同组并列坐标、约束、状态方程或分段条件用
  `\left\{\begin{aligned}...\end{aligned}\right.` 排列并共用一个编号；
- 段内 `\paragraph{...}` 或列表项加粗短语承担引导作用时，以中文冒号结束；
- 公式主体末尾不保留句号、逗号、分号或中文标点，编号后不追加标点；
- 多行公式使用 `aligned`、`split` 或 `multline`，不得越过正文边界；
- 符号首次出现即定义，单位和有效数字保持一致。

推荐写法：

```latex
由运动学关系可得：
\begin{equation}
  \bm x(t)=\bm x_0+\bm v t
  \label{eq:motion}
\end{equation}
```

正文引用写作“由式 \eqref{eq:motion} 可得”。不要在 `\end{equation}` 前后添加标点。

## 编译与检查

先创建主文件和摘要并编译；之后每写入 1--2 个章节就编译一次，不把整篇长稿留到最后一次性落盘。

```bash
xelatex -interaction=nonstopmode 论文.tex
xelatex -interaction=nonstopmode 论文.tex
```

- 摘要末尾必须保留 `\label{abstract:end}`；从 `.aux` 检查其所在页，确保摘要不超过一页；
- `\label{references:start}` 必须紧跟 `\clearpage`，保证参考文献确实另起一页；
- 检查 unresolved reference/citation、Overfull、Float too large 和缺字警告；
- 逐页渲染 PDF，检查空白、重叠、截断、低清图、断裂表头和页码；
- 不通过缩小页边距、字号或行距规避官方页数限制。
