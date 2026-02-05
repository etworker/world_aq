#!/usr/bin/env python
"""
Demo: 生产模型训练

使用实验找到的最佳配置训练生产模型
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("Demo: 训练生产模型")
print("=" * 60)

print("\n[1/3] 检查最佳配置文件...")
# 通常最佳配置文件由 experiment 命令生成
# 这里演示如何指定配置

config_example = """
{
  "GTS": {
    "algorithm": "GradientBoosting",
    "hyperparams": {"max_iter": 200, "max_depth": 5},
    "feature_config": {"experiment_id": "weather"}
  }
}
"""
print("  最佳配置示例:")
print(config_example)

# 实际训练需要先有配置文件
# 这里演示 Pipeline 的用法
print("\n[2/3] 初始化生产训练流水线...")
from src.training.production import ProductionPipeline

# 注意: 需要实际的最佳配置文件才能运行
# pipeline = ProductionPipeline(config_path="models/experiments/EXP_xxx/best_config.json")

print("\n[3/3] 训练模型...")
print("  pipeline.train_mode('GTS', data_path='...')")
print("  或使用 CLI: python -m src.cli train --config <config_path>")

print("\n" + "=" * 60)
print("提示: 先运行 experiment 命令生成最佳配置文件")
print("      然后再运行 train 命令训练生产模型")
print("=" * 60)
