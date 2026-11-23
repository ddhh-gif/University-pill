"""
杨氏弹性模量测定实验 - 光杠杆法
公式: E = 8·m·g·L_丝·L / (π·d²·b·Δn)
作图法: 线性拟合 n-m 关系得斜率 k, E = 8·g·L_丝·L / (π·d²·b·|k|)

不确定度分类:
  A类: 多次测量统计 (标准差/√n, 拟合标准误差)
  B类: 仪器误差 (假设均匀分布, u_B = Δ_仪/√3)
"""

import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. 实验参数
# ============================================================
g          = 9.8066       # 重力加速度 m/s²

b          = 7.11e-2      # 光杠杆臂长 (m)
L_mirror   = 1.330        # 平面镜-标尺距离 (m)
L_wire     = 0.6681       # 金属丝长度 (m)

# 仪器误差 (来自说明书)
delta_b    = 0.5e-3       # Δb = 0.5 mm
delta_L    = 10e-3        # ΔL = 10 mm
delta_l    = 5e-3         # Δl = 5 mm
delta_d    = 0.004e-3     # Δd = 0.004 mm

# ============================================================
# 2. 金属丝直径测量 (mm)
# ============================================================
d_zero     = -0.003                                   # 螺旋测微器零位
d_readings = [0.481, 0.483, 0.484, 0.477, 0.482,0.480]      # 5次读数 (mm)

d_corr     = np.array(d_readings) - d_zero            # 零位修正
d_mean     = np.mean(d_corr) * 1e-3                   # 平均直径 (m)
d_std      = np.std(d_corr, ddof=1) * 1e-3            # 标准差 (m)

print("="*65)
print("【1】金属丝直径测量")
print("="*65)
print(f"零位修正后 (mm) : {[f'{x:.4f}' for x in d_corr]}")
print(f"平均   d = {d_mean*1000:.4f} mm")
print(f"标准差 s = {d_std*1000:.4f} mm")
print()

# ============================================================
# 3. 加减重标尺读数 (cm)
# ============================================================
data = [
    # m(kg), n_加重(cm), n_减重(cm)
    (0.0,   2.78,        2.78),
    (1.0,   2.10,        2.08),
    (2.0,   1.35,        1.39),
    (3.0,   0.69,        0.60),
    (4.0,  -0.10,       -0.04),
    (5.0,  -0.70,       -0.71),
    (6.0,  -1.40,       -1.40),
]

m_arr     = np.array([row[0] for row in data])
n_up_cm   = np.array([row[1] for row in data])
n_down_cm = np.array([row[2] for row in data])
n_mean_cm = (n_up_cm + n_down_cm) / 2
n_mean_m  = n_mean_cm * 1e-2

print("="*65)
print("【2】标尺读数")
print("="*65)
print(f"{'m(kg)':>6} {'n加(cm)':>10} {'n减(cm)':>10} {'平均(cm)':>10}")
for i in range(len(m_arr)):
    print(f"{m_arr[i]:>6.1f} {n_up_cm[i]:>10.3f} {n_down_cm[i]:>10.3f} {n_mean_cm[i]:>10.3f}")
print()

# ============================================================
# 4. 线性拟合
# ============================================================
coeffs    = np.polyfit(m_arr, n_mean_m, 1)
k_fit     = coeffs[0]
n0_fit    = coeffs[1]
abs_k     = abs(k_fit)

# 拟合标准差
n_pred    = k_fit*m_arr + n0_fit
ss_res    = np.sum((n_mean_m - n_pred)**2)
ss_tot    = np.sum((n_mean_m - np.mean(n_mean_m))**2)
R2        = 1 - ss_res/ss_tot
n_pts     = len(m_arr)
sigma_y   = np.sqrt(ss_res/(n_pts-2))
sigma_k   = sigma_y / np.sqrt(np.sum((m_arr - np.mean(m_arr))**2))   # 斜率标准误差

print("="*65)
print("【3】线性拟合 n = k·m + n₀")
print("="*65)
print(f"斜率  k  = {k_fit*1000:.4f} mm/kg   (|k| = {abs_k*1000:.4f} mm/kg)")
print(f"截距  n₀ = {n0_fit*100:.4f} cm")
print(f"σ_k     = {sigma_k*1000:.4f} mm/kg")
print(f"R²      = {R2:.6f}")
print()

# ============================================================
# 5. 计算杨氏模量
# ============================================================
E = (8 * g * L_wire * L_mirror) / (np.pi * d_mean**2 * b * abs_k)

print("="*65)
print("【4】杨氏模量")
print("="*65)
print(f"E = 8·g·L_丝·L / (π·d²·b·|k|)  = {E:.4e} Pa = {E/1e9:.3f} GPa")
print()

# ============================================================
# 6. 不确定度分析 (A 类 + B 类)
# ============================================================
# ---- A类不确定度 ----
u_A_d = (d_std) / np.sqrt(len(d_corr))     # 直径 A类 (m): s/√n
u_A_k = sigma_k                            # 斜率 A类 (m/kg)

# ---- B类不确定度 (均匀分布 → Δ/√3) ----
u_B_d        = delta_d        / np.sqrt(3)
u_B_L_wire   = delta_l        / np.sqrt(3)
u_B_L_mirror = delta_L        / np.sqrt(3)
u_B_b        = delta_b        / np.sqrt(3)

# ---- 合成各量的不确定度 ----
u_d = np.sqrt(u_A_d**2 + u_B_d**2)         # d 的总不确定度
u_k = u_A_k                                # k 只有A类
u_Lw = u_B_L_wire                          # L_丝只测一次,只B类
u_Lm = u_B_L_mirror
u_b  = u_B_b

print("="*65)
print("【5】不确定度分析 (分 A 类 / B 类)")
print("="*65)
print(f"{'量':<10}{'A类 u_A':<18}{'B类 u_B':<18}{'合成 u':<15}")
print("-"*65)
print(f"{'d':<10}{u_A_d*1000:<10.5f} mm    {u_B_d*1000:<10.5f} mm    {u_d*1000:.5f} mm")
print(f"{'k':<10}{u_A_k*1000:<10.5f} mm/kg {'  —':<14}{u_k*1000:.5f} mm/kg")
print(f"{'L_丝':<10}{'  —':<14}{u_B_L_wire*1000:<10.4f} mm    {u_Lw*1000:.4f} mm")
print(f"{'L':<10}{'  —':<14}{u_B_L_mirror*1000:<10.4f} mm    {u_Lm*1000:.4f} mm")
print(f"{'b':<10}{'  —':<14}{u_B_b*1000:<10.4f} mm    {u_b*1000:.4f} mm")
print()

# ---- E 的相对不确定度合成 ----
# (ΔE/E)² = (ΔL_丝/L_丝)² + (ΔL/L)² + (Δb/b)² + (2Δd/d)² + (Δk/k)²

# 分A类、B类两部分计算E的相对不确定度
rel_A_d = 2 * u_A_d / d_mean
rel_A_k = u_A_k / abs_k
rel_A_E = np.sqrt(rel_A_d**2 + rel_A_k**2)

rel_B_d  = 2 * u_B_d / d_mean
rel_B_Lw = u_B_L_wire / L_wire
rel_B_Lm = u_B_L_mirror / L_mirror
rel_B_b  = u_B_b / b
rel_B_E  = np.sqrt(rel_B_d**2 + rel_B_Lw**2 + rel_B_Lm**2 + rel_B_b**2)

# 总相对不确定度
rel_E   = np.sqrt(rel_A_E**2 + rel_B_E**2)
u_E     = E * rel_E

print("="*65)
print("【6】E 的相对不确定度合成 (按 A、B 类列出贡献)")
print("="*65)
print("A类贡献:")
print(f"  2·u_A(d)/d     = {rel_A_d*100:7.4f} %")
print(f"  u_A(k)/|k|     = {rel_A_k*100:7.4f} %")
print(f"  → 小计 u_A(E)/E = {rel_A_E*100:7.4f} %")
print()
print("B类贡献:")
print(f"  u_B(L_丝)/L_丝 = {rel_B_Lw*100:7.4f} %")
print(f"  u_B(L)/L       = {rel_B_Lm*100:7.4f} %")
print(f"  2·u_B(d)/d     = {rel_B_d*100:7.4f} %")
print(f"  u_B(b)/b       = {rel_B_b*100:7.4f} %")
print(f"  → 小计 u_B(E)/E = {rel_B_E*100:7.4f} %")
print()
print(f"合成: u(E)/E = √[(u_A/E)² + (u_B/E)²] = {rel_E*100:.4f} %")
print(f"u(E) = E × {rel_E*100:.4f}% = {u_E:.3e} Pa = {u_E/1e9:.3f} GPa")
print()

# ============================================================
# 7. 最终结果
# ============================================================
print("="*65)
print("【7】最终结果")
print("="*65)
print(f"  E = ({E/1e9:.2f} ± {u_E/1e9:.2f}) GPa")
print(f"  E = ({E:.3e} ± {u_E:.2e}) Pa")
print(f"  相对不确定度 u_r(E) = {rel_E*100:.2f}%")
print("="*65)

# ============================================================
# 8. 拟合图
# ============================================================
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(m_arr, n_mean_cm, 'o', markersize=11, color='#FF6B6B',
        markeredgewidth=2, markeredgecolor='#CC4444', label='Experimental data')
m_smooth = np.linspace(m_arr.min()-0.3, m_arr.max()+0.3, 100)
n_smooth = (k_fit*m_smooth + n0_fit) * 100
ax.plot(m_smooth, n_smooth, '--', linewidth=2.5, color='#4ECDC4',
        label=f'Linear fit:  n = {k_fit*100:.4f}·m + {n0_fit*100:.4f}\nR² = {R2:.5f}')
ax.set_xlabel('Mass m (kg)', fontsize=13, fontweight='bold')
ax.set_ylabel('Scale reading n (cm)', fontsize=13, fontweight='bold')
ax.set_title("Young's Modulus: Scale Reading vs Mass", fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(fontsize=11, loc='upper right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('young_modulus_fit.png', dpi=300, bbox_inches='tight')
plt.show()
print("\n✓ 拟合图已保存")