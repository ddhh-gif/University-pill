from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT = Path(__file__).resolve().parent
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font_manager.fontManager.addfont(font_path)
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font_path).get_name(), 'axes.unicode_minus':False, 'font.size':11})
td = np.array([0,30,90,150,210,270,330,390,450,510,570])
tc = np.arange(0,601,60)
samples = [
    dict(name='有机玻璃', stem='有机玻璃', R=140.6, S=.100*.100, rho=1171,
         vd=[.027,.091,.138,.165,.173,.202,.207,.214,.226,.233,.241],
         vc=[.027,.034,.035,.040,.051,.058,.068,.078,.088,.099,.110]),
    dict(name='橡胶', stem='橡胶', R=140.17, S=.095*.095, rho=1401,
         vd=[.022,.067,.097,.102,.105,.105,.105,.104,.104,.105,.104],
         vc=[-.020,.010,.011,.029,.049,.072,.094,.114,.133,.154,.171]),
]
results = []
tables = []
for s in samples:
    vd, vc = np.array(s['vd']), np.array(s['vc'])
    delta, theta = vd/.040, vc/.040
    b, a = np.polyfit(tc[-5:], theta[-5:], 1)
    fit = a+b*tc[-5:]
    r2 = 1-np.sum((theta[-5:]-fit)**2)/np.sum((theta[-5:]-theta[-5:].mean())**2)
    P = 20**2/s['R']; q = P/(2*s['S']); D = delta[-5:].mean()
    lam = q*.010/(2*D); c = q/(s['rho']*.010*b)
    assert np.isclose(D, np.mean(vd[-5:])/.040)
    assert np.isclose(s['rho']*s['S']*.010*c*b, P/2)
    results.append(dict(material=s['name'], P_W=P, q_W_m2=q, delta_C=D,
                        beta_C_s=b, intercept_C=a, R2=r2, lambda_W_mK=lam,
                        c_J_kgK=c, lambda_if_initial_is_zero_bias=q*.010/(2*(D-vd[0]/.040))))
    fig, ax = plt.subplots(figsize=(9,4.9),layout='constrained')
    ax2 = ax.twinx()
    l1=ax.plot(tc,theta,'o-',color='#166aa3',label='中心面相对冷端温度 θ')[0]
    l2=ax2.plot(td,delta,'s-',color='#c85229',label='加热面—中心面温差 ΔT')[0]
    l3=ax.plot(tc[-5:],fit,'--',color='#173d62',lw=2,label='中心面后五点线性拟合')[0]
    ax2.hlines(D,330,600,colors='#c85229',linestyles=':',lw=2)
    ax.axvspan(330,600,color='#959595',alpha=.10)
    ax.set(xlabel='时间 t / s',ylabel='θ = T − Tref / ℃',xlim=(-10,620),xticks=np.arange(0,601,60))
    ax2.set_ylabel('ΔT / ℃',color='#c85229');ax.tick_params(axis='y',labelcolor='#166aa3')
    ax2.tick_params(axis='y',labelcolor='#c85229');ax.grid(alpha=.2)
    ax.set_title(s['name']+'：中心面温度与温差随时间变化',pad=13)
    ax.legend(handles=[l1,l2,l3],loc='lower right',fontsize=9)
    fig.savefig(OUT/(s['stem']+'_双Y轴曲线.png'),dpi=220)
    fig.savefig(OUT/(s['stem']+'_双Y轴曲线.pdf'))
    plt.close(fig)
    rows = []
    for i in range(11):
        rows.append(f'{td[i]} & {vd[i]:.3f} & {delta[i]:.3f} & {tc[i]} & {vc[i]:.3f} & {theta[i]:.3f} '+r'\\')
    tables.append('\n'.join(rows))

(OUT/'计算结果.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
tex = r'''\documentclass[UTF8,a4paper,11pt]{ctexart}
\usepackage[margin=2.15cm]{geometry}
\usepackage{amsmath,amssymb,booktabs,array,graphicx,float,xcolor,hyperref,fancyhdr}
\hypersetup{colorlinks=true,urlcolor=blue,linkcolor=black}
\setlength{\parindent}{2em}
\setlength{\parskip}{4pt}
\setlength{\headheight}{14pt}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{大学物理实验：准稳态法}\fancyhead[R]{数据处理与问题解答}\fancyfoot[C]{\thepage}
\newcommand{\unit}[1]{\,\mathrm{#1}}
\begin{document}
\begin{center}
{\LARGE\bfseries 用准稳态法测定不良导体的\\[5pt]比热容和导热系数}\\[12pt]
{\large 实验报告：原始数据、曲线、计算与问题解答}
\end{center}
\noindent 姓名：\underline{\hspace{2.6cm}}\quad 学号：\underline{\hspace{3.0cm}}\quad 日期：\underline{\hspace{2.3cm}}

\section{实验目的与结果概述}
了解一维非稳态导热模型及准稳态法测量原理；掌握热电偶测温、测温差方法；根据温差平台和中心面升温速率计算导热系数与比热容。

\textbf{结果判断：}橡胶约从 $210\unit{s}$ 起出现温差平台，后段中心面近似线性升温，满足本组数据可检验的准稳态特征。有机玻璃到 $570\unit{s}$ 温差仍明显增长，尚未形成稳定平台。其后段代入值作为估算，不能与橡胶的准稳态测定结果等同。

\begin{center}
\begin{tabular}{lccc}
\toprule 材料 & $\lambda/[\mathrm{W/(m\cdot K)}]$ & $c/[\mathrm{J/(kg\cdot K)}]$ & 结果性质\\
\midrule 有机玻璃 & 0.127 & $2.78\times10^3$ & 后段估算\\
橡胶 & 0.303 & $1.40\times10^3$ & 准稳态模型计算\\\bottomrule
\end{tabular}
\end{center}
以上采用原始温差读数，不作未经标定的初始零偏扣除；采用单块样品厚度 $h=10\unit{mm}$、加热器电功率向两侧等分的模型。

\section{已知参数与读数说明}
\begin{center}
\begin{tabular}{lcc}\toprule 参数 & 有机玻璃 & 橡胶\\\midrule
加热电压 $U$ & $20.0\unit{V}$ & $20.0\unit{V}$\\
电阻 $R$ & $140.6\unit{\Omega}$ & $140.17\unit{\Omega}$\\
加热面尺寸 & $100\times100\unit{mm^2}$ & $95\times95\unit{mm^2}$\\
加热面积 $S$ & $0.010000\unit{m^2}$ & $0.009025\unit{m^2}$\\
密度 $\rho$ & $1171\unit{kg/m^3}$ & $1401\unit{kg/m^3}$\\
厚度 $h$ & $0.010\unit{m}$ & $0.010\unit{m}$\\
热电偶系数 $K$ & \multicolumn{2}{c}{$40\unit{\mu V/{}^\circ C}=0.040\unit{mV/{}^\circ C}$}\\\bottomrule
\end{tabular}
\end{center}
数据来自用户提供的原始记录照片和实验讲义照片。原始表上半部为两种材料的温差电偶读数，下半部为中心面电偶读数，两部分采样时刻不同，按各自时间列处理。

\textbf{转录标记：}有机玻璃温差 $30\unit{s}$ 处涂改后暂读为 $0.091\unit{mV}$，$210\unit{s}$ 处暂读为 $0.173\unit{mV}$；橡胶中心面 $240\unit{s}$ 处暂读为 $0.049\unit{mV}$。这三点均不进入后五点计算窗口，故不影响本报告所列数值结果。橡胶中心面初始读数按照片记为 $-0.020\unit{mV}$，保留符号；有机玻璃初始读数按 $0.027\unit{mV}$ 转录。

照片未给出冷端绝对温度 $T_{\mathrm{ref}}$。本报告列出中心面相对冷端温度 $\theta=T-T_{\mathrm{ref}}$，不虚设室温；若补入冷端温度，绝对温度为 $T=T_{\mathrm{ref}}+\theta$。冷端恒温时，$d\theta/dt=dT/dt$，故不妨碍升温速率计算。

\section{实验原理与计算公式}
\subsection{导热模型及数据处理流程}
以样品中心面为 $x=0$，加热面为 $x=h$。同种材料对称装配、均匀薄膜加热，并通过外侧样品和保温结构减小散热，近似实现无限大平板沿厚度方向的一维导热。单个加热膜电阻记为 $R$；对称条件下，其电功率有一半流入所研究的一侧：
\[
P=\frac{U^2}{R},\qquad q=\frac{P}{2S}=\frac{U^2}{2RS}.
\]
这里 $q$ 是进入该侧试样的热流密度，单位 $\mathrm{W/m^2}$；$h$ 为中心面到加热面的距离，即本模型中的单块厚度。此处 $R$ 专指电阻，不作几何厚度符号。

实验输入为电压、电阻、面积、厚度、密度以及两类电偶读数。由电参数算 $P$、$q$；由电偶读数算 $\Delta T$ 和 $\theta$；联合判断温差平台与线性升温区间；对温差取平均、对中心面温度作最小二乘拟合；最后代入下列公式求 $\lambda$ 和 $c$。

设材料均匀、物性在本次温升范围内近似不变、侧向散热可忽略，则
\[
\rho c\frac{\partial T}{\partial t}=\lambda\frac{\partial^2T}{\partial x^2},
\quad a=\frac{\lambda}{\rho c},\quad
\left.\frac{\partial T}{\partial x}\right|_{x=0}=0,\quad
\left.\lambda\frac{\partial T}{\partial x}\right|_{x=h}=q.
\]
其中 $T(x,t)$ 为温度，$t$ 为加热时间，$\lambda$ 为导热系数，$c$ 为质量比热容，$\rho$ 为密度，$a$ 为热扩散率。初始条件为样品各处温度近似一致。

进入准稳态后，各点以同一速率 $\beta$ 升温。对半厚度试样作能量平衡，$qS=\rho Shc\beta$；同时温度曲率恒定，积分并利用中心面对称条件，得到
\[
\beta=\frac{q}{\rho ch},\qquad
T(x,t)-T(0,t)=\frac{q}{2\lambda h}x^2.
\]
因此加热面与中心面温差为 $\Delta T=qh/(2\lambda)$，最终计算式为
\[
\boxed{\lambda=\frac{qh}{2\overline{\Delta T}}=\frac{U^2h}{4RS\overline{\Delta T}}},\qquad
\boxed{c=\frac{q}{\rho h\beta}=\frac{U^2}{2RS\rho h\beta}}.
\]
公式中的两个因子 $2$ 分别来自加热膜两侧功率分配及准稳态抛物线温度场，不能直接套用稳态线性温度梯度公式。

\subsection{热电偶换算与拟合}
同一冷端下，两只电偶分别输出 $V_h=K(T_h-T_{\mathrm{ref}})$ 和 $V_c=K(T_c-T_{\mathrm{ref}})$，反向串联或差接得
\[
V_d=V_h-V_c=K(T_h-T_c),\qquad
\Delta T=\frac{V_d}{K}=25V_d,\qquad \theta=\frac{V_c}{K}=25V_c.
\]
上式中电压用 $\mathrm{mV}$，温度差用摄氏度。对选定区间拟合 $\theta=A+\beta t$，其中
\[
\beta=\frac{\sum_i(t_i-\bar t)(\theta_i-\bar\theta)}{\sum_i(t_i-\bar t)^2}.
\]
\noindent 例如橡胶 $330\unit{s}$ 的 $V_d=0.105\unit{mV}$，换算 $\Delta T=2.625\,{}^\circ\mathrm C$；橡胶 $360\unit{s}$ 中心面 $V_c=0.094\unit{mV}$，换算 $\theta=2.350\,{}^\circ\mathrm C$。

\clearpage
\section{原始读数与换算数据}
每张表左侧为温差测量，右侧为中心面测量；同一行两侧并非同一时刻。
\subsection{有机玻璃}
\begin{center}\small
\begin{tabular}{rrrrrr}\toprule
$t_d$/s & $V_d$/mV & $\Delta T$/℃ & $t_c$/s & $V_c$/mV & $\theta$/℃\\\midrule
@@TABLE0@@
\bottomrule\end{tabular}\end{center}
\subsection{橡胶}
\begin{center}\small
\begin{tabular}{rrrrrr}\toprule
$t_d$/s & $V_d$/mV & $\Delta T$/℃ & $t_c$/s & $V_c$/mV & $\theta$/℃\\\midrule
@@TABLE1@@
\bottomrule\end{tabular}\end{center}
\noindent 注：$\theta$ 是相对冷端温度，负数表示热端温度低于冷端，或读数含零偏；仅凭初始一个读数不能区分原因。涂改读数的转录说明见前文。

\clearpage
\section{双 Y 轴图像与准稳态判定}
\begin{figure}[H]\centering
\includegraphics[width=0.88\linewidth]{有机玻璃_双Y轴曲线.pdf}
\caption{有机玻璃：左轴为中心面相对冷端温度，右轴为加热面与中心面温差。灰区标出用于后段分析的范围。}
\end{figure}
\textbf{有机玻璃：未观察到稳定温差平台。}后五个温差点对应 $330$--$570\unit{s}$，从 $5.175$ 增至 $6.025\,{}^\circ\mathrm C$，增加 $0.850\,{}^\circ\mathrm C$，约为该段平均值的 $15.2\%$。中心面 $360$--$600\unit{s}$ 虽有较好的线性关系，但线性升温和恒定温差必须同时满足，故不能据此单独认定准稳态。

\begin{figure}[H]\centering
\includegraphics[width=0.88\linewidth]{橡胶_双Y轴曲线.pdf}
\caption{橡胶：后段温差近似恒定，中心面近似匀速升温。水平点线为后五个温差点的平均值。}
\end{figure}
\textbf{橡胶：约从 $210\unit{s}$ 起出现准稳态特征。}温差电势在 $0.104$--$0.105\unit{mV}$ 间波动，对应 $2.600$--$2.625\,{}^\circ\mathrm C$。末段中心面温度近似线性增长。计算取最后五个温差点 $330$--$570\unit{s}$，以及最后五个中心面点 $360$--$600\unit{s}$。两种测量交错采样，采用各自实际时间拟合，不强行配成同时刻。

\clearpage
\section{数据计算与结果分析}
\subsection{橡胶：准稳态计算}
\[
S=(0.095)^2=0.009025\unit{m^2},\quad
P=\frac{20.0^2}{140.17}=2.85368\unit W,\quad
q=\frac{2.85368}{2\times0.009025}=158.098\unit{W/m^2}.
\]
末五次温差电势为 $0.105,0.104,0.104,0.105,0.104\unit{mV}$：
\[
\bar V_d=0.1044\unit{mV},\qquad \overline{\Delta T}=\frac{0.1044}{0.040}=2.610\,{}^\circ\mathrm C.
\]
中心面后五点拟合结果为
\[
\theta=-0.5500+0.00808333t,\qquad R_{\mathrm{fit}}^2=0.999150,
\]
其中 $t$ 用秒，$\theta$ 用摄氏度；拟合截距是后段直线外推值，不等于实际初始温度。
\[
\beta=0.00808333\unit{K/s}=0.4850\unit{K/min}.
\]
\[
\lambda=\frac{158.098\times0.010}{2\times2.610}
=\boxed{0.303\unit{W/(m\cdot K)}};
\]
\[
c=\frac{158.098}{1401\times0.010\times0.00808333}
=\boxed{1.40\times10^3\unit{J/(kg\cdot K)}}.
\]
后五点温差极差为 $0.025\unit K$，相对均值约 $0.96\%$。拟合优度与平台范围描述数据形态，均不替代测量不确定度。

\subsection{有机玻璃：后段估算}
\[
P=\frac{20.0^2}{140.6}=2.84495\unit W,\qquad
q=\frac{2.84495}{2\times0.010000}=142.248\unit{W/m^2}.
\]
末五次温差电势为 $0.207,0.214,0.226,0.233,0.241\unit{mV}$：
\[
\bar V_d=0.2242\unit{mV},\qquad\overline{\Delta T}=5.605\,{}^\circ\mathrm C.
\]
中心面后五点拟合为
\[
\theta=0.1150+0.00437500t,\qquad R_{\mathrm{fit}}^2=0.999365,
\quad \beta=0.2625\unit{K/min}.
\]
\[
\lambda_{\mathrm{est}}=\frac{142.248\times0.010}{2\times5.605}
=\boxed{0.127\unit{W/(m\cdot K)}};
\]
\[
c_{\mathrm{est}}=\frac{142.248}{1171\times0.010\times0.00437500}
=\boxed{2.78\times10^3\unit{J/(kg\cdot K)}}.
\]
这些数值完成现有数据的代入计算，但因温差尚未稳定，不能作为已满足准稳态条件的材料常数。判断未达准稳态的依据是温差持续增长，而非与某个材料手册值比较。

\subsection{初始温差、模型条件与误差}
\textbf{初始非零温差的处理。}两组初始温差读数分别为 $0.027$ 和 $0.022\unit{mV}$，相当于 $0.675$ 和 $0.550\unit K$。它们可能来自真实初始温差、通道零偏或装配温度不均。照片缺少等温零点校准，不能把这三者直接归为仪器零偏。

如果另有等温校准证明上述读数全是恒定通道零偏，应使用 $\Delta T_{\mathrm{corr}}=(V_d-V_{d,0})/K$。作为敏感性计算：
\begin{center}
\begin{tabular}{lccc}\toprule 材料 & 校正后均值/℃ & $\lambda_{\mathrm{corr}}/[\mathrm{W/(m\cdot K)}]$ & 相对原计算值变化\\\midrule
有机玻璃 & 4.930 & 0.144 & $+13.7\%$\\
橡胶 & 2.060 & 0.384 & $+26.7\%$\\\bottomrule
\end{tabular}
\end{center}
此表是假设得到校准证据后的换算，不与前述未校正结果混用。恒定的中心面电势零偏只改截距，不改拟合斜率，因而不改变本算法的比热容；随时间漂移的零偏则会改变斜率。

\textbf{主要误差来源及方向。}若实际进入试样的有效热流为名义值的 $\eta$ 倍，则在其余条件成立时，$\lambda$ 和 $c$ 应同时乘以 $\eta$；照片未给出热损失修正系数，本报告按 $\eta=1$ 的理想模型计算。接触热阻若使测得温差高于样品内部温差，会使按该温差算出的导热系数偏小。初始温度不均与未达准稳态会影响曲线形状，需要更长时间的原始测量来判断。

\textbf{几何与电路约定。}计算将讲义中的 $h=10\unit{mm}$ 作为单块厚度，$R$ 作为单个加热膜电阻，$S$ 作为所记录的加热面积。若仪器铭牌将 $R$ 定义为两膜等效电阻，或将 $h$ 定义为两块总厚度，需要依真实电路、装配尺寸重算；现有照片未展示这部分铭牌和原理公式，报告明确保留上述模型约定。

\textbf{不确定度。}现有资料缺少电压、电势、厚度及面积的仪器精度、热电偶系数校准误差和重复测量数据，故不编造扩展不确定度或相对真值误差。若各量独立，传播关系可写为
\[
\left(\frac{u_\lambda}{\lambda}\right)^2\simeq
\left(2\frac{u_U}{U}\right)^2+\left(\frac{u_h}{h}\right)^2+
\left(\frac{u_R}{R}\right)^2+\left(\frac{u_S}{S}\right)^2+
\left(\frac{u_{\Delta T}}{\Delta T}\right)^2.
\]
比热容另需考虑密度与升温斜率误差；非准稳态模型偏差不属于单纯仪器随机误差。

\clearpage
\section{预习指导问题解答}
\subsection*{1. 本实验采用何种导热模型？装置如何实现？}
采用两侧受恒定、均匀热流加热的无限大平板一维非稳态导热模型。对称装配使中心面的温度梯度近似为零，温度主要沿厚度方向变化。装置以横向尺寸较大而厚度较小的平板近似无限大平板，使用薄膜加热器产生均匀热流，并用同种材料对称夹持和保温结构减小两侧热阻差及边缘散热。样品与传感器应压紧、接触良好，测温点置于面内中央。

\subsection*{2. 温度场微分方程中各量的物理意义是什么？}
方程为 $\partial T/\partial t=a\,\partial^2T/\partial x^2$。$T$ 是位置 $x$、时间 $t$ 处的温度；$x$ 是垂直平板方向的坐标；$t$ 是加热时间；$a=\lambda/(\rho c)$ 是热扩散率，单位为 $\mathrm{m^2/s}$。$\lambda$ 衡量导热能力，$\rho c$ 是单位体积的热容量。左侧表示局部温升速率，右侧体现温度场曲率导致的净导热；等价形式 $\rho c\,\partial T/\partial t=\lambda\,\partial^2T/\partial x^2$ 表示局部能量守恒。

\subsection*{3. 何谓准稳态？如何判断？进入后有哪些特征？}
准稳态是初始瞬态分量已足够小，各点仍随时间升温，但温度场的空间形状基本不变的状态。它与各点温度不再变化的稳态不同。

判据是：加热面与中心面的温差近似恒定；中心面温度随时间近似线性；若同时测量加热面温度，两者升温斜率应相同。进入后各点温升速率近似相同，空间温度分布近似抛物线，任意固定两点间温差近似不变。本次橡胶符合平台与线性升温的联合判据，有机玻璃只显示后段中心面近似线性，缺少稳定温差平台。

\subsection*{4. 如何利用两只热电偶测量加热面与中心面的温差？}
两只同型号热电偶的热端分别置于加热面和中心面，冷端置于同一恒温环境。两电偶反向串联或差接时，电表测得 $V_d=V_h-V_c$，共同冷端项相消，故 $\Delta T=V_d/K$。转换开关切到中心面单偶测量时，得到 $V_c=K(T_c-T_{\mathrm{ref}})$，用于求中心面温度随时间的变化。

\section{讨论题：冷端处于恒温空气中是否影响结果？}
\textbf{在讲义采用的热电势线性关系下，只要两只冷端同温且温度保持恒定，冷端放在恒温空气中不影响导热系数和比热容的计算。}理由如下。

第一，温差由 $V_h-V_c=K(T_h-T_c)$ 求得，共同冷端温度完全相消，因此 $\Delta T$ 不受冷端绝对温度影响。

第二，中心面电势满足
\[
\frac{dV_c}{dt}=K\left(\frac{dT_c}{dt}-\frac{dT_{\mathrm{ref}}}{dt}\right).
\]
冷端恒温时，$dT_{\mathrm{ref}}/dt=0$，因此 $\beta=(1/K)dV_c/dt$ 不变，比热容计算不变。中心面绝对温度仍须加回冷端温度，不能将 $V_c/K$ 直接当作绝对摄氏温度。

若冷端随时间漂移，按电势斜率直接求得的是 $\beta_{\mathrm{meas}}=\beta_{\mathrm{true}}-dT_{\mathrm{ref}}/dt$；冷端升温会使测得斜率偏小，从而使算得比热容偏大。两冷端不等温还会使温差测量引入附加项。因此关键是冷端同温、恒温，而不是必须处于 $0\,{}^\circ\mathrm C$ 冰水混合物中。

\section{实验结论}
根据现有记录，橡胶在后段达到近似准稳态，按名义电功率两侧等分模型、未扣除未经标定的初始读数，测得 $\lambda\approx0.303\unit{W/(m\cdot K)}$，$c\approx1.40\times10^3\unit{J/(kg\cdot K)}$。有机玻璃温差未稳定，后段估算为 $\lambda_{\mathrm{est}}\approx0.127\unit{W/(m\cdot K)}$、$c_{\mathrm{est}}\approx2.78\times10^3\unit{J/(kg\cdot K)}$，需要继续记录温差平台及相应的中心面温升数据，才能完成严格的准稳态测定。

\section*{资料依据}
实验参数、采样时刻、预习问题、讨论题和报告要求以用户提供的三张照片为准。导热模型及加热膜向两侧等分热流的约定，参照南昌大学物理实验中心《准稳态法测导热系数和比热》的原理及装置说明；本报告从该模型推导计算式，未引入其他仪器的电压、密度或修正系数。\\
\href{https://wlsyzx.ncu.edu.cn/docs/2023-07/151e7eb1bc0f44c6a7972251a086caaa.pdf}{南昌大学物理实验中心：准稳态法测导热系数和比热}
\end{document}
'''
for i, table in enumerate(tables):
    tex=tex.replace('@@TABLE'+str(i)+'@@',table)
(OUT/'导热实验报告.tex').write_text(tex,encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
