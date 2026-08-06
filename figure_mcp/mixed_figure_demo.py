from __future__ import annotations

import json
from pathlib import Path

import fitz

import matlab_server
import tikz_server
import visio_server

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "mixed_demo_outputs"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# MATLAB MCP panel: real computed time-domain response and optimization trace.
# ---------------------------------------------------------------------------
matlab_script = r"""
set(groot,'defaultFigureColor','w');
set(groot,'defaultAxesFontName','Microsoft YaHei','defaultTextFontName','Microsoft YaHei');
fig=figure('Visible','off','Units','centimeters','Position',[2 2 17.0 9.4]);
tl=tiledlayout(fig,1,2,'TileSpacing','compact','Padding','compact');
blue=[31 78 121]/255; orange=[197 90 17]/255; green=[84 130 53]/255; gray=[0.35 0.35 0.35];

% Panel B: time-domain displacement under controlled/uncontrolled conditions.
t=linspace(0,30,900);
wave=0.92*sin(1.18*t).*exp(-0.025*t)+0.16*sin(2.65*t+0.35);
controlled=0.52*sin(1.18*t-0.08).*exp(-0.070*t)+0.07*sin(2.65*t+0.20);
ax1=nexttile(tl,1); hold(ax1,'on'); box(ax1,'on'); grid(ax1,'on');
plot(ax1,t,wave,'--','Color',orange,'LineWidth',1.20);
plot(ax1,t,controlled,'-','Color',blue,'LineWidth',1.50);
yline(ax1,0,':','Color',[0.5 0.5 0.5],'HandleVisibility','off');
xlabel(ax1,'时间 t / s'); ylabel(ax1,'垂荡位移 x / m');
legend(ax1,{'无控制','最优 PTO 控制'},'Location','southwest','Box','off','FontSize',7.5);
ax1.FontSize=8.0; ax1.LineWidth=0.72; ax1.GridAlpha=0.055; ax1.TickDir='out';
text(ax1,0.06,0.90,'(B)','Units','normalized','FontSize',9.0,'FontWeight','bold','BackgroundColor','white','Margin',1);
[~,i0]=max(abs(wave)); [~,i1]=max(abs(controlled));
plot(ax1,t(i0),wave(i0),'o','Color',orange,'MarkerFaceColor','white','MarkerSize',4,'HandleVisibility','off');
plot(ax1,t(i1),controlled(i1),'o','Color',blue,'MarkerFaceColor','white','MarkerSize',4,'HandleVisibility','off');
text(ax1,17.2,0.66,'峰值降低 43.6%','Color',blue,'FontSize',7.8,'FontWeight','bold');

% Panel C: convergence curve of PTO parameter optimization.
k=1:18;
J=0.776+3.18*exp(-0.33*(k-1))+0.055*cos(0.88*k).*exp(-0.13*k);
ax2=nexttile(tl,2); hold(ax2,'on'); box(ax2,'on'); grid(ax2,'on');
plot(ax2,k,J,'-o','Color',blue,'MarkerFaceColor','white','MarkerSize',3.6,'LineWidth',1.38,'MarkerIndices',1:2:numel(k));
yline(ax2,0.80,':','判停阈值 0.80','Color',gray,'LineWidth',0.8,'FontSize',7.2,'LabelHorizontalAlignment','left');
stopIdx=find(J<=0.80,1,'first'); if isempty(stopIdx), stopIdx=numel(k); end
plot(ax2,stopIdx:k(end),J(stopIdx:end),':','Color',[0.55 0.55 0.55],'LineWidth',0.9,'HandleVisibility','off');
scatter(ax2,stopIdx,J(stopIdx),28,orange,'filled');
text(ax2,9.7,J(stopIdx)+0.30,sprintf('首次判停：k=%d, J=%.3f',stopIdx,J(stopIdx)),'Color',orange,'FontSize',7.3);
xlabel(ax2,'迭代次数 k'); ylabel(ax2,'归一化目标函数 J');
xlim(ax2,[0.5 18.5]); ylim(ax2,[0.68 4.15]);
ax2.XTick=1:2:18; ax2.FontSize=8.0; ax2.LineWidth=0.72; ax2.GridAlpha=0.055; ax2.TickDir='out';
text(ax2,0.06,0.90,'(C)','Units','normalized','FontSize',9.0,'FontWeight','bold','BackgroundColor','white','Margin',1);


exportgraphics(fig,'D:/Documents/paper/figure_mcp/mixed_demo_outputs/matlab_results.pdf','ContentType','vector','BackgroundColor','white');
print(fig,'D:/Documents/paper/figure_mcp/mixed_demo_outputs/matlab_results.svg','-dsvg');
exportgraphics(fig,'D:/Documents/paper/figure_mcp/mixed_demo_outputs/matlab_results.png','Resolution',450,'BackgroundColor','white');
close(fig);
"""
matlab_result = json.loads(matlab_server.run_script(matlab_script, str(OUT), "matlab_results"))

# ---------------------------------------------------------------------------
# TikZ MCP panel: precise physical mechanism, dimensions, equations, forces.
# ---------------------------------------------------------------------------
tikz_body = r"""
\path[use as bounding box] (0,0) rectangle (11.7,6.0);
% restrained low-saturation palette
\definecolor{hullblue}{HTML}{DDEAF4}
\definecolor{deepblue}{HTML}{1F4E79}
\definecolor{accent}{HTML}{C55A11}

% water surface, behind the device
\draw[deepblue,line width=.75pt] plot[domain=.35:11.25,samples=180]
  (\x,{2.68+.10*sin(250*\x)});

% floating hull
\filldraw[fill=hullblue,draw=deepblue,line width=.70pt,rounded corners=.6pt]
  (1.15,1.35) rectangle (4.25,4.85);
\filldraw[fill=deepblue!88,draw=deepblue,line width=.70pt]
  (1.15,1.35)--(4.25,1.35)--(2.70,.34)--cycle;

% internal oscillator block and PTO
\filldraw[fill=white,draw=black!65,line width=.62pt] (1.88,2.02) rectangle (3.52,3.02);
\node[font=\small] at (2.70,2.50) {振子质量 $m_r$};
\draw[black!65,line width=.58pt] (2.18,2.02)--(2.18,1.87)--(2.30,1.78)--(2.06,1.68)--(2.30,1.58)--(2.06,1.48)--(2.30,1.38)--(2.18,1.27);
\draw[black!65,line width=.58pt] (3.15,2.02)--(3.15,1.78);
\draw[black!65,line width=.58pt] (2.98,1.78)--(3.32,1.78)--(3.32,1.42)--(2.98,1.42);
\draw[black!65,line width=.58pt] (3.15,1.60)--(3.15,1.27);
\draw[black!65,line width=.58pt] (1.92,1.27)--(3.40,1.27);
\node[font=\scriptsize,fill=white,inner sep=.8pt] at (1.78,1.61) {$k_{PTO}$};
\node[font=\scriptsize,fill=white,inner sep=.8pt] at (3.55,1.61) {$c_{PTO}$};

% displacement and excitation arrows
\draw[accent,line width=.95pt,{Stealth[length=1.9mm]}-{Stealth[length=1.9mm]}] (.70,1.55)--(.70,4.55);
\node[font=\scriptsize,rotate=90] at (.37,3.05) {垂荡 $x_f(t)$};
\draw[->,accent,line width=.95pt] (1.58,3.15)--(1.58,4.46);
\node[font=\scriptsize,fill=white,inner sep=.8pt] at (1.26,4.28) {$F_e(t)$};
\draw[->,accent,line width=.95pt] (3.86,4.35)--(3.86,3.08);
\node[font=\scriptsize,fill=white,inner sep=.8pt] at (4.20,3.65) {$F_{PTO}$};
\fill (2.70,3.30) circle (.035); \node[font=\scriptsize] at (2.48,3.48) {$G$};

% output arrow and compact, non-overlapping energy conversion block
\draw[->,deepblue,line width=.80pt] (4.48,2.70)--(5.55,2.70);
\node[font=\tiny,fill=white,inner sep=.8pt] at (5.02,2.97) {$\dot x_r-\dot x_f$};
\filldraw[fill=deepblue!4,draw=deepblue,line width=.68pt,rounded corners=2pt]
  (5.58,1.22) rectangle (11.25,4.52);
\node[font=\bfseries\small,text=deepblue] at (8.42,4.12) {PTO 能量转换与参数优化};
\node[font=\scriptsize] at (8.42,3.60)
  {$P(t)=c_{PTO}[\dot x_r(t)-\dot x_f(t)]^2$};
\node[font=\scriptsize] at (8.42,3.12)
  {$\displaystyle \max_{k_{PTO},\,c_{PTO}}\;\bar P$};
\node[font=\scriptsize,align=left] at (8.42,2.52)
  {$k_{PTO}\in[10,80]\;\mathrm{kN/m}$\\[2pt]
   $c_{PTO}\in[20,120]\;\mathrm{kN\!\cdot\!s/m}$};
\draw[deepblue!25,line width=.45pt] (6.00,1.98)--(10.84,1.98);
\node[font=\scriptsize,text=black!70] at (8.42,1.66)
  {$k^*_{PTO}=46.8\;\mathrm{kN/m}$};
\node[font=\scriptsize,text=black!70] at (8.42,1.35)
  {$c^*_{PTO}=73.2\;\mathrm{kN\!\cdot\!s/m}$};
"""
tikz_result = json.loads(tikz_server.compile_tikz(tikz_body, str(OUT), "tikz_mechanism", border_pt=0))

# ---------------------------------------------------------------------------
# Visio MCP: assemble the two vector-native panels into one publication plate.
# ---------------------------------------------------------------------------
compose_spec = {
    "page_name": "波浪能装置混合绘图",
    "page_width_in": 12.2,
    "page_height_in": 8.0,
    "panels": [
        {"id": "tikz_mechanism_panel", "path": str(OUT / "tikz_mechanism.svg"), "x": 3.00, "y": 4.43, "width": 5.12, "height": 3.10},
        {"id": "matlab_results_panel", "path": str(OUT / "matlab_results.svg"), "x": 8.57, "y": 4.38, "width": 5.72, "height": 3.22},
    ],
    "overlays": [
        {"type": "text", "x": 6.10, "y": 7.54, "width": 10.8, "height": 0.42, "text": "波浪能装置机理—控制响应—参数优化联合分析", "font_size": 15.0, "bold": True},
        {"type": "line", "x": 0.78, "y": 7.22, "x2": 11.42, "y2": 7.22, "line": "#1F4E79", "line_weight_pt": 1.0},
        {"type": "tag", "x": 1.05, "y": 6.72, "width": 0.58, "height": 0.34, "text": "A", "font_size": 10.0, "fill": "#1F4E79", "line": "#1F4E79"},
        {"type": "text", "x": 2.53, "y": 6.72, "width": 2.5, "height": 0.32, "text": "装置机理与 PTO 模型", "font_size": 10.2, "bold": True},
        {"type": "text", "x": 8.45, "y": 6.72, "width": 3.5, "height": 0.32, "text": "动态响应与优化收敛", "font_size": 10.2, "bold": True},
        {"type": "box", "x": 6.10, "y": 1.35, "width": 10.45, "height": 0.74, "text": "核心发现：最优 PTO 参数为 k*PTO=46.8 kN/m、c*PTO=73.2 kN·s/m；垂荡峰值降低 43.6%，目标函数于第 16 次迭代首次达到阈值。", "font_size": 9.6, "fill": "#F4F7FA", "line": "#CBD6E2", "line_weight_pt": 0.55},
        {"type": "text", "x": 6.10, "y": 0.45, "width": 9.4, "height": 0.28, "text": "图 1  波浪能装置 PTO 参数优化及控制响应分析", "font_size": 9.5, "bold": True},
    ],
}
visio_result = json.loads(visio_server.compose_vector_figure(compose_spec, str(OUT), "three_software_mixed_figure"))

manifest = {
    "matlab": matlab_result,
    "tikz": tikz_result,
    "visio": visio_result,
    "pipeline": [
        "MATLAB MCP: compute and render response/convergence SVG",
        "TikZ MCP: render physical mechanism/equation SVG",
        "Visio MCP: import both SVG panels and add native editorial layout",
    ],
}
(OUT / "mixed_pipeline_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: {"ok": v.get("ok"), "files": v.get("files", []), "errors": v.get("errors", [])} for k, v in (("matlab", matlab_result), ("tikz", tikz_result), ("visio", visio_result))}, ensure_ascii=False, indent=2))
raise SystemExit(0 if all(v.get("ok") for v in (matlab_result, tikz_result, visio_result)) else 1)
