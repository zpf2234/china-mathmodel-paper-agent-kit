from __future__ import annotations
import sys, time
import pythoncom, win32com.client
from pathlib import Path

def p(s):
    print(s, flush=True)

pythoncom.CoInitialize(); p('1 coinit')
a=d=st=None
try:
    a=win32com.client.DispatchEx('Visio.Application'); a.Visible=False; p('2 app')
    d=a.Documents.Add(''); p('3 doc')
    st=a.Documents.OpenEx('BASFLO_U.VSSX',64); p('4 stencil')
    m=st.Masters.Item('判定'); p('5 master')
    page=d.Pages.Item(1); p('6 page')
    s=page.Drop(m,4,6); p('7 drop')
    s.CellsU('Width').FormulaU='2.3 in'; s.CellsU('Height').FormulaU='1.18 in'; s.Text='误差小于阈值？'; p('8 style')
    line=page.DrawLine(4,7,4,6.59); line.CellsU('EndArrow').FormulaU='13'; p('9 line')
    out=Path(r'D:\Documents\paper\figure_mcp\benchmark_outputs')
    d.SaveAs(str(out/'diag_visio.vsdx')); p('10 save')
    d.ExportAsFixedFormat(1,str(out/'diag_visio.pdf'),1,0); p('11 pdf')
    page.Export(str(out/'diag_visio.svg')); p('12 svg')
    page.Export(str(out/'diag_visio.png')); p('13 png')
finally:
    if d:
        try:d.Close();p('14 doc close')
        except Exception as e:p(f'doc close err {e!r}')
    if st:
        try:st.Close();p('15 stencil close')
        except Exception as e:p(f'st close err {e!r}')
    if a:
        try:a.Quit();p('16 quit')
        except Exception as e:p(f'quit err {e!r}')
    pythoncom.CoUninitialize(); p('17 done')
