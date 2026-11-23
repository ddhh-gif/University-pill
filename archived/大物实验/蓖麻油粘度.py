"""
蓖麻油粘度-温度实验数据处理
公式: η = (1/18) × (ρ - ρ₀) × g × t × d² / [L × (1 + 2.4d/D)]
"""

import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. 常数与仪器参数（确认/修改）
# ============================================================
rho      = 7.700e3      # 钢球密度 kg/m³
rho_0    = 0.9741e3     # 蓖麻油密度 kg/m³
g        = 9.8066       # 重力加速度 m/s²

L        =    0.20           # 两标线间距 (m)，例: 0.100
D        =    0.082          # 量筒直径 (m)，例: 0.040

# 仪器误差
delta_t  = 0.2          # 计时器不确定度 (s)
delta_L  = 0.5e-3       # 标线间距误差 (m)
delta_D  = 1.0e-3       # 量筒直径误差 (m)
delta_d  = 0.007e-3     # 显微镜误差 (m)

# ============================================================
# 2. 直径测量数据（mm）
#    格式：每行 [读数1, 读数2]，直径 = |读数2 - 读数1|
# ============================================================

# 钢球1号
ball_1_readings = [
    [29.471,30.655],    # 第1次
    [29.495,30.672],    # 第2次
    [28.521,27.332 ],    # 第3次
    [27.679,28.871 ],    # 第4次
    [27.761,29.002 ],    # 第5次
]

# 钢球2号
ball_2_readings = [
    [27.431,28.600 ],
    [29.021,30.187 ],
    [30.591,29.439 ],
    [29.721,30.871 ],
    [29.012,30.211 ],
]

# 钢球3号
ball_3_readings = [
    [25.721,26.910 ],
    [25.710,26.920 ],
    [27.348,26.131 ],
    [28.046,29.235 ],
    [29.248, 28.051],
]

# 钢球4号
ball_4_readings = [
    [27.160,25.965 ],
    [27.785,26.595 ],
    [27.765,26.573 ],
    [27.766,26.575 ],
    [27.300,26.065 ],
]

# 钢球5号
ball_5_readings = [
    [29.929,31.120 ],
    [29.941,31.110 ],
    [31.220,30.000 ],
    [32.255,31.131 ],
    [31.060, 29.851],
]

# ============================================================
# 3. 实验数据：温度、钢球号、下落时间
# ============================================================
experiments = [
    # (温度°C, 钢球号, 下落时间s)
    (25, 1, 26.67),
    (35, 2, 13.96),
    (30, 3, 18.29),
    (40, 4, 10.04),
    (20, 5, 33.75),
]

# ============================================================
# 4. 计算各钢球平均直径
# ============================================================
def calc_diameter(readings):
    """从两边读数计算直径，返回平均值和标准差(单位:m)"""
    diameters_mm = [abs(r[1] - r[0]) for r in readings]
    d_mean_mm = np.mean(diameters_mm)
    d_std_mm  = np.std(diameters_mm, ddof=1)
    return d_mean_mm * 1e-3, d_std_mm * 1e-3, diameters_mm

ball_diameters = {}
all_readings   = {1: ball_1_readings, 2: ball_2_readings, 3: ball_3_readings,
                  4: ball_4_readings, 5: ball_5_readings}

print("="*60)
print("各钢球直径测量结果")
print("="*60)
for ball_id, readings in all_readings.items():
    d_mean, d_std, d_list = calc_diameter(readings)
    ball_diameters[ball_id] = d_mean
    print(f"钢球{ball_id}号：")
    print(f"  各次直径(mm): {[f'{d:.4f}' for d in d_list]}")
    print(f"  平均直径 d = {d_mean*1000:.4f} mm")
    print(f"  标准差     = {d_std*1000:.4f} mm")
    print()

# ============================================================
# 5. 粘度计算
# ============================================================
def calc_viscosity(t, d):
    """斯托克斯法粘度公式"""
    numerator   = (rho - rho_0) * g * t * d**2
    denominator = 18 * L * (1 + 2.4 * d / D)
    return numerator / denominator

def calc_uncertainty(eta, t, d):
    """计算合成不确定度"""
    rel_t = delta_t / t
    rel_d = 2 * delta_d / d           # d²项系数为2
    rel_L = delta_L / L
    rel_D = (2.4 * d / D) / (1 + 2.4 * d / D) * (delta_D / D)
    rel_total = np.sqrt(rel_t**2 + rel_d**2 + rel_L**2 + rel_D**2)
    return eta * rel_total, rel_total

# ============================================================
# 6. 计算每个实验点的粘度
# ============================================================
print("="*60)
print("各温度下粘度计算结果")
print("="*60)

T_list, eta_list, err_list = [], [], []
for T, ball_id, t in experiments:
    d   = ball_diameters[ball_id]
    eta = calc_viscosity(t, d)
    u, rel_u = calc_uncertainty(eta, t, d)
    T_list.append(T)
    eta_list.append(eta)
    err_list.append(u)
    print(f"T={T}°C  球{ball_id}号  t={t}s  d={d*1000:.4f}mm")
    print(f"  η = {eta:.4f} ± {u:.4f} Pa·s  (相对不确定度 {rel_u*100:.2f}%)")
    print()

# ============================================================
# 7. 绘图：粘度-温度曲线（按温度升序排列）
# ============================================================
order = np.argsort(T_list)
T_sorted   = np.array(T_list)[order]
eta_sorted = np.array(eta_list)[order]
err_sorted = np.array(err_list)[order]

fig, ax = plt.subplots(figsize=(10, 6))
ax.errorbar(T_sorted, eta_sorted, yerr=err_sorted,
            fmt='o-', markersize=10, linewidth=2.2, capsize=6, capthick=2,
            color='#FF6B6B', elinewidth=2, markeredgewidth=1.8,
            markeredgecolor='#CC4444')

ax.set_xlabel('Temperature T (°C)', fontsize=13, fontweight='bold')
ax.set_ylabel('Viscosity η (Pa·s)', fontsize=13, fontweight='bold')
ax.set_title('Castor Oil: Viscosity vs Temperature', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('viscosity_T_curve.png', dpi=300, bbox_inches='tight')
plt.show()
print("✓ 曲线已保存为 viscosity_T_curve.png")
