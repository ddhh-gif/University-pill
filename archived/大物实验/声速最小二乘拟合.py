# -*- coding: utf-8 -*-
"""空气中声速测量 —— 最小二乘拟合插图

对"换能器位置 x(mm) ~ 记录序号 i"做一元线性最小二乘 x = a + b·i，
斜率 |b| = λ/2。四个子图分别对应：
极值法去程 / 极值法回程 / 位相法第1组 / 位相法第2组。
拟合结果(斜率 b、截距 a、R²、波长 λ)已用 numpy.polyfit 求得，本脚本仅负责绘图。
"""

import matplotlib

matplotlib.use("Agg")  # 无显示环境下后台渲染

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# ----------------------------------------------------------------------------
# 1. 中文字体检测：从偏好列表中选第一个 matplotlib 实际注册的字体
# ----------------------------------------------------------------------------
CANDIDATES = [
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
    "WenQuanYi Micro Hei",
    "AR PL UMing CN",
    "Source Han Sans SC",
    "PingFang SC",
]

registered = {f.name for f in fm.fontManager.ttflist}
FONT_CN = next((c for c in CANDIDATES if c in registered), None)

if FONT_CN is not None:
    plt.rcParams["font.sans-serif"] = [FONT_CN]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    USE_CN = True
else:
    USE_CN = False

# 深灰 ink 色，坐标轴/刻度/文字不喧宾夺主
INK = "#333333"
plt.rcParams["text.color"] = INK
plt.rcParams["axes.labelcolor"] = INK
plt.rcParams["xtick.color"] = INK
plt.rcParams["ytick.color"] = INK
plt.rcParams["axes.edgecolor"] = INK

ACCENT = "#1f77b4"  # 拟合直线强调色
POINT = "#333333"   # 数据点深灰
GRID = "#dddddd"    # 浅灰背景网格

# ----------------------------------------------------------------------------
# 2. 数据与拟合结果
# ----------------------------------------------------------------------------
# 每组: (title, x_data, b, a, R2, lam)
subplots = [
    (
        "极值法 去程",
        [70.10, 65.35, 61.08, 56.85, 52.17, 47.80, 43.39, 39.00,
         35.39, 30.30, 26.77, 21.37, 17.10, 13.44],
        -4.3654, 69.811, 0.99968, 8.7308,
    ),
    (
        "极值法 回程",
        [69.62, 65.31, 61.01, 57.08, 52.43, 48.02, 43.76, 39.41,
         35.23, 30.80, 26.65, 21.32, 18.19, 13.50],
        -4.3274, 69.723, 0.99977, 8.6548,
    ),
    (
        "位相法 第1组",
        [13.02, 17.35, 22.69, 27.20, 30.50, 35.00, 40.50, 44.91,
         49.37, 53.81, 57.24, 62.58, 67.04],
        +4.4832, 13.194, 0.99930, 8.9665,
    ),
    (
        "位相法 第2组",
        [13.03, 17.32, 21.65, 26.92, 30.11, 34.90, 40.43, 45.01,
         48.98, 53.60, 56.955, 61.00, 68.03],
        +4.4918, 12.890, 0.99837, 8.9836,
    ),
]

# ----------------------------------------------------------------------------
# 3. 绘图
# ----------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

XLABEL = "记录序号 i" if USE_CN else "Index i"
YLABEL = "换能器位置 x / mm" if USE_CN else "Transducer position x / mm"
SUPTITLE = "声速测量最小二乘拟合" if USE_CN else "Least-Squares Fit for Sound Speed"

for ax, (title, x_data, b, a, r2, lam) in zip(axes.ravel(), subplots):
    n = len(x_data)
    i = np.arange(n)
    x = np.array(x_data)

    # 拟合直线（覆盖略超出数据点范围）
    i_line = np.array([-0.6, n - 0.4])
    x_line = a + b * i_line

    ax.plot(i_line, x_line, color=ACCENT, linewidth=1.5, zorder=2)
    ax.scatter(i, x, s=22, marker="o", color=POINT, edgecolors="none", zorder=3)

    ax.set_xlim(-0.7, n - 0.3)
    ax.set_xlabel(XLABEL)
    ax.set_ylabel(YLABEL)
    ax.set_title(title, fontsize=11, color=INK)

    ax.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

    # 在子图空白处直接标注拟合结果（不用图例）
    b_text = f"斜率 b = {b:+.4f} mm"
    lam_text = f"λ = {lam:.4f} mm"
    r2_text = f"R² = {r2:.5f}"
    annot = "\n".join([b_text, lam_text, r2_text])

    if b < 0:  # 负斜率：数据占据左上-右下，右上角留空
        ax.text(0.58, 0.94, annot, transform=ax.transAxes,
                ha="left", va="top", fontsize=9, color=INK,
                linespacing=1.6)
    else:      # 正斜率：数据占据左下-右上，左上角留空
        ax.text(0.03, 0.94, annot, transform=ax.transAxes,
                ha="left", va="top", fontsize=9, color=INK,
                linespacing=1.6)

fig.suptitle(SUPTITLE, fontsize=14, color=INK, y=0.97)
fig.tight_layout(rect=[0, 0, 1, 0.95])

OUT_PNG = "/home/zihan/Desktop/大物/大物实验/声速最小二乘拟合.png"
fig.savefig(OUT_PNG, dpi=300)
print("saved:", OUT_PNG)
print("chinese_font:", FONT_CN)
print("use_cn:", USE_CN)
