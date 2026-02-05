#!/usr/bin/env python
"""
Demo: AQI 计算工具

计算空气质量指数和健康建议
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.aqi import calculate_aqi, get_category, get_health_advice, format_advice

print("=" * 60)
print("Demo: AQI 计算工具")
print("=" * 60)

# 1. 计算 PM2.5 的 AQI
print("\n[1/3] 计算 PM2.5 的 AQI...")
pm25_concentration = 35.5  # μg/m³
aqi = calculate_aqi(pm25_concentration, "pm25")
category = get_category(aqi)

print(f"  PM2.5 浓度: {pm25_concentration} μg/m³")
print(f"  AQI 值: {aqi}")
print(f"  类别: {category['label']} ({category['chinese']})")
print(f"  颜色: {category['color']}")

# 2. 获取健康建议
print("\n[2/3] 获取健康建议...")
advice = get_health_advice(aqi)
print(f"  建议内容:\n{advice}")

# 3. 格式化输出
print("\n[3/3] 格式化建议...")
formatted = format_advice(aqi)
print(formatted)

# 测试不同浓度
print("\n" + "=" * 60)
print("不同 PM2.5 浓度对应的 AQI:")
print("=" * 60)
test_values = [10, 35, 75, 150, 250]
for val in test_values:
    aqi = calculate_aqi(val, "pm25")
    cat = get_category(aqi)
    print(f"  PM2.5 = {val:3} μg/m³  →  AQI = {aqi:3}  ({cat['chinese']})")

print("\n" + "=" * 60)
print("CLI 用法:")
print("  python -m src.cli aqi --calculate --pollutant pm25 --concentration 35.5")
print("  python -m src.cli aqi --advice --aqi-value 150")
print("=" * 60)
