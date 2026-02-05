"""
OpenAQ 城市空气质量数据处理 Pipeline

完整流程：站点匹配 -> 数据下载(S3/API) -> 清洗处理 -> 多站点合并 -> 保存
"""

import pandas as pd
from typing import Optional, List, Dict, Tuple
from pathlib import Path

from loguru import logger

from ...config import OPENAQ_CACHE_DIR, OPENAQ_PROCESSED_DIR, DEFAULT_START_YEAR, DEFAULT_END_YEAR
from ..acquisition.openaq.client import OpenAQClient
from ..processing.openaq_processor import OpenAQDataProcessor
from ..storage.openaq_saver import OpenAQDataSaver


class OpenAQCityPipeline:
    """OpenAQ 城市空气质量数据完整处理流程"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        processed_dir: Optional[str] = None,
        use_s3: bool = True,
        max_workers: int = 10,
    ):
        """
        初始化 Pipeline

        Args:
            api_key: OpenAQ API Key
            cache_dir: 原始数据缓存目录
            processed_dir: 处理后数据保存目录
            use_s3: 是否使用 S3 下载历史数据
            max_workers: S3 并发下载线程数
        """
        self.client = OpenAQClient(api_key)
        self.processor = OpenAQDataProcessor()
        self.saver = OpenAQDataSaver(processed_dir)
        self.cache_dir = Path(cache_dir) if cache_dir else Path(OPENAQ_CACHE_DIR)
        self.use_s3 = use_s3
        self.max_workers = max_workers

        if use_s3:
            try:
                from ..acquisition.openaq.s3_downloader import OpenAQS3Downloader

                self.s3_downloader = OpenAQS3Downloader(cache_dir, max_workers)
                logger.info(f"使用 S3 下载器 (并发: {max_workers})")
            except ImportError:
                logger.warning("boto3 未安装，回退到 API 模式")
                self.use_s3 = False

    def process_city(
        self,
        city_data: Dict,
        pollutants: Optional[List[str]] = None,
        start_date: str = None,
        end_date: str = None,
        search_radius_m: int = 25000,
        max_stations: int = 20,
        use_cache: bool = True,
        fill_missing_dates: bool = False,
    ) -> Optional[List[str]]:
        """
        处理单个城市的完整流程

        Args:
            city_data: 城市信息字典
            pollutants: 污染物列表，默认 ["pm25"]
            start_date: 开始日期，默认当年1月1日
            end_date: 结束日期，默认当年12月31日
            search_radius_m: 搜索半径（米）
            max_stations: 最多使用站点数
            use_cache: 是否使用缓存
            fill_missing_dates: 是否填充缺失日期

        Returns:
            保存的文件路径列表
        """
        if pollutants is None:
            pollutants = ["pm25"]

        if start_date is None:
            start_date = f"{DEFAULT_START_YEAR}-01-01"
        if end_date is None:
            end_date = f"{DEFAULT_END_YEAR}-12-31"

        city_name = city_data.get("city_ascii", city_data.get("city", "Unknown"))
        logger.info(f"\n{'='*60}")
        logger.info(f"处理城市: {city_name}")
        logger.info(f"污染物: {', '.join(pollutants)}")
        logger.info(f"{'='*60}")

        # Step 1: 搜索监测站点
        logger.info(f"[1/4] 搜索监测站点...")
        stations = self.client.get_locations(
            city_data["lat"],
            city_data["lng"],
            radius=search_radius_m,
            limit=max_stations,
        )

        if not stations:
            logger.warning(f"未找到 {city_name} 附近的监测站点")
            return None

        logger.info(f"  -> 找到 {len(stations)} 个站点")

        # Step 2: 下载数据
        logger.info(f"[2/4] 下载空气质量数据...")

        # 根据配置选择 S3 或 API 下载
        if self.use_s3 and hasattr(self, "s3_downloader"):
            logger.info("  使用 S3 历史数据下载")
            all_pollutant_data = self._download_from_s3(
                city_name, stations, start_date, end_date, pollutants, use_cache
            )
        else:
            logger.info("  使用 API 实时数据下载")
            all_pollutant_data = self._download_from_api(stations, start_date, end_date, pollutants)

        # Step 3: 合并多污染物数据
        logger.info(f"[3/4] 合并多污染物数据...")
        final_df = self._merge_pollutants(all_pollutant_data)
        final_df["city_name"] = city_name

        # Step 4: 保存
        logger.info(f"[4/4] 保存处理后数据...")
        saved_files = self.saver.save(
            final_df,
            city_name,
            stations_count=len(stations),
            pollutants=pollutants,
            fill_missing_dates=fill_missing_dates,
        )

        logger.info(f"[完成] {city_name} - 已保存 {len(saved_files)} 个文件")
        return saved_files

    def _merge_pollutants(self, pollutant_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """合并不同污染物的数据"""
        result = None

        for pollutant, df in pollutant_data.items():
            if result is None:
                result = df.copy()
            else:
                existing_cols = set(result.columns)
                new_cols = [c for c in df.columns if c not in existing_cols or c == "date"]
                result = pd.merge(result, df[new_cols], on="date", how="outer")

        return result.sort_values("date").reset_index(drop=True) if result is not None else pd.DataFrame()

    def _download_from_api(
        self,
        stations: List[Dict],
        start_date: str,
        end_date: str,
        pollutants: List[str],
    ) -> Dict[str, pd.DataFrame]:
        """
        使用 API 下载数据

        Args:
            stations: 站点列表
            start_date: 开始日期
            end_date: 结束日期
            pollutants: 污染物列表

        Returns:
            Dict[污染物, DataFrame]
        """
        all_pollutant_data = {}

        for pollutant in pollutants:
            logger.info(f"  API下载 {pollutant.upper()}...")
            station_dfs = {}

            for station in stations:
                loc_id = station.get("id")
                sensors = station.get("sensors", [])
                param_ids = {2: "pm25", 1: "pm10", 10: "o3", 7: "no2", 9: "so2", 8: "co"}
                sensor_id = None
                for s in sensors:
                    if param_ids.get(s.get("parameter_id")) == pollutant:
                        sensor_id = s.get("id")
                        break

                if not sensor_id:
                    continue

                df = self.client.get_measurements(sensor_id, start_date, end_date, pollutant)
                if not df.empty:
                    df = self.processor.detect_outliers(df, pollutant)
                    station_dfs[sensor_id] = df

            if station_dfs:
                if len(station_dfs) > 1:
                    stations_info = [{"sensor_id": k, "distance_m": 0} for k in station_dfs.keys()]
                    merged_df = self.processor.merge_multi_station_data(station_dfs, stations_info)
                else:
                    merged_df = list(station_dfs.values())[0]
                    merged_df["data_source"] = "single_station"
                    merged_df["data_quality_score"] = 1.0
                all_pollutant_data[pollutant] = merged_df
            else:
                logger.warning(f"  {pollutant}: API无数据")

        return all_pollutant_data

    def _download_from_s3(
        self,
        city_name: str,
        stations: List[Dict],
        start_date: str,
        end_date: str,
        pollutants: List[str],
        use_cache: bool = True,
    ) -> Dict[str, pd.DataFrame]:
        """
        使用 S3 下载历史数据

        Args:
            city_name: 城市名称，用于缓存目录
            stations: 站点列表
            start_date: 开始日期
            end_date: 结束日期
            pollutants: 污染物列表
            use_cache: 是否使用缓存

        Returns:
            Dict[污染物, DataFrame]
        """
        import gzip

        start_year = int(start_date[:4])
        end_year = int(end_date[:4])
        all_pollutant_data = {}

        for pollutant in pollutants:
            logger.info(f"  S3下载 {pollutant.upper()}...")
            station_dfs = {}

            for station in stations:
                loc_id = station.get("id")
                loc_name = station.get("name", f"Station-{loc_id}")

                # 使用 S3 下载器下载该站点多年数据
                files = self.s3_downloader.download_stations_for_city(
                    city_data={"city_ascii": city_name},
                    stations=[{"location_id": loc_id, "name": loc_name}],
                    start_year=start_year,
                    end_year=end_year,
                    use_cache=use_cache,
                )

                if loc_id in files and files[loc_id]:
                    # 读取并合并所有下载的文件
                    dfs = []
                    for f in files[loc_id]:
                        try:
                            with gzip.open(f, "rt") as gf:
                                df = pd.read_csv(gf)
                                # 过滤指定污染物
                                if "parameter" in df.columns:
                                    df = df[df["parameter"] == pollutant]
                                if not df.empty:
                                    dfs.append(df)
                        except Exception as e:
                            logger.warning(f"    读取文件失败 {f.name}: {e}")

                    if dfs:
                        combined_df = pd.concat(dfs, ignore_index=True)
                        # 标准化列名
                        if "datetime" in combined_df.columns and "date" not in combined_df.columns:
                            # 使用 utc=True 避免时区混合警告，并处理解析失败
                            try:
                                dt_series = pd.to_datetime(combined_df["datetime"], utc=True)
                                combined_df["date"] = dt_series.dt.tz_localize(None).dt.date
                            except Exception as e:
                                logger.warning(f"    datetime解析失败: {e}")
                                combined_df["date"] = combined_df["datetime"]
                        if "value" in combined_df.columns:
                            combined_df[pollutant] = combined_df["value"]

                        combined_df = self.processor.detect_outliers(combined_df, pollutant)
                        station_dfs[loc_id] = combined_df
                        logger.info(f"    站点 {loc_name}: {len(combined_df)} 条记录")

            if station_dfs:
                if len(station_dfs) > 1:
                    stations_info = [{"sensor_id": k, "distance_m": 0} for k in station_dfs.keys()]
                    merged_df = self.processor.merge_multi_station_data(station_dfs, stations_info)
                else:
                    merged_df = list(station_dfs.values())[0]
                    merged_df["data_source"] = "single_station"
                    merged_df["data_quality_score"] = 1.0
                all_pollutant_data[pollutant] = merged_df
                logger.info(f"  {pollutant}: 合并 {len(station_dfs)} 个站点")
            else:
                logger.warning(f"  {pollutant}: S3无数据")

        return all_pollutant_data


def process_openaq_cities(
    cities: List[Tuple[str, str]],
    config: Optional[Dict] = None,
) -> Dict[str, List[str]]:
    """
    处理多个城市的 OpenAQ 空气质量数据

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

    pipeline = OpenAQCityPipeline(
        use_s3=config.get("use_s3", True),
        max_workers=config.get("max_workers", 10),
    )
    results = {}

    pollutants = config.get("pollutants", ["pm25"])
    start_date = config.get("start_date", f"{DEFAULT_START_YEAR}-01-01")
    end_date = config.get("end_date", f"{DEFAULT_END_YEAR}-12-31")
    search_radius_m = config.get("search_radius_m", 25000)
    max_stations = config.get("max_stations", 20)

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
            pollutants=pollutants,
            start_date=start_date,
            end_date=end_date,
            search_radius_m=search_radius_m,
            max_stations=max_stations,
        )

        if saved_paths:
            results[city_name] = saved_paths

    return results
