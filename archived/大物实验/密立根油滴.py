# -*- coding: utf-8 -*-
"""
密立根油滴法测定电子电荷 —— 数据处理
对每个油滴带电量 q：n = round(q/e0)，e_i = q/n，再求 e 平均值与相对误差
公认电子电荷 e0 = 1.60e-19 C
"""
import numpy as np

q = np.array([8.31e-19, 1.336e-18, 5.48e-19, 1.709e-18, 3.05e-19])   # 各油滴带电量 / C
e0 = 1.60e-19                                                        # 公认电子电荷 / C


def round_sig(x, sig=4):
    """四舍五入到 sig 位有效数字（与报告表格一致）"""
    return float(f"{x:.{sig-1}e}")


n = np.array([round(v / e0) for v in q])          # 基本电荷数
e_i = q / n                                       # 每个油滴的电子电荷
e_i_disp = np.array([round_sig(v) for v in e_i])  # 4 位有效数字（报告表格值）
e_mean = e_i_disp.mean()                          # 用表格中的 e_i 求平均
rel = (e_mean - e0) / e0 * 100.0                  # 相对误差 / %

print("=" * 80)
print("密立根油滴法测定电子电荷 —— 数据处理")
print(f"公认电子电荷 e0 = {e0:.2e} C")
print("=" * 80)
print(f"{'序号':<5}{'q / C':>13}{'q/e0':>10}{'n':>5}{'e_i = q/n / C':>19}{'e_i 相对 e0 偏差':>18}")
for k in range(len(q)):
    ei_rel = (e_i_disp[k] - e0) / e0 * 100.0
    print(f"{k+1:<5}{q[k]:>13.4g}{q[k]/e0:>10.3f}{n[k]:>5}"
          f"{e_i_disp[k]:>19.3e}{ei_rel:>+17.1f}%")

print()
e_str = " + ".join([f"{v:.3e}" for v in e_i_disp])
print(f"e 平均值 = ({e_str}) / 5 = {e_mean:.3e} C")
print(f"相对误差 E = (ē − e0)/e0 × 100% = ({e_mean:.3e} − {e0:.3e})/{e0:.3e} × 100% = {rel:+.1f}%")
