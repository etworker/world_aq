"""
核心模块

提供项目核心数据类型、配置、日志和工具
"""

from .config import TrainConfig, ModelConfig, ExperimentConfig
from .types import ModelResult, ExperimentResult, PredictionResult, ModelArtifact
from .logger import LoggerManager, get_logger
from .registry import ModelRegistry, register_sklearn_models
from .exceptions import (
    WorldAQException,
    DataNotFoundError,
    ModelNotFoundError,
    ConfigurationError,
    TrainingError,
    InferenceError,
    ValidationError,
    ExperimentError,
)

__all__ = [
    # config
    "TrainConfig",
    "ModelConfig",
    "ExperimentConfig",
    # types
    "ModelResult",
    "ExperimentResult",
    "PredictionResult",
    "ModelArtifact",
    # logger
    "LoggerManager",
    "get_logger",
    # registry
    "ModelRegistry",
    "register_sklearn_models",
    # exceptions
    "WorldAQException",
    "DataNotFoundError",
    "ModelNotFoundError",
    "ConfigurationError",
    "TrainingError",
    "InferenceError",
    "ValidationError",
    "ExperimentError",
]
