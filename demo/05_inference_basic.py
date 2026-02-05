#!/usr/bin/env python
"""
Demo: 推理功能 - 基础用法

使用训练好的模型进行预测
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("Demo: 模型推理")
print("=" * 60)

print("\n[1/3] 列出可用模型...")
from src.inference import list_models

list_models()

print("\n[2/3] 加载预测器...")
print("  from src.inference import Predictor")
print("  predictor = Predictor('models/production/GTS/xxx/model.joblib')")

# 示例代码
from src.inference import Predictor

print("\n  # 准备天气数据")
print("  weather_data = {")
print("      'temp_avg_c': 25.0,")
print("      'wind_speed_kmh': 15.0,")
print("      'visibility_km': 8.0,")
print("      'station_pressure_hpa': 1015.0,")
print("  }")

print("\n[3/3] 进行预测...")
print("  result = predictor.predict(weather_data, city='Beijing')")
print("  print(result['pm25'])  # 输出 PM2.5 预测值")
print("  print(result['aqi'])   # 输出 AQI 值")
print("  print(result['health_advice'])  # 健康建议")

print("\n" + "=" * 60)
print("CLI 用法:")
print("  python -m src.cli inference --model <path> \\")
print("    --temperature 25 --wind-speed 15 \\")
print("    --visibility 8 --pressure 1015")
print("=" * 60)
