"""
NOAA 城市气象数据处理 Pipeline

完整流程：站点匹配 -> 数据下载 -> 清洗处理 -> 多站点合并 -> 插值 -> 保存
"""

import pandas as pd
from typing import Optional, List, Dict, Tuple
from pathlib import Path

from loguru import logger

from ...config import NOAA_CACHE_DIR, NOAA_PROCESSED_DIR, DEFAULT_START_YEAR, DEFAULT_END_YEAR
from ..acquisition.noaa.client import NOAAClient
from ..acquisition.noaa.matcher import NOAAStationMatcher
from ..processing.noaa_processor import NOAADataProcessor
from ..storage.noaa_saver import NOAADataSaver


class NOAACityPipeline:
    """NOAA 城市气象数据完整处理流程"""

    def __init__(
        self,
        isd_history_path: Optional[str] = None,
        cache_dir: Optional[str] = None,
        processed_dir: Optional[str] = None,
    ):
        self.matcher = NOAAStationMatcher(isd_history_path)
        self.client = NOAAClient()
        self.processor = NOAADataProcessor()
        self.saver = NOAADataSaver(processed_dir)
        self.cache_dir = Path(cache_dir) if cache_dir else Path(NOAA_CACHE_DIR)

    def process_city(
        self,
        city_data: Dict,
        start_year: int = DEFAULT_START_YEAR,
        end_year: int = DEFAULT_END_YEAR,
        search_radius_km: float = 50,
        max_stations: int = 5,
        min_coverage: float = 0.3,
        enable_interpolation: bool = True,
        interpolation_limit: int = 3,
    ) -> Optional[List[str]]:
        """
        处理单个城市的完整流程

        Args:
            city_data: 城市信息字典 (city_ascii, lat, lng)
            start_year: 起始年份
            end_year: 结束年份
            search_radius_km: 搜索半径（公里）
            max_stations: 最多使用站点数
            min_coverage: 最小数据覆盖率阈值
            enable_interpolation: 是否启用插值
            interpolation_limit: 最大连续插值天数

        Returns:
            保存的文件路径列表
        """
        city_name = city_data.get("city_ascii", city_data.get("city", "Unknown"))
        logger.info(f"\n{'='*60}")
        logger.info(f"处理城市: {city_name}")
        logger.info(f"{'='*60}")

        # Step 1: 匹配周边站点
        logger.info(f"[1/5] 搜索周边站点 (半径 {search_radius_km}km)...")
        stations = self.matcher.find_nearest_stations(
            city_data["lat"],
            city_data["lng"],
            n=max_stations,
            max_distance_km=search_radius_km,
        )

        if not stations:
            logger.warning(f"未找到 {city_name} 附近的气象站点")
            return None

        logger.info(f"  -> 找到 {len(stations)} 个站点")

        # Step 2: 下载数据
        logger.info(f"[2/5] 下载气象数据 ({start_year}-{end_year})...")
        station_ids = [s["station_id"] for s in stations]
        downloaded_files = self._download_city_data(city_name, station_ids, start_year, end_year)

        if not downloaded_files:
            logger.error("未能下载任何数据")
            return None

        # Step 3: 清洗处理
        logger.info(f"[3/5] 数据清洗与处理...")
        station_dfs = {}

        for station_id, file_paths in downloaded_files.items():
            dfs = [pd.read_csv(f) for f in file_paths]
            if not dfs:
                continue

            raw_df = pd.concat(dfs, ignore_index=True)
            clean_df = self.processor.process(raw_df)

            if not clean_df.empty:
                station_dfs[station_id] = clean_df

        if not station_dfs:
            logger.error("没有有效的数据可处理")
            return None

        # Step 4: 多站点合并
        logger.info(f"[4/5] 多站点数据合并...")

        if len(station_dfs) > 1:
            station_dfs = self.processor.filter_low_coverage_stations(station_dfs, min_coverage=min_coverage)

        if not station_dfs:
            logger.error("所有站点均不符合质量要求")
            return None

        if len(station_dfs) > 1:
            final_df = self.processor.merge_multi_station_data(station_dfs, stations, quality_control=True)
        else:
            final_df = list(station_dfs.values())[0].copy()
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
                if col in final_df.columns:
                    final_df[f"{col}_source_count"] = 1
            final_df["station_count"] = 1
            final_df["data_source"] = "single_station"
            final_df["data_quality_score"] = 1.0

        final_df["city_name"] = city_name

        # Step 5: 缺失值插值
        if enable_interpolation and not final_df.empty:
            logger.info(f"[5/5] 缺失值插值...")
            final_df = self.processor.interpolate_missing_values(final_df, limit=interpolation_limit)

        # 保存
        logger.info(f"[保存] 保存处理后数据...")
        saved_files = self.saver.save(final_df, city_name, stations_count=len(station_dfs))

        # 生成报告
        self.saver.generate_report(final_df, city_name, len(station_dfs))

        logger.info(f"[完成] {city_name} - 已保存 {len(saved_files)} 个文件")
        return saved_files

    def _download_city_data(
        self,
        city_name: str,
        station_ids: List[str],
        start_year: int,
        end_year: int,
    ) -> Dict[str, List[Path]]:
        """
        下载城市气象数据

        Args:
            city_name: 城市名
            station_ids: 站点ID列表
            start_year: 起始年份
            end_year: 结束年份

        Returns:
            Dict[station_id, List[Path]]
        """
        safe_city_name = city_name.replace(" ", "_").replace("/", "_")
        city_cache_dir = self.cache_dir / safe_city_name
        city_cache_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        for station_id in station_ids:
            station_files = []
            for year in range(start_year, end_year + 1):
                file_path = self.client.download_year(year, station_id, str(city_cache_dir))
                if file_path:
                    station_files.append(Path(file_path))

            if station_files:
                results[station_id] = station_files

        return results


def process_noaa_cities(
    cities: List[Tuple[str, str]],
    config: Optional[Dict] = None,
) -> Dict[str, List[str]]:
    """
    处理多个城市的 NOAA 气象数据

    Args:
        cities: 城市列表 [(城市名, 国家代码), ...]
        config: 配置字典

    Returns:
        Dict[城市名, 文件路径列表]
    """
    from ...config import WORLDCITIES_PATH

    config = config or {}

    # 加载城市数据
    world_cities = pd.read_csv(WORLDCITIES_PATH)

    pipeline = NOAACityPipeline()
    results = {}

    start_year = config.get("start_year", DEFAULT_START_YEAR)
    end_year = config.get("end_year", DEFAULT_END_YEAR)
    search_radius_km = config.get("search_radius_km", 50)
    max_stations = config.get("max_stations", 5)

    for city_name, country_code in cities:
        # 查找城市坐标
        city_row = world_cities[
            (world_cities["city_ascii"].str.lower() == city_name.lower()) & (world_cities["iso2"] == country_code)
        ]

        if city_row.empty:
            logger.warning(f"未找到城市: {city_name}, {country_code}")
            continue

        city_data = {
            "city_ascii": city_name,
            "lat": city_row.iloc[0]["lat"],
            "lng": city_row.iloc[0]["lng"],
        }

        saved_paths = pipeline.process_city(
            city_data=city_data,
            start_year=start_year,
            end_year=end_year,
            search_radius_km=search_radius_km,
            max_stations=max_stations,
        )

        if saved_paths:
            results[city_name] = saved_paths

    return results
