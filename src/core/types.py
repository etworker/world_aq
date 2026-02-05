"""
核心数据类型定义
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import pandas as pd


@dataclass
class ModelResult:
    """训练结果报告载体"""

    model_name: str
    metrics: Dict[str, float] = field(default_factory=dict)
    val_metrics: Dict[str, float] = field(default_factory=dict)
    feature_importance: Optional[pd.DataFrame] = None
    model: Optional[Any] = None
    training_time: float = 0.0
    algorithm: str = ""
    hyperparams: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（排除模型对象）"""
        return {
            "model_name": self.model_name,
            "metrics": self.metrics,
            "val_metrics": self.val_metrics,
            "training_time": self.training_time,
            "algorithm": self.algorithm,
            "hyperparams": self.hyperparams,
        }


@dataclass
class ExperimentResult:
    """实验结果"""

    experiment_id: str
    mode: str
    algorithm: str
    metrics: Dict[str, float]
    val_metrics: Dict[str, float]
    model_config: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "mode": self.mode,
            "algorithm": self.algorithm,
            "metrics": self.metrics,
            "val_metrics": self.val_metrics,
            "model_config": self.model_config,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentResult":
        return cls(**data)


@dataclass
class PredictionResult:
    """预测结果"""

    predictions: Union[List[float], Dict[str, List[float]]]
    mode: str
    model_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelArtifact:
    """模型产物信息"""

    model_path: str
    config_path: str
    metadata_path: str
    algorithm: str
    mode: str
    metrics: Dict[str, float]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_path": self.model_path,
            "config_path": self.config_path,
            "metadata_path": self.metadata_path,
            "algorithm": self.algorithm,
            "mode": self.mode,
            "metrics": self.metrics,
            "created_at": self.created_at,
            "version": self.version,
        }
