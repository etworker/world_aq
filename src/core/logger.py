"""
统一日志管理 - 使用 loguru
"""

import os
import sys
from pathlib import Path
from loguru import logger

# 移除默认处理器
logger.remove()

# 屏幕日志：时间(HH:mm:ss.ms) + 级别首字母 + 消息
logger.add(
    lambda msg: print(msg, end=""),
    colorize=True,
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: ^1}</level> | <level>{message}</level>")

# 文件日志：时间(YYYYMMDD) + 级别首字母 + 消息
os.makedirs("logs", exist_ok=True)
logger.add(
    "logs/world_aq.log",
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
    format="{time:YYYYMMDD} | {level: ^1} | {message}"
)


class LoggerManager:
    """日志管理器（兼容旧接口，实际使用 loguru）"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str = "world_aq", log_dir: str = "logs", level=None, log_to_file: bool = True):
        """获取 logger（兼容旧接口）"""
        return logger

    @classmethod
    def setup_training_logger(cls, log_dir: str = "logs"):
        """设置训练专用logger（兼容旧接口）"""
        return logger

    @classmethod
    def setup_experiment_logger(cls, log_dir: str = "logs"):
        """设置实验专用logger（兼容旧接口）"""
        return logger


def get_logger(name: str = "world_aq"):
    """
    获取 logger（兼容旧接口，实际返回 loguru logger）
    
    Args:
        name: logger名称（loguru中不使用，仅作兼容）
    
    Returns:
        loguru logger
    """
    return logger


def setup_training_logger(log_dir: str = "logs"):
    """设置训练专用logger（兼容旧接口）"""
    return logger


def setup_experiment_logger(log_dir: str = "logs"):
    """设置实验专用logger（兼容旧接口）"""
    return logger
