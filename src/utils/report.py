"""
报告生成工具
"""

import json
import os.path as osp
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd


class NumpyEncoder(json.JSONEncoder):
    """自定义JSON编码器，支持numpy类型"""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
            return str(obj)
        elif isinstance(obj, (np.bool_,)):
            return bool(obj)
        return super().default(obj)


class ReportGenerator:
    """报告生成器"""

    def __init__(self, module_name: str = "data_processing"):
        """
        初始化报告生成器

        Args:
            module_name: 模块名称
        """
        self.module_name = module_name
        self.report_data = {
            "report_info": {
                "module": module_name,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "data_sources": [],
            "fields": {},
            "processing_steps": [],
            "summary": {},
        }
        self._step_index = 0

    def add_data_source(self, source_info: Dict[str, Any]) -> "ReportGenerator":
        """添加数据源信息"""
        self.report_data["data_sources"].append(source_info)
        return self

    def add_field_info(self, field_name: str, field_info: Dict[str, Any]) -> "ReportGenerator":
        """添加字段信息"""
        self.report_data["fields"][field_name] = field_info
        return self

    def add_processing_step(
        self, step_name: str, description: str, details: Optional[Dict[str, Any]] = None
    ) -> "ReportGenerator":
        """添加处理步骤"""
        self._step_index += 1
        step = {
            "step_number": self._step_index,
            "name": step_name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.report_data["processing_steps"].append(step)
        return self

    def add_summary(self, summary: Dict[str, Any]) -> "ReportGenerator":
        """添加汇总信息"""
        self.report_data["summary"].update(summary)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return self.report_data

    def to_json(self, indent: int = 2) -> str:
        """导出为JSON字符串"""
        return json.dumps(self.report_data, cls=NumpyEncoder, indent=indent, ensure_ascii=False)

    def save_json(self, output_path: str) -> str:
        """
        保存为JSON文件

        Args:
            output_path: 输出路径

        Returns:
            保存的文件路径
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        return output_path

    def to_markdown(self) -> str:
        """生成Markdown报告"""
        lines = [f"# {self.module_name} 处理报告\n"]

        # 报告信息
        info = self.report_data["report_info"]
        lines.extend(
            [
                "## 报告信息\n",
                f"- **模块**: {info['module']}",
                f"- **生成时间**: {info['created_at']}\n",
            ]
        )

        # 数据源
        if self.report_data["data_sources"]:
            lines.extend(["## 数据源\n"])
            for i, source in enumerate(self.report_data["data_sources"], 1):
                lines.append(f"### 数据源 {i}: {source.get('name', 'Unknown')}")
                for key, value in source.items():
                    if key != "name":
                        lines.append(f"- **{key}**: {value}")
                lines.append("")

        # 处理步骤
        if self.report_data["processing_steps"]:
            lines.extend(["## 处理步骤\n"])
            for step in self.report_data["processing_steps"]:
                lines.append(f"### 步骤 {step['step_number']}: {step['name']}")
                lines.append(f"- **描述**: {step['description']}")
                if step.get("details"):
                    for key, value in step["details"].items():
                        lines.append(f"- **{key}**: {value}")
                lines.append("")

        # 汇总
        if self.report_data["summary"]:
            lines.extend(["## 汇总统计\n"])
            for key, value in self.report_data["summary"].items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        return "\n".join(lines)

    def save_markdown(self, output_path: str) -> str:
        """
        保存为Markdown文件

        Args:
            output_path: 输出路径

        Returns:
            保存的文件路径
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.to_markdown())
        return output_path


def save_experiment_report(
    experiment_results: List[Dict[str, Any]], output_dir: str, experiment_id: str
) -> Dict[str, str]:
    """
    保存实验报告

    Args:
        experiment_results: 实验结果列表
        output_dir: 输出目录
        experiment_id: 实验ID

    Returns:
        保存的文件路径字典
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = {
        "experiment_id": experiment_id,
        "created_at": datetime.now().isoformat(),
        "results": experiment_results,
    }

    # 保存JSON
    json_path = output_path / "report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, cls=NumpyEncoder, indent=2, ensure_ascii=False)

    # 生成Markdown
    md_lines = [
        f"# 实验报告: {experiment_id}\n",
        f"**生成时间**: {report['created_at']}\n",
        "## 实验结果\n",
    ]

    for result in experiment_results:
        md_lines.append(f"### {result.get('mode', 'Unknown')} - {result.get('algorithm', 'Unknown')}")
        md_lines.append(f"- **验证RMSE**: {result.get('val_metrics', {}).get('rmse', 'N/A')}")
        md_lines.append(f"- **测试RMSE**: {result.get('metrics', {}).get('rmse', 'N/A')}")
        md_lines.append(f"- **R²**: {result.get('metrics', {}).get('r2', 'N/A')}")
        md_lines.append("")

    md_path = output_path / "report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return {
        "json": str(json_path),
        "markdown": str(md_path),
    }
