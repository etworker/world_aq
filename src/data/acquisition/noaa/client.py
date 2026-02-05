"""
NOAA GSOD 数据客户端

从 NOAA 官网下载历史气象数据 (HTTP 方式)
"""

from typing import Optional, List
from pathlib import Path
import requests

from ....config import NOAA_BASE_URL, NOAA_CACHE_DIR

from loguru import logger


class NOAAClient:
    """NOAA HTTP 客户端"""

    def __init__(self):
        """初始化客户端"""
        self.base_url = NOAA_BASE_URL

    def download_year(
        self,
        year: int,
        station_id: str,
        output_dir: Optional[str] = None,
        use_cache: bool = True,
    ) -> Optional[str]:
        """
        下载某年某站点的数据

        Args:
            year: 年份
            station_id: 站点ID (格式: USAFWBAN 或 USAF-WBAN)
            output_dir: 输出目录
            use_cache: 是否使用缓存

        Returns:
            下载的文件路径
        """
        import os.path as osp

        if output_dir is None:
            output_dir = NOAA_CACHE_DIR

        # 标准化站点ID (移除横线)
        clean_station_id = station_id.replace("-", "")

        # 构建本地文件路径
        output_path = osp.join(output_dir, f"{year}_{clean_station_id}.csv")

        # 检查缓存
        if use_cache and Path(output_path).exists():
            logger.debug(f"使用缓存: {output_path}")
            return output_path

        # 构建URL (与原代码一致)
        url = f"{self.base_url}/{year}/{clean_station_id}.csv"

        try:
            logger.debug(f"下载: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # 创建目录并保存文件 (与原代码一致)
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)

            logger.info(f"下载完成: {output_path}")
            return output_path

        except requests.exceptions.HTTPError:
            logger.debug(f"文件不存在: {url}")
            return None
        except Exception as e:
            logger.error(f"下载失败 {clean_station_id} {year}: {e}")
            return None

    def download_city_year(
        self,
        city: str,
        year: int,
        station_ids: List[str],
        output_dir: Optional[str] = None,
    ) -> List[str]:
        """
        下载城市某年的所有站点数据

        Args:
            city: 城市名
            year: 年份
            station_ids: 站点ID列表
            output_dir: 输出目录

        Returns:
            下载的文件路径列表
        """
        downloaded = []
        for station_id in station_ids:
            path = self.download_year(year, station_id, output_dir)
            if path:
                downloaded.append(path)

        return downloaded
