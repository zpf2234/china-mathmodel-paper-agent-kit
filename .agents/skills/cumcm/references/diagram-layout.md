# 几何图与流程图布局约束

本规则适用于几何机理图、坐标关系图、问题关系图、算法流程图和计算框图。数据图的坐标轴
排版仍按 `figure-routing.md` 执行。

所有连接还必须执行 [diagram-connection-audit.md](diagram-connection-audit.md)：
先逐条登记与验收引线、箭头、分支和反馈，再做整图构图审查；两层任一失败均停止导出。

## 单一对象与锚定

- 有边框的节点必须把文字写入形状自身的 `TextFrame`，不得用独立文本框覆盖在矩形或
  菱形上。形状移动、缩放和字体替换时，边框与文字必须作为同一对象变化。
- 节点文字水平、垂直居中，四周保留安全内边距；标题和说明可使用同一文本框中的不同段落，
  不拆成多个浮动文本框。
- 流程节点只写一个动作、条件或输入输出，默认使用统一字号与字重，主动控制在一至两行。
  不采用“大标题 + 小号解释”的卡片式层级；参数含义、方法理由和结果解释放在图前后正文。
- 连接线从节点边界锚点出发并终止于另一节点边界，不从节点中心穿过，不依赖视觉上“差不多
  对齐”的绝对坐标。
- 流程箭头的起点与终点必须绑定节点外轮廓锚点；箭头尖端止于目标框边界，箭头线段和尖端
  均不得伸入目标框内部。反馈线先在节点外侧正交绕行，再从指定边界锚点接入。
- 几何标注必须记录被标注对象的锚点。标注放在对象外部时使用细引线；不得把文字直接压在
  轨迹、边界线、圆周、箭头或其他标签上。

## 固定画布

- 生成器显式设置画布宽高和纵横比，所有对象坐标均相对于该画布。
- Office 文本框写入文字后必须再次显式设置 `Left/Top/Width/Height`，并关闭自动适应。
  PowerPoint 可能在写入中文时先收缩文本框；只在创建时传入坐标不足以锁定成品位置。
- 文本检查使用实际字形包围盒，不用名义文本框代替；字形四周至少保留 1--2 pt 安全距离。
- 文本框不得旋转，字体、字号、水平对齐、垂直锚定、换行和段前段后距均显式设置。
- 导出 PDF/SVG 时保持原画布，不使用 `bbox_inches="tight"`、Office 自动裁边或其他会改变
  页面坐标原点的紧边界导出。
- 示意图和流程图在 LaTeX 中只允许 `page` 与 `width`/`height` 的等比例缩放；禁止使用
  `trim`、`clip`、非等比 `resizebox` 修补源图留白或错位。应回到源图调整画布。

## 源端检查

每个正式示意图或流程图必须在同目录生成同名 `.layout.json`，至少包含：

```json
{
  "pass": true,
  "canvas_pt": [720, 405],
  "checks": {
    "objects_inside_canvas": true,
    "node_text_embedded": true,
    "text_inside_parent": true,
    "node_lines_max_2": true,
    "uniform_node_text_style": true,
    "decision_lines_max_2": true,
    "annotation_anchors": true,
    "leader_endpoint_on_target": true,
    "arrow_endpoints_on_node_boundary": true,
    "arrowheads_outside_node_interior": true,
    "connection_inventory_complete": true,
    "non_target_crossings_zero": true,
    "branch_label_clearance": true,
    "final_render_connections_checked": true,
    "line_direction_semantics_complete": true,
    "arrow_direction_matches_meaning": true,
    "line_style_matches_meaning": true,
    "text_line_clearance": true,
    "label_object_clearance": true,
    "final_font_size_readable": true,
    "composition_balance": true,
    "latex_trim_required": false
  }
}
```

生成器在导出前执行：

1. 所有形状和文本的边界位于画布内；
2. 节点文本的实际包围盒不超过节点扣除内边距后的可用区域；
3. 所有流程节点不超过两行且使用统一字号与字重；判断菱形超过两行时，先缩短判断语句或放宽菱形，
   不通过自动压缩字号容纳；
4. 独立注释框互不重叠，并且都有对象锚点或明确的轴标签职责；
5. 实际字形包围盒不与轨迹、视线、轮廓、箭头或非目标实体相交；
6. 箭头不穿过非目标节点，回路线从节点外侧正交绕行；
7. 几何引线的目标端点位于对应线段、圆周、轮廓或关键点上，不能只停在目标附近；
8. 流程箭头逐条检查“源节点边界—节点外部连线—目标节点边界”，箭头尖端不得越过边界；
9. 节点主轴、反馈回路和画布留白形成可辨识层级，不把全部对象机械铺满；
10. 最小字号按论文实际插入宽度换算后仍不低于 8 pt。

任一检查失败时停止导出，不通过缩小字体或 LaTeX 裁边掩盖。

`.layout.json` 还必须包含 `diagram-connection-audit.md` 规定的 `connection_audit` 与
`line_semantics_audit`、`overall_audit`。不得只写汇总布尔值而省略逐连接与逐线族 `items`。

## 成品检查

- 先把矢量图按论文实际宽度插入，再渲染整页 PDF；只看源 PPT 或单独打开 PDF 不算验收。
- 至少在 100% 页面视图和缩略图视图各检查一次：框内居中、引线归属、箭头端点、文字压线、
  节点间距、图题间距和页面留白。
- 修改字体、文字、节点尺寸、画布、导出软件或 LaTeX 插入尺寸后，布局审计和整页渲染必须
  重新执行。
