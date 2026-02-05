"""
OpenAQ数据客户端

使用 openaq-python 库从 OpenAQ API 获取空气质量数据
参考: https://python.openaq.org/
"""

import pandas as pd
from pandas import json_normalize
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import time

try:
    from openaq import OpenAQ
except ImportError:
    OpenAQ = None

from loguru import logger


class OpenAQClient:
    """OpenAQ API客户端 (基于 openaq-python 库)"""

    # 污染物参数ID映射
    PARAMETER_IDS = {
        "pm25": 2,
        "pm10": 1,
        "o3": 10,
        "no2": 7,
        "so2": 9,
        "co": 8,
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: OpenAQ API Key，默认从环境变量 OPENAQ_API_KEY 读取
        """
        if OpenAQ is None:
            raise ImportError("openaq 库未安装，请运行: pip install openaq")

        self.api_key = api_key or __import__("os").environ.get("OPENAQ_API_KEY")
        self._client = OpenAQ(api_key=self.api_key)

    def close(self):
        """关闭客户端连接"""
        self._client.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def get_rate_limit_info(self) -> Optional[Dict]:
        """
        获取最后一次请求的速率限制信息

        Returns:
            包含速率限制信息的字典，如果没有请求过则返回 None
        """
        # OpenAQ Python SDK 内部会自动处理速率限制
        # 这里提供一个获取信息的方法
        return None

    def get_locations(
        self,
        lat: float,
        lon: float,
        radius: int = 25000,
        limit: int = 100,
        bbox: Optional[Tuple[float, float, float, float]] = None,
    ) -> List[Dict]:
        """
        获取指定位置周边的监测站点

        参考: https://python.openaq.org/how-to-guides/geospatial-queries/

        Args:
            lat: 纬度 (coordinates 模式使用)
            lon: 经度 (coordinates 模式使用)
            radius: 搜索半径（米），默认25000米(25km)
            limit: 每页返回数量，默认100，最大1000
            bbox: 边界框 (min_lon, min_lat, max_lon, max_lat)，与 coordinates/radius 互斥

        Returns:
            站点数据列表（字典列表）
        """
        try:
            # 构建查询参数
            params = {"limit": min(limit, 1000)}

            if bbox:
                # 使用边界框查询
                params["bbox"] = bbox
            else:
                # 使用坐标和半径查询
                # 注意: coordinates 参数格式为 (纬度, 经度) 元组
                params["coordinates"] = (lat, lon)
                params["radius"] = radius

            response = self._client.locations.list(**params)

            # 使用 json_normalize 扁平化嵌套数据，然后转换为字典列表
            if response.results:
                data = response.dict()
                df = json_normalize(data["results"], sep="_")
                return df.to_dict("records")
            else:
                return []

        except Exception as e:
            logger.error(f"获取站点列表失败: {e}")
            return []

    def get_sensor_measurements(
        self,
        sensor_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 1000,
        max_pages: int = 10,
    ) -> pd.DataFrame:
        """
        获取指定传感器的测量数据

        参考: https://python.openaq.org/how-to-guides/paging-results/

        Args:
            sensor_id: 传感器ID
            date_from: 开始日期 (YYYY-MM-DD)，可选
            date_to: 结束日期 (YYYY-MM-DD)，可选
            limit: 每页限制，默认1000，最大1000
            max_pages: 最大分页数，防止无限循环，默认10

        Returns:
            测量数据DataFrame
        """
        all_results = []
        page = 1
        limit = min(limit, 1000)  # API 最大限制为 1000

        try:
            from datetime import datetime as dt, timezone

            # 准备基础参数
            params = {
                "sensors_id": sensor_id,
                "limit": limit,
            }

            # 添加日期过滤参数
            if date_from:
                if isinstance(date_from, str):
                    date_from = dt.strptime(date_from, "%Y-%m-%d")
                params["datetime_from"] = date_from

            if date_to:
                if isinstance(date_to, str):
                    date_to = dt.strptime(date_to, "%Y-%m-%d")
                # 设置时间为当天结束
                date_to = date_to.replace(hour=23, minute=59, second=59)
                params["datetime_to"] = date_to

            logger.debug(
                f"请求参数: sensors_id={sensor_id}, datetime_from={params.get('datetime_from')}, datetime_to={params.get('datetime_to')}"
            )

            # 分页获取所有数据
            # 参考文档: 对于 measurements，found 是估计值，应该检查 results 是否为空
            while page <= max_pages:
                params["page"] = page

                logger.debug(f"获取传感器 {sensor_id} 第 {page} 页数据")
                response = self._client.measurements.list(**params)

                if not response.results:
                    break

                # 使用 dict() 方法获取原始数据，然后用 json_normalize 处理
                data = response.dict()
                all_results.extend(data["results"])

                # 如果当前页结果数小于限制，说明已经是最后一页
                if len(response.results) < limit:
                    break

                page += 1
                # 添加短暂延迟，避免触发速率限制
                time.sleep(0.2)

            if not all_results:
                return pd.DataFrame()

            # 使用 json_normalize 扁平化嵌套数据
            df = json_normalize(all_results, sep="_")

            # 重命名 datetime 列以便更清晰
            if "period_datetimeFrom_utc" in df.columns:
                df["datetime"] = pd.to_datetime(df["period_datetimeFrom_utc"], utc=True, errors="coerce")
            if "period_datetimeFrom_local" in df.columns:
                df["datetime_local"] = pd.to_datetime(df["period_datetimeFrom_local"], utc=True, errors="coerce")
            if "period_datetimeTo_utc" in df.columns:
                df["datetime_to"] = pd.to_datetime(df["period_datetimeTo_utc"], utc=True, errors="coerce")

            # 添加传感器ID列
            df["sensor_id"] = sensor_id

            return df

        except Exception as e:
            import traceback

            logger.error(f"获取传感器 {sensor_id} 测量数据失败: {e}")
            logger.debug(f"错误详情:\n{traceback.format_exc()}")
            return pd.DataFrame()

    def get_location_sensors(self, location_id: int, parameter: str = "pm25") -> List[Dict]:
        """
        获取站点的传感器列表

        Args:
            location_id: 站点ID
            parameter: 污染物参数

        Returns:
            传感器列表
        """
        try:
            # 使用 openaq 库的 locations.get 方法
            response = self._client.locations.get(location_id)

            if not response or not response.results:
                return []

            location = response.results[0] if isinstance(response.results, list) else response.results
            sensors = location.sensors or []

            # 筛选指定参数的传感器
            param_id = self.PARAMETER_IDS.get(parameter)
            matching_sensors = []

            for sensor in sensors:
                sensor_param = sensor.parameter if hasattr(sensor, "parameter") else None
                if sensor_param and getattr(sensor_param, "id", None) == param_id:
                    matching_sensors.append(
                        {
                            "sensor_id": sensor.id,
                            "name": sensor.name,
                            "parameter": parameter,
                        }
                    )

            return matching_sensors

        except Exception as e:
            logger.error(f"获取站点 {location_id} 传感器列表失败: {e}")
            return []

    def get_measurements(self, location_id: int, date_from: str, date_to: str, parameter: str = "pm25") -> pd.DataFrame:
        """
        获取指定站点的测量数据（通过传感器）

        Args:
            location_id: 站点ID
            date_from: 开始日期 (YYYY-MM-DD)
            date_to: 结束日期 (YYYY-MM-DD)
            parameter: 污染物参数

        Returns:
            测量数据DataFrame
        """
        # 获取该站点的传感器
        sensors = self.get_location_sensors(location_id, parameter)

        if not sensors:
            logger.warning(f"站点 {location_id} 没有找到 {parameter} 传感器")
            return pd.DataFrame()

        # 使用第一个匹配的传感器
        sensor_id = sensors[0]["sensor_id"]
        logger.debug(f"使用传感器 {sensor_id} 获取 {parameter} 数据")

        return self.get_sensor_measurements(sensor_id, date_from, date_to)

    def get_city_data(
        self, city: str, lat: float, lon: float, year: int, parameters: Optional[List[str]] = None, radius: int = 25000
    ) -> pd.DataFrame:
        """
        获取城市某年的空气质量数据

        Args:
            city: 城市名
            lat: 纬度
            lon: 经度
            year: 年份
            parameters: 污染物列表，默认pm25
            radius: 搜索半径（米），默认25000米(25km)

        Returns:
            合并的DataFrame
        """
        if parameters is None:
            parameters = ["pm25"]

        # 获取周边站点（返回字典列表）
        locations = self.get_locations(lat, lon, radius=radius, limit=100)

        if not locations:
            logger.info(f"城市 {city} 没有找到监测站点")
            return pd.DataFrame()

        logger.info(f"城市 {city} 找到 {len(locations)} 个监测站点")

        # 获取每个站点的数据
        date_from = f"{year}-01-01"
        date_to = f"{year}-12-31"

        all_data = []

        for loc in locations:
            # 从扁平化的键名中获取 id 和 name
            loc_id = loc.get("id")
            loc_name = loc.get("name", "Unknown")

            if not loc_id:
                continue

            for param in parameters:
                df = self.get_measurements(int(loc_id), date_from, date_to, param)
                if not df.empty:
                    df["location_id"] = loc_id
                    df["location_name"] = loc_name
                    df["city"] = city
                    all_data.append(df)

        if not all_data:
            return pd.DataFrame()

        return pd.concat(all_data, ignore_index=True)
