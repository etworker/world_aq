#!/usr/bin/env python
"""
Demo: 运行基础实验 - 逐个运行
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from demo_03_experiment_basic import (
    demo_simple_experiment,
    demo_standard_experiment,
    demo_full_experiment_no_autogluon,
    demo_full_experiment_with_autogluon,
    demo_specific_cities,
)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行实验 demo")
    parser.add_argument(
        "--demo",
        type=str,
        choices=["simple", "standard", "full-no-ag", "full-with-ag", "cities", "all"],
        default="simple",
        help="选择要运行的 demo",
    )

    args = parser.parse_args()

    if args.demo == "simple":
        demo_simple_experiment()
    elif args.demo == "standard":
        demo_standard_experiment()
    elif args.demo == "full-no-ag":
        demo_full_experiment_no_autogluon()
    elif args.demo == "full-with-ag":
        demo_full_experiment_with_autogluon()
    elif args.demo == "cities":
        demo_specific_cities()
    elif args.demo == "all":
        demo_simple_experiment()
        demo_standard_experiment()
        demo_full_experiment_no_autogluon()
        demo_full_experiment_with_autogluon()
        demo_specific_cities()