"""
城市数据解析器

用于解析 worldcities.csv，根据城市名称查找经纬度等信息
"""

import os.path as osp
import pandas as pd
from typing import Optional, Dict, Any


class CityParser:
    """城市数据解析器"""

    def __init__(self, csv_path: Optional[str] = None):
        """
        初始化城市解析器

        Args:
            csv_path: worldcities.csv 文件路径，为None则使用配置路径
        """
        from ..config import WORLDCITIES_PATH

        if csv_path is None:
            csv_path = WORLDCITIES_PATH

        if not osp.exists(csv_path):
            raise FileNotFoundError(
                f"城市数据文件不存在: {csv_path}\n" f"请从 SimpleMaps 或其他数据源下载 worldcities.csv 并放置到该路径。"
            )

        # Load CSV with string dtype for all columns
        self.df = pd.read_csv(csv_path, dtype=str)

        # Convert numeric columns safely
        numeric_columns = {"lat": 0.0, "lng": 0.0, "population": 0}

        for col, default_value in numeric_columns.items():
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").fillna(default_value)
            else:
                self.df[col] = default_value

    def get_city_data(self, city_name: str, country_iso2: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        查找城市数据

        Args:
            city_name: 城市名称（英文）
            country_iso2: 国家 ISO2 代码（可选）

        Returns:
            城市数据字典，未找到返回None
        """
        # Normalize input
        city_normalized = city_name.strip().lower()

        # Create normalized column for comparison
        self.df["city_normalized"] = self.df["city"].str.strip().str.lower()

        # Match
        mask = self.df["city_normalized"] == city_normalized

        if country_iso2:
            mask = mask & (self.df["iso2"] == country_iso2.upper())

        matches = self.df[mask]

        if matches.empty:
            return None

        # If multiple matches, return the one with largest population
        if len(matches) > 1:
            matches = matches.sort_values("population", ascending=False)

        city_data = matches.iloc[0]

        return {
            "city": city_data["city"],
            "country": city_data.get("country", ""),
            "iso2": city_data.get("iso2", ""),
            "iso3": city_data.get("iso3", ""),
            "lat": float(city_data["lat"]),
            "lng": float(city_data["lng"]),
            "population": int(city_data["population"]) if pd.notna(city_data["population"]) else 0,
            "admin_name": city_data.get("admin_name", ""),
        }

    def search_cities(self, query: str, limit: int = 10) -> pd.DataFrame:
        """
        搜索城市

        Args:
            query: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            匹配的城市DataFrame
        """
        query_lower = query.lower()
        mask = self.df["city"].str.lower().str.contains(query_lower, na=False) | self.df[
            "country"
        ].str.lower().str.contains(query_lower, na=False)
        return self.df[mask].head(limit)[["city", "country", "iso2", "lat", "lng", "population"]]
