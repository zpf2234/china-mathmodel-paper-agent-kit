# 高教杯优秀论文三软件 MCP 绘图控制

三个绘图后端和一个语义路由 MCP（stdio），可同时接入 Hermes 和 Codex：

- `figure_router_server.py`：判断是否需要插图、图型、绘图后端、正文落点与证据要求。
- `matlab_server.py`：数据曲线、轨迹、热力图、三维曲面、仿真结果；输出 `.m/.json/.pdf/.svg/.png`。
- `tikz_server.py`：精确二维几何、角度、尺寸、公式关系；输出 `.tex/.json/.pdf/.svg`。
- `visio_server.py`：流程图、问题关系、技术路线、模型结构；输出可编辑 `.vsdx` 以及 `.pdf/.svg/.png/.json`。

## 固定环境

- MATLAB：`D:/MATLAB2026a/MATLAB R2024b/bin/matlab.exe`
- XeLaTeX：`D:/MiKTeX/miktex/bin/x64/xelatex.exe`
- Visio：`C:/Program Files/Microsoft Office/root/Office16/VISIO.EXE`
- Python：Hermes 自带 Python（含 `mcp`、`pywin32`）

## 设计原则

1. 不做鼠标键盘屏幕模拟；MATLAB 走 batch，TikZ 走编译器，Visio 走 COM。
2. 所有图优先交付可编辑源文件和 PDF/SVG 矢量结果。
3. 统一白底、微软雅黑、克制蓝橙配色、论文版心宽度和线宽。
4. 数值点只从结构化数据生成，不在 Visio 中手工挪动。
5. 复杂混合图：MATLAB/TikZ 生成主体，Visio 负责关系组织。

## A/B 特色主视觉 benchmark

`benchmarks/signature_specs/` 提供跨赛题、非 2024B 专用的三类结构化规格：

- `a_mechanism_result.json`：A 类机理—临界事件—误差闭合；
- `b_strategy_landscape.json`：B 类策略区域—价值等高线—推荐点；
- `uncertainty_decision_linkage.json`：A/B 通用不确定性收缩—阈值穿越—策略切换。

运行 `python signature_benchmarks.py` 会先检查核心命题、十秒结论、语义阅读链和数据联动，再真实
调用 MATLAB 生成 `.m/.json/.pdf/.svg/.png`。`pytest -q test_signature_benchmarks.py` 包含仅换配色、
装饰性拼图和缺科学证据的负回归；这些情况即使视觉风格完整也不能通过。

## Codex 配置

Windows 原生命令使用 `codex mcp add` 加入；配置名称固定为：

- `paper-matlab`
- `paper-tikz`
- `paper-visio`
- `paper-figure-router`

接入后用 `codex mcp list` 核对。
