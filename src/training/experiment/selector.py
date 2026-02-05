"""
最佳模型选择器模块

根据实验结果选择最佳模型配置
"""

import json
import os.path as osp
from typing import Dict, List, Optional, Any
from pathlib import Path

from ...core import ExperimentResult
from ...core.config import ModelConfig
from .modes import get_mode_config, list_modes

from loguru import logger


class BestModelSelector:
    """最佳模型选择器"""

    def __init__(self, metric: str = "val_rmse"):
        """
        初始化选择器

        Args:
            metric: 选择指标，越小越好
        """
        self.metric = metric

    def select(self, results: List[ExperimentResult], modes: Optional[List[str]] = None) -> Dict[str, ModelConfig]:
        """
        为各模式选择最佳模型

        Args:
            results: 实验结果列表
            modes: 要选择的模式列表，None则所有模式

        Returns:
            模式到模型配置的映射
        """
        if modes is None:
            modes = list_modes()

        best_configs = {}

        for mode in modes:
            mode_results = [r for r in results if r.mode == mode]
            if not mode_results:
                logger.warning(f"模式 {mode} 没有实验结果")
                continue

            # 按指标排序，取最佳
            best = min(mode_results, key=lambda r: r.val_metrics.get("rmse", float("inf")))

            config = ModelConfig(
                algorithm=best.algorithm,
                hyperparams=best.model_config.get("hyperparams", {}),
                feature_config=best.model_config.get("feature_config", {}),
            )

            best_configs[mode] = config
            logger.info(f"模式 {mode} 最佳模型: {best.algorithm}, " f"验证RMSE: {best.val_metrics.get('rmse', 0):.4f}")

        return best_configs

    def select_global_best(self, results: List[ExperimentResult]) -> Optional[tuple]:
        """
        选择全局最佳模型

        Args:
            results: 实验结果列表

        Returns:
            (mode, ModelConfig) 或 None
        """
        if not results:
            return None

        best = min(results, key=lambda r: r.val_metrics.get("rmse", float("inf")))

        config = ModelConfig(
            algorithm=best.algorithm,
            hyperparams=best.model_config.get("hyperparams", {}),
            feature_config=best.model_config.get("feature_config", {}),
        )

        return best.mode, config


class ExperimentManifest:
    """实验清单管理"""

    def __init__(self, experiment_id: str, output_dir: str):
        """
        初始化清单

        Args:
            experiment_id: 实验ID
            output_dir: 输出目录
        """
        self.experiment_id = experiment_id
        self.output_dir = output_dir
        self.manifest_path = osp.join(output_dir, "manifest.json")
        self.best_config_path = osp.join(output_dir, "best_config.json")

    def save_manifest(self, results: List[ExperimentResult], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        保存实验清单

        Args:
            results: 实验结果
            metadata: 元数据

        Returns:
            保存的文件路径
        """
        manifest = {
            "experiment_id": self.experiment_id,
            "results": [r.to_dict() for r in results],
            "metadata": metadata or {},
        }

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info(f"实验清单已保存: {self.manifest_path}")
        return self.manifest_path

    def save_best_config(self, best_configs: Dict[str, ModelConfig], global_best_mode: Optional[str] = None) -> str:
        """
        保存最佳配置

        Args:
            best_configs: 各模式的最佳配置
            global_best_mode: 全局最佳模式

        Returns:
            保存的文件路径
        """
        config_data = {
            "experiment_id": self.experiment_id,
            "global_best_mode": global_best_mode,
            "best_models": {
                mode: {
                    "algorithm": config.algorithm,
                    "hyperparams": config.hyperparams,
                    "feature_config": config.feature_config,
                }
                for mode, config in best_configs.items()
            },
        }

        with open(self.best_config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        logger.info(f"最佳配置已保存: {self.best_config_path}")
        return self.best_config_path

    def load_manifest(self) -> Optional[Dict[str, Any]]:
        """加载实验清单"""
        if not osp.exists(self.manifest_path):
            return None

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_best_config(self) -> Optional[Dict[str, Any]]:
        """加载最佳配置"""
        if not osp.exists(self.best_config_path):
            return None

        with open(self.best_config_path, "r", encoding="utf-8") as f:
            return json.load(f)


def create_production_config(mode: str, model_config: ModelConfig, feature_names: List[str]) -> Dict[str, Any]:
    """
    创建生产配置文件

    Args:
        mode: 预测模式
        model_config: 模型配置
        feature_names: 特征名列表

    Returns:
        生产配置字典
    """
    mode_cfg = get_mode_config(mode)

    return {
        "mode": mode,
        "algorithm": model_config.algorithm,
        "hyperparams": model_config.hyperparams,
        "feature_config": model_config.feature_config,
        "feature_names": feature_names,
        "use_historical": mode_cfg.use_historical,
        "multi_output": mode_cfg.multi_output,
        "target": mode_cfg.target,
    }
