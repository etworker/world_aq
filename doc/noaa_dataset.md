# noaa数据集

NOAA Global Surface Summary of the Day (GSOD)

## 索引文件 (isd-history.csv) 

全球气象站元数据索引。它记录了所有进入 NOAA 数据库的气象站的基础信息（位置、名称、ID）以及其数据的时间跨度。

在：https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv

前几行及北京站点：

```
"USAF","WBAN","STATION NAME","CTRY","STATE","ICAO","LAT","LON","ELEV(M)","BEGIN","END"
"007018","99999","WXPOD 7018","","","","+00.000","+000.000","+7018.0","20110309","20130730"
"007026","99999","WXPOD 7026","AF","","","+00.000","+000.000","+7026.0","20120713","20170822"
...
"008307","99999","WXPOD 8318","AF","","","+00.000","+000.000","+8318.0","20100421","20100421"
"008411","99999","XM20","","","","","","","20160217","20160217"
...
"545110","99999","BEIJING - CAPITAL INTERNATIONAL AIRPORT","CH","","ZBAA","+40.080","+116.585","+0035.4","19451031","20250824"
...
```

### 字段含义

| 字段名   | 全称                 | 详细说明                                                     |
| -------- | -------------------- | ------------------------------------------------------------ |
| **USAF** | Air Force Station ID | **第一 ID** (6位数字)。<br>这是数据文件名的第一部分。<br>⚠️ **注意**: 如果该站只有 WBAN 编号，这里通常填 999999。 |
| **WBAN** | WBAN Station ID      | **第二 ID** (5位数字)。<br>这是数据文件名的第二部分。<br>⚠️ **注意**: 绝大多数非美国站点没有此编号，会填 99999。 |
| **STATION NAME** | 站点名称  | 通常是英文的机场名、城市名或基地名。<br>📝 **提示**: 您提供的样本中 "WXPOD 7018" 表示这是一个便携式气象单元 (Weather Pod)，而非固定机场。 |
| **CTRY**         | 国家代码  | **⚠️ 高危坑点**: 这里使用的是 **FIPS 10-4** 代码，**不是 ISO 代码**。<br>• 中国 = CH (ISO 是 CN)<br>• 德国 = GM (ISO 是 DE)<br>• 样本中的 "AF" = 阿富汗。 |
| **STATE**        | 州/省代码 | 主要用于美国 (CA, TX) 和加拿大。国际站点通常为空。           |
| **ICAO**         | 民航代码  | 4位字母代码 (如 ZBAA, KJFK)。<br>这是查找主要机场最准确的方法。如果为空，说明该站点不是民用机场（可能是军事基地或小型观测点）。 |
| **LAT**     | 纬度 | 格式：+DD.ddd。<br>+ = 北纬 (North), - = 南纬 (South)。 |
| **LON**     | 经度 | 格式：+DDD.ddd。<br>+ = 东经 (East), - = 西经 (West)。  |
| **ELEV(M)** | 海拔 | 单位：**米**。                                          |
| **BEGIN** | 起始日期 | 该站点第一次上传数据的日期。                                 |
| **END**   | 结束日期 | 该站点最后一次上传数据的日期。<br>✅ **查找最新数据**: 必须筛选 END 日期接近当前的站点（如 2026xxxx）。<br>❌ **样本分析**: 样本中的 20130730 和 20170822 意味着这俩站点**早已废弃**，你找不到它们 2025 年的数据。 |

## 历史数据

### 数据集描述

https://registry.opendata.aws/noaa-gsod/

```
Global Surface Summary of the Day is derived from The Integrated Surface Hourly (ISH) dataset. 
The ISH dataset includes global data obtained from the USAF Climatology Center, located in the Federal Climate Complex with NCDC. 
The latest daily summary data are normally available 1-2 days after the date-time of the observations used in the daily summaries. 
The online data files begin with 1929 and are at the time of this writing at the Version 8 software level. 
Over 9000 stations' data are typically available. 
The daily elements included in the dataset (as available from each station) are:

Mean temperature (.1 Fahrenheit)
Mean dew point (.1 Fahrenheit)
Mean sea level pressure (.1 mb)
Mean station pressure (.1 mb)
Mean visibility (.1 miles)
Mean wind speed (.1 knots)
Maximum sustained wind speed (.1 knots)
Maximum wind gust (.1 knots)
Maximum temperature (.1 Fahrenheit)
Minimum temperature (.1 Fahrenheit)
Precipitation amount (.01 inches)
Snow depth (.1 inches)
Indicator for occurrence of: Fog, Rain or Drizzle, Snow or Ice Pellets, Hail, Thunder, Tornado/Funnel Cloud.

Global summary of day data for 18 surface meteorological elements are derived from the synoptic/hourly observations contained in USAF DATSAV3 Surface data and Federal Climate Complex Integrated Surface Hourly (ISH). 
Historical data are generally available for 1929 to the present, with data from 1973 to the present being the most complete. 
For some periods, one or more countries' data may not be available due to data restrictions or communications problems. 
In deriving the summary of day data, a minimum of 4 observations for the day must be present (allows for stations which report 4 synoptic observations/day). 
Since the data are converted to constant units (e.g, knots), slight rounding error from the originally reported values may occur (e.g, 9.9 instead of 10.0). 
The mean daily values described below are based on the hours of operation for the station. 
For some stations/countries, the visibility will sometimes 'cluster' around a value (such as 10 miles) due to the practice of not reporting visibilities greater than certain distances. 
The daily extremes and totals--maximum wind gust, precipitation amount, and snow depth--will only appear if the station reports the data sufficiently to provide a valid value. 
Therefore, these three elements will appear less frequently than other values. 
Also, these elements are derived from the stations' reports during the day, and may comprise a 24-hour period which includes a portion of the previous day. 
The data are reported and summarized based on Greenwich Mean Time (GMT, 0000Z - 2359Z) since the original synoptic/hourly data are reported and based on GMT.
```

### 浏览数据

可以使用aws cli浏览：

```shell
aws s3 ls --no-sign-request s3://noaa-gsod-pds/
```

也可以在web来看：

https://noaa-gsod-pds.s3.amazonaws.com/index.html

文件举例：

```
# 2025年A5125600451站点的数据汇总
s3://noaa-gsod-pds/2025/A5125600451.csv
```

### 下载数据

#### http下载

举例，下载2025年A5125600451站点的数据：

```shell
wget https://noaa-gsod-pds.s3.amazonaws.com/2025/A5125600451.csv
```

前几行：
```csv
"STATION","DATE","LATITUDE","LONGITUDE","ELEVATION","NAME","TEMP","TEMP_ATTRIBUTES","DEWP","DEWP_ATTRIBUTES","SLP","SLP_ATTRIBUTES","STP","STP_ATTRIBUTES","VISIB","VISIB_ATTRIBUTES","WDSP","WDSP_ATTRIBUTES","MXSPD","GUST","MAX","MAX_ATTRIBUTES","MIN","MIN_ATTRIBUTES","PRCP","PRCP_ATTRIBUTES","SNDP","FRSHTT"
"A5125600451","2025-01-01","36.6985","-93.4022","411.2","BRANSON WEST MUNICIPAL EMERSON FIELD AIRPORT, MO US","  34.8","20","  22.6","20","9999.9"," 0","976.8","20","  9.8","20","  6.3","20"," 12.0"," 18.1","  42.8","*","  30.2","*"," 0.00","I","999.9","000000"
"A5125600451","2025-01-02","36.6985","-93.4022","411.2","BRANSON WEST MUNICIPAL EMERSON FIELD AIRPORT, MO US","  37.1","24","  27.3","24","9999.9"," 0","975.8","24","  9.8","24","  1.3","24","  8.0"," 15.0","  48.2","*","  30.2","*"," 0.00","I","999.9","000000"
```

举例，下载2025年北京站点（54511099999）的数据：

```shell
wget https://noaa-gsod-pds.s3.amazonaws.com/2025/54511099999.csv
```

末几行：

```
"54511099999","2025-08-23","40.080111","116.584556","35.35","BEIJING CAPITAL INTERNATIONAL AIRPORT, CH","  72.5","24","  67.0","24","9999.9"," 0","999.9"," 0","  6.7","24","  7.9","24"," 15.5","999.9","  90.0"," ","  68.0","*"," 0.15","G","999.9","010000"
"54511099999","2025-08-24","40.080111","116.584556","35.35","BEIJING CAPITAL INTERNATIONAL AIRPORT, CH","  72.6","22","  67.1","22","9999.9"," 0","999.9"," 0","  6.1","22","  3.2","22","  5.8","999.9","  82.9"," ","  68.0","*"," 0.17","G","999.9","010000"
```

#### Amazon S3 (boto3) 下载

通过 Amazon S3 (boto3) 下载 CSV 文件：

```python
 # S3 桶: noaa-gsod-pds
 # 路径格式: s3://noaa-gsod-pds/{year}/{stationid}.csv
 s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
 for year in range(yearStart, yearEnd + 1):
     key = f'{year}/{stationID}.csv'
     csv_obj = s3.get_object(Bucket='noaa-gsod-pds', Key=key)
```

### 数据格式

以`s3://noaa-gsod-pds/2025/A5125600451.csv`为例，前3行内容为：

```
"STATION","DATE","LATITUDE","LONGITUDE","ELEVATION","NAME","TEMP","TEMP_ATTRIBUTES","DEWP","DEWP_ATTRIBUTES","SLP","SLP_ATTRIBUTES","STP","STP_ATTRIBUTES","VISIB","VISIB_ATTRIBUTES","WDSP","WDSP_ATTRIBUTES","MXSPD","GUST","MAX","MAX_ATTRIBUTES","MIN","MIN_ATTRIBUTES","PRCP","PRCP_ATTRIBUTES","SNDP","FRSHTT"
"A5125600451","2025-01-01","36.6985","-93.4022","411.2","BRANSON WEST MUNICIPAL EMERSON FIELD AIRPORT, MO US","  34.8","20","  22.6","20","9999.9"," 0","976.8","20","  9.8","20","  6.3","20"," 12.0"," 18.1","  42.8","*","  30.2","*"," 0.00","I","999.9","000000"
"A5125600451","2025-01-02","36.6985","-93.4022","411.2","BRANSON WEST MUNICIPAL EMERSON FIELD AIRPORT, MO US","  37.1","24","  27.3","24","9999.9"," 0","975.8","24","  9.8","24","  1.3","24","  8.0"," 15.0","  48.2","*","  30.2","*"," 0.00","I","999.9","000000"
```

### 表头含义

| CSV Header           | 含义（英文）                 | 中文名称/说明    | 单位/格式           | 示例值            | 备注                                                         |
| -------------------- | ---------------------------- | ---------------- | ------------------- | ----------------- | ------------------------------------------------------------ |
| **STATION**          | Station ID                   | 气象站ID         | 字符串              | `A5125600451`     | 全球唯一标识符，前缀字母表示数据来源（如 `A`=美国）          |
| **DATE**             | Observation Date             | 观测日期         | `YYYY-MM-DD`（GMT） | `2025-01-01`      | **所有时间基于 GMT/UTC**，非本地时区；跨时区分析需转换       |
| **LATITUDE**         | Latitude                     | 纬度             | 十进制度            | `36.6985`         | 北纬为正，南纬为负；部分老旧站点坐标精度较低（±0.1°）        |
| **LONGITUDE**        | Longitude                    | 经度             | 十进制度            | `-93.4022`        | 东经为正，西经为负；注意西经为负值（如美国站点多为负）       |
| **ELEVATION**        | Elevation                    | 海拔高度         | 米（m）             | `411.2`           | 部分站点缺失时可能为 `9999.9` 或 `0`，需验证合理性           |
| **NAME**             | Station Name                 | 气象站名称       | 字符串              | `BRANSON WEST...` | 包含地点、州/省、国家；名称可能随时间变更（历史数据需注意）  |
| **TEMP**             | Mean Temperature             | 日平均温度       | °F                  | `34.8`            | **直接使用（已含小数点）**；`9999.9` = 缺失；注意华氏度需转换为摄氏度（℃ = (°F−32)×5/9） |
| **TEMP_ATTRIBUTES**  | Temperature Attributes       | 温度数据质量     | 观测次数            | `20`              | 数值 = 当日有效观测次数（0–24）；<4 次时日均值可能不可靠     |
| **DEWP**             | Mean Dew Point               | 日平均露点温度   | °F                  | `22.6`            | **直接使用**；`9999.9` = 缺失；露点 > 温度 时数据异常（需过滤） |
| **DEWP_ATTRIBUTES**  | Dew Point Attributes         | 露点数据质量     | 观测次数            | `20`              | 同 `TEMP_ATTRIBUTES`，用于评估数据可靠性                     |
| **SLP**              | Mean Sea Level Pressure      | 日平均海平面气压 | mb (hPa)            | `1016.1`          | **直接使用**；`9999.9` = 缺失（山区站点常缺失）；mb = hPa      |
| **SLP_ATTRIBUTES**   | SLP Attributes               | 海平面气压质量   | 观测次数            | `0`               | 0 表示无有效观测，该日海平面气压不可用                       |
| **STP**              | Mean Station Pressure        | 日平均站气压     | mb (hPa)            | `976.8`           | **直接使用**；站气压（未修正海拔）比海平面气压更可靠           |
| **STP_ATTRIBUTES**   | Station Pressure Attributes  | 站气压数据质量   | 观测次数            | `20`              | 优先使用 STP（缺失率低于 SLP）                               |
| **VISIB**            | Mean Visibility              | 日平均能见度     | 英里                | `9.8`             | **直接使用**；部分国家报告上限为 10 英里（出现“堆积效应”）     |
| **VISIB_ATTRIBUTES** | Visibility Attributes        | 能见度数据质量   | 观测次数            | `20`              | 低能见度（<1 英里）可能指示雾/霾/降水                        |
| **WDSP**             | Mean Wind Speed              | 日平均风速       | 节 (knots)          | `6.3`             | **直接使用**；1 节 = 1.852 km/h；无风时可能为 `0.0` 或缺失     |
| **WDSP_ATTRIBUTES**  | Wind Speed Attributes        | 风速数据质量     | 观测次数            | `20`              | 风速为 0 时仍可能有有效观测（非缺失）                        |
| **MXSPD**            | Maximum Sustained Wind Speed | 最大持续风速     | 节 (knots)          | `12.0`            | **直接使用**；`999.9` = 缺失；注意与阵风（GUST）区分           |
| **GUST**             | Maximum Wind Gust            | 最大阵风风速     | 节 (knots)          | `18.1`            | **直接使用**；`999.9` = 无阵风报告或缺失；出现频率低于其他风速字段 |
| **MAX**              | Maximum Temperature          | 日最高温度       | °F                  | `42.8`            | **直接使用**；`9999.9` = 缺失；可能跨日（见 `MAX_ATTRIBUTES`） |
| **MAX_ATTRIBUTES**   | Max Temp Attributes          | 最高温度标记     | `*` 标记            | `*`               | `*` = 极值出现在前一日 23:00–24:00（GMT）；影响日极值归属    |
| **MIN**              | Minimum Temperature          | 日最低温度       | °F                  | `30.2`            | **直接使用**；`9999.9` = 缺失；可能跨日（见 `MIN_ATTRIBUTES`） |
| **MIN_ATTRIBUTES**   | Min Temp Attributes          | 最低温度标记     | `*` 标记            | `*`               | `*` = 极值出现在次日 00:00–01:00（GMT）；影响日极值归属      |
| **PRCP**             | Precipitation                | 降水量           | 英寸                | `0.15`            | **直接使用**；1 英寸 = 25.4 mm；`99.99` = 缺失；微量降水可能记为 `0.01` |
| **PRCP_ATTRIBUTES**  | Precipitation Attributes     | 降水数据标记     | 标记字符            | `I`               | `I` = Incomplete（数据不完整，如仅部分时段有观测）；`A` = Accumulated（累积值） |
| **SNDP**             | Snow Depth                   | 雪深             | 英寸                | `999.9`           | **直接使用**；`999.9` = 无雪或缺失；热带/亚热带站点常年缺失    |
| **FRSHTT**           | Weather Phenomena Flags      | 天气现象指示器   | 6位二进制字符串     | `000000`          | 6 位分别对应：`F`og, `R`ain/Drizzle, `S`now/Ice, `H`ail, `T`hunder, `T`ornado；`1`=发生，`0`=未发生；可拆分为 6 个布尔特征 |

###  全局数据处理建议

#### 1. **单位统一**：

- 温度：`°F → °C`：`df['TEMP_C'] = (df['TEMP'] - 32) * 5/9`
- 降水：`英寸 → mm`：`df['PRCP_MM'] = df['PRCP'] * 25.4`
- 风速：`节 → km/h`：`df['WDSP_KMH'] = df['WDSP'] * 1.852`

#### 2. **缺失值处理**：

```python
# 标准缺失值替换（GSOD 规范）
df.replace({
    'TEMP': 9999.9, 'DEWP': 9999.9, 'SLP': 9999.9, 'STP': 9999.9,
    'VISIB': 999.9, 'WDSP': 999.9, 'MXSPD': 999.9, 'GUST': 999.9,
    'MAX': 9999.9, 'MIN': 9999.9, 'PRCP': 99.99, 'SNDP': 999.9
}, np.nan, inplace=True)
```

#### 3. **数据质量过滤**：

- 保留 `TEMP_ATTRIBUTES >= 4` 的记录（确保日均值基于足够观测）
- 检查 `DEWP <= TEMP`（露点不应高于气温，否则为异常值）

#### 4. **时间对齐**：

- 分析本地时间需将 `DATE` (GMT) 转换为目标时区（如北京时间 = GMT+8）
- 注意跨日极值（`MAX_ATTRIBUTES='*'` / `MIN_ATTRIBUTES='*'`）可能影响日统计

> 💡 **最佳实践**：建议先进行单位转换 → 缺失值替换 → 数据质量过滤 → 时区转换，再进行分析或建模。历史数据（1929–1972）缺失率较高，建议优先使用 1973 年后数据。

### 模型关心的值

| 特征  | 含义            | 说明                 |
| ----- | --------------- | -------------------- |
| DEWP  | Dew Point       | 露点温度             |
| WDSP  | Wind Speed      | 平均风速             |
| MAX   | Temperature Max | 最高温度             |
| MIN   | Temperature Min | 最低温度             |
| PRCP  | Precipitation   | 降水量               |
| MONTH | Month           | 月份（特征工程添加） |