"""
推理预测模块

提供模型推理功能
"""

import os.path as osp
from typing import Dict, List, Optional, Union, Any

import pandas as pd
import numpy as np
import joblib

from ..data.processing.engineer import FeatureEngineer
from ..aqi import AQICalculator, get_health_advice
from ..training.production.trainer import load_production_model

from loguru import logger


class Predictor:
    """预测器"""

    def __init__(
        self,
        model_path: str,
        mode: Optional[str] = None,
    ):
        """
        初始化预测器

        Args:
            model_path: 模型路径
            mode: 预测模式，None则自动检测
        """
        self.model_path = model_path
        self.mode = mode

        # 加载模型
        self.model_info = load_production_model(osp.dirname(model_path))
        self.model = self.model_info["model"]
        self.model_name = self.model_info.get("model_name", "unknown")
        self.feature_names = self.model_info.get("feature_names", [])

        # 特征工程
        self.feature_engineer = FeatureEngineer()
        self.aqi_calculator = AQICalculator()

        # 自动检测模式
        if self.mode is None:
            self.mode = self._detect_mode()

        logger.info(f"预测器初始化: mode={self.mode}, model={self.model_name}")

    def _detect_mode(self) -> str:
        """自动检测预测模式"""
        config = self.model_info.get("config", {})
        mode = config.get("mode", "unknown")

        # 如果config中没有，根据特征数量推断
        if mode == "unknown" and self.feature_names:
            n_features = len(self.feature_names)
            # 简单启发式：特征少=GTS，特征多=GHS
            if n_features < 15:
                return "GTS"
            else:
                return "GHS"

        return mode

    def predict(
        self,
        weather_data: Dict[str, Any],
        historical_data: Optional[pd.DataFrame] = None,
        city: str = "Unknown",
    ) -> Dict[str, Any]:
        """
        预测污染物浓度

        Args:
            weather_data: 当日天气数据
            historical_data: 历史数据（用于GHM/GHS/CHM/CHS）
            city: 城市名称

        Returns:
            预测结果字典
        """
        # 构建输入DataFrame
        input_df = self._build_input_df(weather_data, historical_data, city)

        # 特征工程
        df_processed = self.feature_engineer.run(
            input_df,
            experiment_id=self._get_feature_experiment(),
            target_transform=None,  # 预测时不需要变换
        )

        # 准备特征
        X = self._prepare_features(df_processed)

        # 预测
        prediction = self.model.predict(X)

        # 逆变换（如果需要）
        prediction = self._inverse_transform(prediction)

        # 构建结果
        result = self._build_result(prediction, weather_data, city)

        return result

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        批量预测

        Args:
            df: 输入数据

        Returns:
            包含预测结果的DataFrame
        """
        # 特征工程
        df_processed = self.feature_engineer.run(
            df.copy(),
            experiment_id=self._get_feature_experiment(),
            target_transform=None,
        )

        # 准备特征
        X = self._prepare_features(df_processed)

        # 预测
        predictions = self.model.predict(X)

        # 逆变换
        predictions = self._inverse_transform(predictions)

        # 添加预测列
        result_df = df.copy()
        result_df["predicted_pm25"] = predictions

        # 计算AQI
        result_df = self.aqi_calculator.calculate_dataframe(result_df)

        return result_df

    def _build_input_df(
        self, weather_data: Dict[str, Any], historical_data: Optional[pd.DataFrame], city: str
    ) -> pd.DataFrame:
        """构建输入DataFrame"""
        from datetime import datetime

        # 基础数据
        data = {
            "date": [weather_data.get("date", datetime.now().strftime("%Y-%m-%d"))],
            "city_name": [city],
            **{k: [v] for k, v in weather_data.items() if k != "date"},
        }

        df = pd.DataFrame(data)

        # 如果有历史数据，合并
        if historical_data is not None and not historical_data.empty:
            # 添加历史滞后特征
            df = self._add_historical_features(df, historical_data)

        return df

    def _add_historical_features(self, df: pd.DataFrame, historical_data: pd.DataFrame) -> pd.DataFrame:
        """添加历史特征"""
        # 计算滞后特征
        if "pm25" in historical_data.columns:
            df["pm25_lag1"] = historical_data["pm25"].iloc[-1] if len(historical_data) > 0 else np.nan
            df["pm25_lag7"] = historical_data["pm25"].iloc[-7] if len(historical_data) >= 7 else np.nan

            # 滚动平均
            df["pm25_roll7_mean"] = historical_data["pm25"].tail(7).mean()
            df["pm25_roll30_mean"] = historical_data["pm25"].tail(30).mean() if len(historical_data) >= 30 else np.nan

        return df

    def _get_feature_experiment(self) -> str:
        """获取特征工程类型"""
        config = self.model_info.get("config", {})
        feature_config = config.get("feature_config", {})
        return feature_config.get("experiment_id", "full")

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备特征"""
        # 选择模型需要的特征
        available_cols = [c for c in self.feature_names if c in df.columns]

        if len(available_cols) != len(self.feature_names):
            missing = set(self.feature_names) - set(available_cols)
            logger.warning(f"缺失特征: {missing}")

        X = df[available_cols].copy()

        # 填充缺失值
        X = X.fillna(X.median())

        return X

    def _inverse_transform(self, predictions: np.ndarray) -> np.ndarray:
        """逆变换预测值"""
        config = self.model_info.get("config", {})
        target_transform = config.get("target_transform", "log")

        if target_transform == "log":
            return np.expm1(predictions)
        return predictions

    def _build_result(self, prediction: np.ndarray, weather_data: Dict[str, Any], city: str) -> Dict[str, Any]:
        """构建预测结果"""
        pm25 = float(prediction[0]) if isinstance(prediction, np.ndarray) else float(prediction)

        # 计算AQI
        aqi = self.aqi_calculator.calculate(pm25, "pm25")
        category = self.aqi_calculator.get_category(aqi)
        advice = get_health_advice(aqi)

        return {
            "city": city,
            "pm25": round(pm25, 2),
            "aqi": aqi,
            "category": category["label"],
            "category_chinese": category["chinese"],
            "color": category["color"],
            "health_advice": advice,
            "weather": weather_data,
        }


class MultiModelPredictor:
    """多模型预测器（用于同时加载多个模式）"""

    def __init__(self, models_dir: str):
        """
        初始化多模型预测器

        Args:
            models_dir: 模型目录
        """
        self.models_dir = models_dir
        self.predictors: Dict[str, Predictor] = {}

    def load_mode(self, mode: str, model_path: str) -> None:
        """加载指定模式的模型"""
        self.predictors[mode] = Predictor(model_path, mode=mode)
        logger.info(f"加载模型: {mode}")

    def predict(
        self,
        mode: str,
        weather_data: Dict[str, Any],
        historical_data: Optional[pd.DataFrame] = None,
        city: str = "Unknown",
    ) -> Dict[str, Any]:
        """
        使用指定模式预测

        Args:
            mode: 预测模式
            weather_data: 天气数据
            historical_data: 历史数据
            city: 城市名称

        Returns:
            预测结果
        """
        if mode not in self.predictors:
            raise ValueError(f"未加载模式: {mode}，可用模式: {list(self.predictors.keys())}")

        return self.predictors[mode].predict(weather_data, historical_data, city)

    def predict_auto(
        self,
        weather_data: Dict[str, Any],
        historical_data: Optional[pd.DataFrame] = None,
        city: str = "Unknown",
    ) -> Dict[str, Any]:
        """
        自动选择最佳模式预测

        Args:
            weather_data: 天气数据
            historical_data: 历史数据
            city: 城市名称

        Returns:
            预测结果
        """
        # 根据历史数据可用性选择模式
        has_history = historical_data is not None and len(historical_data) >= 7

        if has_history and "GHS" in self.predictors:
            return self.predict("GHS", weather_data, historical_data, city)
        elif "GTS" in self.predictors:
            return self.predict("GTS", weather_data, None, city)
        else:
            # 使用第一个可用模式
            mode = list(self.predictors.keys())[0]
            return self.predict(mode, weather_data, historical_data, city)
