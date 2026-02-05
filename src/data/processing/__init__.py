"""
数据处理模块

提供数据合并和特征工程功能
"""

from .merger import DataMerger
from .engineer import FeatureEngineer
from .transformers import (
    BaseTransformer,
    TemporalTransformer,
    LagFeatureTransformer,
    RollingFeatureTransformer,
    TemperatureFeatureTransformer,
    TargetTransformer,
    WeatherInteractionTransformer,
)
from .features import (
    select_numeric_features,
    handle_missing_values,
    encode_categorical,
    split_features_target,
    calculate_feature_importance,
)

__all__ = [
    "DataMerger",
    "FeatureEngineer",
    "BaseTransformer",
    "TemporalTransformer",
    "LagFeatureTransformer",
    "RollingFeatureTransformer",
    "TemperatureFeatureTransformer",
    "TargetTransformer",
    "WeatherInteractionTransformer",
    "select_numeric_features",
    "handle_missing_values",
    "encode_categorical",
    "split_features_target",
    "calculate_feature_importance",
]
