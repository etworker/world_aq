#!/usr/bin/env python
"""
Demo: 数据校验

验证数据质量和完整性
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

print("=" * 60)
print("Demo: 数据质量校验")
print("=" * 60)

# 示例数据检查
print("\n[1/4] 加载示例数据进行校验...")

# 创建示例数据
df = pd.DataFrame(
    {
        "date": pd.date_range("2023-01-01", periods=10),
        "pm25": [35, 42, None, 55, 60, 9999, 45, 38, None, 50],
        "temp_avg_c": [20, 22, 21, None, 25, 26, 24, 23, 22, None],
        "city_name": ["Beijing"] * 10,
    }
)

print(f"  示例数据: {len(df)} 行")
print(df.head())

print("\n[2/4] 数据质量检查...")

# 检查缺失值
missing = df.isnull().sum()
print("  缺失值统计:")
for col, count in missing.items():
    if count > 0:
        print(f"    - {col}: {count} 个缺失 ({count/len(df)*100:.1f}%)")

# 检查异常值
print("\n  异常值检查:")
print(f"    - PM2.5 范围: {df['pm25'].min():.1f} ~ {df['pm25'].max():.1f}")
if df["pm25"].max() > 1000:
    print(f"      ⚠️ 发现异常高值: {df['pm25'].max()} (可能是缺失值标记)")

print("\n[3/4] 使用校验工具...")
print(
    """
  from src.data.processing.merger import DataMerger
  
  # 数据质量检查
  quality_report = DataMerger.validate_data(df)
  
  print(f"数据质量报告:")
  print(f"  - 总行数: {quality_report['total_rows']}")
  print(f"  - 缺失率: {quality_report['missing_rate']:.2%}")
  print(f"  - 时间跨度: {quality_report['date_range']}")
  print(f"  - 异常值数量: {quality_report['outliers']}")
"""
)

print("\n[4/4] 数据预处理建议...")
print(
    """
  常见问题及处理:
  
  1. 缺失值处理:
     - 气象数据: 使用线性插值
     - 空气质量: 使用前向填充 + 插值
     
  2. 异常值处理:
     - 识别: 基于物理合理范围 (如 PM2.5 > 500)
     - 处理: 标记为缺失后插值
     
  3. 数据对齐:
     - 确保气象和空气质量日期对齐
     - 处理时区问题
     
  4. 特征工程:
     - 添加滞后特征 (lag-1, lag-7)
     - 添加滚动统计 (7天均值、30天均值)
     - 添加时间特征 (星期、月份、季节)
"""
)

print("\n" + "=" * 60)
print("数据校验要点:")
print("  ✅ 检查缺失值比例 (< 20%)")
print("  ✅ 检查异常值和离群点")
print("  ✅ 验证时间序列连续性")
print("  ✅ 确认特征和目标变量范围合理")
print("=" * 60)
