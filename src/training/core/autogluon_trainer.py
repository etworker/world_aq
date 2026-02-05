"""
AutoGluon AutoML 训练器模块

提供自动化机器学习功能，自动搜索最佳模型
"""

import time
import tempfile
import uuid
import os.path as osp
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

import pandas as pd
import numpy as np

from ...core import ModelResult
from ...core.logger import get_logger

logger = get_logger("autogluon")

# AutoGluon 可用性检查
try:
    from autogluon.tabular import TabularPredictor

    AUTOGluon_AVAILABLE = True
except ImportError:
    AUTOGluon_AVAILABLE = False
    logger.warning("AutoGluon 未安装，AutoML 功能不可用。请运行: pip install autogluon")


class AutoGluonTrainer:
    """AutoGluon 自动机器学习训练器"""

    def __init__(
        self,
        target_col: str = "pm25",
        target_transform: Optional[str] = "log",
        time_limit: int = 300,
        presets: str = "medium_quality",
        eval_metric: str = "rmse",
    ):
        """
        初始化 AutoGluon 训练器

        Args:
            target_col: 目标变量列名
            target_transform: 目标变量变换类型 ('log', 'boxcox', None)
            time_limit: 训练时间限制（秒）
            presets: 预设配置 ('best_quality', 'high_quality', 'good_quality', 'medium_quality')
            eval_metric: 评估指标
        """
        if not AUTOGluon_AVAILABLE:
            raise ImportError("AutoGluon 未安装。请运行: pip install autogluon")

        self.target_col = target_col
        self.target_transform = target_transform
        self.time_limit = time_limit
        self.presets = presets
        self.eval_metric = eval_metric
        self.predictor: Optional[TabularPredictor] = None
        self.feature_names: List[str] = []
        self.temp_dir: Optional[str] = None

    def prepare_data(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        准备 AutoGluon 格式数据

        Args:
            X_train: 训练特征
            y_train: 训练目标
            X_val: 验证特征
            y_val: 验证目标

        Returns:
            (ag_train, ag_val) AutoGluon 格式数据
        """
        # 合并特征和目标
        ag_train = X_train.copy()
        ag_train[self.target_col] = y_train.values

        ag_val = X_val.copy()
        ag_val[self.target_col] = y_val.values

        self.feature_names = list(X_train.columns)

        return ag_train, ag_val

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> ModelResult:
        """
        使用 AutoGluon 训练模型

        Args:
            X_train: 训练特征
            y_train: 训练目标
            X_val: 验证特征
            y_val: 验证目标
            X_test: 测试特征
            y_test: 测试目标

        Returns:
            ModelResult 训练结果
        """
        start_time = time.time()

        logger.info(f"[AutoML] 启动 AutoGluon 自动训练，时间限制: {self.time_limit}秒")
        logger.info(f"[AutoML] 预设配置: {self.presets}, 评估指标: {self.eval_metric}")

        # 准备数据
        ag_train, ag_val = self.prepare_data(X_train, y_train, X_val, y_val)

        # 创建临时目录保存模型
        self.temp_dir = tempfile.mkdtemp(prefix=f"ag_{uuid.uuid4().hex[:8]}_")

        try:
            # 训练 AutoGluon 模型
            self.predictor = TabularPredictor(
                label=self.target_col,
                path=self.temp_dir,
                eval_metric=self.eval_metric,
            ).fit(
                train_data=ag_train,
                tuning_data=ag_val,
                time_limit=self.time_limit,
                presets=self.presets,
                verbosity=1,
            )

            # 预测
            y_val_pred = self.predictor.predict(X_val)
            y_test_pred = self.predictor.predict(X_test)

            # 逆变换（如果需要）
            if self.target_transform == "log":
                y_val_orig = np.expm1(y_val.values)
                y_test_orig = np.expm1(y_test.values)
                y_val_pred_orig = np.maximum(np.expm1(y_val_pred), 0)
                y_test_pred_orig = np.maximum(np.expm1(y_test_pred), 0)
            else:
                y_val_orig = y_val.values
                y_test_orig = y_test.values
                y_val_pred_orig = y_val_pred
                y_test_pred_orig = y_test_pred

            # 计算指标
            from .metrics import calculate_metrics

            val_metrics = calculate_metrics(y_val_orig, y_val_pred_orig, None)
            test_metrics = calculate_metrics(y_test_orig, y_test_pred_orig, None)

            # 获取特征重要性
            importance = self._get_feature_importance(ag_train)

            # 获取模型信息
            leaderboard = self.predictor.leaderboard(silent=True)
            best_model = leaderboard.iloc[0]["model"] if len(leaderboard) > 0 else "Unknown"

            logger.info(f"[AutoML] 最佳模型: {best_model}")
            logger.info(f"[AutoML] 测试集 RMSE: {test_metrics.get('rmse', 0):.4f}")

            training_time = time.time() - start_time

            return ModelResult(
                model_name=f"AutoGluon({best_model})",
                metrics=test_metrics,
                val_metrics=val_metrics,
                feature_importance=importance,
                model=self.predictor,
                training_time=training_time,
                algorithm="AutoGluon",
                hyperparams={
                    "time_limit": self.time_limit,
                    "presets": self.presets,
                    "eval_metric": self.eval_metric,
                    "best_model": best_model,
                },
            )

        except Exception as e:
            logger.error(f"[AutoML] AutoGluon 训练失败: {e}")
            raise

    def _get_feature_importance(self, ag_train: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        获取特征重要性

        Args:
            ag_train: 训练数据

        Returns:
            特征重要性 DataFrame
        """
        if self.predictor is None:
            return None

        try:
            importance_df = self.predictor.feature_importance(
                ag_train,
                silent=True,
            ).reset_index()

            # 标准化列名
            importance_df.columns = ["feature", "importance", "std", "p_value", "n"]
            importance_df = importance_df.sort_values("importance", ascending=False)

            return importance_df

        except Exception as e:
            logger.warning(f"[AutoML] 获取特征重要性失败: {e}")
            return None

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        使用训练好的模型进行预测

        Args:
            X: 输入特征

        Returns:
            预测结果
        """
        if self.predictor is None:
            raise ValueError("模型尚未训练")

        return self.predictor.predict(X)

    def get_leaderboard(self) -> Optional[pd.DataFrame]:
        """
        获取模型排行榜

        Returns:
            排行榜 DataFrame
        """
        if self.predictor is None:
            return None

        return self.predictor.leaderboard(silent=True)

    def save(self, path: str) -> str:
        """
        保存模型

        Args:
            path: 保存路径

        Returns:
            模型保存路径
        """
        if self.predictor is None:
            raise ValueError("模型尚未训练")

        model_path = osp.join(path, "autogluon_model")
        self.predictor.save(model_path)
        logger.info(f"[AutoML] 模型已保存到: {model_path}")
        return model_path

    @classmethod
    def load(cls, path: str) -> "AutoGluonTrainer":
        """
        加载模型

        Args:
            path: 模型路径

        Returns:
            AutoGluonTrainer 实例
        """
        if not AUTOGluon_AVAILABLE:
            raise ImportError("AutoGluon 未安装")

        trainer = cls()
        trainer.predictor = TabularPredictor.load(path)
        return trainer


def check_autogluon_available() -> bool:
    """检查 AutoGluon 是否可用"""
    return AUTOGluon_AVAILABLE
