"""
AQI 计算器模块

根据污染物浓度计算 AQI 值
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union

from .breakpoints import get_breakpoints, get_category

from loguru import logger


class AQICalculator:
    """AQI计算器"""

    def __init__(self):
        """初始化计算器"""
        pass

    def calculate(self, concentration: float, pollutant: str) -> int:
        """
        计算单一污染物的AQI

        使用EPA线性插值公式:
        AQI = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low

        Args:
            concentration: 污染物浓度
            pollutant: 污染物名称 (pm25, pm10, o3, no2, so2, co)

        Returns:
            AQI值 (整数)
        """
        breakpoints = get_breakpoints(pollutant)

        if not breakpoints:
            logger.warning(f"未知污染物: {pollutant}")
            return 0

        # 找到对应的断点区间
        for c_low, c_high, i_low, i_high in breakpoints:
            if c_low <= concentration <= c_high:
                # 线性插值
                aqi = ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
                return int(round(aqi))

        # 超出最高断点
        if concentration > breakpoints[-1][1]:
            _, c_high, _, i_high = breakpoints[-1]
            # 线性外推
            c_low, _, i_low, _ = breakpoints[-2] if len(breakpoints) > 1 else (0, c_high, 0, i_high)
            aqi = ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
            return min(int(round(aqi)), 500)  # 最大500

        return 0

    def calculate_for_pollutants(self, concentrations: Dict[str, float]) -> Dict[str, int]:
        """
        计算多种污染物的AQI

        Args:
            concentrations: 污染物浓度字典 {pollutant: concentration}

        Returns:
            各污染物的AQI字典
        """
        return {
            pollutant: self.calculate(conc, pollutant) for pollutant, conc in concentrations.items() if pd.notna(conc)
        }

    def get_overall_aqi(self, concentrations: Dict[str, float]) -> tuple:
        """
        获取综合AQI（取最大值）

        Args:
            concentrations: 污染物浓度字典

        Returns:
            (overall_aqi, primary_pollutant)
        """
        aqi_values = self.calculate_for_pollutants(concentrations)

        if not aqi_values:
            return 0, None

        primary_pollutant = max(aqi_values, key=aqi_values.get)
        overall_aqi = aqi_values[primary_pollutant]

        return overall_aqi, primary_pollutant

    def calculate_series(self, series: pd.Series, pollutant: str) -> pd.Series:
        """
        计算Series的AQI

        Args:
            series: 浓度Series
            pollutant: 污染物名称

        Returns:
            AQI Series
        """
        return series.apply(lambda x: self.calculate(x, pollutant) if pd.notna(x) else np.nan)

    def calculate_dataframe(self, df: pd.DataFrame, pollutant_cols: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        计算DataFrame中各污染物的AQI

        Args:
            df: 数据DataFrame
            pollutant_cols: 污染物列名映射 {column_name: pollutant_type}

        Returns:
            包含AQI列的DataFrame
        """
        result = df.copy()

        if pollutant_cols is None:
            # 自动检测
            pollutant_cols = {col: col for col in df.columns if col in ["pm25", "pm10", "o3", "no2", "so2", "co"]}

        for col, pollutant in pollutant_cols.items():
            if col in df.columns:
                aqi_col = f"{col}_aqi"
                result[aqi_col] = self.calculate_series(df[col], pollutant)

        # 计算综合AQI
        aqi_cols = [f"{col}_aqi" for col in pollutant_cols.keys() if f"{col}_aqi" in result.columns]
        if aqi_cols:
            result["aqi"] = result[aqi_cols].max(axis=1)
            result["aqi_category"] = result["aqi"].apply(
                lambda x: get_category(int(x))["label"] if pd.notna(x) else "Unknown"
            )

        return result


def calculate_aqi(concentration: float, pollutant: str) -> int:
    """
    便捷函数：计算AQI

    Args:
        concentration: 浓度
        pollutant: 污染物名称

    Returns:
        AQI值
    """
    calculator = AQICalculator()
    return calculator.calculate(concentration, pollutant)


def get_health_advice(aqi: int) -> str:
    """
    根据AQI获取健康建议

    Args:
        aqi: AQI值

    Returns:
        健康建议
    """
    category = get_category(aqi)

    advice_map = {
        "Good": "空气质量良好，适合户外活动",
        "Moderate": "空气质量一般，敏感人群减少户外活动",
        "Unhealthy for Sensitive Groups": "敏感人群应避免户外活动",
        "Unhealthy": "所有人应减少户外活动",
        "Very Unhealthy": "避免户外活动，关闭门窗",
        "Hazardous": "紧急健康警告，留在室内",
    }

    return advice_map.get(category["label"], "未知")
