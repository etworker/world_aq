"""
配置模块

提供项目全局配置、常量和路径管理
"""

from .settings import (
    # 路径
    ISD_HISTORY_PATH,
    WORLDCITIES_PATH,
    CITY_FEATURES_PATH,
    CACHE_DIR,
    NOAA_CACHE_DIR,
    OPENAQ_CACHE_DIR,
    PROCESSED_DIR,
    NOAA_PROCESSED_DIR,
    OPENAQ_PROCESSED_DIR,
    MERGED_DIR,
    MODELS_DIR,
    EXPERIMENTS_DIR,
    PRODUCTION_DIR,
    # NOAA配置
    NOAA_S3_BUCKET,
    NOAA_BASE_URL,
    NOAA_MISSING_VALUES,
    # OpenAQ配置
    OPENAQ_API_BASE,
    OPENAQ_S3_BUCKET,
    OPENAQ_S3_BASE_URL,
    # 默认配置
    DEFAULT_CITIES,
    DEFAULT_START_YEAR,
    DEFAULT_END_YEAR,
    TRAINING_CORE_CITIES,
    # 函数
    check_required_files,
    ensure_dirs,
)

from .constants import (
    # 污染物
    POLLUTANT_COLS,
    TARGET_COL,
    POLLUTANT_UNITS,
    # 城市元数据
    CITY_METADATA,
    # 气象
    WEATHER_COLS,
    # 模式
    PredictionMode,
    MODE_METADATA,
    # 算法
    Algorithm,
    ALGORITHM_DEFAULT_PARAMS,
    # 训练
    DEFAULT_TRAIN_CONFIG,
    LAG_CONFIG,
    # AQI
    EPA_AQI_BREAKPOINTS,
    AQI_CATEGORIES,
)

from .paths import (
    get_project_root,
    get_data_dir,
    get_merged_data_path,
    get_experiment_dir,
    get_production_dir,
    generate_timestamp,
    generate_experiment_id,
)

__all__ = [
    # settings
    "ISD_HISTORY_PATH",
    "WORLDCITIES_PATH",
    "CITY_FEATURES_PATH",
    "CACHE_DIR",
    "NOAA_CACHE_DIR",
    "OPENAQ_CACHE_DIR",
    "PROCESSED_DIR",
    "NOAA_PROCESSED_DIR",
    "OPENAQ_PROCESSED_DIR",
    "MERGED_DIR",
    "MODELS_DIR",
    "EXPERIMENTS_DIR",
    "PRODUCTION_DIR",
    "NOAA_S3_BUCKET",
    "NOAA_BASE_URL",
    "NOAA_MISSING_VALUES",
    "OPENAQ_API_BASE",
    "OPENAQ_S3_BUCKET",
    "OPENAQ_S3_BASE_URL",
    "DEFAULT_CITIES",
    "DEFAULT_START_YEAR",
    "DEFAULT_END_YEAR",
    "TRAINING_CORE_CITIES",
    "check_required_files",
    "ensure_dirs",
    # constants
    "POLLUTANT_COLS",
    "TARGET_COL",
    "POLLUTANT_UNITS",
    "CITY_METADATA",
    "WEATHER_COLS",
    "PredictionMode",
    "MODE_METADATA",
    "Algorithm",
    "ALGORITHM_DEFAULT_PARAMS",
    "DEFAULT_TRAIN_CONFIG",
    "LAG_CONFIG",
    "EPA_AQI_BREAKPOINTS",
    "AQI_CATEGORIES",
    # paths
    "get_project_root",
    "get_data_dir",
    "get_merged_data_path",
    "get_experiment_dir",
    "get_production_dir",
    "generate_timestamp",
    "generate_experiment_id",
]
