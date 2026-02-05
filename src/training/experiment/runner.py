"""
实验运行器模块

批量执行实验，探索最佳模型配置
"""

import time
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np

from ...core import ExperimentResult, ModelResult
from ...core.config import TrainConfig
from ...core.logger import get_logger
from ...data.processing.engineer import FeatureEngineer
from ...data.processing.features import split_features_target
from ...training.core.base_trainer import BaseTrainer
from ...training.core.cross_validation import TimeSeriesDataSplitter
from ...training.core.autogluon_trainer import AutoGluonTrainer, check_autogluon_available
from ...config import Algorithm, get_experiment_dir, generate_experiment_id
from .modes import ModeConfig, get_mode_config, list_modes
from .evaluator import ModelEvaluator
from .selector import BestModelSelector, ExperimentManifest
from .reporter import ExperimentReporter
from ...config import MODE_METADATA

logger = get_logger("experiment")


class ExperimentRunner:
    """实验运行器"""

    def __init__(
        self,
        output_dir: Optional[str] = None,
        train_config: Optional[TrainConfig] = None,
    ):
        """
        初始化实验运行器

        Args:
            output_dir: 输出目录
            train_config: 训练配置
        """
        self.experiment_id = generate_experiment_id()
        self.output_dir = output_dir or get_experiment_dir(self.experiment_id)
        self.train_config = train_config or TrainConfig()

        # 组件
        self.feature_engineer = FeatureEngineer()
        self.data_splitter = TimeSeriesDataSplitter(
            test_size=self.train_config.test_size,
            val_size=self.train_config.val_size,
        )
        self.evaluator = ModelEvaluator()
        self.selector = BestModelSelector()
        self.manifest = ExperimentManifest(self.experiment_id, self.output_dir)
        self.reporter = ExperimentReporter(self.output_dir)

        # 结果存储
        self.results: List[ExperimentResult] = []

        logger.info(f"实验运行器初始化: {self.experiment_id}")
        logger.info(f"输出目录: {self.output_dir}")

    def run_separate_experiment(
        self,
        df: pd.DataFrame,
        mode: str,
        algorithm: str,
        target_col: str,
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> ExperimentResult:
        """
        运行单独目标变量的实验（GTS, GHS, CTS, CHS）

        Args:
            df: 原始数据
            mode: 预测模式
            algorithm: 算法名称
            target_col: 目标变量名（如 'pm25', 'o3'）
            hyperparams: 超参数

        Returns:
            实验结果
        """
        mode_config = get_mode_config(mode)

        # 为特定目标变量创建特征工程器
        fe = FeatureEngineer(target_col=target_col)

        # 特征工程
        df_processed = fe.run(
            df.copy(),
            experiment_id=mode_config.feature_experiment,
            target_transform=self.train_config.target_transform,
            forecast_horizon=mode_config.forecast_horizon,
        )

        # 数据分割
        train_df, val_df, test_df = self.data_splitter.split(df_processed)

        # 准备特征
        trainer = BaseTrainer(
            target_col=target_col,
            target_transform=self.train_config.target_transform,
        )

        X_train, y_train, feature_names = trainer.prepare_features(train_df, is_train=True)
        X_val, y_val, _ = trainer.prepare_features(val_df, is_train=False)
        X_test, y_test, _ = trainer.prepare_features(test_df, is_train=False)

        # 训练模型
        if algorithm == "AutoGluon":
            if not self.train_config.enable_autogluon:
                raise ValueError("AutoGluon 已在配置中禁用")
            if not check_autogluon_available():
                raise ImportError("AutoGluon 未安装")

            ag_trainer = AutoGluonTrainer(
                target_col=target_col,
                target_transform=self.train_config.target_transform,
                time_limit=hyperparams.get("time_limit", 300) if hyperparams else 300,
                presets=hyperparams.get("presets", "medium_quality") if hyperparams else "medium_quality",
                eval_metric=hyperparams.get("eval_metric", "rmse") if hyperparams else "rmse",
            )
            model_result = ag_trainer.train(
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                X_test=X_test,
                y_test=y_test,
            )
        else:
            model_result = trainer.train_model(
                model_name=algorithm,
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                X_test=X_test,
                y_test=y_test,
                hyperparams=hyperparams,
            )

        # 创建实验结果（带目标变量标识）
        exp_result = ExperimentResult(
            experiment_id=f"{self.experiment_id}_{target_col}",
            mode=f"{mode}_{target_col}",
            algorithm=algorithm,
            metrics=model_result.metrics,
            val_metrics=model_result.val_metrics,
            model_config={
                "hyperparams": model_result.hyperparams,
                "feature_config": {"experiment_id": mode_config.feature_experiment},
                "feature_names": feature_names,
                "target_col": target_col,
            },
        )

        return exp_result

    def run_multi_output_experiment(
        self,
        df: pd.DataFrame,
        mode: str,
        algorithm: str,
        target_cols: List[str],
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> ExperimentResult:
        """
        运行全局多输出实验（GTM, GHM）

        Args:
            df: 原始数据
            mode: 预测模式
            algorithm: 算法名称
            target_cols: 目标变量列表
            hyperparams: 超参数

        Returns:
            实验结果
        """
        from ...training.core.multi_output_trainer import MultiOutputTrainer

        mode_config = get_mode_config(mode)

        # 使用第一个目标创建特征工程，并保留其他目标列
        additional_targets = target_cols[1:] if len(target_cols) > 1 else []
        fe = FeatureEngineer(target_col=target_cols[0], additional_targets=additional_targets)
        df_processed = fe.run(
            df.copy(),
            experiment_id=mode_config.feature_experiment,
            target_transform=self.train_config.target_transform,
            forecast_horizon=mode_config.forecast_horizon,
        )

        # 数据分割
        train_df, val_df, test_df = self.data_splitter.split(df_processed)

        # 准备多输出特征
        trainer = MultiOutputTrainer(
            target_cols=target_cols,
            target_transform=self.train_config.target_transform,
        )
        
        try:
            X_train, Y_train, feature_names = trainer.prepare_features_multi(train_df)
            X_val, Y_val, _ = trainer.prepare_features_multi(val_df)
            X_test, Y_test, _ = trainer.prepare_features_multi(test_df)
        except ValueError as e:
            # 数据不足或目标列缺失，跳过此实验
            raise ValueError(f"多输出训练数据准备失败: {e}")

        # 检查数据是否有效
        if len(X_train) == 0 or len(X_val) == 0 or len(X_test) == 0:
            raise ValueError(f"数据集为空: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")

        # 训练多输出模型
        if algorithm == "AutoGluon":
            if not self.train_config.enable_autogluon:
                raise ValueError("AutoGluon 已在配置中禁用")
            if not check_autogluon_available():
                raise ImportError("AutoGluon 未安装")
            
        results = trainer.train_model(
            model_name=algorithm,
            X_train=X_train,
            Y_train=Y_train,
            X_val=X_val,
            Y_val=Y_val,
            X_test=X_test,
            Y_test=Y_test,
            hyperparams=hyperparams,
        )

        # 取平均指标作为整体结果
        first_result = list(results.values())[0]
        exp_result = ExperimentResult(
            experiment_id=self.experiment_id,
            mode=mode,
            algorithm=algorithm,
            metrics=first_result.metrics,
            val_metrics=first_result.val_metrics,
            model_config={
                "hyperparams": first_result.hyperparams,
                "feature_config": {"experiment_id": mode_config.feature_experiment},
                "feature_names": feature_names,
                "target_cols": target_cols,
            },
        )

        return exp_result

    def run_city_multi_output_experiment(
        self,
        city_df: pd.DataFrame,
        mode: str,
        algorithm: str,
        city: str,
        target_cols: List[str],
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> ExperimentResult:
        """
        运行城市级多输出实验（CTM, CHM）

        Args:
            city_df: 城市数据
            mode: 预测模式
            algorithm: 算法名称
            city: 城市名
            target_cols: 目标变量列表
            hyperparams: 超参数

        Returns:
            实验结果
        """
        from ...training.core.multi_output_trainer import MultiOutputTrainer

        mode_config = get_mode_config(mode)

        # 特征工程（保留其他目标列）
        additional_targets = target_cols[1:] if len(target_cols) > 1 else []
        fe = FeatureEngineer(target_col=target_cols[0], additional_targets=additional_targets)
        df_processed = fe.run(
            city_df.copy(),
            experiment_id=mode_config.feature_experiment,
            target_transform=self.train_config.target_transform,
            forecast_horizon=mode_config.forecast_horizon,
        )

        # 数据分割
        train_df, val_df, test_df = self.data_splitter.split(df_processed)

        # 准备多输出特征
        trainer = MultiOutputTrainer(
            target_cols=target_cols,
            target_transform=self.train_config.target_transform,
        )
        
        try:
            X_train, Y_train, feature_names = trainer.prepare_features_multi(train_df)
            X_val, Y_val, _ = trainer.prepare_features_multi(val_df)
            X_test, Y_test, _ = trainer.prepare_features_multi(test_df)
        except ValueError as e:
            # 数据不足或目标列缺失，跳过此实验
            raise ValueError(f"城市 {city} 多输出训练数据准备失败: {e}")

        # 检查数据是否有效
        if len(X_train) == 0 or len(X_val) == 0 or len(X_test) == 0:
            raise ValueError(f"城市 {city} 数据集为空: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")

# 训练多输出模型
        if algorithm == "AutoGluon":
            if not self.train_config.enable_autogluon:
                raise ValueError("AutoGluon 已在配置中禁用")
            if not check_autogluon_available():
                raise ImportError("AutoGluon 未安装")
        
        results = trainer.train_model(
            model_name=algorithm,
            X_train=X_train,
            Y_train=Y_train,
            X_val=X_val,
            Y_val=Y_val,
            X_test=X_test,
            Y_test=Y_test,
            hyperparams=hyperparams,
        )

        first_result = list(results.values())[0]
        exp_result = ExperimentResult(
            experiment_id=f"{self.experiment_id}_{city}",
            mode=f"{mode}_{city}",
            algorithm=algorithm,
            metrics=first_result.metrics,
            val_metrics=first_result.val_metrics,
            model_config={
                "hyperparams": first_result.hyperparams,
                "feature_config": {"experiment_id": mode_config.feature_experiment},
                "feature_names": feature_names,
                "target_cols": target_cols,
                "city": city,
            },
        )

        return exp_result

    def run_city_separate_experiment(
        self,
        city_df: pd.DataFrame,
        mode: str,
        algorithm: str,
        city: str,
        target_col: str,
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> ExperimentResult:
        """
        运行城市级独立模型实验（CTS, CHS）

        Args:
            city_df: 城市数据
            mode: 预测模式
            algorithm: 算法名称
            city: 城市名
            target_col: 目标变量名
            hyperparams: 超参数

        Returns:
            实验结果
        """
        mode_config = get_mode_config(mode)

        fe = FeatureEngineer(target_col=target_col)
        df_processed = fe.run(
            city_df.copy(),
            experiment_id=mode_config.feature_experiment,
            target_transform=self.train_config.target_transform,
            forecast_horizon=mode_config.forecast_horizon,
        )

        train_df, val_df, test_df = self.data_splitter.split(df_processed)

        trainer = BaseTrainer(
            target_col=target_col,
            target_transform=self.train_config.target_transform,
        )

        X_train, y_train, feature_names = trainer.prepare_features(train_df, is_train=True)
        X_val, y_val, _ = trainer.prepare_features(val_df, is_train=False)
        X_test, y_test, _ = trainer.prepare_features(test_df, is_train=False)

        if algorithm == "AutoGluon":
            if not self.train_config.enable_autogluon:
                raise ValueError("AutoGluon 已在配置中禁用")
            if not check_autogluon_available():
                raise ImportError("AutoGluon 未安装")

            ag_trainer = AutoGluonTrainer(
                target_col=target_col,
                target_transform=self.train_config.target_transform,
                time_limit=hyperparams.get("time_limit", 300) if hyperparams else 300,
                presets=hyperparams.get("presets", "medium_quality") if hyperparams else "medium_quality",
            )
            model_result = ag_trainer.train(
                X_train=X_train, y_train=y_train,
                X_val=X_val, y_val=y_val,
                X_test=X_test, y_test=y_test,
            )
        else:
            model_result = trainer.train_model(
                model_name=algorithm,
                X_train=X_train, y_train=y_train,
                X_val=X_val, y_val=y_val,
                X_test=X_test, y_test=y_test,
                hyperparams=hyperparams,
            )

        exp_result = ExperimentResult(
            experiment_id=f"{self.experiment_id}_{city}_{target_col}",
            mode=f"{mode}_{city}_{target_col}",
            algorithm=algorithm,
            metrics=model_result.metrics,
            val_metrics=model_result.val_metrics,
            model_config={
                "hyperparams": model_result.hyperparams,
                "feature_config": {"experiment_id": mode_config.feature_experiment},
                "feature_names": feature_names,
                "target_col": target_col,
                "city": city,
            },
        )

        return exp_result

    def run_single_experiment(
        self,
        df: pd.DataFrame,
        mode: str,
        algorithm: str,
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> ExperimentResult:
        """
        运行单次实验

        Args:
            df: 原始数据
            mode: 预测模式
            algorithm: 算法名称
            hyperparams: 超参数

        Returns:
            实验结果
        """
        mode_config = get_mode_config(mode)

        # 特征工程
        df_processed = self.feature_engineer.run(
            df.copy(),
            experiment_id=mode_config.feature_experiment,
            target_transform=self.train_config.target_transform,
            forecast_horizon=mode_config.forecast_horizon,
        )

        # 数据分割
        train_df, val_df, test_df = self.data_splitter.split(df_processed)

        # 准备特征
        trainer = BaseTrainer(
            target_col=self.train_config.target_col,
            target_transform=self.train_config.target_transform,
        )

        X_train, y_train, feature_names = trainer.prepare_features(train_df, is_train=True)
        X_val, y_val, _ = trainer.prepare_features(val_df, is_train=False)
        X_test, y_test, _ = trainer.prepare_features(test_df, is_train=False)

        # 训练模型（支持 AutoGluon AutoML）
        if algorithm == "AutoGluon":
            if not self.train_config.enable_autogluon:
                raise ValueError("AutoGluon 已在配置中禁用，请设置 enable_autogluon=True 以启用")
            if not check_autogluon_available():
                raise ImportError("AutoGluon 未安装，请运行: pip install autogluon")

            # AutoGluon 训练
            ag_trainer = AutoGluonTrainer(
                target_col=self.train_config.target_col,
                target_transform=self.train_config.target_transform,
                time_limit=hyperparams.get("time_limit", 300) if hyperparams else 300,
                presets=hyperparams.get("presets", "medium_quality") if hyperparams else "medium_quality",
                eval_metric=hyperparams.get("eval_metric", "rmse") if hyperparams else "rmse",
            )
            model_result = ag_trainer.train(
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                X_test=X_test,
                y_test=y_test,
            )
        else:
            # 标准 sklearn 训练
            model_result = trainer.train_model(
                model_name=algorithm,
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                X_test=X_test,
                y_test=y_test,
                hyperparams=hyperparams,
            )

        # 创建实验结果
        exp_result = ExperimentResult(
            experiment_id=self.experiment_id,
            mode=mode,
            algorithm=algorithm,
            metrics=model_result.metrics,
            val_metrics=model_result.val_metrics,
            model_config={
                "hyperparams": model_result.hyperparams,
                "feature_config": {"experiment_id": mode_config.feature_experiment},
                "feature_names": feature_names,
            },
        )

        return exp_result

    def run_mode_experiments(
        self,
        df: pd.DataFrame,
        mode: str,
        algorithms: Optional[List[str]] = None,
    ) -> List[ExperimentResult]:
        """
        运行某模式的所有实验

        Args:
            df: 原始数据
            mode: 预测模式
            algorithms: 算法列表，None则使用默认算法

        Returns:
            实验结果列表
        """
        if algorithms is None:
            if self.train_config.enable_autogluon:
                algorithms = Algorithm.ALL_ALGORITHMS
            else:
                algorithms = [alg for alg in Algorithm.ALL_ALGORITHMS if alg != Algorithm.AUTOGluon]

        mode_config = get_mode_config(mode)
        logger.info(f"运行模式 {mode} 的实验，算法: {algorithms}")

        mode_results = []

        if mode_config.city_level:
            # 城市级模式: CTM, CTS, CHM, CHS
            mode_results = self._run_city_level_experiments(df, mode, algorithms, mode_config)
        else:
            # 全局模式: GTM, GTS, GHM, GHS
            mode_results = self._run_global_experiments(df, mode, algorithms, mode_config)

        return mode_results

    def _run_global_experiments(
        self,
        df: pd.DataFrame,
        mode: str,
        algorithms: List[str],
        mode_config,
    ) -> List[ExperimentResult]:
        """运行全局级实验"""
        mode_results = []

        if mode_config.multi_output:
            # 全局多输出: GTM, GHM
            for algorithm in algorithms:
                try:
                    logger.info(f"  训练全局多输出模型: {algorithm}")
                    result = self.run_multi_output_experiment(df, mode, algorithm, mode_config.target_cols)
                    mode_results.append(result)
                    self.results.append(result)
                    self.evaluator.add_result(result)
                    logger.info(f"  完成: val_rmse={result.val_metrics.get('rmse', 0):.4f}")
                except Exception as e:
                    logger.error(f"  失败: {algorithm}, 错误: {e}")
        else:
            # 全局独立模型: GTS, GHS - 为每个目标单独训练
            for target_col in mode_config.target_cols:
                logger.info(f"\n  训练目标: {target_col}")
                for algorithm in algorithms:
                    try:
                        logger.info(f"    算法: {algorithm}")
                        result = self.run_separate_experiment(df, mode, algorithm, target_col)
                        mode_results.append(result)
                        self.results.append(result)
                        self.evaluator.add_result(result)
                        logger.info(f"    完成: val_rmse={result.val_metrics.get('rmse', 0):.4f}")
                    except Exception as e:
                        logger.error(f"    失败: {algorithm}, 错误: {e}")

        return mode_results

    def _run_city_level_experiments(
        self,
        df: pd.DataFrame,
        mode: str,
        algorithms: List[str],
        mode_config,
    ) -> List[ExperimentResult]:
        """运行城市级实验"""
        mode_results = []
        cities = df["city_name"].unique()

        for city in cities:
            city_df = df[df["city_name"] == city].copy()
            if len(city_df) < 100:
                logger.warning(f"{city} 数据不足，跳过")
                continue

            logger.info(f"\n  训练城市模型: {city}")

            if mode_config.multi_output:
                # 城市级多输出: CTM, CHM
                for algorithm in algorithms:
                    try:
                        logger.info(f"    算法: {algorithm}")
                        result = self.run_city_multi_output_experiment(city_df, mode, algorithm, city, mode_config.target_cols)
                        mode_results.append(result)
                        self.results.append(result)
                        self.evaluator.add_result(result)
                        logger.info(f"    完成: val_rmse={result.val_metrics.get('rmse', 0):.4f}")
                    except Exception as e:
                        logger.error(f"    失败: {algorithm}, 错误: {e}")
            else:
                # 城市级独立模型: CTS, CHS - 为每个目标单独训练
                for target_col in mode_config.target_cols:
                    logger.info(f"\n    训练目标: {target_col}")
                    for algorithm in algorithms:
                        try:
                            logger.info(f"      算法: {algorithm}")
                            result = self.run_city_separate_experiment(city_df, mode, algorithm, city, target_col)
                            mode_results.append(result)
                            self.results.append(result)
                            self.evaluator.add_result(result)
                            logger.info(f"      完成: val_rmse={result.val_metrics.get('rmse', 0):.4f}")
                        except Exception as e:
                            logger.error(f"      失败: {algorithm}, 错误: {e}")

        return mode_results

    def run_all_experiments(
        self,
        df: pd.DataFrame,
        modes: Optional[List[str]] = None,
        algorithms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        运行所有实验

        Args:
            df: 原始数据
            modes: 模式列表，None则所有8种模式
            algorithms: 算法列表

        Returns:
            实验汇总
        """
        if modes is None:
            modes = list_modes()

        # 计算实际的算法数量（考虑enable_autogluon配置）
        if algorithms is None:
            alg_count = len(Algorithm.ALL_ALGORITHMS if self.train_config.enable_autogluon
                          else [alg for alg in Algorithm.ALL_ALGORITHMS if alg != Algorithm.AUTOGluon])
        else:
            alg_count = len(algorithms)

        logger.info(f"开始批量实验: {len(modes)} 种模式 × {alg_count} 种算法")

        # 运行各模式实验
        for mode in modes:
            logger.info(f"\n{'='*50}")
            logger.info(f"模式: {mode}")
            logger.info(f"{'='*50}")
            self.run_mode_experiments(df, mode, algorithms)

        # 选择最佳配置
        best_configs = self.selector.select(self.results)
        global_best = self.selector.select_global_best(self.results)

        # 检查是否有有效的实验结果
        if not self.results:
            logger.warning("所有实验都失败了，没有有效的实验结果")
            return {
                "total_experiments": 0,
                "modes": [],
                "algorithms": [],
                "mode_best": {},
                "global_best": None,
                "error": "所有实验都失败了",
            }

        # 保存结果
        self.manifest.save_manifest(self.results, {"total_modes": len(modes)})
        self.manifest.save_best_config(best_configs, global_best_mode=global_best[0] if global_best else None)

        # 生成报告
        self.reporter.generate_report(self.experiment_id, self.results, best_configs)
        self.reporter.generate_comparison_charts(self.results)
        self.reporter.save_results_csv(self.results)

        summary = self.evaluator.generate_summary()
        logger.info(f"\n实验完成! 汇总: {summary}")

        return summary

    def get_best_config(self, mode: Optional[str] = None) -> Optional[Any]:
        """获取最佳配置"""
        if mode:
            configs = self.selector.select(self.results, [mode])
            return configs.get(mode)

        global_best = self.selector.select_global_best(self.results)
        return global_best[1] if global_best else None
