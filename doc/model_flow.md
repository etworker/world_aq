# 空气质量预测模型：特征工程与 AutoGluon 使用流程

> **文档目标**：为实习生提供完整、可执行的模型开发指南，包含每一步的详细操作说明、代码示例和预期输出。

---

## 目录

1. [项目概述](#1-项目概述)
2. [数据准备](#2-数据准备)
3. [探索性数据分析 (EDA)](#3-探索性数据分析-eda)
4. [特征工程](#4-特征工程)
5. [数据集构建](#5-数据集构建)
6. [AutoGluon 模型训练](#6-autogluon-模型训练)
7. [模型评估](#7-模型评估)
8. [AQI 计算](#8-aqi-计算)
9. [模型推理](#9-模型推理)
10. [完整代码示例](#10-完整代码示例)

---

## 1. 项目概述

### 1.1 业务目标

根据历史气象数据和污染物浓度，预测未来一天的空气质量指数（AQI）。

### 1.2 技术路线

```
原始数据 → 数据清洗 → 特征工程 → 数据集构建 → AutoGluon训练 → 模型评估 → AQI计算 → 推理服务
```

### 1.3 数据源

| 数据源 | 内容 | 用途 |
|--------|------|------|
| NOAA GSOD | 气象数据（温度、降水、风速、气压等） | 气象特征 |
| OpenAQ | 污染物浓度（PM2.5、PM10、O3、NO2、SO2、CO） | 目标变量 |

### 1.4 输出格式

- **单步预测**：未来 1 天的 AQI 预报
- **AQI 标准**：美国 EPA 标准
- **预测变量**：PM2.5、PM10、O3、NO2、SO2、CO 的 24 小时平均浓度

---

## 2. 数据准备

### 2.1 数据目录结构

```
data/
├── cache/
│   ├── noaa/          # NOAA 原始气象数据（压缩包下载）
│   │   ├── Beijing/
│   │   │   ├── 2022_54511099999.csv
│   │   │   └── ...
│   │   ├── New_York/
│   │   │   ├── 2022_72503014732.csv
│   │   │   └── ...
│   │   └── ...
│   └── openaq/        # OpenAQ 原始污染物数据
├── processed/
│   ├── noaa/          # 清洗后的气象数据（单位已转换）
│   │   ├── Beijing/
│   │   │   ├── 2022.csv
│   │   │   ├── 2023.csv
│   │   │   ├── 2024.csv
│   │   │   └── 2025.csv
│   │   ├── New_York/
│   │   │   ├── 2022.csv
│   │   │   └── ...
│   │   └── ...
│   └── openaq/        # 清洗后的污染物数据
│       ├── Beijing/
│       │   ├── 2022.csv
│       │   └── ...
│       ├── New_York/
│       │   ├── 2022.csv
│       │   └── ...
│       └── ...
└── merged/
    ├── Beijing/
    │   ├── 2022.csv
    │   ├── 2023.csv
    │   └── ...
    ├── New_York/
    │   ├── 2022.csv
    │   └── ...
    └── ...           # 按城市分目录存放
```

### 2.2 NOAA 清洗后数据结构

**文件位置**：`data/processed/noaa/{city}/{year}.csv`

**字段说明**：

| 字段名 | 类型 | 单位 | 说明 |
|--------|------|------|------|
| date | string | - | 日期 (YYYY-MM-DD) |
| station_id | string | - | 气象站ID |
| lat | float | 度 | 纬度 |
| lon | float | 度 | 经度 |
| elev_m | float | 米 | 海拔高度 |
| temp_avg_c | float | °C | 日平均温度 |
| temp_max_c | float | °C | 日最高温度 |
| temp_min_c | float | °C | 日最低温度 |
| dewpoint_c | float | °C | 露点温度 |
| precip_mm | float | mm | 日降水量 |
| wind_speed_kmh | float | km/h | 平均风速 |
| visibility_km | float | km | 能见度 |
| station_pressure_hpa | float | hPa | 站点气压 |
| weather_flags | int | - | 天气标识 |
| data_source | string | - | 数据来源 |
| data_quality_score | float | - | 数据质量评分 |
| city_name | string | - | 城市名称 |
| precip_mm_interpolated | bool | - | 降水量是否插值 |

**数据清洗规则**（参考 `src/noaa_downloader.py`）：
- 温度：华氏度 → 摄氏度 `(temp_f - 32) * 5/9`
- 降水量：英寸 → 毫米 `precip_in * 25.4`
- 缺失值标记：`9999.9`, `999.9`, `99.99` → `NA`
- 异常值标记：自动生成布尔字段 `{col}_is_outlier`

### 2.3 OpenAQ 清洗后数据结构

**文件位置**：`data/processed/openaq/{city}/{year}.csv`

**字段说明**：

| 字段名 | 类型 | 单位 | 说明 |
|--------|------|------|------|
| date | string | - | 日期 (YYYY-MM-DD) |
| pm25 | float | μg/m³ | PM2.5 浓度 |
| pm25_source_count | int | - | PM2.5 数据源数量 |
| station_count | int | - | 监测站数量 |
| data_source | string | - | 数据来源 (weighted_average) |
| data_quality_score | float | - | 数据质量评分 |
| pm10 | float | μg/m³ | PM10 浓度 |
| o3 | float | μg/m³ | O3 浓度 |
| no2 | float | μg/m³ | NO2 浓度 |
| so2 | float | μg/m³ | SO2 浓度 |
| co | float | μg/m³ | CO 浓度 |
| city_name | string | - | 城市名称 |

**数据清洗规则**：
- 多站点数据按时间对齐，取加权平均
- 缺失数据自动标记
- 单位保持标准单位 (μg/m³)

### 2.4 数据加载步骤

#### 步骤 2.4.1：加载清洗后的 NOAA 数据

```python
# src/noaa_loader.py
import pandas as pd
from pathlib import Path

def load_noaa_data(city_name: str, year: int) -> pd.DataFrame:
    """
    加载指定城市、指定年份的清洗后 NOAA 数据
    
    Args:
        city_name: 城市名称（如 'New_York', 'Beijing'）
        year: 年份（如 2025）
    
    Returns:
        DataFrame: 包含气象数据的 DataFrame
    """
    file_path = Path(f"data/processed/noaa/{city_name}/{year}.csv")
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    df = pd.read_csv(file_path)
    
    # 日期列转换
    df['date'] = pd.to_datetime(df['date'])
    
    return df
```

#### 步骤 2.4.2：加载清洗后的 OpenAQ 数据

```python
# src/openaq_loader.py
import pandas as pd
from pathlib import Path

def load_openaq_data(city_name: str, year: int) -> pd.DataFrame:
    """
    加载指定城市、指定年份的清洗后 OpenAQ 数据
    
    Args:
        city_name: 城市名称（如 'New_York', 'Beijing'）
        year: 年份（如 2025）
    
    Returns:
        DataFrame: 包含污染物浓度的 DataFrame
    """
    file_path = Path(f"data/processed/openaq/{city_name}/{year}.csv")
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    return df
```

#### 步骤 2.4.3：批量加载多年数据

```python
# src/data_loader.py
import pandas as pd
from pathlib import Path
from typing import List

def load_city_years(city: str, years: List[int], data_type: str) -> pd.DataFrame:
    """
    批量加载城市多年数据
    
    Args:
        city: 城市名称
        years: 年份列表
        data_type: 'noaa' 或 'openaq'
    
    Returns:
        DataFrame: 合并后的数据
    """
    dfs = []
    
    for year in years:
        if data_type == 'noaa':
            path = Path(f"data/processed/noaa/{city}/{year}.csv")
        else:
            path = Path(f"data/processed/openaq/{city}/{year}.csv")
        
        if path.exists():
            df = pd.read_csv(path)
            dfs.append(df)
            print(f"  加载 {city}/{year}.csv: {len(df)} 行")
    
    if not dfs:
        raise ValueError(f"未找到 {city} 的数据")
    
    result = pd.concat(dfs, ignore_index=True)
    
    if 'date' in result.columns:
        result['date'] = pd.to_datetime(result['date'])
        result = result.sort_values('date')
    
    return result
```

#### 步骤 2.2.2：加载污染物数据

```python
# src/openaq_loader.py
import pandas as pd
from pathlib import Path

def load_openaq_data(city_name: str, pollutant: str, year: int) -> pd.DataFrame:
    """
    加载指定城市、指定污染物、指定年份的 OpenAQ 数据
    
    Args:
        city_name: 城市名称
        pollutant: 污染物类型（pm25, pm10, o3, no2, so2, co）
        year: 年份
    
    Returns:
        DataFrame: 包含污染物浓度的 DataFrame
    """
    data_dir = Path(f"data/cache/openaq/{city_name}")
    files = list(data_dir.glob(f"{year}_{pollutant}_*.csv"))
    
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True)
```

### 2.3 数据合并

```python
# src/data_merger.py
import pandas as pd
from datetime import timedelta

def merge_weather_pollution(
    weather_df: pd.DataFrame,
    pollution_df: pd.DataFrame,
    city: str
) -> pd.DataFrame:
    """
    合并气象数据和污染物数据
    
    关键：确保日期对齐，气象数据用于预测当日的污染物浓度
    """
    # 统一日期格式
    weather_df['date'] = pd.to_datetime(weather_df['DATE'])
    pollution_df['date'] = pd.to_datetime(pollution_df['date'])
    
    # 按日期合并
    merged = pd.merge(
        weather_df,
        pollution_df,
        on=['date', 'station_id'],
        how='inner'
    )
    
    merged['city'] = city
    
    return merged
```

### 2.4 实习生检查清单

- [ ] 确认数据目录存在且包含所需文件
- [ ] 检查数据文件格式是否正确
- [ ] 确认缺失值标记（9999.9、999.9、99.99）已被识别
- [ ] 确认温度转换公式正确（华氏度 → 摄氏度）
- [ ] 确认降水量转换公式正确（英寸 → 毫米）
- [ ] 验证合并后的数据行数合理

---

## 3. 探索性数据分析 (EDA)

### 3.1 目标变量分布分析

```python
# src/eda_analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def analyze_target_distribution(df: pd.DataFrame, target_cols: list):
    """
    分析目标变量（污染物浓度）的分布
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for idx, col in enumerate(target_cols):
        # 原始分布
        ax1 = axes[idx]
        df[col].dropna().hist(bins=50, ax=ax1, alpha=0.7)
        ax1.set_title(f'{col} 原始分布')
        ax1.set_xlabel('浓度')
        ax1.set_ylabel('频次')
        
        # 统计信息
        skewness = df[col].dropna().skew()
        kurtosis = df[col].dropna().kurtosis()
        print(f"{col}: 偏度={skewness:.2f}, 峰度={kurtosis:.2f}")
    
    plt.tight_layout()
    plt.savefig('reports/eda/target_distribution.png', dpi=150)
    plt.close()
```

### 3.2 相关性分析

```python
def analyze_correlation(df: pd.DataFrame, feature_cols: list, target_cols: list):
    """
    分析气象特征与污染物浓度的相关性
    """
    # 计算相关系数矩阵
    all_cols = feature_cols + target_cols
    corr_matrix = df[all_cols].corr()
    
    # 绘制热力图
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('特征与目标变量相关性矩阵')
    plt.tight_layout()
    plt.savefig('reports/eda/correlation_matrix.png', dpi=150)
    plt.close()
    
    # 提取与目标变量相关的特征
    for target in target_cols:
        print(f"\n{target} 相关性排名:")
        corr_with_target = corr_matrix[target].drop(target_cols).sort_values(key=abs, ascending=False)
        print(corr_with_target.head(10))
```

### 3.3 时间序列分解

```python
from statsmodels.tsa.seasonal import STL

def decompose_time_series(series: pd.Series, period: int = 365):
    """
    对时间序列进行 STL 分解
    
    Args:
        series: 时间序列数据
        period: 周期（年数据用 365，周数据用 7）
    """
    # 设置日期索引
    ts = series.copy()
    ts.index = pd.date_range(start='2022-01-01', periods=len(ts), freq='D')
    
    # STL 分解
    stl = STL(ts, period=period)
    result = stl.fit()
    
    # 绘制分解结果
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    
    axes[0].plot(result.observed)
    axes[0].set_title('原始数据')
    
    axes[1].plot(result.trend)
    axes[1].set_title('趋势项')
    
    axes[2].plot(result.seasonal)
    axes[2].set_title('季节项')
    
    axes[3].plot(result.resid)
    axes[3].set_title('残差项')
    
    plt.tight_layout()
    plt.savefig(f'reports/eda/decomposition_{series.name}.png', dpi=150)
    plt.close()
    
    return result
```

### 3.4 EDA 输出清单

| 输出文件 | 说明 |
|----------|------|
| `reports/eda/target_distribution.png` | 各污染物浓度分布图 |
| `reports/eda/correlation_matrix.png` | 相关性热力图 |
| `reports/eda/decomposition_*.png` | 时间序列分解图 |
| `reports/eda/summary_stats.csv` | 汇总统计表 |

### 3.5 实习生检查清单

- [ ] 生成各污染物浓度的分布图
- [ ] 识别严重偏斜的变量（偏度 > 1）
- [ ] 计算气象-污染物的相关系数
- [ ] 验证降水与 PM2.5 负相关（物理规律）
- [ ] 生成时间序列分解图
- [ ] 识别明显的季节性模式

---

## 4. 特征工程

### 4.1 特征分类总览

| 特征类型 | 说明 | 预期数量 |
|----------|------|----------|
| 气象特征 | 当日气象数据 | 8-10 个 |
| 时间特征 | 日期周期编码 | 4-6 个 |
| 滞后特征 | 前 1-7 天数据 | 50-80 个 |
| 滚动统计 | 7 天均值、标准差 | 10-15 个 |
| 地理特征 | 城市静态信息 | 5-8 个 |
| **总计** | | **80-120 个** |

### 4.2 时间特征构建

```python
# src/feature_time.py
import numpy as np

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    添加时间周期特征
    
    使用正弦/余弦编码保证跨年连续性
    例如：12月31日和1月1日在编码空间中相近
    """
    df = df.copy()
    
    # 一年中的第几天
    day_of_year = df['date'].dt.dayofyear
    
    # 年度周期编码（正弦）
    df['day_of_year_sin'] = np.sin(2 * np.pi * day_of_year / 365)
    df['day_of_year_cos'] = np.cos(2 * np.pi * day_of_year / 365)
    
    # 月度周期编码
    month = df['date'].dt.month
    df['month_sin'] = np.sin(2 * np.pi * month / 12)
    df['month_cos'] = np.cos(2 * np.pi * month / 12)
    
    # 周周期编码（检测工作日/周末差异）
    day_of_week = df['date'].dt.dayofweek
    df['day_of_week'] = day_of_week
    df['is_weekend'] = (day_of_week >= 5).astype(int)
    
    # 是否为采暖季（北京等北方城市 11-3 月）
    df['is_heating_season'] = ((month >= 11) | (month <= 3)).astype(int)
    
    return df
```

### 4.3 滞后特征构建

```python
# src/feature_lag.py
import pandas as pd

# 污染物列名（来自 OpenAQ 清洗后数据）
POLLUTANT_COLS = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']

# 气象特征列名（来自 NOAA 清洗后数据）
WEATHER_COLS = ['temp_avg_c', 'temp_max_c', 'temp_min_c', 'dewpoint_c', 
                'precip_mm', 'wind_speed_kmh', 'visibility_km', 'station_pressure_hpa']

def add_lag_features(
    df: pd.DataFrame,
    lag_days: list = [1, 2, 3, 4, 5, 6, 7],
    pollutant_cols: list = POLLUTANT_COLS,
    weather_cols: list = WEATHER_COLS
) -> pd.DataFrame:
    """
    添加滞后特征
    
    Args:
        df: 原始数据（需按城市、日期排序）
        lag_days: 滞后天数列表
        pollutant_cols: 污染物列名
        weather_cols: 气象列名
    """
    df = df.copy()
    df = df.sort_values(['city_name', 'date']).reset_index(drop=True)
    
    all_lag_cols = pollutant_cols + weather_cols
    
    for lag in lag_days:
        for col in all_lag_cols:
            if col in df.columns:
                # 按城市分组，创建滞后特征
                df[f'{col}_lag{lag}'] = df.groupby('city_name')[col].shift(lag)
    
    return df
```

### 4.4 滚动统计特征构建

```python
# src/feature_rolling.py
import pandas as pd

def add_rolling_features(
    df: pd.DataFrame,
    window: int = 7,
    target_cols: list = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
) -> pd.DataFrame:
    """
    添加滚动统计特征
    
    Args:
        df: 原始数据（需按城市、日期排序）
        window: 滚动窗口大小
        target_cols: 目标变量列名
    """
    df = df.copy()
    df = df.sort_values(['city', 'date']).reset_index(drop=True)
    
    for col in target_cols:
        # 滚动均值
        df[f'{col}_rolling_mean_{window}d'] = df.groupby('city')[col].transform(
            lambda x: x.shift(1).rolling(window=window, min_periods=1).mean()
        )
        
        # 滚动标准差
        df[f'{col}_rolling_std_{window}d'] = df.groupby('city')[col].transform(
            lambda x: x.shift(1).rolling(window=window, min_periods=2).std()
        )
    
    return df
```

### 4.5 地理静态特征

```python
# src/feature_static.py
import pandas as pd
import numpy as np

# 城市静态特征配置
CITY_STATIC_FEATURES = {
    'New_York': {
        'lat': 40.7128,
        'lon': -74.0060,
        'elevation_m': 10,
        'distance_to_coast_km': 0,  # 沿海城市
        'climate_zone': 'humid_subtropical',
        'population': 8_400_000,
        'annual_pm25_baseline': 8.5,
        'pm25_seasonal_variance': 5.2
    },
    'Los_Angeles': {
        'lat': 34.0522,
        'lon': -118.2437,
        'elevation_m': 71,
        'distance_to_coast_km': 0,  # 沿海城市
        'climate_zone': 'mediterranean',
        'population': 4_000_000,
        'annual_pm25_baseline': 12.1,
        'pm25_seasonal_variance': 4.8
    },
    'Chicago': {
        'lat': 41.8781,
        'lon': -87.6298,
        'elevation_m': 181,
        'distance_to_coast_km': 30,  # 距五大湖较近
        'climate_zone': 'humid_continental',
        'population': 2_700_000,
        'annual_pm25_baseline': 9.8,
        'pm25_seasonal_variance': 6.1
    },
    # ... 其他城市
}

def add_static_features(df: pd.DataFrame, static_config: dict = CITY_STATIC_FEATURES) -> pd.DataFrame:
    """
    添加城市静态特征
    """
    df = df.copy()
    
    # 映射静态特征
    for city, features in static_config.items():
        mask = df['city_name'] == city
        for feat_name, feat_value in features.items():
            df.loc[mask, f'city_{feat_name}'] = feat_value
    
    # 对人口取对数（压缩尺度）
    if 'city_population' in df.columns:
        df['city_population_log'] = np.log(df['city_population'] + 1)
    
    return df
```

### 4.6 完整特征工程管道

```python
# src/feature_pipeline.py
import pandas as pd
from typing import List

class FeaturePipeline:
    """
    特征工程完整管道
    
    使用方法:
        pipeline = FeaturePipeline()
        df_features = pipeline.run(df_raw)
    """
    
    def __init__(
        self,
        lag_days: List[int] = [1, 2, 3, 4, 5, 6, 7],
        rolling_window: int = 7,
        static_config: dict = CITY_STATIC_FEATURES
    ):
        self.lag_days = lag_days
        self.rolling_window = rolling_window
        self.static_config = static_config
        
        # 目标变量：污染物浓度（来自 OpenAQ 清洗后数据）
        self.target_cols = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
        # 气象特征（来自 NOAA 清洗后数据）
        self.weather_cols = ['temp_avg_c', 'temp_max_c', 'temp_min_c', 'dewpoint_c', 
                            'precip_mm', 'wind_speed_kmh', 'visibility_km', 'station_pressure_hpa']
    
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        执行完整特征工程流程
        """
        print("Step 1: 添加时间特征...")
        df = self._add_time_features(df)
        
        print("Step 2: 添加滞后特征...")
        df = self._add_lag_features(df)
        
        print("Step 3: 添加滚动统计特征...")
        df = self._add_rolling_features(df)
        
        print("Step 4: 添加静态城市特征...")
        df = self._add_static_features(df)
        
        print("Step 5: 处理缺失值...")
        df = self._handle_missing(df)
        
        print(f"完成! 最终特征数: {len(df.columns)}")
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        # 复用上面的 add_time_features
        df['date'] = pd.to_datetime(df['date'])
        
        day_of_year = df['date'].dt.dayofyear
        df['day_of_year_sin'] = np.sin(2 * np.pi * day_of_year / 365)
        df['day_of_year_cos'] = np.cos(2 * np.pi * day_of_year / 365)
        
        month = df['date'].dt.month
        df['month_sin'] = np.sin(2 * np.pi * month / 12)
        df['month_cos'] = np.cos(2 * np.pi * month / 12)
        
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_heating_season'] = ((month >= 11) | (month <= 3)).astype(int)
        
        return df
    
    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(['city_name', 'date']).reset_index(drop=True)
        all_lag_cols = self.target_cols + self.weather_cols
        
        for lag in self.lag_days:
            for col in all_lag_cols:
                if col in df.columns:
                    df[f'{col}_lag{lag}'] = df.groupby('city_name')[col].shift(lag)
        
        return df
    
    def _add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(['city_name', 'date']).reset_index(drop=True)
        
        for col in self.target_cols:
            if col in df.columns:
                df[f'{col}_rolling_mean_{self.rolling_window}d'] = df.groupby('city_name')[col].transform(
                    lambda x: x.shift(1).rolling(window=self.rolling_window, min_periods=1).mean()
                )
                df[f'{col}_rolling_std_{self.rolling_window}d'] = df.groupby('city_name')[col].transform(
                    lambda x: x.shift(1).rolling(window=self.rolling_window, min_periods=2).std()
                )
        
        return df
    
    def _add_static_features(self, df: pd.DataFrame) -> pd.DataFrame:
        for city, features in self.static_config.items():
            mask = df['city_name'] == city
            for feat_name, feat_value in features.items():
                df.loc[mask, f'city_{feat_name}'] = feat_value
        
        df['city_population_log'] = np.log(df['city_population'] + 1)
        
        return df
    
    def _handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        # 移除滞后特征导致的起始行缺失
        df = df.dropna(subset=['pm25_lag1'])
        
        # 剩余缺失值用 -999 填充（AutoGluon 会识别为缺失）
        df = df.fillna(-999)
        
        return df
    
    def get_feature_names(self, df: pd.DataFrame) -> dict:
        """获取特征列表，按类型分组"""
        exclude_cols = ['date', 'city_name', 'station_id'] + self.target_cols
        
        feature_cols = [c for c in df.columns if c not in exclude_cols]
        
        return {
            'all': feature_cols,
            'time': [c for c in feature_cols if 'day_of_year' in c or 'month' in c or 'weekend' in c],
            'lag': [c for c in feature_cols if '_lag' in c],
            'rolling': [c for c in feature_cols if 'rolling' in c],
            'static': [c for c in feature_cols if 'city_' in c],
            'weather': [c for c in feature_cols if c in self.weather_cols]
        }
```

### 4.7 实习生检查清单

- [ ] 确认时间特征使用正弦/余弦编码（非简单数值）
- [ ] 确认滞后特征正确使用 `shift()` 和 `groupby()`
- [ ] 确认滚动特征使用 `shift(1)` 避免数据泄露
- [ ] 确认静态特征已添加到每个城市
- [ ] 确认最终数据集无目标变量缺失行
- [ ] 记录最终特征数量

---

## 5. 数据集构建

### 5.1 特征与目标变量分离

```python
# src/dataset_builder.py
import pandas as pd
from sklearn.model_selection import train_test_split

def prepare_dataset(
    df: pd.DataFrame,
    feature_pipeline: FeaturePipeline,
    target_cols: list = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co'],
    test_size: float = 0.2,
    use_temporal_split: bool = True
) -> dict:
    """
    准备训练/测试数据集
    
    Args:
        df: 特征工程后的数据
        feature_pipeline: 特征管道实例
        target_cols: 目标变量列表
        test_size: 测试集比例
        use_temporal_split: 是否使用时序分割（推荐 True）
    
    Returns:
        dict: 包含 X_train, X_test, y_train, y_test 的字典
    """
    # 获取特征列名
    feature_names = feature_pipeline.get_feature_names(df)
    feature_cols = feature_names['all']
    
    X = df[feature_cols]
    y = df[target_cols]
    
    if use_temporal_split:
        # 时序分割：保持时间顺序，用较早数据训练，较晚数据测试
        split_idx = int(len(df) * (1 - test_size))
        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]
    else:
        # 随机分割（不推荐，会导致数据泄露）
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
    
    print(f"训练集: {len(X_train)} 样本")
    print(f"测试集: {len(X_test)} 样本")
    print(f"特征数: {len(feature_cols)}")
    print(f"目标变量: {target_cols}")
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'feature_cols': feature_cols,
        'target_cols': target_cols
    }
```

### 5.2 数据集划分示意

```
时间线：2022-01-01 ──────────────────────────────────────── 2025-08-24
        │                                                      │
        │=====================│==============================│
              训练集 (80%)            测试集 (20%)
         (较早时间段)              (较晚时间段)
```

### 5.3 实习生检查清单

- [ ] 确认使用时间序列分割（而非随机分割）
- [ ] 确认测试集在训练集时间之后
- [ ] 记录训练/测试集大小
- [ ] 保存数据集划分信息

---

## 6. AutoGluon 模型训练

### 6.1 安装 AutoGluon

```bash
# 安装命令
pip install autogluon
```

### 6.2 基础训练代码

```python
# src/autogluon_trainer.py
import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor

def train_with_autogluon(
    train_data: pd.DataFrame,
    label_col: str,
    eval_metric: str = 'rmse',
    time_limit: int = 600,  # 10 分钟
    save_path: str = 'models/autogluon'
) -> TabularPredictor:
    """
    使用 AutoGluon 训练模型
    
    Args:
        train_data: 训练数据（包含特征和标签）
        label_col: 目标变量列名
        eval_metric: 评估指标
        time_limit: 时间限制（秒）
        save_path: 模型保存路径
    
    Returns:
        TabularPredictor: 训练好的预测器
    """
    # 创建 TabularDataset
    train_tabular = TabularDataset(train_data)
    
    # 训练模型
    predictor = TabularPredictor(
        label=label_col,
        eval_metric=eval_metric,
        path=save_path
    ).fit(
        train_tabular,
        time_limit=time_limit,
        presets='medium_quality'  # 可选: 'low_quality', 'medium_quality', 'high_quality'
    )
    
    return predictor
```

### 6.3 多目标训练

```python
# src/autogluon_multitask.py
import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor
from pathlib import Path

class AutoGluonMultiTargetTrainer:
    """
    多目标 AutoGluon 训练器
    
    为每个污染物训练一个模型，支持多输出预测
    """
    
    def __init__(self, save_dir: str = 'models/autogluon_multitask'):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.predictors = {}
        self.target_cols = []
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.DataFrame,
        eval_metric: str = 'rmse',
        time_limit_per_target: int = 300,  # 每个目标 5 分钟
        presets: str = 'medium_quality'
    ):
        """
        训练多目标模型
        
        Args:
            X_train: 训练特征
            y_train: 训练标签（多列）
            eval_metric: 评估指标
            time_limit_per_target: 每个目标的训练时间限制
            presets: 预设质量
        """
        # 合并特征和标签
        train_data = pd.concat([X_train, y_train], axis=1)
        
        self.target_cols = y_train.columns.tolist()
        
        for target in self.target_cols:
            print(f"\n{'='*50}")
            print(f"训练目标: {target}")
            print(f"{'='*50}")
            
            # 创建 TabularDataset
            train_tabular = TabularDataset(train_data)
            
            # 训练单个目标
            predictor = TabularPredictor(
                label=target,
                eval_metric=eval_metric,
                path=str(self.save_dir / target)
            ).fit(
                train_tabular,
                time_limit=time_limit_per_target,
                presets=presets,
                verbosity=2
            )
            
            self.predictors[target] = predictor
            
            # 打印 leaderboard
            print(f"\n{target} 模型 Leaderboard:")
            print(predictor.leaderboard().to_string(index=False))
    
    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        使用所有目标模型进行预测
        
        Args:
            X: 特征数据
        
        Returns:
            DataFrame: 包含所有目标预测值的 DataFrame
        """
        predictions = {}
        
        for target, predictor in self.predictors.items():
            predictions[target] = predictor.predict(X)
        
        return pd.DataFrame(predictions)
```

### 6.4 高级训练配置

```python
# src/autogluon_advanced.py
from autogluon.tabular import TabularDataset, TabularPredictor

def train_with_custom_config(
    train_data: pd.DataFrame,
    label_col: str,
    eval_metric: str = 'rmse'
):
    """
    使用自定义配置训练 AutoGluon 模型
    """
    train_tabular = TabularDataset(train_data)
    
    # 自定义 hyperparameters
    hyperparameters = {
        'GBM': [
            {'num_boost_round': 100},
            {'num_boost_round': 300},
        ],
        'CAT': [
            {'iterations': 100},
            {'iterations': 300},
        ],
        'RF': [
            {'n_estimators': 100},
            {'n_estimators': 200},
        ],
        'XT': [
            {'n_estimators': 100},
        ],
        'KNN': [
            {'weights': 'distance', 'n_neighbors': 5},
        ],
    }
    
    # 自定义 feature generator
    feature_generator = None  # 使用默认
    
    predictor = TabularPredictor(
        label=label_col,
        eval_metric=eval_metric,
        path='models/autogluon_custom'
    ).fit(
        train_tabular,
        time_limit=600,  # 10 分钟
        hyperparameters=hyperparameters,
        feature_generator=feature_generator,
        num_bag_folds=5,  # 交叉验证折数
        num_bag_sets=1,
        stack_ensemble_levels=2,  # 集成层数
        verbosity=2
    )
    
    return predictor
```

### 6.5 模型选择实验

```python
# src/experiment_runner.py
import pandas as pd
import time
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

class ExperimentRunner:
    """
    实验运行器：管理多个实验的配置、训练和评估
    """
    
    EXPERIMENTS = {
        'exp1_weather_only': {
            'description': '仅使用当日气象特征',
            'feature_subset': ['weather', 'time']
        },
        'exp2_plus_time': {
            'description': '气象 + 时间周期特征',
            'feature_subset': ['weather', 'time']
        },
        'exp3_plus_lag1': {
            'description': '添加 lag-1 特征',
            'feature_subset': ['weather', 'time', 'lag']
        },
        'exp4_plus_lag7_rolling': {
            'description': '添加 lag-7 和滚动统计特征',
            'feature_subset': ['weather', 'time', 'lag', 'rolling']
        },
        'exp5_full': {
            'description': '完整特征集（含静态城市特征）',
            'feature_subset': ['all']
        }
    }
    
    def __init__(self, dataset: dict, output_dir: str = 'reports/experiments'):
        self.dataset = dataset
        self.output_dir = output_dir
        self.results = []
    
    def run_all_experiments(self, trainer_class, **trainer_kwargs):
        """
        运行所有实验
        """
        for exp_name, exp_config in self.EXPERIMENTS.items():
            print(f"\n{'='*60}")
            print(f"运行实验: {exp_name}")
            print(f"描述: {exp_config['description']}")
            print(f"{'='*60}")
            
            # 选择特征子集
            if exp_config['feature_subset'] == ['all']:
                X_train = self.dataset['X_train']
                X_test = self.dataset['X_test']
            else:
                feature_names = self.dataset['feature_names']
                feature_cols = []
                for subset in exp_config['feature_subset']:
                    feature_cols.extend(feature_names.get(subset, []))
                X_train = self.dataset['X_train'][feature_cols]
                X_test = self.dataset['X_test'][feature_cols]
            
            # 训练和评估
            start_time = time.time()
            
            trainer = trainer_class(**trainer_kwargs)
            trainer.train(X_train, self.dataset['y_train'])
            predictions = trainer.predict(X_test)
            
            train_time = time.time() - start_time
            
            # 计算评估指标
            metrics = {}
            for target in self.dataset['target_cols']:
                y_true = self.dataset['y_test'][target]
                y_pred = predictions[target]
                
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                mae = mean_absolute_error(y_true, y_pred)
                r2 = r2_score(y_true, y_pred)
                
                metrics[target] = {'RMSE': rmse, 'MAE': mae, 'R2': r2}
            
            # 保存结果
            result = {
                'experiment': exp_name,
                'description': exp_config['description'],
                'n_features': X_train.shape[1],
                'train_time': train_time,
                'metrics': metrics
            }
            self.results.append(result)
            
            # 打印摘要
            avg_rmse = np.mean([m['RMSE'] for m in metrics.values()])
            print(f"\n实验结果摘要:")
            print(f"  特征数: {X_train.shape[1]}")
            print(f"  训练时间: {train_time:.1f}秒")
            print(f"  平均 RMSE: {avg_rmse:.2f}")
    
    def save_results(self, filename: str = 'experiment_results.csv'):
        """
        保存实验结果
        """
        # 转换为 DataFrame 格式
        rows = []
        for result in self.results:
            for target, metrics in result['metrics'].items():
                rows.append({
                    'experiment': result['experiment'],
                    'description': result['description'],
                    'n_features': result['n_features'],
                    'train_time': result['train_time'],
                    'target': target,
                    **metrics
                })
        
        results_df = pd.DataFrame(rows)
        results_df.to_csv(f'{self.output_dir}/{filename}', index=False)
        
        return results_df
```

### 6.6 实习生检查清单

- [ ] 确认 AutoGluon 已正确安装
- [ ] 设置合理的时间限制（10-30 分钟）
- [ ] 监控训练过程中的 log 输出
- [ ] 检查每个目标的 leaderboard
- [ ] 保存训练好的模型
- [ ] 记录实验配置和结果

---

## 7. 模型评估

### 7.1 评估指标计算

```python
# src/model_evaluator.py
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def evaluate_regression(
    y_true: pd.DataFrame,
    y_pred: pd.DataFrame,
    target_names: list
) -> pd.DataFrame:
    """
    计算回归模型的评估指标
    
    Args:
        y_true: 真实值 DataFrame
        y_pred: 预测值 DataFrame
        target_names: 目标变量名称列表
    
    Returns:
        DataFrame: 包含各指标的结果表
    """
    results = []
    
    for target in target_names:
        y_t = y_true[target].values
        y_p = y_pred[target].values
        
        rmse = np.sqrt(mean_squared_error(y_t, y_p))
        mae = mean_absolute_error(y_t, y_p)
        r2 = r2_score(y_t, y_p)
        
        # MAPE（避免除零）
        mask = y_t != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_t[mask] - y_p[mask]) / y_t[mask])) * 100
        else:
            mape = np.nan
        
        results.append({
            'target': target,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2,
            'MAPE(%)': mape
        })
    
    return pd.DataFrame(results)
```

### 7.2 残差分析

```python
# src/residual_analysis.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def residual_analysis(
    y_true: pd.Series,
    y_pred: pd.Series,
    target_name: str,
    save_dir: str = 'reports/residuals'
):
    """
    残差分析
    
    检查：
    1. 残差分布（应接近正态）
    2. 残差 vs 预测值（应无明显模式）
    3. Q-Q 图（检验正态性）
    """
    residuals = y_true - y_pred
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. 残差分布
    ax1 = axes[0, 0]
    ax1.hist(residuals, bins=50, edgecolor='black', alpha=0.7)
    ax1.axvline(x=0, color='red', linestyle='--')
    ax1.set_title(f'{target_name} 残差分布')
    ax1.set_xlabel('残差')
    ax1.set_ylabel('频次')
    
    # 2. 残差 vs 预测值
    ax2 = axes[0, 1]
    ax2.scatter(y_pred, residuals, alpha=0.3, s=10)
    ax2.axhline(y=0, color='red', linestyle='--')
    ax2.set_title(f'{target_name} 残差 vs 预测值')
    ax2.set_xlabel('预测值')
    ax2.set_ylabel('残差')
    
    # 3. Q-Q 图
    ax3 = axes[1, 0]
    stats.probplot(residuals, dist="norm", plot=ax3)
    ax3.set_title(f'{target_name} Q-Q 图')
    
    # 4. 时间序列残差图
    ax4 = axes[1, 1]
    ax4.plot(range(len(residuals)), residuals.values, alpha=0.7)
    ax4.axhline(y=0, color='red', linestyle='--')
    ax4.set_title(f'{target_name} 残差时序图')
    ax4.set_xlabel('样本序号')
    ax4.set_ylabel('残差')
    
    plt.tight_layout()
    plt.savefig(f'{save_dir}/residuals_{target_name}.png', dpi=150)
    plt.close()
    
    # 正态性检验
    _, p_value = stats.shapiro(residuals.sample(min(5000, len(residuals))))
    
    return {
        'p_value': p_value,
        'is_normal': p_value > 0.05
    }
```

### 7.3 预测值 vs 真实值对比

```python
# src/prediction_analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_prediction_vs_actual(
    y_true: pd.Series,
    y_pred: pd.Series,
    target_name: str,
    save_dir: str = 'reports/predictions'
):
    """
    绘制预测值 vs 真实值对比图
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 1. 散点图
    ax1 = axes[0]
    ax1.scatter(y_true, y_pred, alpha=0.3, s=10)
    
    # 对角线（完美预测）
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
    
    ax1.set_title(f'{target_name} 预测值 vs 真实值')
    ax1.set_xlabel('真实值')
    ax1.set_ylabel('预测值')
    
    # 2. 时序对比图
    ax2 = axes[1]
    sample_idx = np.random.choice(len(y_true), min(365, len(y_true)), replace=False)
    sample_idx = np.sort(sample_idx)
    
    ax2.plot(range(len(sample_idx)), y_true.iloc[sample_idx].values, 
             label='真实值', alpha=0.8)
    ax2.plot(range(len(sample_idx)), y_pred.iloc[sample_idx].values, 
             label='预测值', alpha=0.8)
    
    ax2.set_title(f'{target_name} 时序对比（随机样本）')
    ax2.set_xlabel('天数')
    ax2.set_ylabel('浓度')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f'{save_dir}/prediction_vs_actual_{target_name}.png', dpi=150)
    plt.close()
```

### 7.4 模型对比表

```python
def generate_model_comparison_table(results: list) -> pd.DataFrame:
    """
    生成模型对比表
    """
    comparison_data = []
    
    for result in results:
        row = {
            '实验': result['experiment'],
            '描述': result['description'],
            '特征数': result['n_features'],
            '训练时间(秒)': round(result['train_time'], 1)
        }
        
        for target, metrics in result['metrics'].items():
            row[f'{target}_RMSE'] = round(metrics['RMSE'], 2)
        
        comparison_data.append(row)
    
    return pd.DataFrame(comparison_data)
```

### 7.5 实习生检查清单

- [ ] 计算所有目标的 RMSE、MAE、R²
- [ ] 生成残差分析图
- [ ] 生成预测值 vs 真实值散点图
- [ ] 生成时序对比图
- [ ] 汇总到模型对比表
- [ ] 识别表现较差的目标变量

---

## 8. AQI 计算

### 8.1 EPA AQI 标准

```python
# src/aqi_calculator.py
import pandas as pd
import numpy as np

class AQICalculator:
    """
    EPA AQI 计算器
    
    EPA 标准：AQI 与污染物浓度呈分段线性关系
    """
    
    # PM2.5 24小时平均浓度的 AQI breakpoints
    PM25_BREAKPOINTS = [
        (0.0, 12.0, 0, 50),       # Good
        (12.1, 35.4, 51, 100),    # Moderate
        (35.5, 55.4, 101, 150),   # Unhealthy for Sensitive Groups
        (55.5, 150.4, 151, 200),  # Unhealthy
        (150.5, 250.4, 201, 300), # Very Unhealthy
        (250.5, 500.4, 301, 500)  # Hazardous
    ]
    
    # AQI 类别
    AQI_CATEGORIES = {
        (0, 50): 'Good',
        (51, 100): 'Moderate',
        (101, 150): 'Unhealthy for Sensitive Groups',
        (151, 200): 'Unhealthy',
        (201, 300): 'Very Unhealthy',
        (301, 500): 'Hazardous'
    }
    
    # 健康建议
    HEALTH_ADVICE = {
        'Good': '空气质量令人满意，基本无空气污染',
        'Moderate': '空气质量可接受，某些污染物可能对极少数异常敏感人群有轻微影响',
        'Unhealthy for Sensitive Groups': '敏感人群（儿童、老人、呼吸疾病患者）可能有健康影响',
        'Unhealthy': '所有人健康可能受到影响，敏感人群可能有更严重健康影响',
        'Very Unhealthy': '健康警告，所有人可能有更严重的健康影响',
        'Hazardous': '健康紧急状况，整个人群都会受到影响'
    }
    
    @classmethod
    def calculate_aqi_single(cls, concentration: float, pollutant: str = 'pm25') -> int:
        """
        计算单个污染物的 AQI
        
        Args:
            concentration: 污染物浓度
            pollutant: 污染物类型
        
        Returns:
            int: AQI 值
        """
        if pd.isna(concentration) or concentration < 0:
            return np.nan
        
        if pollutant == 'pm25':
            breakpoints = cls.PM25_BREAKPOINTS
        else:
            # 其他污染物的 breakpoints（简化示例）
            breakpoints = cls.PM25_BREAKPOINTS
        
        for c_low, c_high, aqi_low, aqi_high in breakpoints:
            if c_low <= concentration <= c_high:
                # 线性插值
                aqi = aqi_low + (aqi_high - aqi_low) * (concentration - c_low) / (c_high - c_low)
                return int(round(aqi))
        
        # 超出范围
        if concentration > 500.4:
            return 500
        else:
            return 0
    
    @classmethod
    def calculate_composite_aqi(cls, concentrations: dict) -> dict:
        """
        计算综合 AQI（取各污染物 AQI 最大值）
        
        Args:
            concentrations: 各污染物浓度字典 {'pm25': 10.5, 'pm10': 20, ...}
        
        Returns:
            dict: 包含综合 AQI、各污染物 AQI、类别的字典
        """
        aqi_values = {}
        
        for pollutant, concentration in concentrations.items():
            aqi_values[pollutant] = cls.calculate_aqi_single(concentration, pollutant)
        
        # 综合 AQI = 最大值
        valid_aqi = [v for v in aqi_values.values() if not pd.isna(v)]
        composite_aqi = max(valid_aqi) if valid_aqi else np.nan
        
        # 确定类别
        category = 'Good'
        for (low, high), cat_name in cls.AQI_CATEGORIES.items():
            if low <= composite_aqi <= high:
                category = cat_name
                break
        
        advice = cls.HEALTH_ADVICE.get(category, '')
        
        return {
            'composite_aqi': composite_aqi,
            'pollutant_aqi': aqi_values,
            'category': category,
            'health_advice': advice
        }
```

### 8.2 AQI 计算示例

```python
# 示例使用
if __name__ == '__main__':
    # 输入：预测的污染物浓度
    concentrations = {
        'pm25': 35.0,   # μg/m³
        'pm10': 55.0,   # μg/m³
        'o3': 45.0,     # μg/m³
        'no2': 30.0,    # μg/m³
        'so2': 15.0,    # μg/m³
        'co': 2.0       # μg/m³
    }
    
    result = AQICalculator.calculate_composite_aqi(concentrations)
    
    print("污染物 AQI:")
    for pol, aqi in result['pollutant_aqi'].items():
        print(f"  {pol}: {aqi}")
    
    print(f"\n综合 AQI: {result['composite_aqi']}")
    print(f"类别: {result['category']}")
    print(f"健康建议: {result['health_advice']}")
```

### 8.3 AQI 气泡图可视化

```python
# src/aqi_visualization.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_aqi_bubble_chart(
    predictions: pd.DataFrame,
    aqi_results: pd.DataFrame,
    save_path: str = 'reports/aqi/aqi_bubble_chart.html'
):
    """
    绘制 AQI 气泡图（用于前端展示）
    
    气泡大小：AQI 值
    气泡颜色：AQI 类别
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 颜色映射
    color_map = {
        'Good': '#00E400',           # 绿色
        'Moderate': '#FFFF00',       # 黄色
        'Unhealthy for Sensitive Groups': '#FF7E00',  # 橙色
        'Unhealthy': '#FF0000',      # 红色
        'Very Unhealthy': '#8F3F97', # 紫色
        'Hazardous': '#7E0023'       # 栗色
    }
    
    for category, color in color_map.items():
        mask = aqi_results['category'] == category
        if mask.sum() > 0:
            sizes = aqi_results.loc[mask, 'composite_aqi'] * 2
            ax.scatter(
                aqi_results.loc[mask, 'date'],
                aqi_results.loc[mask, 'city'],
                s=sizes,
                c=color,
                alpha=0.6,
                label=category,
                edgecolors='black',
                linewidth=0.5
            )
    
    ax.set_xlabel('日期')
    ax.set_ylabel('城市')
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    ax.set_title('AQI 气泡图')
    
    plt.tight_layout()
    plt.savefig(save_path.replace('.html', '.png'), dpi=150)
    
    # 生成 HTML 版本（交互式）
    try:
        import plotly.express as px
        fig = px.scatter(
            aqi_results,
            x='date',
            y='city',
            size='composite_aqi',
            color='category',
            color_discrete_map=color_map,
            title='AQI 气泡图',
            size_max=50
        )
        fig.write_html(save_path)
    except ImportError:
        print("Plotly 未安装，跳过 HTML 导出")
    
    plt.close()
```

### 8.4 实习生检查清单

- [ ] 验证 AQI 计算与 EPA 标准一致
- [ ] 测试各种浓度范围的 AQI 计算
- [ ] 验证综合 AQI 计算逻辑（取最大值）
- [ ] 生成 AQI 气泡图

---

## 9. 模型推理

### 9.1 单步预测

```python
# src/inference.py
import pandas as pd
from typing import Dict, List
import joblib

class AQIInferenceEngine:
    """
    AQI 推理引擎
    
    封装模型加载、数据预处理、预测和后处理
    """
    
    def __init__(self, model_dir: str = 'models/autogluon_multitask'):
        self.model_dir = model_dir
        self.predictors = {}
        self.feature_pipeline = None
        self._load_models()
    
    def _load_models(self):
        """加载所有训练好的模型"""
        from pathlib import Path
        import autogluon.core
        
        target_cols = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
        
        for target in target_cols:
            model_path = Path(self.model_dir) / target
            if model_path.exists():
                self.predictors[target] = autogluon.core.loaders.load_pkl.load(str(model_path / 'predictor.pkl'))
    
    def predict_single_day(
        self,
        city: str,
        date: str,
        weather_features: Dict[str, float],
        historical_data: pd.DataFrame = None
    ) -> Dict:
        """
        单日预测
        
        Args:
            city: 城市名称
            date: 预测日期 (YYYY-MM-DD)
            weather_features: 当日气象特征字典
            historical_data: 历史数据（用于生成滞后特征）
        
        Returns:
            dict: 预测结果
        """
        # 构建特征
        features = self._build_features(city, date, weather_features, historical_data)
        
        # 多目标预测
        predictions = {}
        for target, predictor in self.predictors.items():
            predictions[target] = predictor.predict(features)[0]
        
        # 计算 AQI
        aqi_result = AQICalculator.calculate_composite_aqi(predictions)
        
        return {
            'city': city,
            'date': date,
            'predictions': predictions,
            **aqi_result
        }
    
    def _build_features(self, city, date, weather_features, historical_data):
        """构建推理特征（复用训练时的特征工程逻辑）"""
        # 此处应复用 FeaturePipeline 的逻辑
        # 返回单行 DataFrame
        pass
    
    def predict_batch(
        self,
        test_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        批量预测
        
        Args:
            test_data: 测试集特征
        
        Returns:
            DataFrame: 预测结果
        """
        predictions = {}
        
        for target, predictor in self.predictors.items():
            predictions[target] = predictor.predict(test_data)
        
        return pd.DataFrame(predictions)
```

### 9.2 模型服务 API

```python
# src/api_service.py
from flask import Flask, request, jsonify
from src.inference import AQIInferenceEngine

app = Flask(__name__)
inference_engine = AQIInferenceEngine()

@app.route('/api/v1/aqi/predict', methods=['POST'])
def predict_aqi():
    """
    AQI 预测 API
    
    请求格式:
    {
        "city": "New_York",
        "date": "2025-08-25",
        "weather": {
            "temp_avg": 25.0,
            "temp_max": 30.0,
            "temp_min": 20.0,
            "precip": 0.0,
            "wind_speed": 15.0,
            "pressure": 1013.0
        }
    }
    
    响应格式:
    {
        "success": true,
        "city": "New_York",
        "date": "2025-08-25",
        "aqi": 45,
        "category": "Good",
        "predictions": {
            "pm25": 12.5,
            "pm10": 25.0,
            ...
        }
    }
    """
    data = request.json
    
    result = inference_engine.predict_single_day(
        city=data['city'],
        date=data['date'],
        weather_features=data['weather']
    )
    
    return jsonify({
        'success': True,
        'city': result['city'],
        'date': result['date'],
        'aqi': result['composite_aqi'],
        'category': result['category'],
        'health_advice': result['health_advice'],
        'predictions': {k: round(v, 2) for k, v in result['predictions'].items()}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### 9.3 实习生检查清单

- [ ] 测试单日预测功能
- [ ] 验证批量预测与逐条预测结果一致
- [ ] 启动 API 服务并测试端点
- [ ] 记录 API 调用示例

---

## 10. 完整代码示例

### 10.1 主训练脚本

```python
# main_train.py
"""
空气质量预测模型 - 主训练脚本

使用方法:
    python main_train.py --config config/default.yaml
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path

from src.data_loader import load_all_data
from src.feature_pipeline import FeaturePipeline
from src.dataset_builder import prepare_dataset
from src.autogluon_multitask import AutoGluonMultiTargetTrainer
from src.model_evaluator import evaluate_regression
from src.experiment_runner import ExperimentRunner

def main(config_path: str = 'config/default.yaml'):
    """主函数"""
    
    # 1. 加载数据
    print("=" * 60)
    print("Step 1: 加载数据")
    print("=" * 60)
    df = load_all_data()
    print(f"加载完成: {len(df)} 行")
    
    # 2. 特征工程
    print("\n" + "=" * 60)
    print("Step 2: 特征工程")
    print("=" * 60)
    pipeline = FeaturePipeline()
    df_features = pipeline.run(df)
    print(f"特征数: {len(df_features.columns)}")
    
    # 3. 准备数据集
    print("\n" + "=" * 60)
    print("Step 3: 准备数据集")
    print("=" * 60)
    dataset = prepare_dataset(df_features, pipeline)
    
    # 4. 训练模型
    print("\n" + "=" * 60)
    print("Step 4: 训练 AutoGluon 模型")
    print("=" * 60)
    trainer = AutoGluonMultiTargetTrainer()
    trainer.train(dataset['X_train'], dataset['y_train'])
    
    # 5. 模型预测
    print("\n" + "=" * 60)
    print("Step 5: 模型预测")
    print("=" * 60)
    predictions = trainer.predict(dataset['X_test'])
    
    # 6. 模型评估
    print("\n" + "=" * 60)
    print("Step 6: 模型评估")
    print("=" * 60)
    metrics = evaluate_regression(
        dataset['y_test'],
        predictions,
        dataset['target_cols']
    )
    print("\n评估指标:")
    print(metrics.to_string(index=False))
    metrics.to_csv('reports/final_metrics.csv', index=False)
    
    # 7. 保存模型
    print("\n" + "=" * 60)
    print("Step 7: 保存模型")
    print("=" * 60)
    trainer.save_all()
    
    print("\n" + "=" * 60)
    print("训练完成!")
    print("=" * 60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config/default.yaml')
    args = parser.parse_args()
    
    main(args.config)
```

### 10.2 运行命令

```bash
# 训练模型
python main_train.py --config config/default.yaml

# 运行 API 服务
python -m src.api_service

# 运行 EDA 分析
python -m src.eda_analysis --output reports/eda
```

### 10.3 目录结构

```
project/
├── config/
│   └── default.yaml          # 默认配置
├── data/
│   ├── cache/
│   │   ├── noaa/            # NOAA 原始数据
│   │   │   ├── Beijing/
│   │   │   ├── New_York/
│   │   │   └── ...
│   │   └── openaq/          # OpenAQ 原始数据
│   ├── processed/
│   │   ├── noaa/            # NOAA 清洗后数据
│   │   │   ├── Beijing/
│   │   │   │   ├── 2022.csv
│   │   │   │   ├── 2023.csv
│   │   │   │   └── ...
│   │   │   ├── New_York/
│   │   │   │   └── ...
│   │   │   └── ...
│   │   ├── openaq/          # OpenAQ 清洗后数据
│   │   │   ├── Beijing/
│   │   │   ├── New_York/
│   │   │   └── ...
│   │   └── merged/           # 合并后的数据
│   │       ├── Beijing/
│   │       ├── New_York/
│   │       └── ...
│   └── info/                 # 城市信息（元数据）
├── reports/
│   ├── eda/                  # EDA 输出
│   ├── experiments/           # 实验结果
│   ├── residuals/            # 残差分析
│   ├── predictions/          # 预测分析
│   └── aqi/                  # AQI 可视化
├── models/
│   └── autogluon_multitask/  # 训练好的模型
├── src/
│   ├── data_loader.py
│   ├── feature_pipeline.py
│   ├── dataset_builder.py
│   ├── autogluon_trainer.py
│   ├── model_evaluator.py
│   ├── aqi_calculator.py
│   ├── inference.py
│   └── api_service.py
├── main_train.py
└── requirements.txt
```

---

## 附录 A：常见问题排查

### A.1 特征缺失

**问题**：滞后特征或滚动特征为 NaN

**解决**：
```python
# 确认 groupby 和 shift 顺序正确
df = df.sort_values(['city', 'date'])
df[f'{col}_lag1'] = df.groupby('city')[col].shift(1)
```

### A.2 数据泄露

**问题**：训练集和测试集有重叠

**解决**：
```python
# 使用时序分割
split_idx = int(len(df) * 0.8)
train = df.iloc[:split_idx]
test = df.iloc[split_idx:]
```

### A.3 AutoGluon 内存不足

**解决**：
```python
# 减少特征数量或使用更小的 presets
predictor.fit(train_data, time_limit=600, presets='low_quality')
```

### A.4 AQI 计算错误

**问题**：浓度超出 breakpoints 范围

**解决**：
```python
# 添加边界检查
if concentration < 0:
    return np.nan
if concentration > 500.4:
    return 500
```

---

## 附录 B：参考资源

| 资源 | 链接 |
|------|------|
| AutoGluon 官方文档 | https://auto.gluon.ai/stable/index.html |
| EPA AQI 标准 | https://www.airnow.gov/aqi/aqi-basics/ |
| NOAA GSOD 数据 | https://registry.opendata.aws/noaa-gsod/ |
| OpenAQ 数据 | https://registry.opendata.aws/openaq/ |

---

> **文档版本**: v1.0  
> **最后更新**: 2026-02-04  
> **作者**: NWCD Rapid Prototyping Solutions Architect
