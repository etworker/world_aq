#!/usr/bin/env python
"""
Demo: API 服务

启动 REST API 服务提供预测接口
"""

print("=" * 60)
print("Demo: API 服务")
print("=" * 60)

print("\n[1/3] API 服务说明...")
print("  启动 FastAPI 服务，提供以下端点:")
print("  ")
print("  GET  /health          - 健康检查")
print("  POST /predict         - 空气质量预测")
print("  GET  /aqi/calculate   - AQI 计算")
print("  GET  /models          - 列出可用模型")

print("\n[2/3] 启动服务...")
print("  命令: python -m src.cli api --host 0.0.0.0 --port 8000")
print("  ")
print("  或使用 Python 直接启动:")
print("  from src.api import start_server")
print("  start_server(host='0.0.0.0', port=8000)")

print("\n[3/3] API 使用示例...")
print(
    """
  # 预测请求
  curl -X POST "http://localhost:8000/predict" \\
    -H "Content-Type: application/json" \\
    -d '{
      "temp_avg_c": 25.0,
      "wind_speed_kmh": 15.0,
      "visibility_km": 8.0,
      "station_pressure_hpa": 1015.0,
      "city": "Beijing"
    }'

  # 响应
  {
    "pm25": 45.2,
    "aqi": 127,
    "category": "Unhealthy for Sensitive Groups",
    "category_chinese": "轻度污染",
    "health_advice": "..."
  }
"""
)

print("=" * 60)
print("API 文档: http://localhost:8000/docs")
print("=" * 60)

# 如果直接运行则启动服务
if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from src.api import start_server

    print("\n启动 API 服务...")
    start_server(host="0.0.0.0", port=8000, reload=True)
