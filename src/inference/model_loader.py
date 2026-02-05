"""
模型加载模块

提供模型加载和发现功能
"""

import os
import os.path as osp
from pathlib import Path
from typing import Dict, List, Optional, Any

import joblib

from ..config import get_production_dir, MODELS_DIR

from loguru import logger


class ModelLoader:
    """模型加载器"""

    @staticmethod
    def load_model(model_path: str) -> Dict[str, Any]:
        """
        加载模型

        Args:
            model_path: 模型文件路径

        Returns:
            模型信息字典
        """
        if not osp.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        model_info = joblib.load(model_path)
        logger.info(f"加载模型: {model_path}")
        return model_info

    @staticmethod
    def find_latest_model(mode: Optional[str] = None) -> Optional[str]:
        """
        查找最新的模型

        Args:
            mode: 指定模式，None则查找所有模式中最新的

        Returns:
            模型文件路径
        """
        if mode:
            mode_dir = get_production_dir(mode)
            if not osp.exists(mode_dir):
                return None

            # 找最新的版本目录
            versions = sorted([d for d in os.listdir(mode_dir) if osp.isdir(osp.join(mode_dir, d))])
            if not versions:
                return None

            latest_version = versions[-1]
            model_path = osp.join(mode_dir, latest_version, "model.joblib")
            return model_path if osp.exists(model_path) else None

        else:
            # 遍历所有模式找最新
            from ..config import PredictionMode

            latest_models = []
            for mode in PredictionMode.ALL_MODES:
                model_path = ModelLoader.find_latest_model(mode)
                if model_path:
                    mtime = osp.getmtime(model_path)
                    latest_models.append((mtime, model_path))

            if not latest_models:
                return None

            # 返回最新的
            latest_models.sort(reverse=True)
            return latest_models[0][1]

    @staticmethod
    def list_available_models() -> Dict[str, List[str]]:
        """
        列出所有可用模型

        Returns:
            {mode: [version1, version2, ...]}
        """
        from ..config import PredictionMode

        available = {}
        for mode in PredictionMode.ALL_MODES:
            mode_dir = get_production_dir(mode)
            if osp.exists(mode_dir):
                versions = sorted([d for d in os.listdir(mode_dir) if osp.isdir(osp.join(mode_dir, d))])
                if versions:
                    available[mode] = versions

        return available

    @staticmethod
    def get_model_info(model_path: str) -> Dict[str, Any]:
        """
        获取模型信息（不加载模型）

        Args:
            model_path: 模型路径

        Returns:
            模型信息
        """
        model_dir = osp.dirname(model_path)
        config_path = osp.join(model_dir, "config.json")
        metadata_path = osp.join(model_dir, "metadata.json")

        info = {
            "model_path": model_path,
            "model_dir": model_dir,
        }

        # 加载配置
        if osp.exists(config_path):
            import json

            with open(config_path, "r", encoding="utf-8") as f:
                info["config"] = json.load(f)

        # 加载元数据
        if osp.exists(metadata_path):
            import json

            with open(metadata_path, "r", encoding="utf-8") as f:
                info["metadata"] = json.load(f)

        return info


def list_models() -> None:
    """便捷函数：列出所有可用模型"""
    models = ModelLoader.list_available_models()

    print("可用模型:")
    print("-" * 50)

    for mode, versions in models.items():
        print(f"\n{mode}:")
        for version in versions:
            model_dir = get_production_dir(mode, version)
            print(f"  - {version}")

    if not models:
        print("暂无可用模型，请先训练模型")
