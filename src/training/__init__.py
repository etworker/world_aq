"""
训练模块

提供实验和生产训练功能
"""

# 核心
from .core.base_trainer import BaseTrainer
from .core.cross_validation import TimeSeriesDataSplitter, temporal_split
from .core.metrics import calculate_metrics, calculate_all_metrics
from .core.autogluon_trainer import AutoGluonTrainer, check_autogluon_available

# 实验
from .experiment.runner import ExperimentRunner
from .experiment.modes import get_mode_config, list_modes, get_mode_info
from .experiment.evaluator import ModelEvaluator, ExperimentAnalyzer
from .experiment.selector import BestModelSelector, ExperimentManifest
from .experiment.reporter import ExperimentReporter

# 生产
from .production.pipeline import ProductionPipeline, train_production_model
from .production.trainer import ProductionTrainer, load_production_model

__all__ = [
    # core
    "BaseTrainer",
    "TimeSeriesDataSplitter",
    "temporal_split",
    "calculate_metrics",
    "calculate_all_metrics",
    "AutoGluonTrainer",
    "check_autogluon_available",
    # experiment
    "ExperimentRunner",
    "get_mode_config",
    "list_modes",
    "get_mode_info",
    "ModelEvaluator",
    "ExperimentAnalyzer",
    "BestModelSelector",
    "ExperimentManifest",
    "ExperimentReporter",
    # production
    "ProductionPipeline",
    "train_production_model",
    "ProductionTrainer",
    "load_production_model",
]
