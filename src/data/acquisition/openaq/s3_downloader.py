"""
OpenAQ S3 历史数据下载器

从 AWS S3 公开数据集批量下载年度数据
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

try:
    import boto3
    from botocore.config import Config
    from botocore import UNSIGNED

    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

from ....config import OPENAQ_CACHE_DIR, OPENAQ_S3_BUCKET

from loguru import logger


class OpenAQS3Downloader:
    """OpenAQ S3 历史数据下载器 - 支持并发下载"""

    S3_BUCKET = OPENAQ_S3_BUCKET

    def __init__(self, cache_dir: Optional[str] = None, max_workers: int = 10):
        """
        初始化 S3 下载器

        Args:
            cache_dir: 数据缓存目录
            max_workers: 并发下载线程数
        """
        if not HAS_BOTO3:
            raise ImportError("需要安装 boto3 才能使用 S3 下载功能")

        self.cache_dir = Path(cache_dir) if cache_dir else Path(OPENAQ_CACHE_DIR)
        self.s3_cache_dir = self.cache_dir / "s3"
        self.s3_cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers

        self.s3_client = boto3.client(
            "s3",
            config=Config(
                signature_version=UNSIGNED,
                max_pool_connections=max_workers * 2,
            ),
        )

    def _list_s3_files(self, location_id: int, year: int, month: Optional[int] = None) -> List[str]:
        """
        列出 S3 上指定 location_id 和年份的文件

        Args:
            location_id: OpenAQ 站点 ID
            year: 年份
            month: 月份 (可选)

        Returns:
            文件 key 列表
        """
        prefix = f"records/csv.gz/locationid={location_id}/year={year}/"
        if month:
            prefix += f"month={month:02d}/"

        try:
            response = self.s3_client.list_objects_v2(Bucket=self.S3_BUCKET, Prefix=prefix)

            files = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    key = obj["Key"]
                    if key.endswith(".csv.gz"):
                        files.append(key)

            return sorted(files)

        except Exception as e:
            logger.error(f"列出 S3 文件失败: {e}")
            return []

    def download_year_data(
        self,
        location_id: int,
        year: int,
        city_cache_dir: Path,
        use_cache: bool = True,
    ) -> List[Path]:
        """
        下载指定站点某年的所有数据

        Args:
            location_id: OpenAQ 站点 ID
            year: 年份
            city_cache_dir: 城市专属缓存目录
            use_cache: 是否使用缓存

        Returns:
            下载的文件路径列表
        """
        s3_files = self._list_s3_files(location_id, year)

        if not s3_files:
            logger.warning(f"未找到数据: locationid={location_id}, year={year}")
            return []

        year_cache_dir = city_cache_dir / f"{year}" / str(location_id)
        downloaded_files = []
        failed_count = [0]
        success_count = [0]
        lock = Lock()

        def download_single_file(s3_key: str) -> Optional[Path]:
            filename = s3_key.split("/")[-1]
            local_path = year_cache_dir / filename

            if use_cache and local_path.exists():
                with lock:
                    success_count[0] += 1
                return local_path

            try:
                response = self.s3_client.get_object(Bucket=self.S3_BUCKET, Key=s3_key)
                content = response["Body"].read()

                local_path.parent.mkdir(parents=True, exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(content)

                with lock:
                    success_count[0] += 1
                return local_path

            except Exception as e:
                with lock:
                    failed_count[0] += 1
                logger.error(f"下载失败 {s3_key}: {e}")
                return None

        # 并发下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_key = {executor.submit(download_single_file, key): key for key in s3_files}

            for future in as_completed(future_to_key):
                result = future.result()
                if result:
                    downloaded_files.append(result)

        logger.info(f"站点 {location_id} {year}年: 成功 {success_count[0]}/{len(s3_files)}")
        return downloaded_files

    def download_stations_for_city(
        self,
        city_data: Dict,
        stations: List[Dict],
        start_year: int,
        end_year: int,
        use_cache: bool = True,
    ) -> Dict[int, List[Path]]:
        """
        为城市下载多个站点的年度 S3 数据

        Args:
            city_data: 城市信息
            stations: 站点列表
            start_year: 起始年份
            end_year: 结束年份
            use_cache: 是否使用缓存

        Returns:
            Dict[location_id, List[Path]]
        """
        city_name = city_data.get("city_ascii", city_data.get("city", "unknown"))
        safe_city_name = city_name.replace(" ", "_").replace("/", "_")
        city_cache_dir = self.s3_cache_dir / safe_city_name

        results = {}
        total_files = 0

        logger.info(f"\n[S3下载] 城市: {city_name}, 年份: {start_year}-{end_year}, 站点: {len(stations)}")

        for station in stations:
            location_id = station.get("location_id") or station.get("id")
            if not location_id:
                continue

            station_name = station.get("name", station.get("location_name", f"Station-{location_id}"))
            logger.info(f"  站点: {station_name}")

            station_files = []
            for year in range(start_year, end_year + 1):
                files = self.download_year_data(location_id, year, city_cache_dir, use_cache)
                station_files.extend(files)

            if station_files:
                results[location_id] = station_files
                total_files += len(station_files)

        logger.info(f"[S3下载完成] 总计: {len(results)} 个站点, {total_files} 个文件")
        return results
