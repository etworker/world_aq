"""
多输出训练器模块

支持同时预测多个污染物(PM2.5 + O3)
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any

from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet

from ...core import ModelResult
from ...core.registry import ModelRegistry
from .metrics import calculate_metrics
from .base_trainer import BaseTrainer

from loguru import logger


class MultiOutputTrainer:
    """多输出训练器 - 同时预测多个污染物"""

    def __init__(
        self,
        target_cols: List[str] = None,
        target_transform: Optional[str] = "log",
    ):
        """
        初始化多输出训练器

        Args:
            target_cols: 目标变量列名列表，如 ["pm25", "o3"]
            target_transform: 目标变量变换类型
        """
        self.target_cols = target_cols or ["pm25", "o3"]
        self.target_transform = target_transform

        # 为每个目标创建单独的训练器
        self.trainers: Dict[str, BaseTrainer] = {}
        for col in self.target_cols:
            self.trainers[col] = BaseTrainer(
                target_col=col,
                target_transform=target_transform,
            )

    def prepare_features_multi(
        self,
        df: pd.DataFrame,
        is_train: bool = True,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
        """
        准备多输出特征

        Returns:
            (X, Y, feature_names) - Y是多列DataFrame
        """
        # 使用第一个目标的训练器准备特征（特征相同）
        first_trainer = list(self.trainers.values())[0]
        X, _, feature_names = first_trainer.prepare_features(df, is_train=is_train)

        # 准备多个目标
        Y = pd.DataFrame()
        for col in self.target_cols:
            # 检查列是否存在
            if col not in df.columns:
                logger.warning(f"目标列 '{col}' 不在数据框中，跳过此列")
                continue
                
            if self.target_transform == "log":
                y_col = f"{col}_log"
                if y_col in df.columns:
                    Y[col] = df[y_col].copy()
                else:
                    Y[col] = np.log1p(df[col]).copy()
            else:
                Y[col] = df[col].copy()

        # 检查是否有有效的目标列
        if Y.empty:
            raise ValueError(f"没有找到任何有效的目标列。期望: {self.target_cols}, 实际: {df.columns.tolist()}")

        # 删除任何有缺失目标的行
        valid_idx = Y.notna().all(axis=1)
        X = X[valid_idx]
        Y = Y[valid_idx]

        return X, Y, feature_names

    def train_model(
        self,
        model_name: str,
        X_train: pd.DataFrame,
        Y_train: pd.DataFrame,
        X_val: pd.DataFrame,
        Y_val: pd.DataFrame,
        X_test: pd.DataFrame,
        Y_test: pd.DataFrame,
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, ModelResult]:
        """
        训练多输出模型

        策略:
        1. 对于 AutoGluon，为每个目标单独训练（不支持真正的多输出）
        2. 对于树模型(RF/GB)，使用MultiOutputRegressor包装
        3. 对于线性模型，为每个目标单独训练

        Returns:
            Dict[str, ModelResult] - 每个目标的结果
        """
        start_time = time.time()
        hyperparams = hyperparams or {}

        logger.info(f"训练多输出模型: {model_name}, 目标: {self.target_cols}")

        # 训练模型
        if model_name == "AutoGluon":
            # AutoGluon 不支持多输出，为每个目标单独训练
            try:
                from .autogluon_trainer import AutoGluonTrainer
            except ImportError:
                raise ImportError("AutoGluon 未安装，请运行: pip install autogluon")

            models = []
            y_val_pred = np.zeros_like(Y_val.values)
            y_test_pred = np.zeros_like(Y_test.values)
            results = {}

            for i, col in enumerate(self.target_cols):
                logger.info(f"  训练 AutoGluon 模型: {col}")
                
                ag_trainer = AutoGluonTrainer(
                    target_col=col,
                    target_transform=self.target_transform,
                    time_limit=hyperparams.get("time_limit", 300) if hyperparams else 300,
                    presets=hyperparams.get("presets", "medium_quality") if hyperparams else "medium_quality",
                    eval_metric=hyperparams.get("eval_metric", "rmse") if hyperparams else "rmse",
                )
                
                result = ag_trainer.train(
                    X_train=X_train,
                    y_train=Y_train.iloc[:, i],
                    X_val=X_val,
                    y_val=Y_val.iloc[:, i],
                    X_test=X_test,
                    y_test=Y_test.iloc[:, i],
                )
                
                models.append(result.model)
                y_val_pred[:, i] = result.model.predict(X_val)
                y_test_pred[:, i] = result.model.predict(X_test)
                
                results[col] = result

            return results

        elif model_name in ["RandomForest", "GradientBoosting"]:
            # 使用MultiOutputRegressor包装
            model_class = ModelRegistry.get_model_class(model_name)
            base_model = model_class(**hyperparams)
            model = MultiOutputRegressor(base_model, n_jobs=-1)
            model.fit(X_train, Y_train)

            # 预测
            y_val_pred = model.predict(X_val)
            y_test_pred = model.predict(X_test)

        else:
            # 线性模型：为每个目标单独训练
            model_class = ModelRegistry.get_model_class(model_name)
            models = []
            y_val_pred = np.zeros_like(Y_val.values)
            y_test_pred = np.zeros_like(Y_test.values)

            for i, col in enumerate(self.target_cols):
                model = model_class(**hyperparams)
                model.fit(X_train, Y_train.iloc[:, i])
                models.append(model)

                y_val_pred[:, i] = model.predict(X_val)
                y_test_pred[:, i] = model.predict(X_test)

            model = models  # 保存模型列表

        training_time = time.time() - start_time

        # 为每个目标计算指标
        results = {}
        for i, col in enumerate(self.target_cols):
            # 反变换
            if self.target_transform == "log":
                y_val_true = np.expm1(Y_val.iloc[:, i])
                y_test_true = np.expm1(Y_test.iloc[:, i])
                y_val_pred_col = np.expm1(y_val_pred[:, i])
                y_test_pred_col = np.expm1(y_test_pred[:, i])
            else:
                y_val_true = Y_val.iloc[:, i]
                y_test_true = Y_test.iloc[:, i]
                y_val_pred_col = y_val_pred[:, i]
                y_test_pred_col = y_test_pred[:, i]

            val_metrics = calculate_metrics(y_val_true, y_val_pred_col)
            test_metrics = calculate_metrics(y_test_true, y_test_pred_col)

            results[col] = ModelResult(
                model_name=model_name,
                model=model,
                metrics=test_metrics,
                val_metrics=val_metrics,
                training_time=training_time / len(self.target_cols),
                hyperparams=hyperparams,
            )

        return results


class CitySpecificTrainer:
    """城市级训练器 - 为每个城市单独训练模型"""

    def __init__(
        self,
        target_col: str = "pm25",
        target_transform: Optional[str] = "log",
    ):
        self.target_col = target_col
        self.target_transform = target_transform
        self.city_models: Dict[str, Any] = {}

    def train_city_models(
        self,
        df: pd.DataFrame,
        cities: List[str],
        algorithm: str = "GradientBoosting",
    ) -> Dict[str, ModelResult]:
        """
        为每个城市单独训练模型

        Args:
            df: 完整数据
            cities: 城市列表
            algorithm: 算法名称

        Returns:
            Dict[str, ModelResult] - 每个城市的结果
        """
        results = {}

        for city in cities:
            logger.info(f"训练城市模型: {city}")

            # 筛选城市数据
            city_df = df[df["city_name"] == city].copy()
            if len(city_df) < 100:
                logger.warning(f"{city} 数据不足: {len(city_df)} 条，跳过")
                continue

            # 检查目标变量
            if city_df[self.target_col].notna().sum() < 100:
                logger.warning(f"{city} 目标变量缺失过多，跳过")
                continue

            # 创建训练器
            trainer = BaseTrainer(
                target_col=self.target_col,
                target_transform=self.target_transform,
            )

            # 准备数据
            from ...data.processing.engineer import FeatureEngineer
            from ...training.core.cross_validation import TimeSeriesDataSplitter

            # 特征工程
            fe = FeatureEngineer(target_col=self.target_col)
            city_df = fe.run(city_df.copy(), experiment_id="full", target_transform=self.target_transform)

            # 数据分割
            splitter = TimeSeriesDataSplitter(test_size=0.15, val_size=0.15)
            train_df, val_df, test_df = splitter.split(city_df)

            if len(train_df) < 50:
                logger.warning(f"{city} 训练集太小，跳过")
                continue

            # 准备特征
            X_train, y_train, _ = trainer.prepare_features(train_df, is_train=True)
            X_val, y_val, _ = trainer.prepare_features(val_df, is_train=False)
            X_test, y_test, _ = trainer.prepare_features(test_df, is_train=False)

            if len(X_train) == 0 or len(X_val) == 0 or len(X_test) == 0:
                logger.warning(f"{city} 数据准备失败，跳过")
                continue

            # 训练模型
            result = trainer.train_model(
                model_name=algorithm,
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                X_test=X_test,
                y_test=y_test,
            )

            results[city] = result
            self.city_models[city] = result.model

            logger.info(f"{city} 训练完成: val_rmse={result.val_metrics.get('rmse', 0):.4f}")

        return results
