"""
路径管理工具
提供统一的路径获取方法
"""

import os.path as osp
from datetime import datetime
from typing import Optional

from .settings import (
    _root_dir,
    _data_dir,
    MODELS_DIR,
    EXPERIMENTS_DIR,
    PRODUCTION_DIR,
    MERGED_DIR,
)


def get_project_root() -> str:
    """获取项目根目录"""
    return _root_dir


def get_data_dir() -> str:
    """获取数据目录"""
    return _data_dir


def get_merged_data_path(city: Optional[str] = None, year: Optional[int] = None) -> str:
    """
    获取合并数据路径

    Args:
        city: 城市名，为None则返回目录
        year: 年份，为None则返回城市目录

    Returns:
        数据文件或目录路径
    """
    if city is None:
        return MERGED_DIR
    city_dir = osp.join(MERGED_DIR, city)
    if year is None:
        return city_dir
    return osp.join(city_dir, f"{year}.csv")


def get_experiment_dir(experiment_id: Optional[str] = None) -> str:
    """
    获取实验目录

    Args:
        experiment_id: 实验ID，为None则返回根目录

    Returns:
        实验目录路径
    """
    if experiment_id is None:
        return EXPERIMENTS_DIR
    return osp.join(EXPERIMENTS_DIR, experiment_id)


def get_production_dir(mode: Optional[str] = None, version: Optional[str] = None) -> str:
    """
    获取生产模型目录

    Args:
        mode: 预测模式，如 'GTM'
        version: 版本时间戳，如 '20260205_210000'

    Returns:
        生产模型目录路径
    """
    if mode is None:
        return PRODUCTION_DIR
    mode_dir = osp.join(PRODUCTION_DIR, mode)
    if version is None:
        return mode_dir
    return osp.join(mode_dir, version)


def generate_timestamp() -> str:
    """生成时间戳"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_experiment_id() -> str:
    """生成实验ID"""
    import uuid

    return f"{generate_timestamp()}_{uuid.uuid4().hex[:8]}"
