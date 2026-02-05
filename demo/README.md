# World Air Quality - Demo 目录

本目录包含 CLI 各功能的演示和验证脚本，按数据流转顺序排列。

## 快速开始

```bash
# 查看所有 demo
ls demo/

# 运行任意 demo
python demo/01_data_download_noaa.py
python demo/09_aqi_calculator.py
```

## Demo 列表（按数据流转顺序）

| 编号 | 文件 | 功能 | 说明 |
|------|------|------|------|
| 01 | `01_data_download.py` | 数据下载 | 下载 NOAA 气象 + OpenAQ 空气质量数据 |
| 02 | `02_data_merge.py` | 数据合并 | 合并气象和空气质量数据 |
| 03 | `03_experiment_basic.py` | 基础实验 | 运行简单实验，快速验证 |
| 04 | `04_experiment_full.py` | 完整实验 | 运行所有模式和算法 |
| 05 | `05_experiment_autogluon.py` | AutoML | 使用 AutoGluon 自动搜索最佳模型 |
| 06 | `06_train_production.py` | 生产训练 | 训练生产环境模型 |
| 07 | `07_inference_basic.py` | 模型推理 | 使用模型进行预测 |
| 08 | `08_data_validation.py` | 数据校验 | 验证数据质量和完整性 |
| 09 | `09_aqi_calculator.py` | AQI 计算 | 计算空气质量指数 |
| 10 | `10_api_server.py` | API 服务 | 启动 REST API 服务 |

## 数据流转流程

```
┌─────────────────┐
│ 01 数据下载      │  ← NOAA气象数据 + OpenAQ空气质量数据
└────────┬────────┘
         ▼
┌─────────────────┐
│ 02 数据合并      │  ← 按城市、日期对齐合并
└────────┬────────┘
         ▼
┌─────────────────┐
│ 03/04/05 实验   │  ← 探索最佳模型配置
└────────┬────────┘
         ▼
┌─────────────────┐
│ 06 生产训练      │  ← 使用最佳配置训练生产模型
└────────┬────────┘
         ▼
┌─────────────────┐
│ 07 模型推理      │  ← 使用模型预测空气质量
└────────┬────────┘
         ▼
┌─────────────────┐
│ 08 数据校验      │  ← 验证预测结果质量
└────────┬────────┘
         ▼
┌─────────────────┐
│ 09 AQI计算      │  ← 计算AQI和健康建议
└────────┬────────┘
         ▼
┌─────────────────┐
│ 10 API服务      │  ← 部署REST API服务
└─────────────────┘
```

## CLI 对应关系

| CLI 命令 | Demo 文件 |
|----------|-----------|
| `python -m src.cli fetch-noaa` | `01_data_download.py` |
| `python -m src.cli merge` | `02_data_merge.py` |
| `python -m src.cli experiment` | `03_experiment_basic.py`, `04_experiment_full.py` |
| `python -m src.cli autogluon` | `05_experiment_autogluon.py` |
| `python -m src.cli train` | `06_train_production.py` |
| `python -m src.cli inference` | `07_inference_basic.py` |
| `python -m src.cli validate` | `08_data_validation.py` |
| `python -m src.cli aqi` | `09_aqi_calculator.py` |
| `python -m src.cli api` | `10_api_server.py` |

## 运行顺序建议

### 第一次使用（完整流程）
1. `01_data_download_noaa.py` - 获取原始数据
2. `02_data_merge.py` - 数据预处理
3. `03_experiment_basic.py` - 快速实验验证
4. `06_train_production.py` - 训练生产模型
5. `07_inference_basic.py` - 测试推理

### 模型调优
1. `05_experiment_autogluon.py` - AutoML寻找最佳模型
2. `04_experiment_full.py` - 全量实验对比
3. `06_train_production.py` - 重新训练

### 部署上线
1. `08_data_validation.py` - 数据质量检查
2. `09_aqi_calculator.py` - AQI功能测试
3. `10_api_server.py` - 启动API服务

## 注意事项

- 部分 demo 需要预处理数据存在 (`data/processed/merged/all_cities.csv`)
- AutoGluon demo 需要安装 `pip install autogluon`
- **OpenAQ 下载支持两种方式**:
  1. **API 方式** (近期数据): 需要 API Key，且可能需要付费订阅
     ```bash
     export OPENAQ_API_KEY='your_api_key_here'
     # 获取地址: https://docs.openaq.org/docs/getting-started
     # 注意: 免费账户可能只能访问最近部分数据
     ```
  2. **S3 方式** (历史归档): ✅ **推荐使用**，无需认证
     - 存储桶: `openaq-data-archive`
     - 路径: `records/csv.gz/locationid={id}/year={year}/month={mm}/`
     - 数据格式: gzip 压缩 CSV，每小时一条记录
- 生产训练 demo 需要先有实验生成的最佳配置文件
- API 服务 demo 需要训练好的模型文件
