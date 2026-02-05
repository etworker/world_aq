"""
核心配置类
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class TrainConfig:
    """训练参数配置"""

    target_col: str = "pm25"
    target_transform: Optional[str] = "log"
    date_col: str = "date"
    city_col: str = "city_name"
    test_size: float = 0.15
    val_size: float = 0.15
    n_splits: int = 5
    random_state: int = 42
    autogluon_time_limit: int = 30

    # 多污染物预测配置
    multi_pollutant: bool = False
    pollutant_cols: List[str] = field(default_factory=lambda: ["pm25", "o3", "no2"])

    # 预测模式配置
    use_historical_data: bool = True

    # AutoGluon开关配置
    enable_autogluon: bool = False

    # 训练控制配置
    skip_multi_pollutant: bool = True
    skip_city_models: bool = True

    # 预处理配置
    encode_categorical: bool = True
    impute_strategy: str = "median"

    # 模型默认参数
    rf_n_estimators: int = 100
    rf_max_depth: int = 15
    gb_n_estimators: int = 200
    ridge_alpha: float = 1.0
    lasso_alpha: float = 1.0
    elastic_alpha: float = 1.0
    elastic_l1_ratio: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "target_col": self.target_col,
            "target_transform": self.target_transform,
            "date_col": self.date_col,
            "city_col": self.city_col,
            "test_size": self.test_size,
            "val_size": self.val_size,
            "n_splits": self.n_splits,
            "random_state": self.random_state,
            "multi_pollutant": self.multi_pollutant,
            "pollutant_cols": self.pollutant_cols,
            "use_historical_data": self.use_historical_data,
            "enable_autogluon": self.enable_autogluon,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainConfig":
        """从字典创建"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ModelConfig:
    """模型配置"""

    algorithm: str  # Ridge, Lasso, RandomForest, etc.
    hyperparams: Dict[str, Any] = field(default_factory=dict)
    feature_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "hyperparams": self.hyperparams,
            "feature_config": self.feature_config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        return cls(
            algorithm=data["algorithm"],
            hyperparams=data.get("hyperparams", {}),
            feature_config=data.get("feature_config", {}),
        )


@dataclass
class ExperimentConfig:
    """实验配置"""

    experiment_id: str
    mode: str  # GTM, GTS, GHM, GHS, CTM, CTS, CHM, CHS
    algorithms: List[str] = field(default_factory=list)
    feature_configs: List[Dict[str, Any]] = field(default_factory=list)
    train_config: TrainConfig = field(default_factory=TrainConfig)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "mode": self.mode,
            "algorithms": self.algorithms,
            "feature_configs": self.feature_configs,
            "train_config": self.train_config.to_dict(),
        }
