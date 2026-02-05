"""
预测模式定义模块

定义8种预测模式及其配置
"""

from typing import Dict, List, Any
from dataclasses import dataclass

from ...config import PredictionMode, MODE_METADATA


@dataclass
class ModeConfig:
    """模式配置"""

    name: str
    use_historical: bool
    multi_output: bool
    city_level: bool
    feature_experiment: str
    metadata: Dict[str, Any]
    forecast_horizon: int = 1
    target_cols: List[str] = None


# 8种模式的标准配置
MODE_CONFIGS = {
    PredictionMode.GTM: ModeConfig(
        name=PredictionMode.GTM,
        use_historical=False,
        multi_output=True,
        city_level=False,
        feature_experiment="weather",
        metadata=MODE_METADATA[PredictionMode.GTM],
        target_cols=["pm25", "o3"],
    ),
    PredictionMode.GTS: ModeConfig(
        name=PredictionMode.GTS,
        use_historical=False,
        multi_output=False,
        city_level=False,
        feature_experiment="weather",
        metadata=MODE_METADATA[PredictionMode.GTS],
        target_cols=["pm25"],
    ),
    PredictionMode.GHM: ModeConfig(
        name=PredictionMode.GHM,
        use_historical=True,
        multi_output=True,
        city_level=False,
        feature_experiment="full",
        metadata=MODE_METADATA[PredictionMode.GHM],
        target_cols=["pm25", "o3"],
    ),
    PredictionMode.GHS: ModeConfig(
        name=PredictionMode.GHS,
        use_historical=True,
        multi_output=False,
        city_level=False,
        feature_experiment="full",
        metadata=MODE_METADATA[PredictionMode.GHS],
        target_cols=["pm25"],
    ),
    PredictionMode.CTM: ModeConfig(
        name=PredictionMode.CTM,
        use_historical=False,
        multi_output=True,
        city_level=True,
        feature_experiment="weather",
        metadata=MODE_METADATA[PredictionMode.CTM],
        target_cols=["pm25", "o3"],
    ),
    PredictionMode.CTS: ModeConfig(
        name=PredictionMode.CTS,
        use_historical=False,
        multi_output=False,
        city_level=True,
        feature_experiment="weather",
        metadata=MODE_METADATA[PredictionMode.CTS],
        target_cols=["pm25"],
    ),
    PredictionMode.CHM: ModeConfig(
        name=PredictionMode.CHM,
        use_historical=True,
        multi_output=True,
        city_level=True,
        feature_experiment="full",
        metadata=MODE_METADATA[PredictionMode.CHM],
        target_cols=["pm25", "o3"],
    ),
    PredictionMode.CHS: ModeConfig(
        name=PredictionMode.CHS,
        use_historical=True,
        multi_output=False,
        city_level=True,
        feature_experiment="full",
        metadata=MODE_METADATA[PredictionMode.CHS],
        target_cols=["pm25"],
    ),
}


def get_mode_config(mode: str) -> ModeConfig:
    """
    获取模式配置

    Args:
        mode: 模式名称

    Returns:
        ModeConfig
    """
    if mode not in MODE_CONFIGS:
        raise ValueError(f"未知模式: {mode}，可用模式: {list(MODE_CONFIGS.keys())}")
    return MODE_CONFIGS[mode]


def list_modes() -> List[str]:
    """列出所有可用模式"""
    return list(MODE_CONFIGS.keys())


def get_mode_info(mode: str) -> Dict[str, Any]:
    """获取模式信息"""
    config = get_mode_config(mode)
    return {
        "name": config.name,
        "use_historical": config.use_historical,
        "multi_output": config.multi_output,
        "target_cols": config.target_cols,
        "feature_experiment": config.feature_experiment,
        **config.metadata,
    }
