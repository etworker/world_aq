"""
特征变换器模块

提供各种特征工程变换器
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from loguru import logger


class BaseTransformer(ABC):
    """基础变换器"""

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """执行变换"""
        pass

    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """获取生成的特征名列表"""
        pass


class TemporalTransformer(BaseTransformer):
    """时间特征变换器"""

    def __init__(self, date_col: str = "date"):
        self.date_col = date_col
        self._feature_names: List[str] = []

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加时间特征"""
        df = df.copy()
        df[self.date_col] = pd.to_datetime(df[self.date_col])

        # 年中第几天（循环sin/cos编码）
        day_of_year = df[self.date_col].dt.dayofyear
        df["day_sin"] = np.sin(2 * np.pi * day_of_year / 365.0)
        df["day_cos"] = np.cos(2 * np.pi * day_of_year / 365.0)

        # 月份（循环sin/cos编码）
        df["month"] = df[self.date_col].dt.month
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)

        # 周特征
        df["weekday"] = df[self.date_col].dt.weekday
        df["is_weekend"] = df["weekday"].isin([5, 6]).astype(int)

        # 季度
        df["quarter"] = df[self.date_col].dt.quarter

        self._feature_names = [
            "day_sin",
            "day_cos",
            "month_sin",
            "month_cos",
            "month",
            "weekday",
            "is_weekend",
            "quarter",
        ]

        return df

    def get_feature_names(self) -> List[str]:
        return self._feature_names


class LagFeatureTransformer(BaseTransformer):
    """滞后特征变换器"""

    def __init__(
        self,
        target_col: str = "pm25",
        lag_days: List[int] = None,
        group_col: str = "city_name",
    ):
        self.target_col = target_col
        self.lag_days = lag_days or [1, 7]
        self.group_col = group_col
        self._feature_names: List[str] = []

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加滞后特征"""
        df = df.copy()
        df = df.sort_values([self.group_col, "date"])

        for lag in self.lag_days:
            col_name = f"{self.target_col}_lag{lag}"
            df[col_name] = df.groupby(self.group_col)[self.target_col].shift(lag)
            self._feature_names.append(col_name)

        return df

    def get_feature_names(self) -> List[str]:
        return self._feature_names


class RollingFeatureTransformer(BaseTransformer):
    """滚动特征变换器"""

    def __init__(
        self,
        target_col: str = "pm25",
        windows: List[int] = None,
        group_col: str = "city_name",
    ):
        self.target_col = target_col
        self.windows = windows or [7, 30]
        self.group_col = group_col
        self._feature_names: List[str] = []

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加滚动特征"""
        df = df.copy()
        df = df.sort_values([self.group_col, "date"])

        for window in self.windows:
            # 滚动均值
            mean_col = f"{self.target_col}_roll{window}_mean"
            df[mean_col] = df.groupby(self.group_col)[self.target_col].transform(
                lambda x: x.shift(1).rolling(window=window, min_periods=1).mean()
            )
            self._feature_names.append(mean_col)

            # 滚动标准差
            std_col = f"{self.target_col}_roll{window}_std"
            df[std_col] = df.groupby(self.group_col)[self.target_col].transform(
                lambda x: x.shift(1).rolling(window=window, min_periods=1).std()
            )
            self._feature_names.append(std_col)

        return df

    def get_feature_names(self) -> List[str]:
        return self._feature_names


class TemperatureFeatureTransformer(BaseTransformer):
    """温度特征变换器"""

    def __init__(self, temp_col: str = "temp_avg_c"):
        self.temp_col = temp_col
        self._feature_names: List[str] = []

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加温度特征"""
        df = df.copy()

        if self.temp_col not in df.columns:
            logger.warning(f"温度列 {self.temp_col} 不存在")
            return df

        # U型关系的二次项
        df["temp_avg_sq"] = df[self.temp_col] ** 2
        self._feature_names.append("temp_avg_sq")

        # 温度分类
        df["temp_category"] = pd.cut(
            df[self.temp_col], bins=[-np.inf, 5, 15, 25, np.inf], labels=["cold", "cool", "warm", "hot"]
        )

        # 季节指示器（如果month列存在）
        if "month" in df.columns:
            df["is_winter"] = df["month"].isin([11, 12, 1, 2]).astype(int)
            df["is_summer_ozone"] = df["month"].isin([6, 7, 8]).astype(int)
            self._feature_names.extend(["is_winter", "is_summer_ozone"])

        return df

    def get_feature_names(self) -> List[str]:
        return self._feature_names


class TargetTransformer(BaseTransformer):
    """目标变量变换器"""

    def __init__(self, target_col: str = "pm25", transform: str = "log"):
        self.target_col = target_col
        self.transform_type = transform  # 重命名属性，避免覆盖方法
        self._feature_names: List[str] = []

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """变换目标变量"""
        df = df.copy()

        if self.target_col not in df.columns:
            return df

        if self.transform_type == "log":
            df[f"{self.target_col}_log"] = np.log1p(df[self.target_col])
            self._feature_names.append(f"{self.target_col}_log")
        elif self.transform_type == "boxcox":
            from scipy import stats

            df[f"{self.target_col}_boxcox"], _ = stats.boxcox(df[self.target_col].clip(lower=0.1))
            self._feature_names.append(f"{self.target_col}_boxcox")

        return df

    def inverse_transform(self, values: np.ndarray) -> np.ndarray:
        """逆变换"""
        if self.transform_type == "log":
            return np.expm1(values)
        return values

    def get_feature_names(self) -> List[str]:
        return self._feature_names


class WeatherInteractionTransformer(BaseTransformer):
    """天气交互特征变换器"""

    def __init__(self):
        self._feature_names: List[str] = []

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加天气交互特征"""
        df = df.copy()

        # 风速×能见度（扩散条件）
        if "wind_speed_kmh" in df.columns and "visibility_km" in df.columns:
            df["wind_x_visibility"] = df["wind_speed_kmh"] * df["visibility_km"]
            self._feature_names.append("wind_x_visibility")

        # 温度×湿度（舒适度相关）
        if "temp_avg_c" in df.columns and "dewpoint_c" in df.columns:
            df["temp_minus_dewpoint"] = df["temp_avg_c"] - df["dewpoint_c"]
            self._feature_names.append("temp_minus_dewpoint")

        # 气压变化（如果存在前一天数据）
        if "station_pressure_hpa" in df.columns:
            df["pressure_change"] = df.groupby("city_name")["station_pressure_hpa"].diff()
            self._feature_names.append("pressure_change")

        return df

    def get_feature_names(self) -> List[str]:
        return self._feature_names
