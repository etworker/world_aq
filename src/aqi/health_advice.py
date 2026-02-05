"""
健康建议模块

根据AQI类别生成健康建议
"""

from typing import Dict
from .breakpoints import get_category


# 健康建议配置
HEALTH_ADVICE: Dict[str, Dict[str, str]] = {
    "Good": {
        "message": "空气质量优良，适合所有户外活动",
        "health_effects": "无",
        "recommendation": "正常活动",
        "color": "#00e400",
        "icon": "😊",
    },
    "Moderate": {
        "message": "空气质量一般，敏感人群需注意",
        "health_effects": "敏感人群可能有轻微不适",
        "recommendation": "敏感人群减少长时间户外活动",
        "color": "#ffff00",
        "icon": "😐",
    },
    "Unhealthy for Sensitive Groups": {
        "message": "对敏感人群不健康",
        "health_effects": "敏感人群可能出现呼吸问题",
        "recommendation": "敏感人群减少户外活动，佩戴口罩",
        "color": "#ff7e00",
        "icon": "😷",
    },
    "Unhealthy": {
        "message": "空气质量不健康",
        "health_effects": "所有人可能出现健康问题",
        "recommendation": "减少户外活动，佩戴口罩",
        "color": "#ff0000",
        "icon": "😟",
    },
    "Very Unhealthy": {
        "message": "空气质量非常不健康",
        "health_effects": "健康人群也可能出现不良症状",
        "recommendation": "避免户外活动，关闭门窗",
        "color": "#8f3f97",
        "icon": "😫",
    },
    "Hazardous": {
        "message": "空气质量危险",
        "health_effects": "严重健康风险",
        "recommendation": "留在室内，使用空气净化器",
        "color": "#7e0023",
        "icon": "☠️",
    },
}


def get_health_recommendation(aqi_category: str) -> Dict[str, str]:
    """
    获取健康建议

    Args:
        aqi_category: AQI类别 (Good, Moderate, etc.)

    Returns:
        健康建议字典
    """
    return HEALTH_ADVICE.get(aqi_category, HEALTH_ADVICE["Good"])


def get_advice_by_aqi(aqi: int) -> Dict[str, str]:
    """
    根据AQI值获取健康建议

    Args:
        aqi: AQI值

    Returns:
        健康建议字典
    """
    category = get_category(aqi)
    return get_health_recommendation(category["label"])


def format_advice(aqi: int) -> str:
    """
    格式化健康建议

    Args:
        aqi: AQI值

    Returns:
        格式化的建议字符串
    """
    advice = get_advice_by_aqi(aqi)
    return (
        f"{advice['icon']} {advice['message']}\n"
        f"健康影响: {advice['health_effects']}\n"
        f"建议: {advice['recommendation']}"
    )
