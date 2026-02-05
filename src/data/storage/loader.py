"""
数据加载模块

提供统一的数据加载接口
"""

import os.path as osp
from pathlib import Path
from typing import Optional, List, Union
import pandas as pd

from ...config import (
    MERGED_DIR,
    NOAA_PROCESSED_DIR,
    OPENAQ_PROCESSED_DIR,
    get_merged_data_path,
)

from loguru import logger


class DataLoader:
    """数据加载器"""

    def __init__(
        self,
        merged_dir: Optional[str] = None,
        noaa_dir: Optional[str] = None,
        openaq_dir: Optional[str] = None,
    ):
        """
        初始化数据加载器

        Args:
            merged_dir: 合并数据目录
            noaa_dir: NOAA数据目录
            openaq_dir: OpenAQ数据目录
        """
        self.merged_dir = Path(merged_dir) if merged_dir else Path(MERGED_DIR)
        self.noaa_dir = Path(noaa_dir) if noaa_dir else Path(NOAA_PROCESSED_DIR)
        self.openaq_dir = Path(openaq_dir) if openaq_dir else Path(OPENAQ_PROCESSED_DIR)

    def load_noaa_year(self, city_name: str, year: int) -> Optional[pd.DataFrame]:
        """
        加载指定城市某年的 NOAA 清洗后数据

        Args:
            city_name: 城市名称
            year: 年份

        Returns:
            NOAA DataFrame，失败返回 None
        """
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
        """
        加载指定城市某年的 OpenAQ 清洗后数据

        Args:
            city_name: 城市名称
            year: 年份

        Returns:
            OpenAQ DataFrame，失败返回 None
        """
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

    def load_merged_year(self, city_name: str, year: int) -> Optional[pd.DataFrame]:
        """
        加载指定城市某年的合并数据

        Args:
            city_name: 城市名称
            year: 年份

        Returns:
            合并后的 DataFrame，失败返回 None
        """
        safe_city = city_name.replace(" ", "_").replace("/", "_")
        file_path = self.merged_dir / safe_city / f"{year}.csv"

        if not file_path.exists():
            logger.warning(f"合并数据文件不存在: {file_path}")
            return None

        try:
            df = pd.read_csv(file_path)
            df["date"] = pd.to_datetime(df["date"])
            logger.info(f"加载合并数据 {city_name} {year}年: {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"加载合并数据失败 ({city_name} {year}): {e}")
            return None

    def load_merged_city_all_years(self, city_name: str) -> Optional[pd.DataFrame]:
        """
        加载指定城市所有年份的合并数据

        Args:
            city_name: 城市名称

        Returns:
            合并后的 DataFrame，失败返回 None
        """
        safe_city = city_name.replace(" ", "_").replace("/", "_")
        city_dir = self.merged_dir / safe_city

        if not city_dir.exists():
            logger.warning(f"城市数据目录不存在: {city_dir}")
            return None

        csv_files = sorted(city_dir.glob("*.csv"))
        if not csv_files:
            logger.warning(f"城市 {city_name} 没有数据文件")
            return None

        dfs = []
        for file_path in csv_files:
            try:
                df = pd.read_csv(file_path)
                df["date"] = pd.to_datetime(df["date"])
                dfs.append(df)
                logger.info(f"加载 {file_path.name}: {len(df)} 条记录")
            except Exception as e:
                logger.error(f"加载 {file_path} 失败: {e}")

        if not dfs:
            return None

        combined = pd.concat(dfs, ignore_index=True)
        combined = combined.sort_values("date").reset_index(drop=True)
        logger.info(f"城市 {city_name} 总计: {len(combined)} 条记录")
        return combined

    def load_all_cities(self, cities: Optional[List[str]] = None) -> pd.DataFrame:
        """
        加载所有城市数据

        Args:
            cities: 指定城市列表，None则加载所有可用城市

        Returns:
            所有城市合并的 DataFrame
        """
        if cities is None:
            # 自动发现所有城市目录
            cities = [d.name.replace("_", " ") for d in self.merged_dir.iterdir() if d.is_dir()]

        dfs = []
        for city in cities:
            df = self.load_merged_city_all_years(city)
            if df is not None:
                dfs.append(df)

        if not dfs:
            raise ValueError("没有加载到任何城市数据")

        combined = pd.concat(dfs, ignore_index=True)
        combined = combined.sort_values(["city_name", "date"]).reset_index(drop=True)
        logger.info(f"所有城市总计: {len(combined)} 条记录，{combined['city_name'].nunique()} 个城市")
        return combined


def load_training_data(data_path: Optional[str] = None, cities: Optional[List[str]] = None) -> pd.DataFrame:
    """
    加载训练数据（便捷函数）

    Args:
        data_path: 数据文件路径，None则从merged目录加载
        cities: 指定城市列表

    Returns:
        训练用 DataFrame
    """
    if data_path:
        logger.info(f"从文件加载数据: {data_path}")
        df = pd.read_csv(data_path)
        df["date"] = pd.to_datetime(df["date"])
        return df

    loader = DataLoader()
    return loader.load_all_cities(cities)
