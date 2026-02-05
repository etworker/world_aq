"""
实验评估模块

提供模型评估和对比功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from ...core import ModelResult, ExperimentResult
from ...core.config import TrainConfig

from loguru import logger


class ModelEvaluator:
    """模型评估器"""

    def __init__(self, metric: str = "val_rmse"):
        """
        初始化评估器

        Args:
            metric: 用于排序的指标
        """
        self.metric = metric
        self.results: List[ExperimentResult] = []

    def add_result(self, result: ExperimentResult) -> None:
        """添加实验结果"""
        self.results.append(result)

    def get_best_result(self, mode: Optional[str] = None) -> Optional[ExperimentResult]:
        """
        获取最佳结果

        Args:
            mode: 指定模式，None则所有模式中选最佳

        Returns:
            最佳实验结果
        """
        results = self.results
        if mode:
            results = [r for r in results if r.mode == mode]

        if not results:
            return None

        # 按验证RMSE排序（越小越好）
        best = min(results, key=lambda r: r.val_metrics.get("rmse", float("inf")))
        return best

    def get_ranking(self, mode: Optional[str] = None) -> List[ExperimentResult]:
        """
        获取排名

        Args:
            mode: 指定模式

        Returns:
            按指标排序的结果列表
        """
        results = self.results
        if mode:
            results = [r for r in results if r.mode == mode]

        return sorted(results, key=lambda r: r.val_metrics.get("rmse", float("inf")))

    def compare_algorithms(self, mode: str) -> pd.DataFrame:
        """
        对比某模式下的所有算法

        Args:
            mode: 模式名称

        Returns:
            对比结果DataFrame
        """
        results = [r for r in self.results if r.mode == mode]

        if not results:
            return pd.DataFrame()

        data = []
        for r in results:
            data.append(
                {
                    "algorithm": r.algorithm,
                    "val_rmse": r.val_metrics.get("rmse", np.nan),
                    "val_mae": r.val_metrics.get("mae", np.nan),
                    "val_r2": r.val_metrics.get("r2", np.nan),
                    "test_rmse": r.metrics.get("rmse", np.nan),
                    "test_mae": r.metrics.get("mae", np.nan),
                    "test_r2": r.metrics.get("r2", np.nan),
                }
            )

        return pd.DataFrame(data).sort_values("val_rmse")

    def generate_summary(self) -> Dict[str, Any]:
        """
        生成实验汇总

        Returns:
            汇总字典
        """
        summary = {
            "total_experiments": len(self.results),
            "modes": list(set(r.mode for r in self.results)),
            "algorithms": list(set(r.algorithm for r in self.results)),
        }

        # 各模式最佳结果
        mode_best = {}
        for mode in summary["modes"]:
            best = self.get_best_result(mode)
            if best:
                mode_best[mode] = {
                    "algorithm": best.algorithm,
                    "val_rmse": best.val_metrics.get("rmse"),
                    "test_rmse": best.metrics.get("rmse"),
                }
        summary["mode_best"] = mode_best

        # 全局最佳
        global_best = self.get_best_result()
        if global_best:
            summary["global_best"] = {
                "mode": global_best.mode,
                "algorithm": global_best.algorithm,
                "val_rmse": global_best.val_metrics.get("rmse"),
                "test_rmse": global_best.metrics.get("rmse"),
            }

        return summary


class ExperimentAnalyzer:
    """实验分析器"""

    def __init__(self, results: List[ExperimentResult]):
        """
        初始化分析器

        Args:
            results: 实验结果列表
        """
        self.results = results

    def analyze_feature_importance(self) -> Dict[str, pd.DataFrame]:
        """
        分析特征重要性

        Returns:
            各模型的特征重要性字典
        """
        importance_dict = {}

        for result in self.results:
            # Note: ExperimentResult doesn't have feature_importance directly
            # This would need to be stored in model_config or fetched from saved model
            pass

        return importance_dict

    def analyze_hyperparameter_sensitivity(self, algorithm: str, param_name: str) -> pd.DataFrame:
        """
        分析超参数敏感性

        Args:
            algorithm: 算法名称
            param_name: 参数名称

        Returns:
            参数值与性能的关系
        """
        results = [r for r in self.results if r.algorithm == algorithm]

        data = []
        for r in results:
            param_value = r.model_config.get("hyperparams", {}).get(param_name)
            if param_value is not None:
                data.append(
                    {
                        param_name: param_value,
                        "val_rmse": r.val_metrics.get("rmse"),
                        "test_rmse": r.metrics.get("rmse"),
                    }
                )

        return pd.DataFrame(data).sort_values(param_name)

    def get_mode_comparison(self) -> pd.DataFrame:
        """
        获取模式对比

        Returns:
            各模式最佳结果的对比
        """
        from .modes import list_modes

        modes = list_modes()
        data = []

        for mode in modes:
            mode_results = [r for r in self.results if r.mode == mode]
            if mode_results:
                best = min(mode_results, key=lambda r: r.val_metrics.get("rmse", float("inf")))
                data.append(
                    {
                        "mode": mode,
                        "algorithm": best.algorithm,
                        "val_rmse": best.val_metrics.get("rmse"),
                        "test_rmse": best.metrics.get("rmse"),
                        "val_r2": best.val_metrics.get("r2"),
                    }
                )

        return pd.DataFrame(data)
