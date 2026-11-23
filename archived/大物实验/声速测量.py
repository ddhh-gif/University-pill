# -*- coding: utf-8 -*-
"""
实验：空气中声速的测量 —— 数据处理
方法：对"换能器位置 x ~ 记录序号 i"做一元线性最小二乘（numpy.polyfit），斜率 |b| = λ/2
  - 极值法：相邻波幅极大值间距 = λ/2（往返各 14 个位置）
  - 位相比较法：相邻正/负斜线间距 = λ/2（两组各 13 个位置）
  - 波形移动法：终止 − 起始 = 10λ（三次）
参数：信号频率 f = 39.7 kHz，室温 T = 26 ℃，相对湿度 60%
"""
import numpy as np

f = 39.7e3          # 信号频率 / Hz
T = 26.0            # 室温 / ℃


def lin_fit(pos):
    """对 pos = a + b*i 做一元线性最小二乘，返回 (截距 a, 斜率 b, R²)"""
    i = np.arange(len(pos), dtype=float)
    b, a = np.polyfit(i, pos, 1)
    pred = b * i + a
    ss_res = np.sum((pos - pred) ** 2)
    ss_tot = np.sum((pos - pos.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    return a, b, r2


def print_fit(tag, a, b, r2, lam):
    print(f"  {tag:<6} 斜率 b = {b:+.4f} mm   截距 a = {a:.3f} mm   R² = {r2:.5f}   λ = 2|b| = {lam:.4f} mm")


# ============ 极值法（去程 / 回程，各 14 个位置，单位 mm） ============
go = np.array([70.10, 65.35, 61.08, 56.85, 52.17, 47.80, 43.39, 39.00,
               35.39, 30.30, 26.77, 21.37, 17.10, 13.44])
back = np.array([69.62, 65.31, 61.01, 57.08, 52.43, 48.02, 43.76, 39.41,
                 35.23, 30.80, 26.65, 21.32, 18.19, 13.50])

a_go, b_go, r2_go = lin_fit(go)
a_back, b_back, r2_back = lin_fit(back)
lam_go = 2 * abs(b_go)
lam_back = 2 * abs(b_back)
lam1 = (lam_go + lam_back) / 2

# ============ 位相比较法（第 1 组 / 第 2 组，各 13 个位置，单位 mm） ============
g1 = np.array([13.02, 17.35, 22.69, 27.20, 30.50, 35.00, 40.50, 44.91,
               49.37, 53.81, 57.24, 62.58, 67.04])
g2 = np.array([13.03, 17.32, 21.65, 26.92, 30.11, 34.90, 40.43, 45.01,
               48.98, 53.60, 56.955, 61.00, 68.03])

a_g1, b_g1, r2_g1 = lin_fit(g1)
a_g2, b_g2, r2_g2 = lin_fit(g2)
lam_g1 = 2 * abs(b_g1)
lam_g2 = 2 * abs(b_g2)
lam2 = (lam_g1 + lam_g2) / 2

# ============ 波形移动法（终止 − 起始 = 10λ，三次） ============
start = np.array([62.50, 62.43, 62.54])
stop = np.array([151.00, 149.98, 150.12])
lam_wave = (stop - start) / 10.0
lam3 = lam_wave.mean()

print("=" * 72)
print("一、最小二乘法求波长 λ（位置 x ~ 序号 i，斜率 |b| = λ/2）")
print("=" * 72)
print("\n[1] 极值法（相邻波幅极大值间距 = λ/2）")
print_fit("去程", a_go, b_go, r2_go, lam_go)
print_fit("回程", a_back, b_back, r2_back, lam_back)
print(f"    λ1 = (λ去 + λ回)/2 = ({lam_go:.4f} + {lam_back:.4f})/2 = {lam1:.4f} mm")

print("\n[2] 位相比较法（相邻正/负斜线间距 = λ/2）")
print_fit("第1组", a_g1, b_g1, r2_g1, lam_g1)
print_fit("第2组", a_g2, b_g2, r2_g2, lam_g2)
print(f"    λ2 = (λ组1 + λ组2)/2 = ({lam_g1:.4f} + {lam_g2:.4f})/2 = {lam2:.4f} mm")

print("\n[3] 波形移动法（终止 − 起始 = 10λ）")
for k in range(3):
    print(f"    第{k+1}次  起始 {start[k]:.2f} mm  终止 {stop[k]:.2f} mm  "
          f"10λ = {stop[k]-start[k]:.2f} mm  λ = {lam_wave[k]:.4f} mm")
print(f"    λ3 = ({lam_wave[0]:.4f} + {lam_wave[1]:.4f} + {lam_wave[2]:.4f})/3 = {lam3:.4f} mm")

# ============ 声速 v = f·λ ============
lam_all = np.array([lam1, lam2, lam3])
v_all = f * lam_all * 1e-3          # λ (mm) -> m，再乘 f
v_theory = 331.45 + 0.607 * T
dev = (v_all - v_theory) / v_theory * 100.0
names = ["极值法", "位相比较法", "波形移动法"]

print()
print("=" * 72)
print("二、声速计算  v = f·λ （f = 39.7 kHz）")
print("=" * 72)
print(f"{'方法':<12}{'λ / mm':>14}{'v / (m/s)':>14}")
for name, lam, v in zip(names, lam_all, v_all):
    print(f"{name:<12}{lam:>14.4f}{v:>14.1f}")

print()
print("=" * 72)
print("三、理论值与相对偏差")
print("=" * 72)
print(f"v_theory = 331.45 + 0.607 × T = 331.45 + 0.607 × {T:.0f} = {v_theory:.1f} m/s")
print(f"{'方法':<12}{'v / (m/s)':>14}{'相对偏差':>14}")
for name, v, d in zip(names, v_all, dev):
    print(f"{name:<12}{v:>14.1f}{d:>+13.1f}%")
