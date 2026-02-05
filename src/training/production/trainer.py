"""
生产训练器模块

使用最佳配置训练生产模型
"""

import time
import os.path as osp
from typing import Dict, List, Optional, Any
from pathlib import Path

import joblib
import pandas as pd

from ...core import ModelArtifact
from ...core.config import ModelConfig
from ...core.logger import get_logger
from ...data.processing.engineer import FeatureEngineer
from ...training.core.base_trainer import BaseTrainer
from ...config import get_production_dir, generate_timestamp

logger = get_logger("production")


class ProductionTrainer:
    """生产训练器"""

    def __init__(
        self,
        mode: str,
        model_config: ModelConfig,
        output_dir: Optional[str] = None,
    ):
        """
        初始化生产训练器

        Args:
            mode: 预测模式
            model_config: 模型配置
            output_dir: 输出目录
        """
        self.mode = mode
        self.model_config = model_config
        self.version = generate_timestamp()
        self.output_dir = output_dir or get_production_dir(mode, self.version)

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"生产训练器初始化: mode={mode}, version={self.version}")

    def train(
        self,
        df: pd.DataFrame,
        feature_experiment: str = "full",
        target_transform: str = "log",
    ) -> ModelArtifact:
        """
        训练生产模型

        Args:
            df: 全量训练数据
            feature_experiment: 特征工程类型
            target_transform: 目标变量变换

        Returns:
            模型产物信息
        """
        logger.info("开始生产训练...")

        # 特征工程
        fe = FeatureEngineer()
        df_processed = fe.run(
            df.copy(),
            experiment_id=feature_experiment,
            target_transform=target_transform,
        )

        # 准备特征
        trainer = BaseTrainer(
            target_col="pm25",
            target_transform=target_transform,
        )

        X, y, feature_names = trainer.prepare_features(df_processed, is_train=True)

        logger.info(f"训练数据: {len(X)} 样本, {len(feature_names)} 特征")

        # 训练模型（使用全量数据）
        from ...core.registry import ModelRegistry

        model = ModelRegistry.create_model(self.model_config.algorithm, **self.model_config.hyperparams)

        start_time = time.time()
        model.fit(X, y)
        training_time = time.time() - start_time

        logger.info(f"训练完成，耗时: {training_time:.2f}秒")

        # 保存模型
        model_path = self._save_model(model, feature_names)
        config_path = self._save_config(feature_names)
        metadata_path = self._save_metadata(training_time, feature_names)

        artifact = ModelArtifact(
            model_path=model_path,
            config_path=config_path,
            metadata_path=metadata_path,
            algorithm=self.model_config.algorithm,
            mode=self.mode,
            metrics={},
        )

        logger.info(f"模型已保存到: {self.output_dir}")
        return artifact

    def _save_model(self, model: Any, feature_names: List[str]) -> str:
        """保存模型"""
        model_path = osp.join(self.output_dir, "model.joblib")

        model_info = {
            "model": model,
            "model_name": self.model_config.algorithm,
            "mode": self.mode,
            "feature_names": feature_names,
            "hyperparams": self.model_config.hyperparams,
        }

        joblib.dump(model_info, model_path)
        return model_path

    def _save_config(self, feature_names: List[str]) -> str:
        """保存配置"""
        import json

        config_path = osp.join(self.output_dir, "config.json")

        config = {
            "mode": self.mode,
            "algorithm": self.model_config.algorithm,
            "hyperparams": self.model_config.hyperparams,
            "feature_config": self.model_config.feature_config,
            "feature_names": feature_names,
            "version": self.version,
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return config_path

    def _save_metadata(self, training_time: float, feature_names: List[str]) -> str:
        """保存元数据"""
        import json
        from datetime import datetime

        metadata_path = osp.join(self.output_dir, "metadata.json")

        metadata = {
            "mode": self.mode,
            "algorithm": self.model_config.algorithm,
            "version": self.version,
            "created_at": datetime.now().isoformat(),
            "training_time": training_time,
            "n_features": len(feature_names),
            "feature_names": feature_names,
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return metadata_path


def load_production_model(model_dir: str) -> Dict[str, Any]:
    """
    加载生产模型

    Args:
        model_dir: 模型目录

    Returns:
        模型信息字典
    """
    model_path = osp.join(model_dir, "model.joblib")
    config_path = osp.join(model_dir, "config.json")

    if not osp.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")

    model_info = joblib.load(model_path)

    if osp.exists(config_path):
        import json

        with open(config_path, "r", encoding="utf-8") as f:
            model_info["config"] = json.load(f)

    return model_info
