"""
项目全局常量配置文件

包含数据路径、文件位置等常量定义
"""

import os
import os.path as osp
import sys

# ============ 路径配置 ============
_root_dir = osp.abspath(osp.join(osp.dirname(osp.abspath(__file__)), "../.."))
_data_dir = osp.join(_root_dir, "data")

if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

# ============ 数据文件路径 ============
# ISD历史站点数据 (NOAA)
ISD_HISTORY_PATH: str = osp.join(_data_dir, "info/isd-history.csv")

# 世界城市数据
WORLDCITIES_PATH: str = osp.join(_data_dir, "info/worldcities.csv")

# 城市社会经济特征数据
CITY_FEATURES_PATH: str = osp.join(_data_dir, "info/city_socioeconomic_features.csv")

# 数据缓存目录
CACHE_DIR: str = osp.join(_data_dir, "cache")
NOAA_CACHE_DIR: str = osp.join(_data_dir, "cache/noaa")
OPENAQ_CACHE_DIR: str = osp.join(_data_dir, "cache/openaq")

# 处理后数据目录
PROCESSED_DIR: str = osp.join(_data_dir, "processed")
NOAA_PROCESSED_DIR: str = osp.join(_data_dir, "processed/noaa")
OPENAQ_PROCESSED_DIR: str = osp.join(_data_dir, "processed/openaq")
MERGED_DIR: str = osp.join(_data_dir, "processed/merged")

# 模型输出目录
MODELS_DIR: str = osp.join(_root_dir, "models")
EXPERIMENTS_DIR: str = osp.join(MODELS_DIR, "experiments")
PRODUCTION_DIR: str = osp.join(MODELS_DIR, "production")

# ============ NOAA GSOD 配置 ============
NOAA_S3_BUCKET: str = "noaa-gsod-pds"
NOAA_BASE_URL: str = "https://noaa-gsod-pds.s3.amazonaws.com"

# 数据缺失值标记
NOAA_MISSING_VALUES = {
    "TEMP": 9999.9,
    "DEWP": 9999.9,
    "SLP": 9999.9,
    "STP": 999.9,
    "VISIB": 999.9,
    "WDSP": 999.9,
    "MXSPD": 999.9,
    "GUST": 999.9,
    "MAX": 9999.9,
    "MIN": 9999.9,
    "PRCP": 99.99,
    "SNDP": 999.9,
}

# ============ OpenAQ 配置 ============
OPENAQ_API_BASE: str = "https://api.openaq.org/v3"
OPENAQ_S3_BUCKET: str = "openaq-data-archive"
OPENAQ_S3_BASE_URL: str = "https://openaq-data-archive.s3.amazonaws.com"

# ============ 默认城市和年份配置 ============
# 默认处理的城市列表 (城市名, 国家代码)
DEFAULT_CITIES: list[tuple[str, str]] = [
    ("New York", "US"),
    ("Los Angeles", "US"),
    ("Chicago", "US"),
    ("Houston", "US"),
    ("San Francisco", "US"),
    ("Beijing", "CN"),
]

# 默认年份范围
DEFAULT_START_YEAR: int = 2022
DEFAULT_END_YEAR: int = 2025

# 训练用的核心城市（用于城市独立模型实验）
TRAINING_CORE_CITIES: list[str] = ["Beijing", "Los_Angeles", "Houston"]


def check_required_files() -> None:
    """
    检查必要的输入文件是否存在

    Raises:
        FileNotFoundError: 如果有必要文件缺失
    """
    required_files = {
        "ISD历史站点数据": ISD_HISTORY_PATH,
        "城市数据": WORLDCITIES_PATH,
    }

    missing_files = []
    for name, path in required_files.items():
        if not osp.exists(path):
            missing_files.append(f"  - {name}: {path}")

    if missing_files:
        raise FileNotFoundError(
            "\n" + "=" * 70 + "\n"
            "错误：以下必要数据文件不存在：\n" + "\n".join(missing_files) + "\n" + "=" * 70 + "\n"
            "请按以下方式获取数据文件：\n"
            "  1. isd-history.csv: 从 NOAA 官网下载\n"
            "     https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv\n"
            "  2. worldcities.csv: 从 SimpleMaps 下载\n"
            "     https://simplemaps.com/data/world-cities\n"
            "并将文件放置到 data/info/ 目录下。\n"
            "=" * 70
        )


def ensure_dirs() -> None:
    """确保必要的目录存在"""
    dirs = [
        CACHE_DIR,
        NOAA_CACHE_DIR,
        OPENAQ_CACHE_DIR,
        PROCESSED_DIR,
        NOAA_PROCESSED_DIR,
        OPENAQ_PROCESSED_DIR,
        MERGED_DIR,
        EXPERIMENTS_DIR,
        PRODUCTION_DIR,
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
