"""
生产训练流水线模块

根据最佳配置训练生产模型
"""

import os.path as osp
from typing import Dict, List, Optional, Any
from pathlib import Path

import pandas as pd

from ...core.config import ModelConfig
from ...core.logger import get_logger
from ...data.storage.loader import load_training_data
from ...training.experiment.selector import ExperimentManifest
from .trainer import ProductionTrainer

logger = get_logger("production")


class ProductionPipeline:
    """生产训练流水线"""

    def __init__(
        self,
        config_path: str,
        output_dir: Optional[str] = None,
    ):
        """
        初始化流水线

        Args:
            config_path: 最佳配置文件路径
            output_dir: 输出目录
        """
        self.config_path = config_path
        self.output_dir = output_dir

        # 加载配置
        self.manifest = ExperimentManifest(experiment_id="", output_dir=osp.dirname(config_path))
        self.best_config = self.manifest.load_best_config()

        if not self.best_config:
            raise ValueError(f"无法加载配置文件: {config_path}")

        logger.info(f"加载最佳配置: {config_path}")

    def train_mode(
        self,
        mode: str,
        data_path: Optional[str] = None,
        cities: Optional[List[str]] = None,
    ) -> str:
        """
        训练指定模式的生产模型

        Args:
            mode: 预测模式
            data_path: 数据路径，None则从merged加载
            cities: 城市列表

        Returns:
            模型目录路径
        """
        # 获取模式配置
        mode_config = self.best_config.get("best_models", {}).get(mode)
        if not mode_config:
            raise ValueError(f"配置中未找到模式: {mode}")

        model_cfg = ModelConfig(
            algorithm=mode_config["algorithm"],
            hyperparams=mode_config.get("hyperparams", {}),
            feature_config=mode_config.get("feature_config", {}),
        )

        # 加载数据
        df = load_training_data(data_path, cities)

        # 创建训练器
        trainer = ProductionTrainer(
            mode=mode,
            model_config=model_cfg,
            output_dir=self.output_dir,
        )

        # 训练
        feature_config = model_cfg.feature_config
        artifact = trainer.train(
            df=df,
            feature_experiment=feature_config.get("experiment_id", "full"),
            target_transform=feature_config.get("target_transform", "log"),
        )

        return trainer.output_dir

    def train_all_modes(
        self,
        data_path: Optional[str] = None,
        cities: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        训练所有模式的生产模型

        Args:
            data_path: 数据路径
            cities: 城市列表

        Returns:
            模式到模型目录的映射
        """
        best_models = self.best_config.get("best_models", {})

        results = {}
        for mode in best_models.keys():
            try:
                logger.info(f"\n训练模式: {mode}")
                model_dir = self.train_mode(mode, data_path, cities)
                results[mode] = model_dir
            except Exception as e:
                logger.error(f"训练模式 {mode} 失败: {e}")

        return results


def train_production_model(
    config_path: str,
    mode: str,
    data_path: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """
    便捷函数：训练生产模型

    Args:
        config_path: 最佳配置文件路径
        mode: 预测模式
        data_path: 数据路径
        output_dir: 输出目录

    Returns:
        模型目录路径
    """
    pipeline = ProductionPipeline(config_path, output_dir)
    return pipeline.train_mode(mode, data_path)
