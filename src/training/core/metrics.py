"""
评估指标模块
"""

import numpy as np
from typing import Dict, Tuple
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, target_transform: str = None) -> Dict[str, float]:
    """
    计算评估指标

    Args:
        y_true: 真实值
        y_pred: 预测值
        target_transform: 目标变量变换类型 ('log', 'boxcox', None)

    Returns:
        指标字典
    """
    # 逆变换
    if target_transform == "log":
        y_t = np.expm1(y_true)
        y_p = np.maximum(np.expm1(y_pred), 0)
    else:
        y_t, y_p = y_true, y_pred

    return {
        "rmse": float(np.sqrt(mean_squared_error(y_t, y_p))),
        "mae": float(mean_absolute_error(y_t, y_p)),
        "r2": float(r2_score(y_t, y_p)),
    }


def calculate_all_metrics(
    y_train_true: np.ndarray,
    y_train_pred: np.ndarray,
    y_val_true: np.ndarray,
    y_val_pred: np.ndarray,
    y_test_true: np.ndarray,
    y_test_pred: np.ndarray,
    target_transform: str = None,
) -> Tuple[Dict, Dict, Dict]:
    """
    计算所有数据集的指标

    Returns:
        (train_metrics, val_metrics, test_metrics)
    """
    return (
        calculate_metrics(y_train_true, y_train_pred, target_transform),
        calculate_metrics(y_val_true, y_val_pred, target_transform),
        calculate_metrics(y_test_true, y_test_pred, target_transform),
    )
