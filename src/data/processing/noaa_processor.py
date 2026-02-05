"""
NOAA 气象数据处理模块

数据清洗、单位转换、异常值检测、多站点合并
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from pathlib import Path

from ...config import NOAA_MISSING_VALUES

from loguru import logger


class NOAADataProcessor:
    """NOAA GSOD 数据处理器 - 单位转换、清洗、多站点合并、质量控制"""

    # 异常值阈值定义 (物理合理范围)
    OUTLIER_THRESHOLDS = {
        "temp_avg_c": (-60, 60),
        "temp_max_c": (-60, 60),
        "temp_min_c": (-60, 60),
        "precip_mm": (0, 2000),
        "wind_speed_kmh": (0, 300),
        "visibility_km": (0, 100),
        "station_pressure_hpa": (870, 1085),
    }

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理 NOAA 数据：单位转换与清洗

        Args:
            df: 原始 DataFrame

        Returns:
            处理后的 DataFrame
        """
        if df.empty:
            return df

        result = df.copy()

        # 1. 替换缺失值标记为 NaN
        for col, missing_val in NOAA_MISSING_VALUES.items():
            if col in result.columns:
                result[col] = result[col].replace(missing_val, np.nan)

        # 2. 单位转换
        result = self._convert_units(result)

        # 3. 选择并重命名关键列
        result = self._select_columns(result)

        # 4. 异常值检测与标记
        result = self._detect_outliers(result)

        return result

    def _convert_units(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换数据单位"""
        result = df.copy()

        # 温度: °F -> °C
        if "TEMP" in result.columns:
            result["TEMP_C"] = (result["TEMP"] - 32) * 5 / 9
            result["MAX_C"] = (result["MAX"] - 32) * 5 / 9
            result["MIN_C"] = (result["MIN"] - 32) * 5 / 9
            result["DEWP_C"] = (result["DEWP"] - 32) * 5 / 9

        # 降水量: 英寸 -> mm
        if "PRCP" in result.columns:
            result["PRCP_MM"] = result["PRCP"] * 25.4

        # 风速: 节 -> km/h
        if "WDSP" in result.columns:
            result["WDSP_KMH"] = result["WDSP"] * 1.852

        # 能见度: 英里 -> km
        if "VISIB" in result.columns:
            result["VISIB_KM"] = result["VISIB"] * 1.60934

        # 气压处理
        if "SLP" in result.columns and "STP" in result.columns:
            result["STP_HPA"] = result["SLP"].fillna(result["STP"])
        elif "SLP" in result.columns:
            result["STP_HPA"] = result["SLP"]
        elif "STP" in result.columns:
            result["STP_HPA"] = result["STP"]

        return result

    def _select_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """选择并重命名关键列"""
        columns = {
            "STATION": "station_id",
            "DATE": "date",
            "LATITUDE": "lat",
            "LONGITUDE": "lon",
            "ELEVATION": "elev_m",
            "TEMP_C": "temp_avg_c",
            "MAX_C": "temp_max_c",
            "MIN_C": "temp_min_c",
            "DEWP_C": "dewpoint_c",
            "PRCP_MM": "precip_mm",
            "WDSP_KMH": "wind_speed_kmh",
            "VISIB_KM": "visibility_km",
            "STP_HPA": "station_pressure_hpa",
            "FRSHTT": "weather_flags",
        }

        selected = {}
        for orig, new in columns.items():
            if orig in df.columns:
                selected[new] = df[orig]

        return pd.DataFrame(selected)

    def _detect_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """检测并标记异常值"""
        result = df.copy()

        for col, (min_val, max_val) in self.OUTLIER_THRESHOLDS.items():
            if col not in result.columns:
                continue

            valid_count = result[col].notna().sum()
            if valid_count == 0:
                continue

            # 创建异常值标记列
            outlier_col = f"{col}_is_outlier"
            is_outlier = ((result[col] < min_val) | (result[col] > max_val)) & result[col].notna()
            result[outlier_col] = is_outlier

            # 将异常值设为 NaN
            outlier_count = is_outlier.sum()
            if outlier_count > 0:
                result.loc[is_outlier, col] = np.nan

        return result

    def filter_low_coverage_stations(
        self,
        station_dataframes: Dict[str, pd.DataFrame],
        min_coverage: float = 0.5,
        core_columns: Optional[List[str]] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        过滤数据覆盖率低于阈值的站点

        Args:
            station_dataframes: 各站点数据字典
            min_coverage: 最小数据覆盖率 (0-1)
            core_columns: 核心列列表

        Returns:
            过滤后的数据字典
        """
        if core_columns is None:
            core_columns = ["temp_avg_c", "precip_mm"]

        filtered = {}

        for station_id, df in station_dataframes.items():
            available_cols = [c for c in core_columns if c in df.columns]
            if not available_cols:
                continue

            coverage = df[available_cols].notna().mean().mean()

            if coverage >= min_coverage:
                filtered[station_id] = df

        return filtered

    def merge_multi_station_data(
        self,
        station_dataframes: Dict[str, pd.DataFrame],
        stations_info: List[Dict],
        quality_control: bool = True,
    ) -> pd.DataFrame:
        """
        合并多站点数据，使用距离倒数加权平均

        Args:
            station_dataframes: Dict[station_id, DataFrame]
            stations_info: 站点信息列表（包含 distance_km）
            quality_control: 是否启用质量标记

        Returns:
            合并后的 DataFrame
        """
        if not station_dataframes:
            return pd.DataFrame()

        # 如果只有一个站点
        if len(station_dataframes) == 1:
            df = list(station_dataframes.values())[0].copy()
            core_cols = [
                "temp_avg_c",
                "temp_max_c",
                "temp_min_c",
                "dewpoint_c",
                "precip_mm",
                "wind_speed_kmh",
                "visibility_km",
                "station_pressure_hpa",
            ]
            for col in core_cols:
                if col in df.columns:
                    df[f"{col}_source_count"] = 1
            df["station_count"] = 1
            df["data_source"] = "single_station"
            df["data_quality_score"] = 1.0
            return df

        # 准备加权
        distance_map = {s["station_id"]: s.get("distance_km", 1) for s in stations_info}

        # 合并所有数据
        all_data = []
        for station_id, df in station_dataframes.items():
            df = df.copy()
            df["_station_id"] = station_id
            df["_weight"] = 1.0 / max(distance_map.get(station_id, 1), 0.1)
            all_data.append(df)

        combined = pd.concat(all_data, ignore_index=True)
        combined["date"] = pd.to_datetime(combined["date"])

        # 定义核心气象变量列
        core_cols = [
            "temp_avg_c",
            "temp_max_c",
            "temp_min_c",
            "dewpoint_c",
            "precip_mm",
            "wind_speed_kmh",
            "visibility_km",
            "station_pressure_hpa",
        ]
        numeric_cols = [c for c in core_cols if c in combined.columns]

        weighted_data = []
        total_cols = len(numeric_cols)

        for date, group in combined.groupby("date"):
            row = {"date": date}
            valid_col_count = 0

            for col in numeric_cols:
                if col in group.columns:
                    valid = group[group[col].notna()]
                    valid_count = len(valid)

                    if valid_count > 0:
                        weights = valid["_weight"].values
                        values = valid[col].values
                        row[col] = np.average(values, weights=weights)
                        valid_col_count += 1
                        if quality_control:
                            row[f"{col}_source_count"] = valid_count
                    else:
                        row[col] = np.nan
                        if quality_control:
                            row[f"{col}_source_count"] = 0

            # 保留位置信息
            first_valid = group[group["lat"].notna()]
            if not first_valid.empty:
                row["lat"] = first_valid["lat"].iloc[0]
                row["lon"] = first_valid["lon"].iloc[0]
                row["elev_m"] = first_valid["elev_m"].iloc[0]

            row["station_count"] = len(group["_station_id"].unique())
            row["data_source"] = "weighted_average"

            if quality_control:
                row["data_quality_score"] = valid_col_count / total_cols if total_cols > 0 else 0

            weighted_data.append(row)

        result = pd.DataFrame(weighted_data)
        result = result.sort_values("date").reset_index(drop=True)

        return result

    def interpolate_missing_values(
        self,
        df: pd.DataFrame,
        method: str = "time",
        limit: int = 3,
        columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        对缺失值进行时间序列插值

        Args:
            df: 数据框
            method: 插值方法
            limit: 最大连续插值天数
            columns: 要插值的列

        Returns:
            插值后的数据框
        """
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()

        if columns is None:
            exclude_cols = [
                "city_name",
                "data_source",
                "station_count",
                "data_quality_score",
                "lat",
                "lon",
                "elev_m",
            ]
            exclude_cols.extend([c for c in df.columns if c.endswith("_source_count")])
            exclude_cols.extend([c for c in df.columns if c.endswith("_is_outlier")])
            columns = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude_cols]

        for col in columns:
            if col not in df.columns:
                continue

            missing_before = df[col].isna().sum()
            if missing_before == 0:
                continue

            interpolated_mask = df[col].isna()
            df[col] = df[col].interpolate(method=method, limit=limit)

            interpolated_count = missing_before - df[col].isna().sum()
            if interpolated_count > 0:
                df[f"{col}_interpolated"] = interpolated_mask & df[col].notna()

        return df.reset_index()
