"""
AQI 断点定义模块

EPA AQI Breakpoints 定义
参考: https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf
"""

from typing import Dict, List, Tuple

# EPA 24小时 AQI Breakpoints
# 格式: [(浓度下限, 浓度上限, AQI下限, AQI上限), ...]
EPA_BREAKPOINTS: Dict[str, List[Tuple[float, float, int, int]]] = {
    # PM2.5 (µg/m³) - 24小时平均
    "pm25": [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ],
    # PM10 (µg/m³) - 24小时平均
    "pm10": [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 604, 301, 500),
    ],
    # O3 (ppm) - 8小时平均
    "o3": [
        (0.000, 0.054, 0, 50),
        (0.055, 0.070, 51, 100),
        (0.071, 0.085, 101, 150),
        (0.086, 0.105, 151, 200),
        (0.106, 0.200, 201, 300),
    ],
    # NO2 (ppm) - (EPA原始断点为ppb，已转换为ppm)
    "no2": [
        (0.000, 0.053, 0, 50),
        (0.054, 0.100, 51, 100),
        (0.101, 0.360, 101, 150),
        (0.361, 0.649, 151, 200),
        (0.650, 1.249, 201, 300),
    ],
    # SO2 (ppm) - (EPA原始断点为ppb，已转换为ppm)
    "so2": [
        (0.000, 0.035, 0, 50),
        (0.036, 0.075, 51, 100),
        (0.076, 0.185, 101, 150),
        (0.186, 0.304, 151, 200),
        (0.305, 0.604, 201, 300),
    ],
    # CO (ppm) - 8小时平均
    "co": [
        (0.0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 50.4, 301, 500),
    ],
}

# AQI 类别定义
AQI_CATEGORIES: Dict[Tuple[int, int], Dict[str, str]] = {
    (0, 50): {
        "label": "Good",
        "color": "#00E400",
        "chinese": "优",
        "description": "空气质量令人满意，基本无空气污染",
    },
    (51, 100): {
        "label": "Moderate",
        "color": "#FFFF00",
        "chinese": "良",
        "description": "空气质量可接受，某些污染物可能对极少数敏感人群有轻微影响",
    },
    (101, 150): {
        "label": "Unhealthy for Sensitive Groups",
        "color": "#FF7E00",
        "chinese": "轻度污染",
        "description": "敏感人群症状轻度加剧，健康人群出现刺激症状",
    },
    (151, 200): {
        "label": "Unhealthy",
        "color": "#FF0000",
        "chinese": "中度污染",
        "description": "进一步加剧易感人群症状，可能对健康人群心脏、呼吸系统有影响",
    },
    (201, 300): {
        "label": "Very Unhealthy",
        "color": "#8F3F97",
        "chinese": "重度污染",
        "description": "心脏病和肺病患者症状显著加剧，运动耐受力降低，健康人群普遍出现症状",
    },
    (301, 500): {
        "label": "Hazardous",
        "color": "#7E0023",
        "chinese": "严重污染",
        "description": "健康人群运动耐受力降低，有明显强烈症状，提前出现某些疾病",
    },
}


def get_category(aqi: int) -> Dict[str, str]:
    """
    根据AQI值获取类别信息

    Args:
        aqi: AQI值

    Returns:
        类别信息字典
    """
    for (low, high), info in AQI_CATEGORIES.items():
        if low <= aqi <= high:
            return info
    return AQI_CATEGORIES[(301, 500)]  # 默认最严重


def get_breakpoints(pollutant: str) -> List[Tuple[float, float, int, int]]:
    """
    获取污染物的断点

    Args:
        pollutant: 污染物名称

    Returns:
        断点列表
    """
    return EPA_BREAKPOINTS.get(pollutant, [])
