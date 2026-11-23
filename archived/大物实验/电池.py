# -*- coding: utf-8 -*-
"""
实验三十  太阳能电池基本特性研究 —— 数据处理与作图
- 暗伏安特性曲线（单晶硅 / 非晶硅）
- Voc-I 、Isc-I 关系曲线
- 输出伏安特性 + 功率曲线（双 Y 轴），最大功率点 / 最佳匹配负载 / 填充因子
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# ---- 中文字体（找不到就退回英文标签，避免乱码）----
for f in ["Noto Sans CJK SC", "SimHei", "Microsoft YaHei", "PingFang SC",
          "Hiragino Sans GB", "WenQuanYi Zen Hei"]:
    try:
        matplotlib.font_manager.findfont(f, fallback_to_default=False)
        plt.rcParams["font.sans-serif"] = [f]
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

# =====================================================================
# 表1  暗伏安特性
# =====================================================================
V_dark = np.array([0.0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9])
I_mono = np.array([0.000, 0.012, 0.038, 0.093, 0.223, 0.553, 1.419,
                   3.6, 8.7, 23.5, 77.2, np.nan, np.nan, np.nan])
# 注意：非晶硅 1.8V 处 11.650 与前后趋势严重矛盾（疑为 1.165 笔误），下用 nan 屏蔽该点
I_amor = np.array([0.000, 0.202, 0.410, 0.642, 0.882, 1.205, np.nan,
                   2.4, 3.2, 4.2, 5.8, 9.4, 16.6, 27.6])


def plot_dark_iv():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    # 线性坐标：看整体指数上翘
    ax = axes[0]
    m = ~np.isnan(I_mono)
    ax.plot(V_dark[m], I_mono[m], "o-", label="单晶硅 mono-Si")
    a = ~np.isnan(I_amor)
    ax.plot(V_dark[a], I_amor[a], "s-", label="非晶硅 a-Si")
    ax.set_xlabel("电压 V (V)")
    ax.set_ylabel("电流 I (mA)")
    ax.set_title("暗伏安特性（线性）")
    ax.legend(); ax.grid(True, ls=":")

    # 半对数坐标：指数段呈直线，与二极管对照更直观
    ax = axes[1]
    ax.semilogy(V_dark[m], I_mono[m], "o-", label="单晶硅 mono-Si")
    ax.semilogy(V_dark[a], I_amor[a], "s-", label="非晶硅 a-Si")
    ax.set_xlabel("电压 V (V)")
    ax.set_ylabel("电流 I (mA, log)")
    ax.set_title("暗伏安特性（半对数）")
    ax.legend(); ax.grid(True, which="both", ls=":")
    fig.suptitle("太阳能电池暗伏安特性（具二极管整流特性）", fontsize=13)
    fig.tight_layout()
    fig.savefig("fig1_dark_iv.png", dpi=150)


# =====================================================================
# 表2  开路电压 / 短路电流 随光强变化
# =====================================================================
dist = np.array([20, 25, 30, 35, 40, 45, 15, 50])
light = np.array([343, 208, 142.1, 102.5, 76.8, 61.5, 650, 52.3])
Voc_mono = np.array([2.77, 2.64, 2.53, 2.43, 2.35, 2.27, 2.89, 2.25])
Isc_mono = np.array([41.3, 25.9, 17.6, 12.7, 9.8, 7.8, 74.8, 6.4])
Voc_amor = np.array([2.37, 1.98, 1.67, 1.39, 1.17, 0.97, 2.78, 0.82])
Isc_amor = np.array([3.8, 2.3, 1.6, 1.2, 0.9, 0.7, 6.8, 0.6])

order = np.argsort(light)          # 按光强升序排列再画线
light_s = light[order]


def plot_voc_isc():
    # Voc - I
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot(light_s, Voc_mono[order], "o-", label="单晶硅 mono-Si")
    ax.plot(light_s, Voc_amor[order], "s-", label="非晶硅 a-Si")
    ax.set_xlabel("光强 I (W/m²)")
    ax.set_ylabel("开路电压 Voc (V)")
    ax.set_title("开路电压随光强变化（近对数关系）")
    ax.legend(); ax.grid(True, ls=":")
    fig.tight_layout(); fig.savefig("fig2_voc_light.png", dpi=150)

    # Isc - I
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot(light_s, Isc_mono[order], "o-", label="单晶硅 mono-Si")
    ax.plot(light_s, Isc_amor[order], "s-", label="非晶硅 a-Si")
    ax.set_xlabel("光强 I (W/m²)")
    ax.set_ylabel("短路电流 Isc (mA)")
    ax.set_title("短路电流随光强变化（近线性正比）")
    ax.legend(); ax.grid(True, ls=":")
    fig.tight_layout(); fig.savefig("fig3_isc_light.png", dpi=150)


# =====================================================================
# 表3/表4  输出特性：伏安 + 功率（双 Y 轴），Pmax / 最佳负载 / 填充因子
# =====================================================================
# 单晶硅（乱序，程序内排序）
V_o_mono = np.array([0.04, 0.56, 0.78, 2.14, 2.26, 2.36, 2.40, 2.05, 0.08, 0.94])
I_o_mono = np.array([10.0, 10.2, 8.6, 5.2, 3.1, 0.4, 0.0, 6.3, 10.1, 9.9])
# 非晶硅
V_o_amor = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
I_o_amor = np.array([0.9, 0.8, 0.6, 0.5, 0.3, 0.1, 0.0])


def analyze_output(V, I, name):
    """排序、算功率 P0=V*I、求 Pmax / 最佳负载 / 填充因子"""
    idx = np.argsort(V)
    V, I = V[idx], I[idx]
    P = V * I                              # P0 (mW)，V 单位 V、I 单位 mA → P 单位 mW
    k = int(np.argmax(P))
    Vmp, Imp, Pmax = V[k], I[k], P[k]
    Voc = V[I <= 1e-9].min() if np.any(I <= 1e-9) else V.max()   # I=0 处电压
    Isc = I[np.argmin(V)]                  # V≈0 处电流
    R_opt = Vmp / Imp * 1000 if Imp else np.nan   # V(V)/I(mA)=kΩ → ×1000 得 Ω
    FF = Pmax / (Voc * Isc) if Voc * Isc else np.nan
    print(f"\n=== {name} 输出特性 ===")
    print(f"  {'V(V)':>8}{'I(mA)':>10}{'P0(mW)':>10}")
    for v, i, p in zip(V, I, P):
        mark = "  <- Pmax" if p == Pmax else ""
        print(f"  {v:>8.2f}{i:>10.2f}{p:>10.4f}{mark}")
    print(f"  Voc = {Voc:.3f} V , Isc = {Isc:.3f} mA")
    print(f"  最大功率点: Vmp = {Vmp:.3f} V, Imp = {Imp:.3f} mA, Pmax = {Pmax:.4f} mW")
    print(f"  最佳匹配负载 R_opt = Vmp/Imp = {R_opt:.1f} Ω")
    print(f"  填充因子 FF = Pmax/(Voc·Isc) = {FF:.4f}")
    return V, I, P, (Vmp, Imp, Pmax, FF, R_opt)


def plot_output(V, I, P, mp, name, fname):
    Vmp, Imp, Pmax, FF, R_opt = mp
    fig, ax1 = plt.subplots(figsize=(7, 4.8))
    c1, c2 = "tab:blue", "tab:red"
    ax1.plot(V, I, "o-", color=c1, label="I-V 伏安特性")
    ax1.set_xlabel("输出电压 V (V)")
    ax1.set_ylabel("电流 I (mA)", color=c1)
    ax1.tick_params(axis="y", labelcolor=c1)
    ax1.grid(True, ls=":")

    ax2 = ax1.twinx()
    ax2.plot(V, P, "s--", color=c2, label="P-V 功率曲线")
    ax2.set_ylabel("输出功率 P0 (mW)", color=c2)
    ax2.tick_params(axis="y", labelcolor=c2)

    ax2.plot(Vmp, Pmax, "*", color="k", ms=15)
    ax2.annotate(f"Pmax={Pmax:.2f} mW\n({Vmp:.2f}V, {Imp:.2f}mA)\nFF={FF:.3f}",
                 xy=(Vmp, Pmax), xytext=(0.05, 0.6), textcoords="axes fraction",
                 arrowprops=dict(arrowstyle="->"))
    ax1.set_title(f"{name} 输出伏安特性与功率曲线")
    l1, lab1 = ax1.get_legend_handles_labels()
    l2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lab1 + lab2, loc="upper center")
    fig.tight_layout(); fig.savefig(fname, dpi=150)


if __name__ == "__main__":
    plot_dark_iv()
    plot_voc_isc()
    Vm, Im, Pm, mp_m = analyze_output(V_o_mono, I_o_mono, "单晶硅")
    plot_output(Vm, Im, Pm, mp_m, "单晶硅 mono-Si", "fig4_output_mono.png")
    Va, Ia, Pa, mp_a = analyze_output(V_o_amor, I_o_amor, "非晶硅")
    plot_output(Va, Ia, Pa, mp_a, "非晶硅 a-Si", "fig5_output_amor.png")
    print("\n所有图已保存为 fig1~fig5 *.png")