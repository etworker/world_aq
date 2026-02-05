"""
项目常量定义
"""

from typing import List, Dict, Tuple, Any

# ============ 污染物配置 ============
# 支持的污染物列表
POLLUTANT_COLS: List[str] = ["pm25", "pm10", "o3", "no2", "so2", "co"]

# 主要目标变量（数据质量最佳，覆盖率82%）
TARGET_COL: str = "pm25"

# 城市元数据（用于特征工程）
CITY_METADATA: Dict[str, Dict[str, Any]] = {
    "Beijing": {
        "lat": 39.90,
        "lon": 116.40,
        "elevation_m": 43.5,
        "climate_zone": "continental",
        "population_millions": 21.5,
        "region": "East Asia",
    },
    "Shanghai": {
        "lat": 31.23,
        "lon": 121.47,
        "elevation_m": 4.5,
        "climate_zone": "subtropical",
        "population_millions": 24.3,
        "region": "East Asia",
    },
    "Guangzhou": {
        "lat": 23.13,
        "lon": 113.26,
        "elevation_m": 21.0,
        "climate_zone": "subtropical",
        "population_millions": 15.3,
        "region": "East Asia",
    },
    "Shenzhen": {
        "lat": 22.54,
        "lon": 114.06,
        "elevation_m": 0.0,
        "climate_zone": "subtropical",
        "population_millions": 12.5,
        "region": "East Asia",
    },
    "Chengdu": {
        "lat": 30.67,
        "lon": 104.07,
        "elevation_m": 500.0,
        "climate_zone": "subtropical",
        "population_millions": 16.6,
        "region": "East Asia",
    },
    "Xi'an": {
        "lat": 34.34,
        "lon": 108.94,
        "elevation_m": 397.0,
        "climate_zone": "continental",
        "population_millions": 12.9,
        "region": "East Asia",
    },
    "New_York": {
        "lat": 40.71,
        "lon": -74.01,
        "elevation_m": 10.0,
        "climate_zone": "continental",
        "population_millions": 8.3,
        "region": "North America",
    },
    "Los_Angeles": {
        "lat": 34.05,
        "lon": -118.24,
        "elevation_m": 89.0,
        "climate_zone": "mediterranean",
        "population_millions": 3.9,
        "region": "North America",
    },
    "Chicago": {
        "lat": 41.88,
        "lon": -87.63,
        "elevation_m": 181.0,
        "climate_zone": "continental",
        "population_millions": 2.7,
        "region": "North America",
    },
    "Houston": {
        "lat": 29.76,
        "lon": -95.37,
        "elevation_m": 13.0,
        "climate_zone": "subtropical",
        "population_millions": 2.3,
        "region": "North America",
    },
}

# 污染物单位
POLLUTANT_UNITS: Dict[str, str] = {
    "pm25": "µg/m³",
    "pm10": "µg/m³",
    "o3": "ppm",
    "no2": "ppm",
    "so2": "ppm",
    "co": "ppm",
}

# ============ 气象特征配置 ============
# 核心气象列
WEATHER_COLS: List[str] = [
    "temp_avg_c",
    "temp_max_c",
    "temp_min_c",
    "dewpoint_c",
    "precip_mm",
    "wind_speed_kmh",
    "visibility_km",
    "station_pressure_hpa",
]


# ============ 预测模式定义 ============
class PredictionMode:
    """8种预测模式定义"""

    GTM = "GTM"  # Global_Today_Multi
    GTS = "GTS"  # Global_Today_Sep
    GHM = "GHM"  # Global_Hist_Multi
    GHS = "GHS"  # Global_Hist_Sep
    CTM = "CTM"  # City_Today_Multi
    CTS = "CTS"  # City_Today_Sep
    CHM = "CHM"  # City_Hist_Multi
    CHS = "CHS"  # City_Hist_Sep

    ALL_MODES = [
        GTM, GTS, GHM, GHS,
        CTM, CTS, CHM, CHS,
    ]


# 模式元数据
MODE_METADATA: Dict[str, Dict] = {
    PredictionMode.GTM: {
        "name": "GTM: 全局_当天_多输出",
        "description": "所有城市共用模型，使用当日天气预测多污染物",
        "input_features": "城市特征 + 当日天气（温度、湿度、风速等）",
        "output": "PM2.5, O3",
        "use_case": "快速预测，不需要历史数据",
        "use_historical": False,
        "multi_output": True,
        "city_level": False,
        "forecast_horizon": 1,
    },
    PredictionMode.GTS: {
        "name": "GTS: 全局_当天_独立模型",
        "description": "所有城市共用模型，使用当日天气为每种污染物单独训练",
        "input_features": "城市特征 + 当日天气（温度、湿度、风速等）",
        "output": "PM2.5 或 O3（独立模型）",
        "use_case": "快速预测，专注单一污染物",
        "use_historical": False,
        "multi_output": False,
        "city_level": False,
        "forecast_horizon": 1,
    },
    PredictionMode.GHM: {
        "name": "GHM: 全局_历史_多输出",
        "description": "所有城市共用模型，使用历史+当天数据预测多污染物",
        "input_features": "城市特征 + 当日天气 + 历史污染数据",
        "output": "PM2.5, O3",
        "use_case": "利用历史趋势提高精度",
        "use_historical": True,
        "multi_output": True,
        "city_level": False,
        "forecast_horizon": 1,
    },
    PredictionMode.GHS: {
        "name": "GHS: 全局_历史_独立模型",
        "description": "所有城市共用模型，使用历史+当天数据为每种污染物单独训练",
        "input_features": "城市特征 + 当日天气 + 历史污染数据",
        "output": "PM2.5 或 O3（独立模型）",
        "use_case": "利用历史趋势，专注单一污染物",
        "use_historical": True,
        "multi_output": False,
        "city_level": False,
        "forecast_horizon": 1,
    },
    PredictionMode.CTM: {
        "name": "CTM: 城市级_当天_多输出",
        "description": "每个城市单独模型，使用当日天气预测多污染物",
        "input_features": "当日天气（温度、湿度、风速等）",
        "output": "PM2.5, O3",
        "use_case": "针对特定城市的快速预测",
        "use_historical": False,
        "multi_output": True,
        "city_level": True,
        "forecast_horizon": 1,
    },
    PredictionMode.CTS: {
        "name": "CTS: 城市级_当天_独立模型",
        "description": "每个城市单独模型，使用当日天气为每种污染物单独训练",
        "input_features": "当日天气（温度、湿度、风速等）",
        "output": "PM2.5 或 O3（独立模型）",
        "use_case": "针对特定城市，专注单一污染物",
        "use_historical": False,
        "multi_output": False,
        "city_level": True,
        "forecast_horizon": 1,
    },
    PredictionMode.CHM: {
        "name": "CHM: 城市级_历史_多输出",
        "description": "每个城市单独模型，使用历史+当天数据预测多污染物",
        "input_features": "当日天气 + 历史污染数据",
        "output": "PM2.5, O3",
        "use_case": "针对特定城市，利用历史趋势",
        "use_historical": True,
        "multi_output": True,
        "city_level": True,
        "forecast_horizon": 1,
    },
    PredictionMode.CHS: {
        "name": "CHS: 城市级_历史_独立模型",
        "description": "每个城市单独模型，使用历史+当天数据为每种污染物单独训练",
        "input_features": "当日天气 + 历史污染数据",
        "output": "PM2.5 或 O3（独立模型）",
        "use_case": "针对特定城市，利用历史趋势，专注单一污染物",
        "use_historical": True,
        "multi_output": False,
        "city_level": True,
        "forecast_horizon": 1,
    },
}


# ============ 模型算法配置 ============
class Algorithm:
    """支持的算法"""

    RIDGE = "Ridge"
    LASSO = "Lasso"
    ELASTIC_NET = "ElasticNet"
    RANDOM_FOREST = "RandomForest"
    GRADIENT_BOOSTING = "GradientBoosting"
    AUTOGluon = "AutoGluon"

    ALL_ALGORITHMS = [
        RIDGE,
        LASSO,
        ELASTIC_NET,
        RANDOM_FOREST,
        GRADIENT_BOOSTING,
        AUTOGluon,
    ]


# 算法默认参数
ALGORITHM_DEFAULT_PARAMS: Dict[str, Dict] = {
    Algorithm.RIDGE: {"alpha": 1.0},
    Algorithm.LASSO: {"alpha": 1.0},
    Algorithm.ELASTIC_NET: {"alpha": 1.0, "l1_ratio": 0.5},
    Algorithm.RANDOM_FOREST: {"n_estimators": 100, "max_depth": 15},
    Algorithm.GRADIENT_BOOSTING: {"n_estimators": 200, "max_depth": 5},
}


# ============ 训练配置 ============
# 默认训练参数
DEFAULT_TRAIN_CONFIG = {
    "test_size": 0.15,
    "val_size": 0.15,
    "random_state": 42,
    "n_splits": 5,
    "target_transform": "log",  # 'log', 'boxcox', None
}

# 滞后特征配置
LAG_CONFIG = {
    "days": [1, 7],  # Lag-1, Lag-7
    "rolling_windows": [7, 30],  # 7天和30天滚动平均
}


# ============ AQI 配置 ============
# EPA AQI 断点 (已转换为标准单位)
# 格式: [(浓度下限, 浓度上限, AQI下限, AQI上限), ...]
EPA_AQI_BREAKPOINTS = {
    "pm25": [  # µg/m³, 24小时平均
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ],
    "pm10": [  # µg/m³, 24小时平均
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 604, 301, 500),
    ],
    "o3": [  # ppm, 8小时平均
        (0.000, 0.054, 0, 50),
        (0.055, 0.070, 51, 100),
        (0.071, 0.085, 101, 150),
        (0.086, 0.105, 151, 200),
        (0.106, 0.200, 201, 300),
    ],
    "no2": [  # ppm (EPA原始为ppb，已转换)
        (0.000, 0.053, 0, 50),
        (0.054, 0.100, 51, 100),
        (0.101, 0.360, 101, 150),
        (0.361, 0.649, 151, 200),
        (0.650, 1.249, 201, 300),
    ],
    "so2": [  # ppm (EPA原始为ppb，已转换)
        (0.000, 0.035, 0, 50),
        (0.036, 0.075, 51, 100),
        (0.076, 0.185, 101, 150),
        (0.186, 0.304, 151, 200),
        (0.305, 0.604, 201, 300),
    ],
    "co": [  # ppm, 8小时平均
        (0.0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 50.4, 301, 500),
    ],
}

# AQI 类别
AQI_CATEGORIES = [
    (0, 50, "Good", "优", "#00E400"),
    (51, 100, "Moderate", "良", "#FFFF00"),
    (101, 150, "Unhealthy for Sensitive Groups", "轻度污染", "#FF7E00"),
    (151, 200, "Unhealthy", "中度污染", "#FF0000"),
    (201, 300, "Very Unhealthy", "重度污染", "#8F3F97"),
    (301, 500, "Hazardous", "严重污染", "#7E0023"),
]
