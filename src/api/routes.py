"""
API 路由定义
"""

import os
from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..aqi import AQICalculator, get_advice_by_aqi
from ..inference import Predictor, ModelLoader
from ..config import DEFAULT_CITIES
from .schemas import (
    AQICalculateRequest,
    AQICalculateResponse,
    PredictRequest,
    PredictResponse,
    CitiesResponse,
    CityInfo,
    ErrorResponse,
)

router = APIRouter()

# 全局组件
aqi_calculator = AQICalculator()

# 可用城市
AVAILABLE_CITIES = {
    name: {"lat": lat, "lon": lon, "state": name.split()[-1] if len(name.split()) > 1 else ""}
    for name, (lat, lon) in [(city, (0.0, 0.0)) for city, _ in DEFAULT_CITIES]
}

# 尝试加载模型
_model_cache: Dict[str, Predictor] = {}


def get_predictor(mode: str = "GTS") -> Optional[Predictor]:
    """获取或创建预测器"""
    if mode in _model_cache:
        return _model_cache[mode]

    # 尝试查找最新模型
    model_path = ModelLoader.find_latest_model(mode)
    if model_path:
        predictor = Predictor(model_path, mode=mode)
        _model_cache[mode] = predictor
        return predictor

    return None


@router.get("/health", response_model=dict)
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "World Air Quality Prediction API",
    }


@router.get("/cities", response_model=CitiesResponse)
async def list_cities():
    """获取支持的城市列表"""
    cities = [CityInfo(name=name, **coords) for name, coords in AVAILABLE_CITIES.items()]
    return CitiesResponse(cities=cities)


@router.post("/aqi/calculate", response_model=AQICalculateResponse)
async def calculate_aqi(request: AQICalculateRequest):
    """
    计算AQI

    根据污染物浓度计算空气质量指数
    """
    pollutants = request.pollutants.dict()

    # 检查至少有一个污染物
    valid_pollutants = {k: v for k, v in pollutants.items() if v is not None}
    if not valid_pollutants:
        raise HTTPException(status_code=400, detail="至少需要提供一个污染物浓度")

    # 计算各污染物的AQI
    pollutant_aqis = {}
    for pollutant, value in valid_pollutants.items():
        aqi = aqi_calculator.calculate(value, pollutant)
        pollutant_aqis[pollutant.upper()] = aqi

    # 综合AQI取最大值
    overall_aqi = max(pollutant_aqis.values())

    # 获取类别和建议
    category_info = aqi_calculator.get_category(overall_aqi)
    advice = get_advice_by_aqi(overall_aqi)

    return AQICalculateResponse(
        success=True,
        aqi=overall_aqi,
        category=category_info["label"],
        category_chinese=category_info["chinese"],
        color=category_info["color"],
        pollutant_aqis=pollutant_aqis,
        health_advice=advice["recommendation"],
    )


@router.post("/predict", response_model=PredictResponse)
async def predict_aqi(request: PredictRequest):
    """
    预测AQI

    根据天气数据预测空气质量
    """
    city = request.city

    if city not in AVAILABLE_CITIES:
        raise HTTPException(status_code=400, detail=f"不支持的城市: {city}")

    # 获取预测器
    has_history = request.history_data is not None and len(request.history_data) >= 7
    mode = "GHS" if has_history else "GTS"

    predictor = get_predictor(mode)

    # 构建天气数据
    weather_data = request.weather.dict()
    weather_data["date"] = request.date or datetime.now().strftime("%Y-%m-%d")

    # 构建历史数据
    historical_df = None
    if has_history:
        import pandas as pd

        historical_df = pd.DataFrame(request.history_data)

    # 预测
    if predictor:
        result = predictor.predict(
            weather_data=weather_data,
            historical_data=historical_df,
            city=city,
        )
    else:
        # 无模型时使用简化估算
        result = _simple_prediction(city, weather_data)

    return PredictResponse(
        success=True,
        city=result["city"],
        date=result.get("date", weather_data["date"]),
        predicted_pm25=result["pm25"],
        aqi=result["aqi"],
        category=result["category"],
        category_chinese=result.get("category_chinese", ""),
        color=result["color"],
        health_advice=result["health_advice"],
    )


def _simple_prediction(city: str, weather_data: Dict) -> Dict:
    """简化预测（无模型时使用）"""
    import numpy as np

    base_pm25 = 30.0

    # 温度影响
    temp = weather_data.get("temp_avg_c", 20)
    temp_factor = (temp - 20) * 0.3

    # 风速影响
    wind = weather_data.get("wind_speed_kmh", 10)
    wind_factor = max(0, (15 - wind) * 0.5)

    # 降水影响
    precip = weather_data.get("precip_mm", 0)
    precip_factor = -min(precip, 10) * 0.8

    predicted_pm25 = max(0, base_pm25 + temp_factor + wind_factor + precip_factor)

    # 计算AQI
    aqi = aqi_calculator.calculate(predicted_pm25, "pm25")
    category = aqi_calculator.get_category(aqi)
    advice = get_advice_by_aqi(aqi)

    return {
        "city": city,
        "pm25": round(predicted_pm25, 1),
        "aqi": aqi,
        "category": category["label"],
        "category_chinese": category["chinese"],
        "color": category["color"],
        "health_advice": advice["recommendation"],
    }


@router.get("/aqi/explain")
async def explain_aqi():
    """
    获取AQI计算说明

    返回EPA AQI计算公式和breakpoint表
    """
    from ..config import EPA_AQI_BREAKPOINTS, AQI_CATEGORIES

    return {
        "formula": "AQI = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low",
        "breakpoints": {
            pollutant: [
                {
                    "concentration_low": bp[0],
                    "concentration_high": bp[1],
                    "aqi_low": bp[2],
                    "aqi_high": bp[3],
                }
                for bp in breakpoints
            ]
            for pollutant, breakpoints in EPA_AQI_BREAKPOINTS.items()
        },
        "categories": [
            {
                "aqi_low": low,
                "aqi_high": high,
                "label": info["label"],
                "chinese": info["chinese"],
                "color": info["color"],
            }
            for (low, high), info in [(cat[0], cat[1]) for cat in AQI_CATEGORIES]
        ],
    }
