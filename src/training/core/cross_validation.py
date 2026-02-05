"""
交叉验证模块

提供时间序列数据分割策略
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Generator
from sklearn.model_selection import TimeSeriesSplit


class TimeSeriesDataSplitter:
    """时间序列数据分割器"""

    def __init__(
        self,
        test_size: float = 0.15,
        val_size: float = 0.15,
        date_col: str = "date",
    ):
        """
        初始化分割器

        Args:
            test_size: 测试集比例
            val_size: 验证集比例
            date_col: 日期列名
        """
        self.test_size = test_size
        self.val_size = val_size
        self.date_col = date_col

    def split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        分割数据为训练/验证/测试集

        Args:
            df: 输入数据

        Returns:
            (train_df, val_df, test_df)
        """
        df = df.sort_values(self.date_col).reset_index(drop=True)
        n = len(df)

        # 计算分割点
        test_idx = int(n * (1 - self.test_size))
        val_idx = int(test_idx * (1 - self.val_size / (1 - self.test_size)))

        train_df = df.iloc[:val_idx].copy()
        val_df = df.iloc[val_idx:test_idx].copy()
        test_df = df.iloc[test_idx:].copy()

        return train_df, val_df, test_df

    def get_cv_splits(
        self, df: pd.DataFrame, n_splits: int = 5
    ) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
        """
        获取时间序列交叉验证分割

        Args:
            df: 输入数据
            n_splits: 分割数

        Yields:
            (train_df, val_df)
        """
        df = df.sort_values(self.date_col).reset_index(drop=True)

        tscv = TimeSeriesSplit(n_splits=n_splits)
        for train_idx, val_idx in tscv.split(df):
            train_df = df.iloc[train_idx].copy()
            val_df = df.iloc[val_idx].copy()
            yield train_df, val_df


def temporal_split(
    df: pd.DataFrame,
    date_col: str = "date",
    train_end: str = None,
    val_end: str = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    按时间范围分割数据

    Args:
        df: 输入数据
        date_col: 日期列名
        train_end: 训练集结束日期（验证集开始）
        val_end: 验证集结束日期（测试集开始）

    Returns:
        (train_df, val_df, test_df)
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    if train_end:
        train_mask = df[date_col] < train_end
        train_df = df[train_mask].copy()
        remaining = df[~train_mask].copy()
    else:
        # 默认70%训练
        split_idx = int(len(df) * 0.7)
        train_df = df.iloc[:split_idx].copy()
        remaining = df.iloc[split_idx:].copy()

    if val_end:
        val_mask = remaining[date_col] < val_end
        val_df = remaining[val_mask].copy()
        test_df = remaining[~val_mask].copy()
    else:
        # 剩余部分平分
        split_idx = int(len(remaining) * 0.5)
        val_df = remaining.iloc[:split_idx].copy()
        test_df = remaining.iloc[split_idx:].copy()

    return train_df, val_df, test_df
