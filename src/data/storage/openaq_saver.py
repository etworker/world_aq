"""
OpenAQ 处理后数据保存模块

按年份保存空气质量数据
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional

from ...config import OPENAQ_PROCESSED_DIR

from loguru import logger


class OpenAQDataSaver:
    """OpenAQ 处理后数据保存器"""

    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化保存器

        Args:
            base_dir: 处理后数据的基础存储目录
        """
        self.base_dir = Path(base_dir) if base_dir else Path(OPENAQ_PROCESSED_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        df: pd.DataFrame,
        city_name: str,
        stations_count: int = 1,
        pollutants: Optional[List[str]] = None,
        format: str = "csv",
        decimal_places: int = 2,
        fill_missing_dates: bool = False,
    ) -> List[str]:
        """
        保存处理后的数据

        Args:
            df: 处理后的 DataFrame
            city_name: 城市名称
            stations_count: 使用的站点数量
            pollutants: 污染物列表
            format: 文件格式
            decimal_places: 小数位数
            fill_missing_dates: 是否填充缺失日期

        Returns:
            保存的文件路径列表
        """
        safe_city_name = city_name.replace(" ", "_").replace("/", "_")
        city_dir = self.base_dir / safe_city_name
        city_dir.mkdir(parents=True, exist_ok=True)

        if df.empty:
            logger.warning(f"数据为空，跳过保存: {city_name}")
            return []

        # 确保 date 列是 datetime 类型
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])

        # 去掉 _unit 列
        unit_cols = [c for c in df.columns if c.endswith("_unit")]
        df = df.drop(columns=unit_cols, errors="ignore")

        # 识别列类型
        exclude_cols = [
            "date",
            "year",
            "station_count",
            "data_quality_score",
            "data_source",
            "city_name",
            "_weight",
            "_sensor_id",
        ]
        value_cols = [
            c
            for c in df.columns
            if c not in exclude_cols
            and not c.endswith(("_source_count", "_is_outlier"))
            and df[c].dtype in ["float64", "float32"]
        ]
        int_cols = [c for c in df.columns if c in ["station_count"] or c.endswith("_source_count")]

        # 数值列四舍五入
        for col in value_cols:
            if col in df.columns:
                df[col] = df[col].round(decimal_places)

        # 整数列转换
        for col in int_cols:
            if col in df.columns:
                df[col] = df[col].astype("Int64")

        # 质量评分限制在 0-1
        if "data_quality_score" in df.columns:
            df["data_quality_score"] = df["data_quality_score"].clip(0, 1)

        # 按年份分组
        df["year"] = df["date"].dt.year
        years = df["year"].unique()

        saved_files = []

        for year in sorted(years):
            year_df = df[df["year"] == year].copy()
            year_df = year_df.drop(columns=["year"])

            if fill_missing_dates:
                year_df = self._fill_missing_dates(year_df, year)

            year_df = year_df.sort_values("date").reset_index(drop=True)

            if format == "parquet":
                file_path = city_dir / f"{year}.parquet"
                year_df.to_parquet(file_path, index=False)
            else:
                file_path = city_dir / f"{year}.csv"
                year_df.to_csv(file_path, index=False)

            saved_files.append(str(file_path))
            logger.info(f"保存 {city_name} {year}年数据: {file_path.name} ({len(year_df)}条)")

        # 保存汇总文件
        df_all = df.drop(columns=["year"]).sort_values("date").reset_index(drop=True)
        if fill_missing_dates and not df_all.empty:
            df_all = self._fill_missing_dates_all_years(df_all)

        if format == "parquet":
            all_path = city_dir / f"all_years.parquet"
            df_all.to_parquet(all_path, index=False)
        else:
            all_path = city_dir / f"all_years.csv"
            df_all.to_csv(all_path, index=False)

        saved_files.append(str(all_path))

        return saved_files

    def _fill_missing_dates(self, df: pd.DataFrame, year: int) -> pd.DataFrame:
        """填充单一年份缺失的日期"""
        if df.empty:
            return df

        start_date = pd.Timestamp(f"{year}-01-01")
        end_date = pd.Timestamp(f"{year}-12-31")
        full_date_range = pd.date_range(start=start_date, end=end_date, freq="D")

        full_df = pd.DataFrame({"date": full_date_range})
        result = pd.merge(full_df, df, on="date", how="left")

        # 填充 metadata 列
        metadata_cols = [
            c
            for c in df.columns
            if c not in ["date"]
            and (c in ["data_source", "city_name"] or c.endswith(("_unit", "_source_count", "_is_outlier")))
        ]
        for col in metadata_cols:
            if col in df.columns:
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    fill_value = (
                        non_null_values.mode().iloc[0] if len(non_null_values.mode()) > 0 else non_null_values.iloc[0]
                    )
                    result[col] = result[col].fillna(fill_value)

        return result

    def _fill_missing_dates_all_years(self, df: pd.DataFrame) -> pd.DataFrame:
        """填充所有年份的缺失日期"""
        if df.empty:
            return df

        min_date = df["date"].min()
        max_date = df["date"].max()
        full_date_range = pd.date_range(start=min_date, end=max_date, freq="D")

        full_df = pd.DataFrame({"date": full_date_range})
        result = pd.merge(full_df, df, on="date", how="left")

        metadata_cols = [
            c
            for c in df.columns
            if c not in ["date"]
            and (c in ["data_source", "city_name"] or c.endswith(("_unit", "_source_count", "_is_outlier")))
        ]
        for col in metadata_cols:
            if col in df.columns:
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    fill_value = (
                        non_null_values.mode().iloc[0] if len(non_null_values.mode()) > 0 else non_null_values.iloc[0]
                    )
                    result[col] = result[col].fillna(fill_value)

        return result
