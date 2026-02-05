"""
基础训练器模块

提供统一的模型训练接口
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any

from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

from ...core import ModelResult
from ...core.registry import ModelRegistry
from .metrics import calculate_metrics

from loguru import logger


class BaseTrainer:
    """基础训练器"""

    def __init__(
        self,
        target_col: str = "pm25",
        target_transform: Optional[str] = "log",
        encode_categorical: bool = True,
        impute_strategy: str = "median",
    ):
        """
        初始化基础训练器

        Args:
            target_col: 目标变量列名
            target_transform: 目标变量变换类型
            encode_categorical: 是否编码分类变量
            impute_strategy: 缺失值填充策略
        """
        self.target_col = target_col
        self.target_transform = target_transform
        self.encode_categorical = encode_categorical
        self.impute_strategy = impute_strategy

        self.encoder: Optional[OneHotEncoder] = None
        self.imputer = SimpleImputer(strategy=impute_strategy)
        self.categorical_cols: List[str] = []
        self.valid_feature_cols: List[str] = []

    def prepare_features(
        self,
        df: pd.DataFrame,
        is_train: bool = True,
        exclude_cols: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """
        准备特征

        Args:
            df: 输入数据
            is_train: 是否为训练模式
            exclude_cols: 要排除的列

        Returns:
            (X, y, feature_names)
        """
        # 确定目标变量
        if self.target_transform == "log":
            y_col = f"{self.target_col}_log"
            if y_col in df.columns:
                y = df[y_col].copy()
            else:
                y = np.log1p(df[self.target_col]).copy()
        else:
            y = df[self.target_col].copy()

        # 默认排除列
        default_exclude = [
            "date",
            "city_name",
            "year",
            "data_source",
            "weather_type",
            "visibility_level",
            "wind_level",
            "temp_category",
            "week_position",
            "aqi_category",
            "pollution_level",
            "city_season",
            "quality_level",
            # 标识和地理列（不应作为预测特征）
            "station_id",
            "lat",
            "lon",
            "elev_m",
            "station_count",
            "city_lat",
            "city_lon",
            f"{self.target_col}_log",
            f"{self.target_col}_boxcox",
            self.target_col,
        ]

        if exclude_cols:
            default_exclude.extend(exclude_cols)

        working_df = df.copy()

        # 编码分类变量
        if self.encode_categorical:
            if is_train:
                self.categorical_cols = [
                    c
                    for c in working_df.columns
                    if c not in default_exclude + ["city_name"]
                    and (working_df[c].dtype == "object" or str(working_df[c].dtype).startswith("category"))
                ]
                if self.categorical_cols:
                    self.encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
                    encoded = self.encoder.fit_transform(working_df[self.categorical_cols])
                    names = self.encoder.get_feature_names_out(self.categorical_cols)
                    working_df = working_df.drop(columns=self.categorical_cols)
                    working_df[names] = encoded
            else:
                if self.encoder and self.categorical_cols:
                    cat_in_df = [c for c in self.categorical_cols if c in working_df.columns]
                    if cat_in_df:
                        encoded = self.encoder.transform(working_df[cat_in_df])
                        names = self.encoder.get_feature_names_out(cat_in_df)
                        working_df = working_df.drop(columns=cat_in_df)
                        working_df[names] = encoded

        # 选择数值特征列
        feat_cols = [
            c
            for c in working_df.columns
            if c not in default_exclude
            and not c.startswith("weather_")
            and not c.startswith("aqi_")
            and working_df[c].dtype in ["int64", "float64", "int32", "float32"]
        ]

        if is_train:
            self.valid_feature_cols = [c for c in feat_cols if not working_df[c].isna().all()]

        X = working_df[self.valid_feature_cols].copy()

        # 填充缺失值
        if is_train:
            X_imputed = self.imputer.fit_transform(X)
        else:
            X_imputed = self.imputer.transform(X)

        X_final = pd.DataFrame(X_imputed, columns=self.valid_feature_cols, index=df.index)

        # 删除目标变量为NaN的样本
        valid_mask = y.notna()
        if not valid_mask.all():
            X_final = X_final[valid_mask]
            y = y[valid_mask]

        return X_final, y, self.valid_feature_cols

    def train_model(
        self,
        model_name: str,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> ModelResult:
        """
        训练单个模型

        Args:
            model_name: 模型名称
            X_train: 训练特征
            y_train: 训练目标
            X_val: 验证特征
            y_val: 验证目标
            X_test: 测试特征
            y_test: 测试目标
            hyperparams: 超参数

        Returns:
            ModelResult
        """
        start_time = time.time()

        # 创建模型
        try:
            model = ModelRegistry.create_model(model_name, **(hyperparams or {}))
        except KeyError:
            logger.error(f"未知模型: {model_name}")
            raise

        # 训练
        model.fit(X_train, y_train)

        # 预测
        y_val_pred = model.predict(X_val)
        y_test_pred = model.predict(X_test)

        # 计算指标
        val_metrics = calculate_metrics(y_val.values, y_val_pred, self.target_transform)
        test_metrics = calculate_metrics(y_test.values, y_test_pred, self.target_transform)

        # 特征重要性
        importance = self._get_feature_importance(model, self.valid_feature_cols)

        return ModelResult(
            model_name=model_name,
            metrics=test_metrics,
            val_metrics=val_metrics,
            feature_importance=importance,
            model=model,
            training_time=time.time() - start_time,
            algorithm=model_name,
            hyperparams=hyperparams or {},
        )

    def _get_feature_importance(self, model: Any, feature_names: List[str]) -> Optional[pd.DataFrame]:
        """获取特征重要性"""
        importance = None

        # 树模型
        if hasattr(model, "feature_importances_"):
            importance = model.feature_importances_
        # 线性模型
        elif hasattr(model, "coef_"):
            importance = np.abs(model.coef_)
            if importance.ndim > 1:
                importance = importance.flatten()

        if importance is not None:
            imp_df = pd.DataFrame(
                {
                    "feature": feature_names[: len(importance)],
                    "importance": importance[: len(feature_names)],
                }
            )
            imp_df = imp_df.sort_values("importance", ascending=False)
            return imp_df

        return None
