"""
NOAA气象站点匹配器

根据城市坐标查找最近的气象站点
"""

import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from typing import Optional, List, Dict

from ....config import ISD_HISTORY_PATH

from loguru import logger


class NOAAStationMatcher:
    """气象站点匹配器 - 根据坐标查找最近站点"""

    def __init__(self, isd_history_path: Optional[str] = None):
        """
        初始化站点匹配器

        Args:
            isd_history_path: ISD历史站点数据文件路径
        """
        import os.path as osp

        if isd_history_path is None:
            isd_history_path = ISD_HISTORY_PATH

        if not osp.exists(isd_history_path):
            raise FileNotFoundError(f"ISD历史站点数据文件不存在: {isd_history_path}")

        self.df = pd.read_csv(isd_history_path)
        self._clean_station_data()

    def _clean_station_data(self):
        """清洗站点数据"""
        from datetime import datetime

        # 转换经纬度为数值类型
        self.df["LAT"] = pd.to_numeric(self.df["LAT"], errors="coerce")
        self.df["LON"] = pd.to_numeric(self.df["LON"], errors="coerce")
        self.df["ELEV(M)"] = pd.to_numeric(self.df["ELEV(M)"], errors="coerce")

        # 只保留有有效坐标的站点
        self.df = self.df.dropna(subset=["LAT", "LON"])

        # 只保留结束日期在2年内的站点
        self.df["END"] = pd.to_numeric(self.df["END"], errors="coerce")
        current_year = datetime.now().year
        self.df = self.df[self.df["END"] >= (current_year - 2) * 10000]

        logger.info(f"有效站点数: {len(self.df)}")

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        计算两点间的球面距离（单位：公里）

        Args:
            lat1, lon1: 第一点坐标
            lat2, lon2: 第二点坐标

        Returns:
            距离（公里）
        """
        R = 6371  # 地球半径（公里）

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def find_nearest_station(self, lat: float, lon: float, max_distance_km: Optional[float] = None) -> Optional[Dict]:
        """
        查找距离指定坐标最近的气象站点

        Args:
            lat: 纬度
            lon: 经度
            max_distance_km: 最大距离限制

        Returns:
            站点信息字典
        """
        # 计算到所有站点的距离
        distances = []
        for _, row in self.df.iterrows():
            dist = self.haversine_distance(lat, lon, row["LAT"], row["LON"])
            distances.append(dist)

        self.df["distance_km"] = distances

        # 找到最近的有效站点
        valid_stations = self.df[self.df["distance_km"] < (max_distance_km or float("inf"))]

        if valid_stations.empty:
            return None

        nearest = valid_stations.loc[valid_stations["distance_km"].idxmin()]

        return {
            "usaf": str(nearest["USAF"]).zfill(6),
            "wban": str(nearest["WBAN"]).zfill(5),
            "station_id": f"{str(nearest['USAF']).zfill(6)}-{str(nearest['WBAN']).zfill(5)}",
            "name": nearest["STATION NAME"],
            "lat": nearest["LAT"],
            "lon": nearest["LON"],
            "elevation_m": nearest["ELEV(M)"],
            "distance_km": nearest["distance_km"],
        }

    def find_nearest_stations(
        self, lat: float, lon: float, n: int = 3, max_distance_km: Optional[float] = None
    ) -> List[Dict]:
        """
        查找距离最近的n个站点

        Args:
            lat: 纬度
            lon: 经度
            n: 返回站点数量
            max_distance_km: 最大距离限制

        Returns:
            站点信息列表
        """
        # 计算距离
        distances = []
        for _, row in self.df.iterrows():
            dist = self.haversine_distance(lat, lon, row["LAT"], row["LON"])
            distances.append(dist)

        self.df["distance_km"] = distances

        # 筛选并排序
        valid = self.df[self.df["distance_km"] < (max_distance_km or float("inf"))]
        valid = valid.sort_values("distance_km").head(n)

        stations = []
        for _, row in valid.iterrows():
            stations.append(
                {
                    "usaf": str(row["USAF"]).zfill(6),
                    "wban": str(row["WBAN"]).zfill(5),
                    "station_id": f"{str(row['USAF']).zfill(6)}-{str(row['WBAN']).zfill(5)}",
                    "name": row["STATION NAME"],
                    "lat": row["LAT"],
                    "lon": row["LON"],
                    "distance_km": row["distance_km"],
                }
            )

        return stations

    def find_stations_for_city(self, city_name: str, lat: float, lon: float, n: int = 3) -> List[Dict]:
        """
        为城市查找气象站点

        Args:
            city_name: 城市名
            lat: 纬度
            lon: 经度
            n: 站点数量

        Returns:
            站点列表
        """
        stations = self.find_nearest_stations(lat, lon, n=n, max_distance_km=100)
        logger.info(f"城市 {city_name} 找到 {len(stations)} 个气象站点")
        for s in stations:
            logger.info(f"  - {s['name']}: {s['distance_km']:.1f}km")
        return stations
