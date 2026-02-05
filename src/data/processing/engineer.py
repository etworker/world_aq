"""
特征工程主模块 - 严格遵循旧版实验的19个核心特征

基于验证的EDA结论：
- 关键相关性：visibility_km (-0.52)、wind_speed_kmh (-0.41) 与 PM2.5 相关
- 滞后特征：Lag-1 (0.56) 最重要，其次是 Lag-7 (0.12)
- 7天滚动均值：相关性 0.62
- 季节模式：北京冬季高，洛杉矶夏季O3峰值
- 目标变换：Log(1+x) 将偏度从 3.81 降至 0.87

核心特征列表 (19个):
1. 基础气象特征 (8个): temp_avg_c, temp_max_c, temp_min_c, dewpoint_c, 
                         precip_mm, wind_speed_kmh, visibility_km, station_pressure_hpa
2. 时间特征 (5个): day_of_year, month, day_of_week, is_weekend, season
3. 滞后特征 (2个): pm25_lag1, pm25_lag7
4. 滚动特征 (2个): pm25_roll7_mean, pm25_roll30_mean
5. 目标变量 (1个): pm25
6. 分组列 (1个): city_name
"""

import pandas as pd
import numpy as np
from typing import List, Optional

from ...config import WEATHER_COLS, TARGET_COL
from loguru import logger


class FeatureEngineer:
    """
    空气质量预测特征工程流水线 - 精简版

    严格遵循旧版实验验证的19个核心特征，不引入未经验证的特征。
    """

    # 旧版实验验证的核心特征（19个）
    CORE_WEATHER_FEATURES = [
        "temp_avg_c", "temp_max_c", "temp_min_c", "dewpoint_c",
        "precip_mm", "wind_speed_kmh", "visibility_km", "station_pressure_hpa"
    ]

    CORE_TIME_FEATURES = [
        "day_sin", "day_cos", "month_sin", "month_cos",
        "day_of_week", "is_weekend", "season"
    ]

    # 基础气象滞后特征（不依赖目标变量）
    CORE_METEO_LAG_FEATURES = [
        "temp_avg_c_lag1", "wind_speed_kmh_lag1", "visibility_km_lag1"
    ]

    # 基础滚动窗口大小
    ROLL_WINDOWS = [7, 14, 30]
    ROLL_STD_WINDOWS = [7, 14]
    LAG_DAYS = [1, 2, 3, 7]

    def __init__(self, target_col: str = TARGET_COL, additional_targets: Optional[List[str]] = None):
        self.target_col = target_col
        self.additional_targets = additional_targets or []  # 额外的目标列，为其生成滞后和滚动特征
        # 所有需要生成特征的目标列
        self.all_target_cols = [target_col] + self.additional_targets
    
    def _get_lag_features(self, target_col: str = None) -> List[str]:
        """获取滞后特征列表（基于指定的目标变量）"""
        if target_col is None:
            target_col = self.target_col
        return [f"{target_col}_lag{lag}" for lag in self.LAG_DAYS] + self.CORE_METEO_LAG_FEATURES
    
    def _get_all_lag_features(self) -> List[str]:
        """获取所有目标变量的滞后特征列表"""
        lag_features = []
        for target in self.all_target_cols:
            # 为每个目标生成滞后特征（不重复添加气象滞后特征）
            lag_features += [f"{target}_lag{lag}" for lag in self.LAG_DAYS]
        # 只添加一次气象滞后特征
        lag_features += self.CORE_METEO_LAG_FEATURES
        return lag_features
    
    def _get_roll_features(self, target_col: str = None) -> List[str]:
        """获取滚动特征列表（基于指定的目标变量）"""
        if target_col is None:
            target_col = self.target_col
        mean_features = [f"{target_col}_roll{w}_mean" for w in self.ROLL_WINDOWS]
        std_features = [f"{target_col}_roll{w}_std" for w in self.ROLL_STD_WINDOWS]
        return mean_features + std_features
    
    def _get_all_roll_features(self) -> List[str]:
        """获取所有目标变量的滚动特征列表"""
        roll_features = []
        for target in self.all_target_cols:
            roll_features += self._get_roll_features(target)
        return roll_features

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗与预处理

        处理内容：
        - 数值类型转换
        - 异常值裁剪（基于领域知识）
        - 气象数据缺失值填充
        """
        df = df.copy()

        # 确保日期列是datetime类型
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

        # 确保气象列是数值类型
        for col in WEATHER_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 气象数据异常值裁剪
        if "temp_avg_c" in df.columns:
            df["temp_avg_c"] = df["temp_avg_c"].clip(lower=-30, upper=45)
        if "temp_max_c" in df.columns:
            df["temp_max_c"] = df["temp_max_c"].clip(lower=-25, upper=50)
        if "temp_min_c" in df.columns:
            df["temp_min_c"] = df["temp_min_c"].clip(lower=-35, upper=40)

        # PM2.5裁剪（EPA标准：0-500 μg/m³）
        if self.target_col in df.columns:
            df[self.target_col] = df[self.target_col].clip(lower=0, upper=500)

        # 按城市填充气象数据
        if "city_name" in df.columns:
            for col in WEATHER_COLS:
                if col in df.columns:
                    df[col] = df.groupby("city_name")[col].transform(
                        lambda x: x.interpolate(method="linear").bfill().ffill()
                    )

        return df

    def add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加时间特征（严格旧版实现）

        旧版特征（使用循环编码）：
        - day_sin/cos: 年中第几天的循环编码
        - month_sin/cos: 月份的循环编码（捕捉季节模式）
        - weekday: 星期几 (0=周一)
        - is_weekend: 是否周末
        - season: 季节 (0=冬季, 1=春季, 2=夏季, 3=秋季)
        """
        df = df.copy()

        if "date" not in df.columns:
            return df

        df["date"] = pd.to_datetime(df["date"])

        # 循环编码（关键修复！）
        day_of_year = df["date"].dt.dayofyear
        df["day_sin"] = np.sin(2 * np.pi * day_of_year / 365.0)
        df["day_cos"] = np.cos(2 * np.pi * day_of_year / 365.0)

        df["month"] = df["date"].dt.month
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)

        df["day_of_week"] = df["date"].dt.weekday
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        df["season"] = df["date"].dt.month % 12 // 3

        # 保留旧版核心时间列用于兼容性
        df["day_of_year"] = day_of_year

        return df

    def add_lag_features(self, df: pd.DataFrame, group_col: str = "city_name") -> pd.DataFrame:
        """
        添加滞后特征（支持多个目标变量）

        为所有目标变量生成：
        - {target}_lag{1,2,3,7}: 滞后值
        - 气象滞后: temp_avg_c, wind_speed_kmh, visibility_km (仅一次)
        """
        df = df.copy()

        df = df.sort_values(by=[group_col, "date"])

        # 为所有目标变量生成滞后特征
        for target in self.all_target_cols:
            if target not in df.columns:
                continue
            for lag in self.LAG_DAYS:
                df[f"{target}_lag{lag}"] = df.groupby(group_col)[target].shift(lag)

        # 关键气象特征滞后（仅生成一次）
        for col in ["temp_avg_c", "wind_speed_kmh", "visibility_km"]:
            if col in df.columns:
                df[f"{col}_lag1"] = df.groupby(group_col)[col].shift(1)

        return df

    def add_rolling_features(self, df: pd.DataFrame, group_col: str = "city_name") -> pd.DataFrame:
        """
        添加滚动特征（支持多个目标变量）

        为所有目标变量生成：
        - {target}_roll{7,14,30}_mean: 滚动均值
        - {target}_roll{7,14}_std: 滚动标准差
        """
        df = df.copy()

        df = df.sort_values(by=[group_col, "date"])

        # 为所有目标变量生成滚动特征
        for target in self.all_target_cols:
            if target not in df.columns:
                continue

            shifted = df.groupby(group_col)[target].shift(1)

            # 多窗口滚动均值
            for window in self.ROLL_WINDOWS:
                df[f"{target}_roll{window}_mean"] = shifted.transform(
                    lambda x: x.rolling(window=window, min_periods=1).mean()
                )

            # 滚动标准差（波动性）
            for window in self.ROLL_STD_WINDOWS:
                df[f"{target}_roll{window}_std"] = shifted.transform(
                    lambda x: x.rolling(window=window, min_periods=1).std()
                )

        return df

    def add_target_transformation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        目标变量变换（严格旧版实现）

        旧版使用 Log(1+x) 变换，将偏度从 3.81 降至 0.87
        """
        df = df.copy()

        if self.target_col in df.columns:
            df[f"{self.target_col}_log"] = np.log1p(df[self.target_col])

        return df

    def add_future_target(self, df: pd.DataFrame, forecast_horizon: int = 1, group_col: str = "city_name") -> pd.DataFrame:
        """
        添加未来目标变量 (T+1预测)

        Args:
            df: 输入数据
            forecast_horizon: 预测步长 (1=明天, 7=下周)
            group_col: 分组列

        Returns:
            添加未来目标的DataFrame
        """
        df = df.copy()

        if self.target_col not in df.columns:
            return df

        df = df.sort_values(by=[group_col, "date"])

        # 创建未来目标 (shift -1 表示明天的值)
        future_col = f"{self.target_col}_future_{forecast_horizon}d"
        df[future_col] = df.groupby(group_col)[self.target_col].shift(-forecast_horizon)

        logger.info(f"添加未来目标: {future_col}, 有效样本数: {df[future_col].notna().sum()}")

        return df

    def add_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加关键气象交互特征（旧版核心特征）

        基于EDA分析：
        - visibility_inverse: 最强预测因子（相关性-0.52）
        - wind_pm25_product: 污染扩散指标
        - temp_dewpoint_diff: 湿度代理
        """
        df = df.copy()

        # 能见度倒数（最强单特征）
        if "visibility_km" in df.columns:
            df["visibility_inverse"] = 1 / (df["visibility_km"] + 1)

        # 风速-目标变量交互（污染扩散）
        if "wind_speed_kmh" in df.columns and self.target_col in df.columns:
            df[f"wind_{self.target_col}_product"] = df["wind_speed_kmh"] * df[self.target_col]

        # 温度-露点差（湿度代理）
        if "temp_avg_c" in df.columns and "dewpoint_c" in df.columns:
            df["temp_dewpoint_diff"] = df["temp_avg_c"] - df["dewpoint_c"]

        # 降水指示器
        if "precip_mm" in df.columns:
            df["has_precip"] = (df["precip_mm"] > 0).astype(int)

        return df

    def run(
        self,
        df: pd.DataFrame,
        experiment_id: str = "full",
        target_transform: Optional[str] = "log",
        forecast_horizon: int = 0,  # 0=同期预测, 1=T+1预测
    ) -> pd.DataFrame:
        """
        执行特征工程流水线（严格旧版实现）

        Args:
            df: 输入数据
            experiment_id: 实验类型
                - "weather": 仅天气特征（8个基础气象特征）
                - "temporal": 天气 + 时间特征（13个）
                - "lag": 天气 + 时间 + 滞后特征（15个）
                - "full": 完整特征工程（19个核心特征）
            target_transform: 目标变量变换 ('log', None)

        Returns:
            特征工程后的 DataFrame
        """
        logger.info(f"执行特征工程: experiment_id={experiment_id}")

        # 步骤1: 预处理
        df = self.preprocess(df)

        # 步骤2: 时间特征（所有实验都包含）
        df = self.add_temporal_features(df)

        if experiment_id == "weather":
            # 仅保留基础气象特征 + 时间特征
            cols = ["date", "city_name", self.target_col] + \
                   self.CORE_WEATHER_FEATURES + self.CORE_TIME_FEATURES
            # 添加额外目标列
            cols.extend([t for t in self.additional_targets if t in df.columns])
            cols = [c for c in cols if c in df.columns]
            return df[cols].dropna(subset=[self.target_col])

        if experiment_id == "temporal":
            # 仅保留基础气象 + 时间特征
            cols = ["date", "city_name", self.target_col] + \
                   self.CORE_WEATHER_FEATURES + self.CORE_TIME_FEATURES
            # 添加额外目标列
            cols.extend([t for t in self.additional_targets if t in df.columns])
            cols = [c for c in cols if c in df.columns]
            return df[cols].dropna(subset=[self.target_col])

        # 步骤3: 滞后特征（使用动态目标变量名）
        if experiment_id in ["lag", "full"]:
            df = self.add_lag_features(df)

            # 步骤4: 滚动特征（使用动态目标变量名）
            df = self.add_rolling_features(df)

        # 步骤4b: 关键交互特征（旧版核心）
        if experiment_id == "full":
            df = self.add_interaction_features(df)

        # 步骤5: 目标变量变换
        if target_transform == "log" and self.target_col in df.columns:
            df = self.add_target_transformation(df)

        # 步骤5b: T+1预测 - 添加未来目标
        if forecast_horizon > 0:
            df = self.add_future_target(df, forecast_horizon=forecast_horizon)
            # 对于未来预测，目标列改为未来值
            future_target_col = f"{self.target_col}_future_{forecast_horizon}d"
            if future_target_col in df.columns:
                # 重命名未来目标为当前目标列名
                df = df.drop(columns=[self.target_col])
                df = df.rename(columns={future_target_col: self.target_col})
                if target_transform == "log":
                    df[f"{self.target_col}_log"] = np.log1p(df[self.target_col])
                logger.info(f"T+{forecast_horizon}预测: 目标列改为{self.target_col}")

        # 只保留核心特征列
        # 支持多个目标列：主目标 + 额外目标
        core_cols = ["date", "city_name", self.target_col]
        
        # 添加额外的目标列（保留但不为其生成特征）
        for additional_target in self.additional_targets:
            if additional_target in df.columns:
                core_cols.append(additional_target)
                if target_transform == "log" and f"{additional_target}_log" in df.columns:
                    core_cols.append(f"{additional_target}_log")
        
        if target_transform == "log":
            core_cols.append(f"{self.target_col}_log")

        feature_cols = self.CORE_WEATHER_FEATURES + self.CORE_TIME_FEATURES
        if experiment_id in ["lag", "full"]:
            # 为所有目标变量生成滞后和滚动特征
            feature_cols += self._get_all_lag_features() + self._get_all_roll_features()

        # 添加交互特征列
        interaction_cols = ["visibility_inverse", f"wind_{self.target_col}_product", "temp_dewpoint_diff", "has_precip"]
        if experiment_id == "full":
            feature_cols += [c for c in interaction_cols if c in df.columns]

        final_cols = [c for c in core_cols + feature_cols if c in df.columns]

        logger.info(f"特征工程完成: {len(df)} 行, {len(final_cols)} 列")
        return df[final_cols].dropna(subset=[self.target_col])

    def get_feature_columns(self, df: pd.DataFrame, exclude_cols: Optional[List[str]] = None) -> List[str]:
        """
        获取特征列列表（支持任意目标变量）

        Args:
            df: 数据
            exclude_cols: 要排除的列

        Returns:
            特征列列表
        """
        if exclude_cols is None:
            exclude_cols = []

        # 动态生成特征列表（基于当前目标变量）
        all_features = (
            self.CORE_WEATHER_FEATURES +
            self.CORE_TIME_FEATURES +
            self._get_lag_features() +
            self._get_roll_features()
        )

        # 默认排除列（包含当前目标变量及其变换）
        default_exclude = [
            "date", "city_name", "year", "data_source",
            self.target_col, f"{self.target_col}_log"
        ]

        all_exclude = set(default_exclude + exclude_cols)

        # 只返回存在于df中的核心特征
        feature_cols = [c for c in all_features if c in df.columns and c not in all_exclude]

        return feature_cols
