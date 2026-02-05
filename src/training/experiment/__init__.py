"""
实验模块

提供实验运行、评估、选择和报告功能
"""

from .runner import ExperimentRunner
from .modes import get_mode_config, list_modes, get_mode_info, ModeConfig
from .evaluator import ModelEvaluator, ExperimentAnalyzer
from .selector import BestModelSelector, ExperimentManifest, create_production_config
from .reporter import ExperimentReporter

__all__ = [
    "ExperimentRunner",
    "get_mode_config",
    "list_modes",
    "get_mode_info",
    "ModeConfig",
    "ModelEvaluator",
    "ExperimentAnalyzer",
    "BestModelSelector",
    "ExperimentManifest",
    "create_production_config",
    "ExperimentReporter",
]
