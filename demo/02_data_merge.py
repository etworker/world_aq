#!/usr/bin/env python
"""
Demo: 数据合并

将 NOAA 气象数据和 OpenAQ 空气质量数据合并
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.processing.merger import DataMerger
from src.data.pipeline.noaa_pipeline import process_noaa_cities
from src.data.pipeline.openaq_pipeline import process_openaq_cities
from src.config.settings import PROCESSED_DIR


def demo_merge_single_year():
    """示例1: 合并单个城市单年数据"""
    print("\n" + "=" * 60)
    print("示例1: 合并单个城市单年数据")
    print("=" * 60)

    merger = DataMerger()

    # 合并北京2022年数据
    city_name = "Beijing"
    year = 2022

    print(f"\n合并 {city_name} {year}年数据...")
    merged_df = merger.merge_city_year(
        city_name=city_name,
        year=year,
        save=True  # 保存到 data/processed/merged/Beijing/2022.csv
    )

    if merged_df is not None:
        print(f"  ✅ 合并成功: {len(merged_df)} 条记录")
        print(f"     数据范围: {merged_df['date'].min()} ~ {merged_df['date'].max()}")
        print(f"     列数: {len(merged_df.columns)}")
        print("\n  数据预览:")
        print(merged_df.head(3).to_string())
    else:
        print(f"  ⚠️ 合并失败，请检查数据文件是否存在")
        print(f"     期望文件: {PROCESSED_DIR}/noaa/{city_name}/{year}.csv")
        print(f"     期望文件: {PROCESSED_DIR}/openaq/{city_name}/{year}.csv")


def demo_merge_all_years():
    """示例2: 合并单个城市多年数据"""
    print("\n" + "=" * 60)
    print("示例2: 合并单个城市多年数据")
    print("=" * 60)

    merger = DataMerger()

    city_name = "Beijing"
    years = [2022, 2023, 2024, 2025]

    print(f"\n合并 {city_name} {years}年数据...")
    merged_df = merger.merge_city_all_years(
        city_name=city_name,
        years=years,
        save=True
    )

    if merged_df is not None:
        print(f"  ✅ 合并成功: {len(merged_df)} 条记录")
        print(f"     数据范围: {merged_df['date'].min()} ~ {merged_df['date'].max()}")
        print(f"     总列数: {len(merged_df.columns)}")
    else:
        print(f"  ⚠️ 合并失败，请检查数据是否存在")


def demo_merge_auto_discover():
    """示例3: 自动发现并合并所有年份"""
    print("\n" + "=" * 60)
    print("示例3: 自动发现并合并所有年份")
    print("=" * 60)

    merger = DataMerger()

    city_name = "Beijing"

    print(f"\n自动发现 {city_name} 的所有年份数据...")
    merged_df = merger.merge_city_all_years(
        city_name=city_name,
        years=None,  # None = 自动发现所有年份
        save=True
    )

    if merged_df is not None:
        print(f"  ✅ 合并成功: {len(merged_df)} 条记录")
        print(f"     数据范围: {merged_df['date'].min()} ~ {merged_df['date'].max()}")
    else:
        print(f"  ⚠️ 未找到 {city_name} 的数据")


def demo_pipeline_download_and_merge():
    """示例4: 完整流程（下载 + 合并）"""
    print("\n" + "=" * 60)
    print("示例4: 完整流程（下载 + 合并）")
    print("=" * 60)

    # 城市配置
    cities = [("Beijing", "CN")]
    start_year, end_year = 2022, 2023

    print(f"\n目标城市: {[c[0] for c in cities]}")
    print(f"年份范围: {start_year}-{end_year}")

    # 1. 下载 NOAA 气象数据
    print("\n[1/3] 下载 NOAA 气象数据...")
    noaa_results = process_noaa_cities(
        cities=cities,
        config={
            "start_year": start_year,
            "end_year": end_year,
            "search_radius_km": 50,
            "max_stations": 5,
        },
    )
    print(f"  ✅ NOAA 完成: {noaa_results}")

    # 2. 下载 OpenAQ 空气质量数据
    print("\n[2/3] 下载 OpenAQ 空气质量数据...")
    openaq_results = process_openaq_cities(
        cities=cities,
        config={
            "start_year": start_year,
            "end_year": end_year,
            "use_s3": True,
            "max_workers": 10,
            "pollutants": ["pm25"],
        },
    )
    print(f"  ✅ OpenAQ 完成: {openaq_results}")

    # 3. 合并数据
    print("\n[3/3] 合并数据...")
    merger = DataMerger()

    for city_name, _ in cities:
        print(f"\n  合并 {city_name}...")

        merged_df = merger.merge_city_all_years(
            city_name=city_name,
            years=list(range(start_year, end_year + 1)),
            save=True
        )

        if merged_df is not None:
            print(f"    ✅ 成功: {len(merged_df)} 条记录")
            print(f"       保存路径: {PROCESSED_DIR}/merged/{city_name}/")
        else:
            print(f"    ⚠️ 失败")

    print("\n" + "=" * 60)
    print("全部完成！合并后的数据可用于模型训练")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("Demo: 数据合并流程")
    print("=" * 60)

    # 取消注释以下函数来运行对应示例:

    # demo_merge_single_year()         # 示例1: 合并单年数据
    demo_merge_all_years()           # 示例2: 合并多年数据
    # demo_merge_auto_discover()       # 示例3: 自动发现年份
    # demo_pipeline_download_and_merge()  # 示例4: 完整流程（下载+合并）
