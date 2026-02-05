"""
AQI模块

提供空气质量指数计算和健康建议
"""

from .calculator import AQICalculator, calculate_aqi, get_health_advice
from .breakpoints import get_category, get_breakpoints, EPA_BREAKPOINTS, AQI_CATEGORIES
from .health_advice import get_health_recommendation, get_advice_by_aqi, format_advice

__all__ = [
    "AQICalculator",
    "calculate_aqi",
    "get_health_advice",
    "get_category",
    "get_breakpoints",
    "EPA_BREAKPOINTS",
    "AQI_CATEGORIES",
    "get_health_recommendation",
    "get_advice_by_aqi",
    "format_advice",
]
