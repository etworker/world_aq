"""
NOAA 处理后数据保存模块

按年份保存气象数据，生成报告
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from ...config import NOAA_PROCESSED_DIR

from loguru import logger


class NOAADataSaver:
    """NOAA 处理后数据保存器"""

    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化保存器

        Args:
            base_dir: 处理后数据的基础存储目录
        """
        self.base_dir = Path(base_dir) if base_dir else Path(NOAA_PROCESSED_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _format_numeric_columns(self, df: pd.DataFrame, decimal_places: int = 2) -> pd.DataFrame:
        """格式化数值列为指定小数位数"""
        df = df.copy()

        exclude_cols = ["date", "city_name", "data_source"]
        exclude_cols.extend([c for c in df.columns if c.endswith("_source_count")])
        exclude_cols.extend([c for c in df.columns if c.endswith("_is_outlier")])
        exclude_cols.extend([c for c in df.columns if c.endswith("_interpolated")])

        numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude_cols]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].round(decimal_places)

        return df

    def save(
        self,
        df: pd.DataFrame,
        city_name: str,
        stations_count: int = 1,
        format: str = "csv",
    ) -> List[str]:
        """
        保存清理后的数据

        Args:
            df: 清理后的 DataFrame
            city_name: 城市名称
            stations_count: 使用的站点数量
            format: 文件格式

        Returns:
            保存的文件路径列表
        """
        safe_city_name = city_name.replace(" ", "_").replace("/", "_")
        city_dir = self.base_dir / safe_city_name
        city_dir.mkdir(parents=True, exist_ok=True)

        if df.empty:
            logger.warning(f"数据为空，跳过保存: {city_name}")
            return []

        # 确保 date 列是 datetime 类型
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        # 格式化数值列
        df_formatted = self._format_numeric_columns(df, decimal_places=2)

        # 按年保存数据
        saved_files = []
        years = sorted(df["date"].dt.year.unique())

        for year in years:
            year_df = df_formatted[df_formatted["date"].dt.year == year]

            if format == "parquet":
                file_path = city_dir / f"{year}.parquet"
                year_df.to_parquet(file_path, index=False)
            else:
                file_path = city_dir / f"{year}.csv"
                year_df.to_csv(file_path, index=False)

            saved_files.append(str(file_path))
            logger.info(f"保存 {city_name} {year}年数据: {file_path.name} ({len(year_df)}条)")

        # 保存完整数据
        full_file = city_dir / f"all_years.{format}"
        if format == "parquet":
            df_formatted.to_parquet(full_file, index=False)
        else:
            df_formatted.to_csv(full_file, index=False)
        saved_files.append(str(full_file))

        return saved_files

    def generate_report(
        self,
        df: pd.DataFrame,
        city_name: str,
        stations_count: int,
    ) -> str:
        """
        生成数据报告

        Args:
            df: 数据框
            city_name: 城市名称
            stations_count: 站点数量

        Returns:
            报告文件路径
        """
        safe_city_name = city_name.replace(" ", "_").replace("/", "_")
        city_dir = self.base_dir / safe_city_name
        city_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d")
        report_path = city_dir / f"report_{timestamp}.md"

        total_records = len(df)
        date_range = "unknown"
        if "date" in df.columns and not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            start_date = df["date"].min().strftime("%Y-%m-%d")
            end_date = df["date"].max().strftime("%Y-%m-%d")
            date_range = f"{start_date} 至 {end_date}"

        lines = [
            f"# NOAA 气象数据报告 - {city_name}",
            "",
            "## 基本信息",
            f"- 城市: {city_name}",
            f"- 站点数: {stations_count}",
            f"- 记录数: {total_records}",
            f"- 日期范围: {date_range}",
            "",
            "## 字段统计",
            "",
            "| 字段 | 非空数量 | 覆盖率 | 均值 | 最小值 | 最大值 |",
            "|------|----------|--------|------|--------|--------|",
        ]

        core_columns = [
            "temp_avg_c",
            "temp_max_c",
            "temp_min_c",
            "dewpoint_c",
            "precip_mm",
            "wind_speed_kmh",
            "visibility_km",
            "station_pressure_hpa",
        ]

        for col in core_columns:
            if col in df.columns:
                non_null = df[col].notna().sum()
                coverage = non_null / total_records * 100 if total_records > 0 else 0
                mean_val = df[col].mean()
                min_val = df[col].min()
                max_val = df[col].max()

                mean_str = f"{mean_val:.2f}" if pd.notna(mean_val) else "N/A"
                min_str = f"{min_val:.2f}" if pd.notna(min_val) else "N/A"
                max_str = f"{max_val:.2f}" if pd.notna(max_val) else "N/A"

                lines.append(f"| {col} | {non_null} | {coverage:.1f}% | {mean_str} | {min_str} | {max_str} |")

        lines.extend(
            [
                "",
                f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ]
        )

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"生成报告: {report_path}")
        return str(report_path)
