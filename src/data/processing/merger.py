"""
数据合并模块

将 NOAA 和 OpenAQ 清洗后的数据按城市和日期对齐
"""

import os.path as osp
from pathlib import Path
from typing import Optional, List
import pandas as pd

from ...config import POLLUTANT_COLS, WEATHER_COLS

from loguru import logger


class DataMerger:
    """NOAA 与 OpenAQ 数据合并器"""

    def __init__(
        self,
        noaa_dir: Optional[str] = None,
        openaq_dir: Optional[str] = None,
        merged_dir: Optional[str] = None,
    ):
        """
        初始化合并器

        Args:
            noaa_dir: NOAA 清洗后数据目录
            openaq_dir: OpenAQ 清洗后数据目录
            merged_dir: 合并后数据输出目录
        """
        from ...config import NOAA_PROCESSED_DIR, OPENAQ_PROCESSED_DIR, MERGED_DIR

        self.noaa_dir = Path(noaa_dir) if noaa_dir else Path(NOAA_PROCESSED_DIR)
        self.openaq_dir = Path(openaq_dir) if openaq_dir else Path(OPENAQ_PROCESSED_DIR)
        self.merged_dir = Path(merged_dir) if merged_dir else Path(MERGED_DIR)

        # 确保输出目录存在
        self.merged_dir.mkdir(parents=True, exist_ok=True)

    def load_noaa_year(self, city_name: str, year: int) -> Optional[pd.DataFrame]:
        """加载指定城市某年的 NOAA 数据"""
        safe_city = city_name.replace(" ", "_").replace("/", "_")
        file_path = self.noaa_dir / safe_city / f"{year}.csv"

        if not file_path.exists():
            logger.warning(f"NOAA 数据文件不存在: {file_path}")
            return None

        try:
            df = pd.read_csv(file_path)
            df["date"] = pd.to_datetime(df["date"])
            logger.info(f"加载 NOAA {city_name} {year}年: {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"加载 NOAA 数据失败 ({city_name} {year}): {e}")
            return None

    def load_openaq_year(self, city_name: str, year: int) -> Optional[pd.DataFrame]:
        """加载指定城市某年的 OpenAQ 数据"""
        safe_city = city_name.replace(" ", "_").replace("/", "_")
        file_path = self.openaq_dir / safe_city / f"{year}.csv"

        if not file_path.exists():
            logger.warning(f"OpenAQ 数据文件不存在: {file_path}")
            return None

        try:
            df = pd.read_csv(file_path)
            df["date"] = pd.to_datetime(df["date"])
            logger.info(f"加载 OpenAQ {city_name} {year}年: {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"加载 OpenAQ 数据失败 ({city_name} {year}): {e}")
            return None

    def merge_daily(
        self,
        df_noaa: pd.DataFrame,
        df_openaq: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        按日期和城市合并 NOAA 和 OpenAQ 数据

        使用左连接，保留所有 NOAA 气象数据行，
        缺失的污染物列填充为 NaN。

        Args:
            df_noaa: NOAA DataFrame
            df_openaq: OpenAQ DataFrame

        Returns:
            合并后的 DataFrame
        """
        # 统一列名
        if "city_name" not in df_noaa.columns and "city" in df_noaa.columns:
            df_noaa = df_noaa.rename(columns={"city": "city_name"})
        if "city_name" not in df_openaq.columns and "city" in df_openaq.columns:
            df_openaq = df_openaq.rename(columns={"city": "city_name"})

        # 标准化城市名
        if "city_name" in df_noaa.columns:
            df_noaa["city_name"] = df_noaa["city_name"].str.replace("_", " ")
        if "city_name" in df_openaq.columns:
            df_openaq["city_name"] = df_openaq["city_name"].str.replace("_", " ")

        # 选择需要的列
        noaa_cols = ["date", "city_name"] + [
            c
            for c in df_noaa.columns
            if c not in ["date", "city_name", "year"]
            and not c.endswith(("_source_count", "_is_outlier", "_interpolated"))
        ]
        openaq_cols = ["date", "city_name"] + POLLUTANT_COLS

        df_noaa_clean = df_noaa[[c for c in noaa_cols if c in df_noaa.columns]].copy()
        df_openaq_clean = df_openaq[[c for c in openaq_cols if c in df_openaq.columns]].copy()

        # 补充缺失的污染物列为 NaN
        for col in POLLUTANT_COLS:
            if col not in df_openaq_clean.columns:
                df_openaq_clean[col] = float("nan")

        # 左连接
        merged_df = pd.merge(
            df_noaa_clean,
            df_openaq_clean,
            on=["date", "city_name"],
            how="left",
        )

        return merged_df

    def save_merged(
        self,
        df: pd.DataFrame,
        city_name: str,
        year: int,
    ) -> Optional[Path]:
        """
        保存合并后的数据

        Args:
            df: 合并后的 DataFrame
            city_name: 城市名称
            year: 年份

        Returns:
            保存的文件路径
        """
        safe_city = city_name.replace(" ", "_").replace("/", "_")
        city_dir = self.merged_dir / safe_city
        city_dir.mkdir(parents=True, exist_ok=True)

        file_path = city_dir / f"{year}.csv"

        try:
            df.to_csv(file_path, index=False)
            logger.info(f"保存合并数据: {file_path} ({len(df)} 条记录)")
            return file_path
        except Exception as e:
            logger.error(f"保存合并数据失败: {e}")
            return None

    def merge_city_year(
        self,
        city_name: str,
        year: int,
        save: bool = True,
    ) -> Optional[pd.DataFrame]:
        """
        合并指定城市某年的数据

        Args:
            city_name: 城市名称
            year: 年份
            save: 是否保存结果

        Returns:
            合并后的 DataFrame
        """
        df_noaa = self.load_noaa_year(city_name, year)
        df_openaq = self.load_openaq_year(city_name, year)

        if df_noaa is None:
            logger.warning(f"NOAA 数据缺失，跳过合并: {city_name} {year}")
            return None

        merged = self.merge_daily(df_noaa, df_openaq if df_openaq is not None else pd.DataFrame())

        if save and not merged.empty:
            self.save_merged(merged, city_name, year)

        return merged

    def merge_city_all_years(
        self,
        city_name: str,
        years: Optional[List[int]] = None,
        save: bool = True,
    ) -> Optional[pd.DataFrame]:
        """
        合并指定城市所有年份的数据

        Args:
            city_name: 城市名称
            years: 年份列表，None则自动发现
            save: 是否保存结果

        Returns:
            合并后的 DataFrame
        """
        safe_city = city_name.replace(" ", "_").replace("/", "_")
        noaa_city_dir = self.noaa_dir / safe_city

        if not noaa_city_dir.exists():
            logger.warning(f"NOAA 城市目录不存在: {noaa_city_dir}")
            return None

        if years is None:
            # 自动发现年份
            csv_files = list(noaa_city_dir.glob("*.csv"))
            years = sorted([int(f.stem) for f in csv_files if f.stem.isdigit()])

        dfs = []
        for year in years:
            df = self.merge_city_year(city_name, year, save=save)
            if df is not None:
                dfs.append(df)

        if not dfs:
            return None

        combined = pd.concat(dfs, ignore_index=True)
        combined = combined.sort_values("date").reset_index(drop=True)
        logger.info(f"城市 {city_name} 合并完成: {len(combined)} 条记录")
        return combined
