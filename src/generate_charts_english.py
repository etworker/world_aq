#!/usr/bin/env python
"""
生成实验分析报告（使用英文标签避免字体问题）
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# 设置样式
sns.set_style("whitegrid")

# 路径配置
PROJECT_ROOT = Path("/Users/etworker/Documents/code/others/world_aq")
EXPERIMENT_DIR = PROJECT_ROOT / "models/experiments/20260206_044103_df1679c6"
OUTPUT_DIR = PROJECT_ROOT / "doc/images"

# 确保输出目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Loading experiment data from: {EXPERIMENT_DIR}")

# 加载实验数据
manifest_path = EXPERIMENT_DIR / "manifest.json"
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

results = manifest.get('results', [])
print(f"Total experiments: {len(results)}")

# 转换为 DataFrame
df = pd.DataFrame([{
    'mode': r['mode'],
    'algorithm': r['algorithm'],
    'val_rmse': r['val_metrics'].get('rmse'),
    'test_rmse': r['metrics'].get('rmse'),
    'val_r2': r['val_metrics'].get('r2'),
    'test_r2': r['metrics'].get('r2'),
} for r in results])

# 提取基础模式
df['base_mode'] = df['mode'].apply(lambda x: x.split('_')[0] if '_' in x else x)

# 1. 各模式最佳模型
mode_best = df.loc[df.groupby('mode')['val_rmse'].idxmin()].sort_values('val_rmse')

# 2. 全局最佳模型
global_best = df.loc[df['val_rmse'].idxmin()]

# 3. 算法平均表现
algo_avg = df.groupby('algorithm').agg({
    'val_rmse': ['mean', 'std'],
    'test_rmse': ['mean', 'std'],
    'val_r2': 'mean',
    'test_r2': 'mean',
}).round(4)

# 生成图表
print("Generating charts...")

# 图1: 主分析图表
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# (0,0) 各模式最佳模型验证RMSE
ax1 = axes[0, 0]
sorted_modes = mode_best.sort_values('val_rmse')
colors = plt.cm.RdYlGn_r(len(sorted_modes))
bars = ax1.barh(range(len(sorted_modes)), sorted_modes['val_rmse'], color=colors)
ax1.set_yticks(range(len(sorted_modes)))
ax1.set_yticklabels(sorted_modes['mode'], fontsize=8)
ax1.set_xlabel('Validation RMSE')
ax1.set_title('Best Model by Mode (Validation RMSE)')
for i, (bar, val) in enumerate(zip(bars, sorted_modes['val_rmse'])):
    ax1.text(val, i, f'{val:.2f}', va='center', fontsize=7)
ax1.invert_yaxis()

# (0,1) 各模式最佳模型测试RMSE
ax2 = axes[0, 1]
bars = ax2.barh(range(len(sorted_modes)), sorted_modes['test_rmse'], color=colors)
ax2.set_yticks(range(len(sorted_modes)))
ax2.set_yticklabels(sorted_modes['mode'], fontsize=8)
ax2.set_xlabel('Test RMSE')
ax2.set_title('Best Model by Mode (Test RMSE)')
for i, (bar, val) in enumerate(zip(bars, sorted_modes['test_rmse'])):
    ax2.text(val, i, f'{val:.2f}', va='center', fontsize=7)
ax2.invert_yaxis()

# (0,2) 各模式最佳模型R²对比
ax3 = axes[0, 2]
bars = ax3.barh(range(len(sorted_modes)), sorted_modes['val_r2'], color=plt.cm.GnBu(len(sorted_modes)))
ax3.set_yticks(range(len(sorted_modes)))
ax3.set_yticklabels(sorted_modes['mode'], fontsize=8)
ax3.set_xlabel('Validation R²')
ax3.set_title('Best Model by Mode (Validation R²)')
for i, (bar, val) in enumerate(zip(bars, sorted_modes['val_r2'])):
    ax3.text(val, i, f'{val:.3f}', va='center', fontsize=7)
ax3.axvline(x=0, color='black', linestyle='--', linewidth=0.5)
ax3.invert_yaxis()

# (1,0) 算法平均RMSE
ax4 = axes[1, 0]
algo_sorted = algo_avg.sort_values(('val_rmse', 'mean'))
bars = ax4.barh(range(len(algo_sorted)), algo_sorted[('val_rmse', 'mean')].values.flatten())
ax4.set_yticks(range(len(algo_sorted)))
ax4.set_yticklabels(algo_sorted.index, fontsize=9)
ax4.set_xlabel('Average Validation RMSE')
ax4.set_title('Average Performance by Algorithm')
for i, bar in enumerate(bars):
    val = bar.get_width()
    ax4.text(val, i, f'{val:.2f}', va='center')
ax4.invert_yaxis()

# (1,1) 验证 vs 测试 RMSE 散点图
ax5 = axes[1, 1]
scatter = ax5.scatter(df['val_rmse'], df['test_rmse'], c=df['val_r2'],
                     cmap='RdYlGn', s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
ax5.set_xlabel('Validation RMSE')
ax5.set_ylabel('Test RMSE')
ax5.set_title('Validation vs Test RMSE (Color=R²)')
ax5.plot([0, 100], [0, 100], 'k--', alpha=0.5, label='y=x')
ax5.legend()
ax5.fill_between([0, 100], [0, 100], [0, 50], alpha=0.1, color='green')
ax5.fill_between([0, 100], [0, 100], [50, 100], alpha=0.1, color='red')
plt.colorbar(scatter, ax=ax5, label='Validation R²')

# (1,2) 算法在不同模式下的表现热力图
ax6 = axes[1, 2]
pivot_data = df.pivot_table(values='val_rmse', index='base_mode', columns='algorithm', aggfunc='mean')
sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlOrRd_r', ax=ax6,
            cbar_kws={'label': 'Validation RMSE'})
ax6.set_title('Algorithm Performance by Mode')
ax6.set_xlabel('Algorithm')
ax6.set_ylabel('Base Mode')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'experiment_analysis.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUTPUT_DIR / 'experiment_analysis.png'}")

# 图2: 对比分析图表
fig2, axes2 = plt.subplots(2, 2, figsize=(16, 12))

# (0,0) 全局模式 vs 城市级模式
ax2_1 = axes2[0, 0]
global_df = df[df['base_mode'].isin(['GTM', 'GTS', 'GHM', 'GHS'])]
city_df = df[df['base_mode'].isin(['CTM', 'CTS', 'CHM', 'CHS'])]
global_best_mode = global_df.groupby('base_mode')['val_rmse'].min()
city_best_mode = city_df.groupby('base_mode')['val_rmse'].min()

x = np.arange(len(global_best_mode))
width = 0.35
bars1 = ax2_1.bar(x - width/2, global_best_mode.values, width, label='Global Models')
bars2 = ax2_1.bar(x + width/2, city_best_mode.values, width, label='City-Level Models')
ax2_1.set_xlabel('Base Mode')
ax2_1.set_ylabel('Best Validation RMSE')
ax2_1.set_title('Global vs City-Level Models')
ax2_1.set_xticks(x)
ax2_1.set_xticklabels(['GTM\n(Multi)', 'GTS\n(Sep)', 'GHM\n(Multi)', 'GHS\n(Sep)'])
ax2_1.legend()
ax2_1.grid(axis='y', alpha=0.3)

# (0,1) 当天 vs 历史模式
ax2_2 = axes2[0, 1]
current_df = df[df['base_mode'].isin(['GTM', 'GTS', 'CTM', 'CTS'])]
history_df = df[df['base_mode'].isin(['GHM', 'GHS', 'CHM', 'CHS'])]
current_best = current_df.groupby('base_mode')['val_rmse'].min()
history_best = history_df.groupby('base_mode')['val_rmse'].min()

x = np.arange(len(current_best))
bars1 = ax2_2.bar(x - width/2, current_best.values, width, label='Today')
bars2 = ax2_2.bar(x + width/2, history_best.values, width, label='Historical')
ax2_2.set_xlabel('Base Mode')
ax2_2.set_ylabel('Best Validation RMSE')
ax2_2.set_title('Today vs Historical Models')
ax2_2.set_xticks(x)
ax2_2.set_xticklabels(['GTM', 'GTS', 'CTM', 'CTS'])
ax2_2.legend()
ax2_2.grid(axis='y', alpha=0.3)

# (1,0) 多输出 vs 独立模型
ax2_3 = axes2[1, 0]
multi_df = df[df['base_mode'].isin(['GTM', 'GHM', 'CTM', 'CHM'])]
single_df = df[df['base_mode'].isin(['GTS', 'GHS', 'CTS', 'CHS'])]
multi_best = multi_df.groupby('base_mode')['val_rmse'].min()
single_best = single_df.groupby('base_mode')['val_rmse'].min()

x = np.arange(len(multi_best))
bars1 = ax2_3.bar(x - width/2, multi_best.values, width, label='Multi-Output')
bars2 = ax2_3.bar(x + width/2, single_best.values, width, label='Separate')
ax2_3.set_xlabel('Base Mode')
ax2_3.set_ylabel('Best Validation RMSE')
ax2_3.set_title('Multi-Output vs Separate Models')
ax2_3.set_xticks(x)
ax2_3.set_xticklabels(['GTM', 'GHM', 'CTM', 'CHM'])
ax2_3.legend()
ax2_3.grid(axis='y', alpha=0.3)

# (1,1) 前10最佳模型
ax2_4 = axes2[1, 1]
top10 = df.nsmallest(10, 'val_rmse')
y_pos = np.arange(len(top10))
bars = ax2_4.barh(y_pos, top10['val_rmse'], color=plt.cm.RdYlGn_r(len(top10)))
ax2_4.set_yticks(y_pos)
ax2_4.set_yticklabels([f"{row['mode']}\n({row['algorithm']})" for _, row in top10.iterrows()], fontsize=8)
ax2_4.set_xlabel('Validation RMSE')
ax2_4.set_title('Top 10 Best Models')
ax2_4.invert_yaxis()
ax2_4.grid(axis='x', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, top10['val_rmse'])):
    ax2_4.text(val, i, f'{val:.2f}', va='center', fontsize=7)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'experiment_comparison.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUTPUT_DIR / 'experiment_comparison.png'}")

# 图3: 城市级模式详细分析
fig3, axes3 = plt.subplots(2, 2, figsize=(16, 12))

# 提取城市信息
city_df_filtered = df[df['base_mode'].isin(['CTM', 'CTS', 'CHM', 'CHS'])]
city_df_filtered['city'] = city_df_filtered['mode'].apply(lambda x: x.split('_')[-2] if '_' in x and 'pm25' not in x.split('_')[-1] else x.split('_')[-3] if '_' in x else x)

# (0,0) 各城市最佳模型（CTM）
ax3_1 = axes3[0, 0]
ctm_df = city_df_filtered[city_df_filtered['base_mode'] == 'CTM']
if not ctm_df.empty:
    ctm_best = ctm_df.loc[ctm_df.groupby('city')['val_rmse'].idxmin()].sort_values('val_rmse')
    cities = ctm_best['city'].values
    y_pos = np.arange(len(cities))
    bars = ax3_1.barh(y_pos, ctm_best['val_rmse'], color=plt.cm.RdYlGn_r(len(cities)))
    ax3_1.set_yticks(y_pos)
    ax3_1.set_yticklabels(cities)
    ax3_1.set_xlabel('Validation RMSE')
    ax3_1.set_title('Best CTM Model by City')
    ax3_1.invert_yaxis()
    for i, (bar, val) in enumerate(zip(bars, ctm_best['val_rmse'])):
        ax3_1.text(val, i, f'{val:.2f}', va='center')
ax3_1.grid(axis='x', alpha=0.3)

# (0,1) 各城市最佳模型（CTS）
ax3_2 = axes3[0, 1]
cts_df = city_df_filtered[city_df_filtered['base_mode'] == 'CTS']
if not cts_df.empty:
    cts_best = cts_df.loc[cts_df.groupby('city')['val_rmse'].idxmin()].sort_values('val_rmse')
    cities = cts_best['city'].values
    y_pos = np.arange(len(cities))
    bars = ax3_2.barh(y_pos, cts_best['val_rmse'], color=plt.cm.RdYlGn_r(len(cities)))
    ax3_2.set_yticks(y_pos)
    ax3_2.set_yticklabels(cities)
    ax3_2.set_xlabel('Validation RMSE')
    ax3_2.set_title('Best CTS Model by City')
    ax3_2.invert_yaxis()
    for i, (bar, val) in enumerate(zip(bars, cts_best['val_rmse'])):
        ax3_2.text(val, i, f'{val:.2f}', va='center')
ax3_2.grid(axis='x', alpha=0.3)

# (1,0) 各城市最佳模型（CHM）
ax3_3 = axes3[1, 0]
chm_df = city_df_filtered[city_df_filtered['base_mode'] == 'CHM']
if not chm_df.empty:
    chm_best = chm_df.loc[chm_df.groupby('city')['val_rmse'].idxmin()].sort_values('val_rmse')
    cities = chm_best['city'].values
    y_pos = np.arange(len(cities))
    bars = ax3_3.barh(y_pos, chm_best['val_rmse'], color=plt.cm.RdYlGn_r(len(cities)))
    ax3_3.set_yticks(y_pos)
    ax3_3.set_yticklabels(cities)
    ax3_3.set_xlabel('Validation RMSE')
    ax3_3.set_title('Best CHM Model by City')
    ax3_3.invert_yaxis()
    for i, (bar, val) in enumerate(zip(bars, chm_best['val_rmse'])):
        ax3_3.text(val, i, f'{val:.2f}', va='center')
ax3_3.grid(axis='x', alpha=0.3)

# (1,1) 各城市最佳模型（CHS）
ax3_4 = axes3[1, 1]
chs_df = city_df_filtered[city_df_filtered['base_mode'] == 'CHS']
if not chs_df.empty:
    chs_best = chs_df.loc[chs_df.groupby('city')['val_rmse'].idxmin()].sort_values('val_rmse')
    cities = chs_best['city'].values
    y_pos = np.arange(len(cities))
    bars = ax3_4.barh(y_pos, chs_best['val_rmse'], color=plt.cm.RdYlGn_r(len(cities)))
    ax3_4.set_yticks(y_pos)
    ax3_4.set_yticklabels(cities)
    ax3_4.set_xlabel('Validation RMSE')
    ax3_4.set_title('Best CHS Model by City')
    ax3_4.invert_yaxis()
    for i, (bar, val) in enumerate(zip(bars, chs_best['val_rmse'])):
        ax3_4.text(val, i, f'{val:.2f}', va='center')
ax3_4.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'city_analysis.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {OUTPUT_DIR / 'city_analysis.png'}")

print("\n" + "="*80)
print("Chart generation completed!")
print("="*80)
print(f"\nGenerated files:")
print(f"  - {OUTPUT_DIR / 'experiment_analysis.png'}")
print(f"  - {OUTPUT_DIR / 'experiment_comparison.png'}")
print(f"  - {OUTPUT_DIR / 'city_analysis.png'}")