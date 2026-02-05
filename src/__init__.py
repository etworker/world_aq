"""
World Air Quality Prediction Package

空气质量预测包
"""

__version__ = "1.0.0"

# 核心模块
from . import core
from . import config

# 数据模块
from . import data

# 训练模块
from . import training

# 推理模块
from . import inference

# AQI模块
from . import aqi

# 工具模块
from . import utils

# 模型模块
from . import models

__all__ = [
    "core",
    "config",
    "data",
    "training",
    "inference",
    "aqi",
    "utils",
    "models",
]
