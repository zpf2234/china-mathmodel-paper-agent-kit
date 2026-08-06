# 全国大学生数学建模竞赛 Skills 与 MCP 工具箱

面向 **全国大学生数学建模竞赛（CUMCM）** 的一套 **Skills + MCP 绘图服务**。

这个仓库整理自本地 `D:\Documents\paper` 工程，主要服务于全国大学生数学建模竞赛论文生产、模型论证、结果解释、科研图件和可复用绘图能力建设。相比单纯模板，它更强调：

- 论文结构、摘要、模型、结果解释的完整写作链路
- 面向全国大学生数学建模竞赛/高教社杯风格的严谨推导与证据闭环
- TikZ / MATLAB / Visio / Draw.io 多后端绘图 MCP
- 中文标注、美观排版、可编辑矢量图和复现实验
- 面向中国参赛学生和指导教师的本地化工作流

## 仓库结构

```text
.agents/skills/          # 数模论文与绘图相关 Skills
figure_mcp/              # 图件生成/质量评估/MCP 服务源码
figure_mcp/drawio-mcp/   # Draw.io MCP 相关工程
```

## 适合谁

- 做全国大学生数学建模竞赛/校赛/美赛中文论文的同学
- 需要把 Python/MATLAB 结果变成高质量论文图的用户
- 想把智能体能力沉淀为 Skills 的个人/团队
- 想在本地跑 TikZ、MATLAB、Visio、Draw.io 图件服务的开发者

## 能做什么

### 1. 数模论文 Skills

` .agents/skills/ ` 中包含论文生产相关规则和参考材料，例如：

- 摘要写法
- 问题分析
- 模型选择与推导
- 结果解释
- 图表布局
- 公式与符号规范
- 国奖/优秀论文对标审查
- 附录与代码组织

### 2. Figure MCP 绘图能力

`figure_mcp/` 提供多种图件生成服务和质量门控：

- `tikz_server.py`：TikZ/LaTeX 矢量示意图
- `matlab_server.py`：MATLAB 风格工程图/曲线图
- `visio_server.py`：Visio 可编辑流程图/架构图
- `figure_router_server.py`：根据任务类型路由到合适绘图后端
- `quality_gate.py`、`pixel_fidelity.py`：图件质量检测与回归评估

## 快速开始

### 安装 Python 依赖

本仓库没有强绑定一个统一环境。建议先进入 `figure_mcp` 查看具体脚本需求：

```bash
cd figure_mcp
python -m pip install -U pip
python -m pip install -r requirements.txt  # 如果你的分支包含 requirements.txt
```

如果没有 `requirements.txt`，可按实际报错安装常见依赖，例如：

```bash
python -m pip install matplotlib numpy pandas pillow scipy pydantic fastmcp
```

### 启动 MCP 服务

按需运行：

```bash
python tikz_server.py
python matlab_server.py
python visio_server.py
python figure_router_server.py
```

不同客户端的 MCP 注册方式不同，请把对应 server 脚本配置为本地 MCP command。

## 设计原则

1. **服务论文结论**：图不是装饰，而是为模型、结论和证据链服务。
2. **中文优先**：默认面向中国用户，图注、论文说明和交付文档优先中文。
3. **可编辑优先**：能用 TikZ/Visio/Draw.io 矢量表达，就不只交截图。
4. **审计闭环**：图件、模型、结果和论文叙述要能互相核对。
5. **可复用沉淀**：一次性脚本逐步沉淀为 Skills/MCP 能力。

## 注意事项

- 部分 Visio/MATLAB 功能依赖 Windows 桌面环境和本机软件授权。
- TikZ 编译依赖本地 LaTeX/XeLaTeX 环境。
- `figure_mcp` 中部分 benchmark/output 目录属于运行产物，本仓库已尽量排除大体积缓存。
- 具体比赛论文请遵守赛事规则和学校要求。

## 许可证

MIT License。

如果你基于本仓库做二次开发，建议保留来源说明，并把你的题目数据、最终论文和临时运行产物放到独立目录，避免污染可复用 Skills/MCP。
