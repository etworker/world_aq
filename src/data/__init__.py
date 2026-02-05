"""
数据模块

提供数据获取、处理和存储功能
"""

# 存储层
from .storage.loader import DataLoader, load_training_data

# 处理层
from .processing.merger import DataMerger
from .processing.engineer import FeatureEngineer
from .processing.transformers import (
    BaseTransformer,
    TemporalTransformer,
    LagFeatureTransformer,
    RollingFeatureTransformer,
    TemperatureFeatureTransformer,
    TargetTransformer,
    WeatherInteractionTransformer,
)
from .processing.features import (
    select_numeric_features,
    handle_missing_values,
    encode_categorical,
    split_features_target,
    calculate_feature_importance,
)
from .processing.noaa_processor import NOAADataProcessor
from .processing.openaq_processor import OpenAQDataProcessor
from .storage.noaa_saver import NOAADataSaver
from .storage.openaq_saver import OpenAQDataSaver
from .pipeline import NOAACityPipeline, OpenAQCityPipeline, process_noaa_cities, process_openaq_cities

__all__ = [
    # storage
    "DataLoader",
    "load_training_data",
    "NOAADataSaver",
    "OpenAQDataSaver",
    # processing
    "DataMerger",
    "FeatureEngineer",
    "NOAADataProcessor",
    "OpenAQDataProcessor",
    # transformers
    "BaseTransformer",
    "TemporalTransformer",
    "LagFeatureTransformer",
    "RollingFeatureTransformer",
    "TemperatureFeatureTransformer",
    "TargetTransformer",
    "WeatherInteractionTransformer",
    # features
    "select_numeric_features",
    "handle_missing_values",
    "encode_categorical",
    "split_features_target",
    "calculate_feature_importance",
    # pipeline
    "NOAACityPipeline",
    "OpenAQCityPipeline",
    "process_noaa_cities",
    "process_openaq_cities",
]
