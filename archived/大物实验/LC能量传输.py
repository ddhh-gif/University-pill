"""
LC谐振 / 无线能量传输实验数据绘图
- 表1: 频率扫描 (谐振曲线)
- 表2: 线圈距离扫描 (衰减曲线)
直接用三次样条平滑数据点，不做物理模型拟合。
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# ----- 字体配置 -----
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'SimHei',
                                    'Hiragino Sans GB', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'cm'

# ============================================================
# 表1: 频率 vs Vpp
# ============================================================
freq_MHz = np.array([
    2.09, 2.10, 2.11, 2.12,
    2.122, 2.124, 2.126, 2.127, 2.129,
    2.13, 2.132, 2.133,
    2.14, 2.15, 2.16, 2.17,
])
vpp_freq = np.array([
    4.08,  5.44,  7.75, 11.80,
    12.6, 13.3, 14.3, 14.6, 14.3,
    15.0, 14.4, 14.8,
    13.80, 9.60,  5.50,  5.20,
])
order = np.argsort(freq_MHz)
freq_MHz, vpp_freq = freq_MHz[order], vpp_freq[order]

# ============================================================
# 表2: 距离 vs Vpp
# ============================================================
dist_cm = np.array([
    12.0, 12.5, 13.0, 13.5, 14.0, 14.5,
    15.0, 15.5, 16.0, 16.5, 17.0,
    17.5, 18.0, 18.5, 19.0,
])
vpp_dist = np.array([
    14.0, 13.7, 13.8, 13.1, 12.3, 11.5,
    10.5, 9.36, 8.32, 7.20, 6.40,
    5.52, 4.73, 4.20, 3.60,
])

# ============================================================
# 平滑曲线 (三次样条插值)
# ============================================================
f_smooth = np.linspace(freq_MHz.min(), freq_MHz.max(), 400)
v_freq_smooth = make_interp_spline(freq_MHz, vpp_freq, k=3)(f_smooth)

d_smooth = np.linspace(dist_cm.min(), dist_cm.max(), 400)
v_dist_smooth = make_interp_spline(dist_cm, vpp_dist, k=3)(d_smooth)

# ============================================================
# 绘图
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# --- 左: 谐振曲线 ---
ax1.plot(f_smooth, v_freq_smooth, '-', color='#1f77b4', lw=1.6, alpha=0.85)
ax1.plot(freq_MHz, vpp_freq, 'o', color='#1f77b4', ms=7,
         markerfacecolor='white', markeredgewidth=1.5, zorder=3)
ax1.set_xlabel('Frequency  $f$ / MHz', fontsize=12)
ax1.set_ylabel(r'Amplitude  $V_{\mathrm{pp}}$ / V', fontsize=12)
ax1.set_title('Resonance curve  ($V_{pp}$ vs $f$)', fontsize=13)
ax1.grid(True, alpha=0.3)

# --- 右: 距离衰减 ---
ax2.plot(d_smooth, v_dist_smooth, '-', color='#d62728', lw=1.6, alpha=0.85)
ax2.plot(dist_cm, vpp_dist, 's', color='#d62728', ms=7,
         markerfacecolor='white', markeredgewidth=1.5, zorder=3)
ax2.set_xlabel('Coil separation  $d$ / cm', fontsize=12)
ax2.set_ylabel(r'Amplitude  $V_{\mathrm{pp}}$ / V', fontsize=12)
ax2.set_title('Distance decay  ($V_{pp}$ vs $d$)', fontsize=13)
ax2.grid(True, alpha=0.3)

fig.suptitle(r'$L = 1.21\,\mu\mathrm{H},\ C = 9.7\,\mathrm{nF},\ '
             r'l_{\max} = 17.2\,\mathrm{cm},\ d_{\mathrm{coil}} = 9.4\,\mathrm{cm}$',
             fontsize=11, y=1.02)

plt.tight_layout()
plt.savefig('experiment_curves.png', dpi=200, bbox_inches='tight')
plt.show()