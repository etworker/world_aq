"""
实验报告生成模块

生成实验报告和可视化
"""

import os.path as osp
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
import numpy as np

from ...core import ExperimentResult
from .modes import get_mode_info

from loguru import logger


class ExperimentReporter:
    """实验报告生成器"""

    def __init__(self, output_dir: str):
        """
        初始化报告生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.figures_dir = osp.join(output_dir, "figures")
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)

        # 获取项目根目录
        self.project_root = osp.abspath(osp.join(osp.dirname(__file__), "../../.."))

    def _to_relative_path(self, absolute_path: str) -> str:
        """
        将绝对路径转换为相对于项目根目录的相对路径

        Args:
            absolute_path: 绝对路径

        Returns:
            相对路径
        """
        try:
            rel_path = osp.relpath(absolute_path, self.project_root)
            return rel_path
        except ValueError:
            # 如果无法转换为相对路径（例如跨驱动器），返回原路径
            return absolute_path

    def generate_report(self, experiment_id: str, results: List[ExperimentResult], best_configs: Dict[str, Any]) -> str:
        """
        生成实验报告

        Args:
            experiment_id: 实验ID
            results: 实验结果
            best_configs: 最佳配置

        Returns:
            报告文件路径
        """
        lines = [
            f"# 实验报告: {experiment_id}\n",
            f"**实验时间**: {experiment_id[:15]}\n",
            f"**总实验数**: {len(results)}\n",
            f"**实验目录**: `{self._to_relative_path(self.output_dir)}`\n",
            "\n## 8种预测模式\n",
        ]

        # 模式说明
        modes = set(r.mode for r in results)
        for mode in sorted(modes):
            # 处理独立模型的子模式名称 (如 "GTS_pm25" -> "GTS")
            base_mode = mode.split('_')[0] if '_' in mode else mode
            info = get_mode_info(base_mode)
            lines.extend(
                [
                    f"### {mode}\n",
                    f"- **名称**: {info.get('name', 'N/A')}",
                    f"- **描述**: {info.get('description', 'N/A')}",
                    f"- **输入**: {info.get('input_features', 'N/A')}",
                    f"- **输出**: {info.get('output', 'N/A')}",
                    f"- **使用场景**: {info.get('use_case', 'N/A')}",
                    "\n",
                ]
            )

        # 各模式最佳结果
        lines.append("## 各模式最佳结果\n")
        for mode in sorted(modes):
            mode_results = [r for r in results if r.mode == mode]
            if mode_results:
                best = min(mode_results, key=lambda r: r.val_metrics.get("rmse", float("inf")))
                # 获取算法显示名称（对于 AutoGluon，显示具体子模型）
                algorithm_display = best.algorithm
                if best.algorithm == "AutoGluon":
                    best_model = best.model_config.get("hyperparams", {}).get("best_model", "Unknown")
                    algorithm_display = f"AutoGluon ({best_model})"
                
                lines.extend(
                    [
                        f"### {mode}\n",
                        f"- **最佳算法**: {algorithm_display}",
                        f"- **验证RMSE**: {best.val_metrics.get('rmse', 0):.4f}",
                        f"- **测试RMSE**: {best.metrics.get('rmse', 0):.4f}",
                        f"- **R²**: {best.metrics.get('r2', 0):.4f}",
                        "\n",
                    ]
                )

        # 全局最佳
        global_best = min(results, key=lambda r: r.val_metrics.get("rmse", float("inf")))
        # 获取算法显示名称（对于 AutoGluon，显示具体子模型）
        algorithm_display = global_best.algorithm
        if global_best.algorithm == "AutoGluon":
            best_model = global_best.model_config.get("hyperparams", {}).get("best_model", "Unknown")
            algorithm_display = f"AutoGluon ({best_model})"
        
        lines.extend(
            [
                "## 全局最佳模型\n",
                f"- **模式**: {global_best.mode}",
                f"- **算法**: {algorithm_display}",
                f"- **验证RMSE**: {global_best.val_metrics.get('rmse', 0):.4f}",
                f"- **测试RMSE**: {global_best.metrics.get('rmse', 0):.4f}",
                "\n",
            ]
        )

        # 添加输出文件信息
        lines.extend(
            [
                "## 输出文件\n",
                f"- **实验清单**: `{self._to_relative_path(osp.join(self.output_dir, 'manifest.json'))}`\n",
                f"- **最佳配置**: `{self._to_relative_path(osp.join(self.output_dir, 'best_config.json'))}`\n",
                f"- **结果CSV**: `{self._to_relative_path(osp.join(self.output_dir, 'results.csv'))}`\n",
                f"- **对比图表**: `{self._to_relative_path(osp.join(self.figures_dir, 'comparison_charts.png'))}`\n",
                "\n",
            ]
        )

        # 保存报告
        report_path = osp.join(self.output_dir, "report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"实验报告已保存: {self._to_relative_path(report_path)}")
        return report_path

    def generate_comparison_charts(self, results: List[ExperimentResult]) -> Optional[str]:
        """
        生成对比图表

        Args:
            results: 实验结果

        Returns:
            图表文件路径或None
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "sans-serif"]
            plt.rcParams["axes.unicode_minus"] = False

            fig, axes = plt.subplots(2, 2, figsize=(14, 10))

            # 准备数据
            df = pd.DataFrame(
                [
                    {
                        "mode": r.mode,
                        "algorithm": r.algorithm,
                        "val_rmse": r.val_metrics.get("rmse", np.nan),
                        "test_rmse": r.metrics.get("rmse", np.nan),
                    }
                    for r in results
                ]
            )

            # 1. 各模式最佳模型RMSE对比
            ax1 = axes[0, 0]
            mode_best = df.loc[df.groupby("mode")["val_rmse"].idxmin()]
            ax1.barh(mode_best["mode"], mode_best["val_rmse"])
            ax1.set_xlabel("Validation RMSE")
            ax1.set_title("Best Model per Mode")

            # 2. 算法对比
            ax2 = axes[0, 1]
            algo_avg = df.groupby("algorithm")["val_rmse"].mean().sort_values()
            ax2.barh(algo_avg.index, algo_avg.values)
            ax2.set_xlabel("Average Validation RMSE")
            ax2.set_title("Algorithm Comparison")

            # 3. 散点图：验证 vs 测试
            ax3 = axes[1, 0]
            ax3.scatter(df["val_rmse"], df["test_rmse"], alpha=0.6)
            ax3.set_xlabel("Validation RMSE")
            ax3.set_ylabel("Test RMSE")
            ax3.set_title("Validation vs Test Performance")

            # 4. 热力图：模式×算法
            ax4 = axes[1, 1]
            pivot = df.pivot_table(values="val_rmse", index="mode", columns="algorithm")
            sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax4)
            ax4.set_title("RMSE Heatmap")

            plt.tight_layout()

            chart_path = osp.join(self.figures_dir, "comparison_charts.png")
            plt.savefig(chart_path, dpi=150, bbox_inches="tight")
            plt.close()

            logger.info(f"对比图表已保存: {self._to_relative_path(chart_path)}")
            return chart_path

        except Exception as e:
            logger.warning(f"生成图表失败: {e}")
            return None

    def save_results_csv(self, results: List[ExperimentResult]) -> str:
        """
        保存结果为CSV

        Args:
            results: 实验结果

        Returns:
            CSV文件路径
        """
        data = []
        for r in results:
            data.append(
                {
                    "mode": r.mode,
                    "algorithm": r.algorithm,
                    "val_rmse": r.val_metrics.get("rmse"),
                    "val_mae": r.val_metrics.get("mae"),
                    "val_r2": r.val_metrics.get("r2"),
                    "test_rmse": r.metrics.get("rmse"),
                    "test_mae": r.metrics.get("mae"),
                    "test_r2": r.metrics.get("r2"),
                }
            )

        df = pd.DataFrame(data)
        csv_path = osp.join(self.output_dir, "results.csv")
        df.to_csv(csv_path, index=False)

        logger.info(f"结果CSV已保存: {self._to_relative_path(csv_path)}")
        return csv_path
