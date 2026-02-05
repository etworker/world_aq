"""
特征工程工具函数

提供特征工程相关的便捷函数
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple

from loguru import logger


def select_numeric_features(
    df: pd.DataFrame, exclude_cols: Optional[List[str]] = None, target_col: str = "pm25"
) -> List[str]:
    """
    选择数值特征列

    Args:
        df: 数据
        exclude_cols: 要排除的列
        target_col: 目标变量列名

    Returns:
        数值特征列列表
    """
    if exclude_cols is None:
        exclude_cols = []

    default_exclude = [
        "date",
        "city_name",
        "year",
        "data_source",
        "weather_type",
        "visibility_level",
        "wind_level",
        "temp_category",
        "week_position",
        "aqi_category",
        "pollution_level",
        "city_season",
        "quality_level",
        target_col,
        f"{target_col}_log",
        f"{target_col}_boxcox",
    ]

    all_exclude = set(default_exclude + exclude_cols)

    numeric_cols = [c for c in df.columns if c not in all_exclude and pd.api.types.is_numeric_dtype(df[c])]

    return numeric_cols


def handle_missing_values(
    df: pd.DataFrame, strategy: str = "median", fill_value: Optional[float] = None
) -> pd.DataFrame:
    """
    处理缺失值

    Args:
        df: 数据
        strategy: 填充策略 ('median', 'mean', 'constant')
        fill_value: 常数值（strategy='constant'时使用）

    Returns:
        处理后的数据
    """
    df = df.copy()

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        if df[col].isna().any():
            if strategy == "median":
                fill_val = df[col].median()
            elif strategy == "mean":
                fill_val = df[col].mean()
            elif strategy == "constant":
                fill_val = fill_value if fill_value is not None else 0
            else:
                fill_val = 0

            df[col] = df[col].fillna(fill_val)
            logger.debug(f"列 {col}: 填充 {df[col].isna().sum()} 个缺失值")

    return df


def encode_categorical(
    df: pd.DataFrame, categorical_cols: Optional[List[str]] = None, drop_first: bool = True
) -> Tuple[pd.DataFrame, List[str]]:
    """
    编码分类变量

    Args:
        df: 数据
        categorical_cols: 分类列列表，None则自动检测
        drop_first: 是否删除第一个类别（避免共线性）

    Returns:
        (编码后的数据, 新生成的列名列表)
    """
    df = df.copy()

    if categorical_cols is None:
        categorical_cols = [c for c in df.columns if df[c].dtype == "object" or str(df[c].dtype).startswith("category")]

    if not categorical_cols:
        return df, []

    new_cols = []
    for col in categorical_cols:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=drop_first)
            df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
            new_cols.extend(dummies.columns.tolist())
            logger.debug(f"编码 {col}: 生成 {len(dummies.columns)} 个虚拟变量")

    return df, new_cols


def split_features_target(
    df: pd.DataFrame,
    target_col: str = "pm25",
    target_transform: Optional[str] = "log",
    feature_cols: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    分割特征和目标变量

    Args:
        df: 数据
        target_col: 目标变量列名
        target_transform: 目标变量变换类型
        feature_cols: 特征列列表，None则自动选择

    Returns:
        (X, y)
    """
    # 确定目标列
    if target_transform == "log":
        y_col = f"{target_col}_log"
        if y_col not in df.columns:
            y = np.log1p(df[target_col])
        else:
            y = df[y_col]
    else:
        y = df[target_col]

    # 确定特征列
    if feature_cols is None:
        feature_cols = select_numeric_features(df, target_col=target_col)

    X = df[feature_cols].copy()

    return X, y


def calculate_feature_importance(model, feature_names: List[str]) -> pd.DataFrame:
    """
    计算特征重要性

    Args:
        model: 训练好的模型
        feature_names: 特征名列表

    Returns:
        特征重要性DataFrame
    """
    importance = None

    # 树模型
    if hasattr(model, "feature_importances_"):
        importance = model.feature_importances_
    # 线性模型
    elif hasattr(model, "coef_"):
        importance = np.abs(model.coef_)
        if importance.ndim > 1:
            importance = importance.flatten()

    if importance is not None:
        imp_df = pd.DataFrame({"feature": feature_names[: len(importance)], "importance": importance})
        imp_df = imp_df.sort_values("importance", ascending=False)
        return imp_df

    return pd.DataFrame()
