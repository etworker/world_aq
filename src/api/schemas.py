"""
API 数据模型 (Pydantic Schemas)
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PollutantsInput(BaseModel):
    """污染物输入"""

    pm25: Optional[float] = Field(None, description="PM2.5 浓度 (µg/m³)")
    pm10: Optional[float] = Field(None, description="PM10 浓度 (µg/m³)")
    o3: Optional[float] = Field(None, description="O3 浓度 (ppm)")
    no2: Optional[float] = Field(None, description="NO2 浓度 (ppm)")
    so2: Optional[float] = Field(None, description="SO2 浓度 (ppm)")
    co: Optional[float] = Field(None, description="CO 浓度 (ppm)")


class AQICalculateRequest(BaseModel):
    """AQI计算请求"""

    pollutants: PollutantsInput


class AQICalculateResponse(BaseModel):
    """AQI计算响应"""

    success: bool
    aqi: int
    category: str
    category_chinese: str
    color: str
    pollutant_aqis: Dict[str, int]
    health_advice: str


class WeatherInput(BaseModel):
    """天气输入"""

    temp_avg_c: float = Field(20.0, description="平均温度 (°C)")
    temp_max_c: Optional[float] = Field(None, description="最高温度 (°C)")
    temp_min_c: Optional[float] = Field(None, description="最低温度 (°C)")
    wind_speed_kmh: float = Field(10.0, description="风速 (km/h)")
    precip_mm: Optional[float] = Field(0.0, description="降水量 (mm)")
    dewpoint_c: Optional[float] = Field(None, description="露点温度 (°C)")
    visibility_km: Optional[float] = Field(None, description="能见度 (km)")
    station_pressure_hpa: Optional[float] = Field(None, description="气压 (hPa)")


class PredictRequest(BaseModel):
    """预测请求"""

    city: str = Field(..., description="城市名称")
    weather: WeatherInput
    date: Optional[str] = Field(None, description="日期 (YYYY-MM-DD)")
    history_data: Optional[List[Dict[str, Any]]] = Field(None, description="历史数据 (用于GHM/GHS/CHM/CHS)")


class PredictResponse(BaseModel):
    """预测响应"""

    success: bool
    city: str
    date: str
    predicted_pm25: float
    aqi: int
    category: str
    category_chinese: str
    color: str
    health_advice: str


class CityInfo(BaseModel):
    """城市信息"""

    name: str
    lat: float
    lon: float
    state: Optional[str] = None


class CitiesResponse(BaseModel):
    """城市列表响应"""

    cities: List[CityInfo]


class HealthRecommendation(BaseModel):
    """健康建议"""

    message: str
    health_effects: str
    recommendation: str
    color: str
    icon: str


class ErrorResponse(BaseModel):
    """错误响应"""

    error: str
    detail: Optional[str] = None
