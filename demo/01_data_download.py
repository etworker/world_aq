#!/usr/bin/env python
"""
Demo: 数据下载

下载 NOAA 气象数据和 OpenAQ 空气质量数据
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.acquisition.noaa import NOAAClient, NOAAStationMatcher
from src.data.pipeline.noaa_pipeline import process_noaa_cities
from src.data.pipeline.openaq_pipeline import process_openaq_cities
from src.config import ISD_HISTORY_PATH


def demo_noaa_download():
    """示例1: NOAA 气象数据下载（查找站点 + 下载数据）"""
    print("\n" + "=" * 60)
    print("示例1: NOAA 气象数据下载")
    print("=" * 60)


    print("\n查找气象站点...")
    matcher = NOAAStationMatcher()

    # 北京坐标
    beijing_lat, beijing_lon = 39.9042, 116.4074
    stations = matcher.find_nearest_stations(beijing_lat, beijing_lon, n=3, max_distance_km=100)

    print(f"  找到 {len(stations)} 个站点:")
    for s in stations:
        print(f"    - {s['station_id']}: {s['name']} ({s['distance_km']:.1f}km)")

    print("\n  下载气象数据...")
    client = NOAAClient()

    for station in stations[:1]:  # 只下载第一个站点作为示例
        station_id = station["station_id"]
        year = 2023

        print(f"\n  下载站点 {station_id} 的 {year} 年数据...")
        result = client.download_year(year, station_id, output_dir="/tmp/data_demo/noaa", use_cache=False)

        if result:
            print(f"  ✅ 下载成功: {result}")

            import pandas as pd

            df = pd.read_csv(result)
            print(f"     数据行数: {len(df)}")
            print(f"     日期范围: {df['DATE'].min()} ~ {df['DATE'].max()}")
        else:
            print(f"  ❌ 下载失败")


def demo_openaq_api():
    """示例2: OpenAQ API 方式下载（实时/近期数据，需要 API Key）"""
    print("\n" + "=" * 60)
    print("示例2: OpenAQ API 方式下载")
    print("=" * 60)

    try:
        import os
        from datetime import datetime, timedelta
        from src.data.acquisition.openaq import OpenAQClient

        # 检查 API Key
        api_key = os.environ.get("OPENAQ_API_KEY")
        if not api_key:
            print("  ⚠️  未设置 OPENAQ_API_KEY 环境变量")
            print("     注册获取: https://docs.openaq.org/docs/getting-started")
            print("     设置方法: export OPENAQ_API_KEY='your_api_key'")
            print("\n  跳过此示例，尝试下一个示例...")
            return

        client = OpenAQClient(api_key=api_key)
        print(f"  ✅ OpenAQ API 客户端初始化成功")

        # 查找监测站点
        print("\n  查找纽约周边监测站点...")
        ny_lat, ny_lon = 40.6943, -73.9249
        locations = client.get_locations(lat=ny_lat, lon=ny_lon, radius=25000, limit=5)
        print(f"  找到 {len(locations)} 个监测站点:")
        for loc in locations[:3]:
            print(f"    - {loc.get('name', 'Unknown')}: ID={loc.get('id')}")

        # 下载站点数据
        if locations:
            print("\n  下载站点 PM2.5 数据...")

            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            df = client.get_measurements(
                location_id=locations[0].get("id"),
                date_from=start_date.strftime("%Y-%m-%d"),
                date_to=end_date.strftime("%Y-%m-%d"),
                parameter="pm25",
            )

            if not df.empty:
                output_path = "/tmp/data_demo/openaq/beijing_recent_pm25_api.csv"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                df.to_csv(output_path, index=False)

                print(f"  ✅ API下载成功: {output_path}")
                print(f"     数据行数: {len(df)}")
                print(f"     PM2.5范围: {df['value'].min():.1f} ~ {df['value'].max():.1f} µg/m³")
            else:
                print("  ⚠️  API未返回数据")

    except ImportError as e:
        print(f"  ⚠️  OpenAQ API模块未配置: {e}")
    except Exception as e:
        print(f"  ❌ API下载失败: {e}")


def demo_openaq_s3():
    """示例3: OpenAQ S3 方式下载（历史归档数据，无需 API Key）"""
    print("\n" + "=" * 60)
    print("示例3: OpenAQ S3 方式下载（推荐）")
    print("=" * 60)

    try:
        import gzip
        import pandas as pd
        from src.data.acquisition.openaq.s3_downloader import OpenAQS3Downloader

        print("  初始化 OpenAQ S3 下载器...")
        s3_downloader = OpenAQS3Downloader(cache_dir="/tmp/data_demo/openaq_s3")
        print(f"  ✅ S3下载器初始化成功")

        # 使用已知的北京站点ID (Beijing US Embassy = 21)
        beijing_station_id = 21

        print(f"\n  下载站点 {beijing_station_id} 的2023年数据...")
        print("  (S3数据为月度gzip压缩文件，自动解压合并)")

        files = s3_downloader.download_year_data(
            location_id=beijing_station_id, year=2023, city_cache_dir=Path("/tmp/data_demo/openaq_s3/beijing")
        )

        if files:
            print(f"  ✅ S3下载成功: {len(files)} 个文件")

            # 读取并展示第一个文件的内容
            first_file = files[0]
            print(f"\n  文件示例: {first_file.name}")

            with gzip.open(first_file, "rt") as f:
                df_sample = pd.read_csv(f, nrows=5)
                print(f"  列名: {list(df_sample.columns)}")
                print(f"\n  数据预览:")
                print(df_sample.to_string(index=False))
        else:
            print("  ⚠️  S3未找到该站点/年份数据")

    except ImportError as e:
        print(f"  ⚠️  boto3未安装，无法使用S3下载: {e}")
        print("     安装: pip install boto3")
    except Exception as e:
        print(f"  ❌ S3下载失败: {e}")


def demo_pipeline_full():
    """示例4: 完整 Pipeline（下载多个城市数据）"""
    print("\n" + "=" * 60)
    print("示例4: 完整 Pipeline（下载多个城市数据）")
    print("=" * 60)

    # 城市配置
    # cities = [("London", "GB")]  # (城市名, 国家代码)
    cities = [("Beijing", "CN")]  # (城市名, 国家代码)
    start_year, end_year = 2022, 2025

    print(f"\n目标城市: {[c[0] for c in cities]}")
    print(f"年份范围: {start_year}-{end_year}")

    # 1. 下载 NOAA 气象数据
    print("\n[1/2] 下载 NOAA 气象数据...")
    noaa_results = process_noaa_cities(
        cities=cities,
        config={
            "start_year": start_year,
            "end_year": end_year,
            "search_radius_km": 50,
            "max_stations": 20,
        },
    )
    print(f"  ✅ NOAA 结果: {noaa_results}")

    # 2. 下载 OpenAQ 空气质量数据
    print("\n[2/2] 下载 OpenAQ 空气质量数据...")
    print("  使用 S3 历史数据（无需API Key）")
    openaq_results = process_openaq_cities(
        cities=cities,
        config={
            "start_year": start_year,
            "end_year": end_year,
            "use_s3": True,
            "max_workers": 10,
            "search_radius_m": 25000,
            "max_stations": 20
        },
    )
    print(f"  ✅ OpenAQ 结果: {openaq_results}")

    print("\n" + "=" * 60)
    print("下载完成！数据保存在:")
    print("  - NOAA: data/cache/noaa/")
    print("  - OpenAQ: data/cache/openaq/")
    print("\n下一步: 运行 02_data_merge.py 合并数据")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("Demo: 数据下载 (NOAA + OpenAQ)")
    print("=" * 60)

    # 取消注释以下函数来运行对应示例:

    # demo_noaa_download()     # 示例1: NOAA 气象数据下载
    # demo_openaq_api()        # 示例2: OpenAQ API 下载（需要 API Key）
    # demo_openaq_s3()         # 示例3: OpenAQ S3 下载（推荐，无需认证）
    demo_pipeline_full()       # 示例4: 完整 Pipeline（下载多个城市）
