"""
OpenAQ 空气质量数据处理模块

数据清洗、异常值检测、多站点合并
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict

from loguru import logger


class OpenAQDataProcessor:
    """OpenAQ 数据处理器 - 数据解析、清洗、多站点合并"""

    # 异常值阈值定义 (物理合理范围，基于AQI标准)
    OUTLIER_THRESHOLDS = {
        "pm25": (0, 1000),
        "pm10": (0, 2000),
        "o3": (0, 0.5),
        "no2": (0, 2.0),
        "so2": (0, 1.0),
        "co": (0, 50),
    }

    # 目标单位定义
    TARGET_UNITS = {
        "pm25": "µg/m³",
        "pm10": "µg/m³",
        "o3": "ppm",
        "no2": "ppm",
        "so2": "ppm",
        "co": "ppm",
    }

    def _convert_unit(self, value: float, from_unit: str, to_unit: str) -> float:
        """转换数值单位"""
        if from_unit == to_unit:
            return value

        # PM 类单位转换
        if to_unit == "µg/m³":
            if from_unit == "mg/m³":
                return value * 1000
            elif from_unit == "g/m³":
                return value * 1000000

        # 气体浓度单位转换
        if to_unit == "ppm":
            if from_unit == "ppb":
                return value / 1000
            elif from_unit == "ppt":
                return value / 1000000

        return value

    def process_s3_data(self, df: pd.DataFrame, pollutant: str) -> pd.DataFrame:
        """
        处理 S3 下载的 CSV 数据为统一格式

        Args:
            df: S3 原始数据
            pollutant: 污染物类型

        Returns:
            处理后的 DataFrame
        """
        try:
            if "datetime" not in df.columns:
                logger.warning("S3 数据缺少 datetime 列")
                return pd.DataFrame()

            # 解析日期
            df["date"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
            invalid_dates = df["date"].isna().sum()
            if invalid_dates > 0:
                df = df.dropna(subset=["date"])

            if df.empty:
                return pd.DataFrame()

            # 转换为本地日期
            df["date"] = df["date"].dt.tz_localize(None).dt.normalize()

            # 确保 value 列为数值类型
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df = df.dropna(subset=["value"])

            if df.empty:
                return pd.DataFrame()

            # 按日期聚合
            target_unit = self.TARGET_UNITS.get(pollutant, "µg/m³")
            has_units_col = "units" in df.columns

            if has_units_col:
                df["converted_value"] = df.apply(
                    lambda row: self._convert_unit(row["value"], row.get("units", target_unit), target_unit),
                    axis=1,
                )
                daily = df.groupby("date").agg({"converted_value": "mean"}).reset_index()
                daily.columns = ["date", pollutant]
                daily[f"{pollutant}_unit"] = target_unit
            else:
                daily = df.groupby("date").agg({"value": "mean"}).reset_index()
                daily.columns = ["date", pollutant]
                default_units = {"pm25": "µg/m³", "pm10": "µg/m³", "o3": "ppm", "no2": "ppm", "so2": "ppm", "co": "ppm"}
                daily[f"{pollutant}_unit"] = default_units.get(pollutant, "unknown")

            return daily.sort_values("date").reset_index(drop=True)

        except Exception as e:
            logger.error(f"处理 S3 数据失败: {e}")
            return pd.DataFrame()

    def process_api_file(self, file_path: str, pollutant: str) -> pd.DataFrame:
        """
        处理 API 下载的 JSON 数据文件

        Args:
            file_path: JSON 文件路径
            pollutant: 污染物类型

        Returns:
            处理后的 DataFrame
        """
        import json

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"读取缓存文件失败: {e}")
            return pd.DataFrame()

        records = []
        for m in data:
            try:
                date_str = m.get("period", {}).get("datetimeFrom", {}).get("utc", "")
                if not date_str:
                    continue

                date = date_str[:10]
                value = m.get("value")

                if value is None or value == "":
                    continue

                raw_unit = m.get("parameter", {}).get("units", "µg/m³")
                target_unit = self.TARGET_UNITS.get(pollutant, raw_unit)
                converted_value = self._convert_unit(float(value), raw_unit, target_unit)

                records.append(
                    {
                        "date": date,
                        f"{pollutant}": converted_value,
                        f"{pollutant}_unit": target_unit,
                    }
                )
            except Exception:
                continue

        df = pd.DataFrame(records)

        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)

        return df

    def detect_outliers(self, df: pd.DataFrame, pollutant: str) -> pd.DataFrame:
        """
        检测并标记异常值

        Args:
            df: 数据框
            pollutant: 污染物类型

        Returns:
            添加异常值标记的 DataFrame
        """
        result = df.copy()
        value_col = pollutant

        if value_col not in result.columns:
            return result

        min_val, max_val = self.OUTLIER_THRESHOLDS.get(pollutant, (0, 10000))

        valid_count = result[value_col].notna().sum()
        if valid_count == 0:
            return result

        # 检测异常值
        is_outlier = ((result[value_col] < min_val) | (result[value_col] > max_val)) & result[value_col].notna()
        outlier_count = is_outlier.sum()

        if outlier_count > 0:
            result.loc[is_outlier, value_col] = np.nan

        # 添加异常值标记列
        result[f"{value_col}_is_outlier"] = is_outlier

        return result

    def merge_multi_station_data(
        self,
        station_dataframes: Dict[str, pd.DataFrame],
        stations_info: List[Dict],
    ) -> pd.DataFrame:
        """
        合并多站点数据，使用距离倒数加权平均

        Args:
            station_dataframes: Dict[sensor_id/location_id, DataFrame]
            stations_info: 站点信息列表

        Returns:
            合并后的 DataFrame
        """
        if not station_dataframes:
            return pd.DataFrame()

        if len(station_dataframes) == 1:
            df = list(station_dataframes.values())[0]
            df["data_source"] = "single_station"
            df["data_quality_score"] = 1.0
            return df

        # 构建距离映射
        distance_map = {}
        for s in stations_info:
            distance_m = s.get("distance_m", 1000)

            if "supported_pollutants" in s:
                for p in s["supported_pollutants"]:
                    sensor_id = p.get("sensor_id")
                    if sensor_id:
                        distance_map[str(sensor_id)] = distance_m
            else:
                loc_id = s.get("location_id") or s.get("id")
                if loc_id:
                    distance_map[str(loc_id)] = distance_m

        # 合并所有数据
        all_data = []
        for sensor_id, df in station_dataframes.items():
            df = df.copy()
            df["_sensor_id"] = str(sensor_id)
            df["_weight"] = 1.0 / max(distance_map.get(str(sensor_id), 1000), 100)
            all_data.append(df)

        combined = pd.concat(all_data, ignore_index=True)

        # 识别污染物数值列
        numeric_cols = [
            c
            for c in combined.columns
            if c not in ["date", "station_count", "data_quality_score", "_weight", "_sensor_id"]
            and not c.endswith(("_unit", "_source_count", "_is_outlier", "_value"))
            and pd.api.types.is_numeric_dtype(combined[c])
        ]

        weighted_data = []
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
                        row[f"{col}_source_count"] = valid_count
                    else:
                        row[col] = np.nan

            row["station_count"] = len(group["_sensor_id"].unique())
            row["data_source"] = "weighted_average"
            row["data_quality_score"] = valid_col_count / len(numeric_cols) if numeric_cols else 0

            weighted_data.append(row)

        result = pd.DataFrame(weighted_data)
        result = result.sort_values("date").reset_index(drop=True)

        return result
