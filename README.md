# World Air Quality Prediction

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

全球空气质量预测系统 - 基于 NOAA 气象数据和 OpenAQ 空气质量数据，使用机器学习预测 AQI（空气质量指数）和 PM2.5 浓度。

Global Air Quality Prediction System - Predicting AQI and PM2.5 concentrations using machine learning based on NOAA weather data and OpenAQ air quality data.

---

## 项目简介 / Introduction

本项目构建了一个端到端的空气质量预测系统，集成数据处理、模型训练、实验探索和生产部署功能。系统支持多种预测模式和算法，并提供自动化机器学习（AutoML）能力。

This project builds an end-to-end air quality prediction system integrating data processing, model training, experiment exploration, and production deployment. The system supports multiple prediction modes and algorithms, with automated machine learning (AutoML) capabilities.

### 核心功能 / Core Features

- 🌍 **多城市支持** - 支持全球多个城市的空气质量预测
- 🔄 **多模式预测** - 8种预测模式（全局/城市级 × 当天/历史 × 单/多输出）
- 🤖 **AutoML** - 集成 AutoGluon 自动化模型选择和超参数优化
- 📊 **完整实验追踪** - 实验清单、最佳配置、可视化报告
- 🚀 **生产就绪** - RESTful API、模型版本管理、日志系统
- 🎨 **可视化** - 丰富的图表和报告生成

- 🌍 **Multi-city Support** - Air quality prediction for multiple cities worldwide
- 🔄 **Multi-mode Prediction** - 8 prediction modes (Global/City × Today/Historical × Single/Multi-output)
- 🤖 **AutoML** - Integrated AutoGluon for automated model selection and hyperparameter optimization
- 📊 **Complete Experiment Tracking** - Experiment manifest, best configs, visualization reports
- 🚀 **Production Ready** - RESTful API, model versioning, logging system
- 🎨 **Visualization** - Rich charts and report generation

---

## 快速开始 / Quick Start

### 安装依赖 / Installation

```bash
# 克隆仓库
git clone https://github.com/yourusername/world_aq.git
cd world_aq

# 安装依赖
pip install -r requirements.txt
```

### 运行实验 / Run Experiments

```bash
# 简单实验（推荐用于快速验证）
python -m src.cli experiment --modes GTS --algorithms RandomForest

# 标准实验
python -m src.cli experiment --modes GTS,GHS --algorithms Ridge,RandomForest,GradientBoosting

# 全量实验（包含 AutoGluon）
python -m src.cli autogluon --modes GTS,GHS --time-limit 300
```

### 训练生产模型 / Train Production Model

```bash
# 使用实验结果中的最佳配置训练生产模型
python -m src.cli train --config models/experiments/EXP_xxx/best_config.json --mode GTS
```

### 模型推理 / Model Inference

```bash
# 列出可用模型
python -m src.cli inference --list

# 预测
python -m src.cli inference --model models/production/GTS_20260206_xxx \
  --city "Beijing" \
  --temperature 25.0 \
  --wind-speed 15.0 \
  --visibility 8.0 \
  --pressure 1013.0 \
  --date "2026-02-06"
```

### 启动 API 服务 / Start API Service

```bash
python -m src.cli api --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

Visit http://localhost:8000/docs for API documentation.

---

## 项目结构 / Project Structure

```
world_aq/
├── data/                     # 数据目录
│   ├── cache/                # 原始数据缓存
│   │   ├── noaa/             # NOAA GSOD 数据
│   │   └── openaq/           # OpenAQ 数据
│   ├── processed/            # 处理后数据
│   │   ├── noaa/             # 气象数据
│   │   ├── openaq/           # 空气质量数据
│   │   └── merged/           # 合并后的训练数据
│   └── info/                 # 元数据
├── doc/                      # 文档
│   ├── aws_arch.md           # AWS 架构设计
│   ├── aqi.md                # AQI 技术文档
│   ├── data.md               # 数据说明
│   └── features.md           # 特征工程说明
├── models/                   # 模型目录
│   ├── experiments/          # 实验模型
│   │   └── EXP_xxx/
│   │       ├── manifest.json
│   │       ├── best_config.json
│   │       └── report.md
│   └── production/           # 生产模型
├── src/                      # 源代码
│   ├── api/                  # RESTful API
│   ├── aqi/                  # AQI 计算
│   ├── cli.py                # 命令行接口
│   ├── config/               # 配置管理
│   ├── core/                 # 核心模块
│   ├── data/                 # 数据处理
│   │   ├── acquisition/      # 数据获取
│   │   ├── processing/       # 数据处理
│   │   ├── storage/          # 数据存储
│   │   └── pipeline/         # 数据流水线
│   ├── inference/            # 模型推理
│   ├── training/             # 模型训练
│   │   ├── core/             # 训练核心
│   │   ├── experiment/       # 实验管理
│   │   └── production/       # 生产训练
│   └── utils/                # 工具函数
├── demo/                     # 示例脚本
│   ├── 03_experiment.py      # 实验示例
│   └── 04_train_production.py # 生产训练示例
├── logs/                      # 日志文件
├── notebooks/                 # Jupyter Notebooks
├── requirements.txt           # Python 依赖
└── README.md                  # 本文件
```

---

## 数据源 / Data Sources

### NOAA GSOD
- **描述**: 全球地表每日气象数据
- **来源**: [NOAA GSOD](https://www.ncdc.noaa.gov/gsod/)
- **内容**: 温度、风速、能见度、气压等

### OpenAQ
- **描述**: 全球空气质量监测数据
- **来源**: [OpenAQ](https://openaq.org/)
- **内容**: PM2.5、PM10、O3、NO2、SO2、CO

---

## 预测模式 / Prediction Modes

系统支持 8 种预测模式：

| 模式 | 描述 | 适用场景 |
|------|------|----------|
| **GTM** | 全局_当天_多输出 | 跨城市、多污染物联合预测 |
| **GTS** | 全局_当天_独立模型 | 跨城市、各污染物独立预测 |
| **GHM** | 全局_历史_多输出 | 历史数据增强的多污染物预测 |
| **GHS** | 全局_历史_独立模型 | 历史数据增强的独立预测 |
| **CTM** | 城市级_当天_多输出 | 单城市多污染物预测 |
| **CTS** | 城市级_当天_独立模型 | 单城市各污染物独立预测 |
| **CHM** | 城市级_历史_多输出 | 单城市历史增强预测 |
| **CHS** | 城市级_历史_独立模型 | 单城市历史增强独立预测 |

---

## 训练流程 / Training Pipeline

### 1. 实验阶段 / Experiment Phase

```bash
python demo/03_experiment.py
```

**输出 / Output**:
- `models/experiments/EXP_xxx/manifest.json` - 实验清单
- `models/experiments/EXP_xxx/best_config.json` - 最佳配置
- `models/experiments/EXP_xxx/report.md` - 实验报告
- `models/experiments/EXP_xxx/figures/` - 可视化图表

### 2. 生产训练 / Production Training

```bash
python demo/04_train_production.py
```

**使用最佳配置重新训练，保存到**:
- `models/production/GTS_20260206_xxx/` - 生产模型

---

## 支持的算法 / Supported Algorithms

- **传统机器学习**:
  - Ridge
  - Lasso
  - ElasticNet
  - RandomForest
  - GradientBoosting
  - SVR

- **AutoML**:
  - AutoGluon

---

## API 接口 / API Endpoints

### 预测接口 / Predict Endpoint

```http
POST /predict
Content-Type: application/json

{
  "city": "Beijing",
  "date": "2024-02-05",
  "weather": {
    "temp_avg_c": 25.0,
    "wind_speed_kmh": 15.0,
    "visibility_km": 8.0,
    "station_pressure_hpa": 1013.0
  }
}
```

**响应 / Response**:
```json
{
  "city": "Beijing",
  "pm25": 35.2,
  "aqi": 89,
  "category": "Good",
  "category_chinese": "良",
  "health_advice": "空气质量可接受，适合户外活动。"
}
```

### AQI 计算接口 / AQI Calculator

```http
GET /aqi/calculate?pollutant=pm25&concentration=35.2
```

**响应 / Response**:
```json
{
  "aqi": 89,
  "category": "Good",
  "chinese": "良",
  "color": "#FFFF00"
}
```

---

## 日志系统 / Logging

所有日志统一写入 `logs/world_aq.log`。

- **屏幕输出**: 彩色格式（开发调试）
- **文件日志**: 压缩轮转（生产环境）

---

## 文档 / Documentation

- [AQI 技术文档](doc/aqi.md) - EPA AQI 计算标准
- [数据说明](doc/data.md) - NOAA 和 OpenAQ 数据集
- [特征工程](doc/features.md) - 特征配置说明
- [模型流程](doc/model_flow.md) - 训练和推理流程
- [AWS 架构](doc/aws_arch.md) - 云端部署架构设计

---

## 技术栈 / Tech Stack

| 类别 | 技术 |
|------|------|
| **语言** | Python 3.10 |
| **数据处理** | Pandas, NumPy |
| **机器学习** | scikit-learn, AutoGluon |
| **可视化** | Matplotlib, Seaborn |
| **API 框架** | FastAPI, Uvicorn |
| **日志** | loguru |
| **数据获取** | OpenAQ Python SDK |

---

## 许可证 / License

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 联系方式 / Contact

如有问题或建议，欢迎通过以下方式联系：

- 提交 [Issue](https://github.com/yourusername/world_aq/issues)
- 发送邮件至: etworker@outlook.com

For questions or suggestions, feel free to:

- Submit an [Issue](https://github.com/yourusername/world_aq/issues)
- Send an email to: your.email@example.com

---

## 致谢 / Acknowledgments

- [NOAA](https://www.noaa.gov/) - 提供全球气象数据
- [OpenAQ](https://openaq.org/) - 提供空气质量数据
- [EPA](https://www.epa.gov/) - AQI 计算标准
- [AutoGluon](https://auto.gluon.ai/) - 自动化机器学习框架

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！⭐**

**⭐ If this project helps you, please give it a Star! ⭐**