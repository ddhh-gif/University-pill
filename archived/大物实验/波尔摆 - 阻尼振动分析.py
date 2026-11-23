"""
波尔摆 - 阻尼振动分析
数据修改在最上面的"数据区"，下面的代码自动算 lnθ、做线性拟合、出图
拟合模型: ln θ = ln θ0 − β·t   →   斜率 = −β
"""
import numpy as np
import matplotlib.pyplot as plt

# 中文字体（不同平台都试一下，避免方块）
plt.rcParams['font.sans-serif'] = [
    'Noto Sans CJK JP', 'Noto Sans CJK SC',
    'Hiragino Sans GB', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS'
]
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 数据区  ←  改这里就行
# ============================================================

# 自由振动周期 T0 (s)，10 次测量
T0_measurements = [1.559, 1.560, 1.560, 1.560, 1.561,
                   1.561, 1.561, 1.562, 1.562, 1.562]

# 阻尼组：key 是组名，value 里写 10T 总时长(秒)和 10 个振幅 θ(度)
# 想加阻尼三就直接在字典里再加一项
damping_groups = {
    '阻尼一': {
        '10T': 15.645,
        'theta_deg': [115, 104, 93, 84, 75, 67, 60, 54, 48, 43],
    },
    '阻尼': {
        '10T': 15.628,
        'theta_deg': [112, 100, 89, 79, 71, 63, 56, 50, 45, 40],
    },
}

# ============================================================
# 计算与绘图（一般不用动）
# ============================================================

T0_mean = float(np.mean(T0_measurements))
T0_std  = float(np.std(T0_measurements, ddof=1))
omega0  = 2 * np.pi / T0_mean

print("=" * 56)
print(f"自由振动:  T0 = {T0_mean:.4f} ± {T0_std:.4f} s")
print(f"           ω0 = {omega0:.4f} rad/s")
print("=" * 56)

n_groups = len(damping_groups)
fig, axes = plt.subplots(1, n_groups, figsize=(6.2 * n_groups, 4.8), squeeze=False)
axes = axes[0]

results = {}

for ax, (name, data) in zip(axes, damping_groups.items()):
    T        = data['10T'] / 10
    theta    = np.array(data['theta_deg'], dtype=float)
    n_index  = np.arange(1, len(theta) + 1)
    t        = n_index * T
    ln_theta = np.log(theta)

    # 线性拟合 ln θ = a + b·t
    b, a = np.polyfit(t, ln_theta, 1)
    beta    = -b                     # 阻尼系数 β  [1/s]
    Lambda  = beta * T               # 对数减缩率 Λ
    zeta    = beta / omega0          # 阻尼比 ζ
    Q       = np.pi / Lambda         # 品质因数

    # 残差与拟合优度
    ln_fit  = a + b * t
    ss_res  = np.sum((ln_theta - ln_fit) ** 2)
    ss_tot  = np.sum((ln_theta - ln_theta.mean()) ** 2)
    r2      = 1 - ss_res / ss_tot

    results[name] = dict(T=T, beta=beta, Lambda=Lambda, zeta=zeta, Q=Q, r2=r2)

    # 控制台打印一张完整的 lnθ 表
    print(f"\n--- {name}  (T = {T:.4f} s) ---")
    print(f"{'n':>3} {'t/s':>8} {'θ/deg':>8} {'lnθ':>10}")
    for ni, ti, th, ln in zip(n_index, t, theta, ln_theta):
        print(f"{ni:>3} {ti:>8.4f} {th:>8.1f} {ln:>10.4f}")
    print(f"β = {beta:.5f} s⁻¹    Λ = {Lambda:.5f}")
    print(f"ζ = {zeta:.5f}        Q = {Q:.3f}     R² = {r2:.5f}")

    # 绘图
    ax.plot(t, ln_theta, 'o', ms=7, label='实测 lnθ')
    t_fit = np.linspace(t[0], t[-1], 100)
    ax.plot(t_fit, a + b * t_fit, '-',
            label=f'拟合: lnθ = {a:.3f} − {beta:.4f} t')
    ax.set_xlabel('t / s')
    ax.set_ylabel('ln θ')
    ax.set_title(f'{name}    β = {beta:.4f} 1/s,  Λ = {Lambda:.4f},  R² = {r2:.4f}')
    ax.legend()
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('pohl_damping.png', dpi=130, bbox_inches='tight')
plt.show()

print("\n图已保存为 pohl_damping.png")