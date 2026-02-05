#!/usr/bin/env python
"""
Demo: 实验功能

运行模型实验，探索最佳配置
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.experiment import ExperimentRunner
from src.data.storage.loader import load_training_data
from src.config.settings import MERGED_DIR
from src.core.config import TrainConfig


def demo_simple_experiment():
    """示例1: 简单实验 - 快速验证（推荐用于开发测试）"""
    print("\n" + "=" * 60)
    print("示例1: 简单实验 - 快速验证")
    print("=" * 60)

    # 加载数据
    print(f"\n[1/2] 加载数据...")
    df = load_training_data()
    print(f"  ✅ 数据加载完成: {len(df)} 行, {df['city_name'].nunique()} 个城市")

    # 运行实验
    print("\n[2/2] 运行实验...")
    print("  模式: GTS (全局_当天_独立模型)")
    print("  算法: RandomForest, GradientBoosting")
    print("  预计耗时: ~1-2分钟")

    runner = ExperimentRunner()
    summary = runner.run_all_experiments(
        df=df,
        modes=["GTS"],
        algorithms=["RandomForest", "GradientBoosting"],
    )

    print_results(runner, summary)


def demo_standard_experiment():
    """示例2: 标准实验 - 推荐配置（平衡速度和效果）"""
    print("\n" + "=" * 60)
    print("示例2: 标准实验 - 推荐配置")
    print("=" * 60)

    print(f"\n[1/2] 加载数据...")
    df = load_training_data()
    print(f"  ✅ 数据加载完成: {len(df)} 行")

    print("\n[2/2] 运行实验...")
    print("  模式: GTS, GHS (全局_当天/历史_独立模型)")
    print("  算法: Ridge, RandomForest, GradientBoosting")
    print("  预计耗时: ~5-10分钟")

    runner = ExperimentRunner()
    summary = runner.run_all_experiments(
        df=df,
        modes=["GTS", "GHS"],
        algorithms=["Ridge", "RandomForest", "GradientBoosting"],
    )

    print_results(runner, summary)


def demo_full_experiment_no_autogluon():
    """示例3: 全量实验 - 不含 AutoGluon（完整探索）"""
    print("\n" + "=" * 60)
    print("示例3: 全量实验 - 不含 AutoGluon")
    print("=" * 60)

    print(f"\n[1/2] 加载数据...")
    df = load_training_data()
    print(f"  ✅ 数据加载完成: {len(df)} 行")

    print("\n[2/2] 运行实验...")
    print("  模式: 全部8种模式（包括多输出GTM/GHM/CTM/CHM）")
    print("  算法: Ridge, Lasso, ElasticNet, RandomForest, GradientBoosting")
    print("  预计耗时: ~30-60分钟")

    # 禁用 AutoGluon
    train_config = TrainConfig(enable_autogluon=False)

    runner = ExperimentRunner(train_config=train_config)
    summary = runner.run_all_experiments(
        df=df,
        modes=None,       # None = 所有8种模式
        algorithms=None,  # None = 所有算法（不含AutoGluon）
    )

    print_results(runner, summary)


def demo_full_experiment_with_autogluon():
    """示例4: 全量实验 - 包含 AutoGluon（最完整但最慢）"""
    print("\n" + "=" * 60)
    print("示例4: 全量实验 - 包含 AutoGluon")
    print("=" * 60)

    print(f"\n[1/2] 加载数据...")
    df = load_training_data()
    print(f"  ✅ 数据加载完成: {len(df)} 行")

    print("\n[2/2] 运行实验...")
    print("  模式: 全部8种模式（包括多输出GTM/GHM/CTM/CHM）")
    print("  算法: 所有算法 + AutoGluon")
    print("  预计耗时: ~60-120分钟")

    # 启用 AutoGluon，限制时间
    train_config = TrainConfig(
        enable_autogluon=True,
        autogluon_time_limit=300,  # 5分钟
    )

    runner = ExperimentRunner(train_config=train_config)
    summary = runner.run_all_experiments(
        df=df,
        modes=None,       # None = 所有8种模式
        algorithms=None,  # 包含 AutoGluon
    )

    print_results(runner, summary)


def demo_specific_cities():
    """示例5: 仅使用特定城市数据进行实验"""
    print("\n" + "=" * 60)
    print("示例5: 特定城市实验")
    print("=" * 60)

    print(f"\n[1/2] 加载数据（北京和纽约对比）...")
    df = load_training_data(cities=["Beijing", "New_York"])
    print(f"  ✅ 数据加载完成: {len(df)} 行, {df['city_name'].nunique()} 个城市")

    print("\n[2/2] 运行实验...")
    runner = ExperimentRunner()
    summary = runner.run_all_experiments(
        df=df,
        modes=["GTS"],
        algorithms=["RandomForest", "GradientBoosting"],
    )

    print_results(runner, summary)


def print_results(runner, summary):
    """打印实验结果"""
    import os.path as osp
    from pathlib import Path

    # 获取项目根目录
    project_root = Path(__file__).parent.parent.absolute()

    def to_rel_path(abs_path):
        """将绝对路径转换为相对路径"""
        try:
            return osp.relpath(abs_path, project_root)
        except ValueError:
            return abs_path

    print("\n" + "-" * 60)
    print("实验结果:")
    print("-" * 60)
    print(f"  实验ID: {runner.experiment_id}")
    print(f"  输出目录: {to_rel_path(runner.output_dir)}")
    print(f"  总实验数: {summary.get('total_experiments', 0)}")

    # 显示最佳模型
    global_best = summary.get('global_best', {})
    if global_best:
        print(f"\n  🏆 最佳模型:")
        print(f"     模式: {global_best.get('mode', 'N/A')}")
        print(f"     算法: {global_best.get('algorithm', 'N/A')}")
        print(f"     验证RMSE: {global_best.get('val_rmse', 'N/A'):.4f}")
        print(f"     测试RMSE: {global_best.get('test_rmse', 'N/A'):.4f}")

    print("\n  输出文件:")
    print(f"     - 实验清单: {to_rel_path(osp.join(runner.output_dir, 'manifest.json'))}")
    print(f"     - 最佳配置: {to_rel_path(osp.join(runner.output_dir, 'best_config.json'))}")
    print(f"     - 实验报告: {to_rel_path(osp.join(runner.output_dir, 'report.md'))}")
    print(f"     - 对比图表: {to_rel_path(osp.join(runner.output_dir, 'figures/comparison_charts.png'))}")


if __name__ == "__main__":
    print("=" * 60)
    print("Demo: 运行基础实验")
    print("=" * 60)

    # 运行所有示例:

    # demo_simple_experiment()                 # 示例1: 简单实验（~1-2分钟）
    # demo_standard_experiment()               # 示例2: 标准实验（~5-10分钟）
    # demo_full_experiment_no_autogluon()      # 示例3: 全量实验无AG（~15-30分钟）
    demo_full_experiment_with_autogluon()     # 示例4: 全量实验含AG（~30-60分钟）
    # demo_specific_cities()                   # 示例5: 特定城市实验

    print("\n" + "=" * 60)
    print("提示: 修改 __main__ 中的函数调用来运行不同示例")
    print("=" * 60)

    print("""
【实验配置参考】

1. 简单实验 (示例1)
   模式: GTS (全局_当天_独立模型)
   算法: RandomForest, GradientBoosting
   耗时: ~1-2分钟

2. 标准实验 (示例2)
   模式: GTS, GHS (全局_当天/历史_独立模型)
   算法: Ridge, RandomForest, GradientBoosting
   耗时: ~5-10分钟

3. 全量实验 (示例3)
   模式: 所有8种模式
   算法: Ridge, Lasso, ElasticNet, RF, GB
   耗时: ~30-60分钟

4. 含AutoGluon (示例4)
   模式: 所有8种模式
   算法: 所有 + AutoGluon
   耗时: ~60-120分钟

【8种预测模式说明】
- GTM: 全局_当天_多输出  - 所有城市共用，当日天气预测多污染物
- GTS: 全局_当天_独立模型 - 所有城市共用，当日天气各污染物独立模型
- GHM: 全局_历史_多输出  - 所有城市共用，历史+当日预测多污染物
- GHS: 全局_历史_独立模型 - 所有城市共用，历史+当日各污染物独立模型
- CTM: 城市级_当天_多输出 - 每个城市独立，当日天气预测多污染物
- CTS: 城市级_当天_独立模型 - 每个城市独立，当日天气各污染物独立模型
- CHM: 城市级_历史_多输出 - 每个城市独立，历史+当日预测多污染物
- CHS: 城市级_历史_独立模型 - 每个城市独立，历史+当日各污染物独立模型
""")
