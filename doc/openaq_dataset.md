# openaq数据集

## 历史数据

- 参考 https://registry.opendata.aws/openaq/ 

- 使用aws cli

  ```shell
  $ aws s3 ls --no-sign-request s3://openaq-data-archive/
  ```

  ```shell
  $ aws s3 ls --no-sign-request s3://openaq-data-archive/records/csv.gz/locationid=1/year=2006/month=11/ 
  
  2023-11-09 17:03:21        176 location-1-20061113.csv.gz
  2023-11-09 17:03:26        177 location-1-20061115.csv.gz
  2023-11-09 17:03:27        175 location-1-20061117.csv.gz
  2023-11-09 17:18:51        177 location-1-20061119.csv.gz
  2023-11-09 17:03:25        176 location-1-20061121.csv.gz
  2023-11-09 17:03:09        177 location-1-20061123.csv.gz
  2023-11-09 17:03:02        177 location-1-20061125.csv.gz
  2023-11-09 17:03:03        175 location-1-20061127.csv.gz
  2023-11-09 17:03:19        177 location-1-20061129.csv.gz
  ```

  ```shell
  $ aws s3 ls --no-sign-request s3://openaq-data-archive/records/csv.gz/locationid=3917/year=2024/month=01/
  
  2024-01-05 07:03:37        666 location-3917-20240101.csv.gz
  2024-01-06 07:02:58        607 location-3917-20240102.csv.gz
  2024-01-07 07:02:23        593 location-3917-20240103.csv.gz
  2024-01-08 07:01:21        592 location-3917-20240104.csv.gz
  2024-01-09 07:02:21        551 location-3917-20240105.csv.gz
  2024-01-10 07:00:32        547 location-3917-20240106.csv.gz
  2024-01-11 07:01:07        568 location-3917-20240107.csv.gz
  2024-01-12 07:00:51        593 location-3917-20240108.csv.gz
  2024-01-13 07:02:42        625 location-3917-20240109.csv.gz
  2024-01-14 07:00:32        615 location-3917-20240110.csv.gz
  2024-01-15 07:01:43        596 location-3917-20240111.csv.gz
  2024-01-16 07:03:33        626 location-3917-20240112.csv.gz
  2024-01-17 07:01:03        621 location-3917-20240113.csv.gz
  2024-01-18 07:03:31        618 location-3917-20240114.csv.gz
  2024-01-19 07:01:21        635 location-3917-20240115.csv.gz
  2024-01-20 07:02:03        632 location-3917-20240116.csv.gz
  2024-01-21 07:03:50        578 location-3917-20240117.csv.gz
  2024-01-22 07:02:01        582 location-3917-20240118.csv.gz
  2024-01-23 07:01:30        565 location-3917-20240119.csv.gz
  2024-01-24 07:00:51        598 location-3917-20240120.csv.gz
  2024-01-25 07:02:03        604 location-3917-20240121.csv.gz
  2024-01-26 07:01:51        614 location-3917-20240122.csv.gz
  2024-01-27 07:00:41        510 location-3917-20240123.csv.gz
  2024-01-28 07:02:07        619 location-3917-20240124.csv.gz
  2024-01-29 07:02:42        563 location-3917-20240125.csv.gz
  2024-01-30 07:01:23        534 location-3917-20240126.csv.gz
  2024-01-31 07:02:15        511 location-3917-20240127.csv.gz
  2024-02-01 07:02:48        483 location-3917-20240128.csv.gz
  2024-02-02 07:01:48        436 location-3917-20240129.csv.gz
  ```

## V3 API 基础信息

OpenAQ 是一个开源空气质量数据平台，聚合了来自全球数百个来源的空气质量数据。

- **基础 URL**: `https://api.openaq.org/v3`
- **认证方式**: 需要 API Key，通过请求头 `X-API-Key` 传递
- **官方客户端库**: Python (`openaq`), R (`openaq`)

## 常用端点

| 端点 | 描述 |
|------|------|
| `/v3/locations` | 获取监测位置列表 |
| `/v3/sensors/{id}/measurements` | 获取传感器的原始测量值 |
| `/v3/sensors/{id}/days` | 获取传感器的日平均值 |
| `/v3/sensors/{id}/days/yearly` | 获取传感器的年平均值 |
| `/v3/parameters/{id}/latest` | 获取某参数的最新值 |

## 使用示例

- 使用http调用
- 使用python包``openaq`调用
  - 安装：```pip install openaq```
  - 代码：https://github.com/openaq/openaq-python

### 1. 按参数筛选位置

获取 PM2.5 (参数 ID=2) 的所有监测位置：

```bash
curl --request GET \
    --url "https://api.openaq.org/v3/locations?parameters_id=2&limit=1000" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```python
from openaq import OpenAQ
client = OpenAQ(api_key="YOUR-OPENAQ-API-KEY")
client.locations.list(parameters_id=2, limit=1000)
client.close()
```

```shell
curl --request GET \
    --url "https://api.openaq.org/v3/locations?parameters_id=2&limit=2" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 2,
    "found": ">2"
  },
  "results": [
    {
      "id": 3,
      "name": "NMA - Nima",
      "locality": null,
      "timezone": "Africa/Accra",
      "country": {
        "id": 152,
        "code": "GH",
        "name": "Ghana"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 209,
        "name": "Dr. Raphael E. Arku and Colleagues"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 6,
          "name": "pm10 µg/m³",
          "parameter": {
            "id": 1,
            "name": "pm10",
            "units": "µg/m³",
            "displayName": "PM10"
          }
        },
        {
          "id": 5,
          "name": "pm25 µg/m³",
          "parameter": {
            "id": 2,
            "name": "pm25",
            "units": "µg/m³",
            "displayName": "PM2.5"
          }
        }
      ],
      "coordinates": {
        "latitude": 5.58389,
        "longitude": -0.19968
      },
      "licenses": null,
      "bounds": [
        -0.19968,
        5.58389,
        -0.19968,
        5.58389
      ],
      "distance": null,
      "datetimeFirst": null,
      "datetimeLast": null
    },
    {
      "id": 4,
      "name": "NMT - Nima",
      "locality": null,
      "timezone": "Africa/Accra",
      "country": {
        "id": 152,
        "code": "GH",
        "name": "Ghana"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 209,
        "name": "Dr. Raphael E. Arku and Colleagues"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 7,
          "name": "pm10 µg/m³",
          "parameter": {
            "id": 1,
            "name": "pm10",
            "units": "µg/m³",
            "displayName": "PM10"
          }
        },
        {
          "id": 8,
          "name": "pm25 µg/m³",
          "parameter": {
            "id": 2,
            "name": "pm25",
            "units": "µg/m³",
            "displayName": "PM2.5"
          }
        }
      ],
      "coordinates": {
        "latitude": 5.58165,
        "longitude": -0.19898
      },
      "licenses": null,
      "bounds": [
        -0.19898,
        5.58165,
        -0.19898,
        5.58165
      ],
      "distance": null,
      "datetimeFirst": null,
      "datetimeLast": null
    }
  ]
}
```

### 2. 查找附近位置

查找距离指定坐标 12km 范围内的监测位置:
**注意，本api的coordinates参数传入的是（纬度,经度）**

```bash
curl --request GET \
    --url "https://api.openaq.org/v3/locations?coordinates=35.14942,136.90610&radius=12000&limit=1000" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```python
from openaq import OpenAQ
client = OpenAQ(api_key="YOUR-OPENAQ-API-KEY")
client.locations.list(coordinates=(35.14942, 136.90610), radius=12000, limit=1000)
client.close()
```

```shell
curl --request GET \
    --url "https://api.openaq.org/v3/locations?coordinates=35.14942,136.90610&radius=12000&limit=2" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 2,
    "found": ">2"
  },
  "results": [
    {
      "id": 1214772,
      "name": "名古屋市中区大須２丁目４０４番地先",
      "locality": " ",
      "timezone": "Asia/Tokyo",
      "country": {
        "id": 190,
        "code": "JP",
        "name": "Japan"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 63,
        "name": "Ministry of the Environment Air Pollutant Wide Area Monitoring System"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 6516016,
          "name": "no ppm",
          "parameter": {
            "id": 35,
            "name": "no",
            "units": "ppm",
            "displayName": "NO"
          }
        },
        {
          "id": 6518053,
          "name": "no2 ppm",
          "parameter": {
            "id": 7,
            "name": "no2",
            "units": "ppm",
            "displayName": "NO₂"
          }
        },
        {
          "id": 6520484,
          "name": "nox ppm",
          "parameter": {
            "id": 19840,
            "name": "nox",
            "units": "ppm",
            "displayName": "NOx"
          }
        },
        {
          "id": 6521128,
          "name": "pm25 µg/m³",
          "parameter": {
            "id": 2,
            "name": "pm25",
            "units": "µg/m³",
            "displayName": "PM2.5"
          }
        },
        {
          "id": 6519243,
          "name": "so2 ppm",
          "parameter": {
            "id": 9,
            "name": "so2",
            "units": "ppm",
            "displayName": "SO₂"
          }
        }
      ],
      "coordinates": {
        "latitude": 35.1625,
        "longitude": 136.901111
      },
      "licenses": [
        {
          "id": 39,
          "name": "政府標準利用規約（第2.0版） (Government Standard Terms of Use v2.0)",
          "attribution": {
            "name": "Unknown Governmental Organization",
            "url": null
          },
          "dateFrom": "2023-07-14",
          "dateTo": null
        }
      ],
      "bounds": [
        136.901111,
        35.1625,
        136.901111,
        35.1625
      ],
      "distance": 1522.78921836,
      "datetimeFirst": {
        "utc": "2023-07-14T17:00:00Z",
        "local": "2023-07-15T02:00:00+09:00"
      },
      "datetimeLast": {
        "utc": "2026-02-03T13:00:00Z",
        "local": "2026-02-03T22:00:00+09:00"
      }
    },
    {
      "id": 1214773,
      "name": "名古屋市中川区元中野町２－１１",
      "locality": " ",
      "timezone": "Asia/Tokyo",
      "country": {
        "id": 190,
        "code": "JP",
        "name": "Japan"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 63,
        "name": "Ministry of the Environment Air Pollutant Wide Area Monitoring System"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 6520422,
          "name": "no ppm",
          "parameter": {
            "id": 35,
            "name": "no",
            "units": "ppm",
            "displayName": "NO"
          }
        },
        {
          "id": 6516282,
          "name": "no2 ppm",
          "parameter": {
            "id": 7,
            "name": "no2",
            "units": "ppm",
            "displayName": "NO₂"
          }
        },
        {
          "id": 6517169,
          "name": "nox ppm",
          "parameter": {
            "id": 19840,
            "name": "nox",
            "units": "ppm",
            "displayName": "NOx"
          }
        },
        {
          "id": 6519548,
          "name": "pm25 µg/m³",
          "parameter": {
            "id": 2,
            "name": "pm25",
            "units": "µg/m³",
            "displayName": "PM2.5"
          }
        },
        {
          "id": 6519853,
          "name": "so2 ppm",
          "parameter": {
            "id": 9,
            "name": "so2",
            "units": "ppm",
            "displayName": "SO₂"
          }
        }
      ],
      "coordinates": {
        "latitude": 35.134444,
        "longitude": 136.883333
      },
      "licenses": [
        {
          "id": 39,
          "name": "政府標準利用規約（第2.0版） (Government Standard Terms of Use v2.0)",
          "attribution": {
            "name": "Unknown Governmental Organization",
            "url": null
          },
          "dateFrom": "2023-07-14",
          "dateTo": null
        }
      ],
      "bounds": [
        136.883333,
        35.134444,
        136.883333,
        35.134444
      ],
      "distance": 2656.65295943,
      "datetimeFirst": {
        "utc": "2023-07-14T17:00:00Z",
        "local": "2023-07-15T02:00:00+09:00"
      },
      "datetimeLast": {
        "utc": "2026-02-03T13:00:00Z",
        "local": "2026-02-03T22:00:00+09:00"
      }
    }
  ]
}
```

### 3. 查找边界框内的位置

**注意，本api的coordinates参数传入的是（经度,纬度）**

```bash
curl --request GET \
    --url "https://api.openaq.org/v3/locations?bbox=-118.668153,33.703935,-118.155358,34.337306&limit=1000" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```python
from openaq import OpenAQ
client = OpenAQ(api_key="YOUR-OPENAQ-API-KEY")
client.locations.list(bbox=[-118.668153, 33.703935, -118.155358, 34.337306], limit=1000)
client.close()
```

```shell
curl --request GET \
    --url "https://api.openaq.org/v3/locations?bbox=-118.668153,33.703935,-118.155358,34.337306&limit=2" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 2,
    "found": ">2"
  },
  "results": [
    {
      "id": 847,
      "name": "South Long Beach",
      "locality": null,
      "timezone": "America/Los_Angeles",
      "country": {
        "id": 155,
        "code": "US",
        "name": "United States"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 119,
        "name": "AirNow"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 1502,
          "name": "pm25 µg/m³",
          "parameter": {
            "id": 2,
            "name": "pm25",
            "units": "µg/m³",
            "displayName": "PM2.5"
          }
        }
      ],
      "coordinates": {
        "latitude": 33.792221,
        "longitude": -118.175278
      },
      "licenses": [
        {
          "id": 33,
          "name": "US Public Domain",
          "attribution": {
            "name": "Unknown Governmental Organization",
            "url": null
          },
          "dateFrom": "2016-01-30",
          "dateTo": null
        }
      ],
      "bounds": [
        -118.175278,
        33.792221,
        -118.175278,
        33.792221
      ],
      "distance": null,
      "datetimeFirst": {
        "utc": "2016-03-06T20:00:00Z",
        "local": "2016-03-06T12:00:00-08:00"
      },
      "datetimeLast": {
        "utc": "2022-05-05T22:00:00Z",
        "local": "2022-05-05T15:00:00-07:00"
      }
    },
    {
      "id": 1247,
      "name": "LAX-Hastings",
      "locality": null,
      "timezone": "America/Los_Angeles",
      "country": {
        "id": 155,
        "code": "US",
        "name": "United States"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 119,
        "name": "AirNow"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 2244,
          "name": "o3 ppm",
          "parameter": {
            "id": 10,
            "name": "o3",
            "units": "ppm",
            "displayName": "O₃"
          }
        }
      ],
      "coordinates": {
        "latitude": 33.9517,
        "longitude": -118.4389
      },
      "licenses": [
        {
          "id": 33,
          "name": "US Public Domain",
          "attribution": {
            "name": "Unknown Governmental Organization",
            "url": null
          },
          "dateFrom": "2016-01-30",
          "dateTo": null
        }
      ],
      "bounds": [
        -118.4389,
        33.9517,
        -118.4389,
        33.9517
      ],
      "distance": null,
      "datetimeFirst": {
        "utc": "2016-03-06T20:00:00Z",
        "local": "2016-03-06T12:00:00-08:00"
      },
      "datetimeLast": {
        "utc": "2016-11-09T21:00:00Z",
        "local": "2016-11-09T13:00:00-08:00"
      }
    }
  ]
}
```

### 4. 获取传感器的原始测量值

```bash
curl --request GET \
    --url "https://api.openaq.org/v3/sensors/3917/measurements?limit=1000" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```python
from openaq import OpenAQ
client = OpenAQ(api_key="YOUR-OPENAQ-API-KEY")
client.measurements.list(sensors_id=3917, limit=1000)
client.close()
```

```shell
curl --request GET \
    --url "https://api.openaq.org/v3/sensors/3917/measurements?limit=2" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 2,
    "found": ">2"
  },
  "results": [
    {
      "value": 0.043,
      "flagInfo": {
        "hasFlags": false
      },
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": null
      },
      "period": {
        "label": "raw",
        "interval": "01:00:00",
        "datetimeFrom": {
          "utc": "2016-03-06T19:00:00Z",
          "local": "2016-03-06T12:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-03-06T20:00:00Z",
          "local": "2016-03-06T13:00:00-07:00"
        }
      },
      "coordinates": null,
      "summary": null,
      "coverage": {
        "expectedCount": 1,
        "expectedInterval": "01:00:00",
        "observedCount": 1,
        "observedInterval": "01:00:00",
        "percentComplete": 100,
        "percentCoverage": 100,
        "datetimeFrom": {
          "utc": "2016-03-06T19:00:00Z",
          "local": "2016-03-06T12:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-03-06T20:00:00Z",
          "local": "2016-03-06T13:00:00-07:00"
        }
      }
    },
    {
      "value": 0.044,
      "flagInfo": {
        "hasFlags": false
      },
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": null
      },
      "period": {
        "label": "raw",
        "interval": "01:00:00",
        "datetimeFrom": {
          "utc": "2016-03-06T20:00:00Z",
          "local": "2016-03-06T13:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-03-06T21:00:00Z",
          "local": "2016-03-06T14:00:00-07:00"
        }
      },
      "coordinates": null,
      "summary": null,
      "coverage": {
        "expectedCount": 1,
        "expectedInterval": "01:00:00",
        "observedCount": 1,
        "observedInterval": "01:00:00",
        "percentComplete": 100,
        "percentCoverage": 100,
        "datetimeFrom": {
          "utc": "2016-03-06T20:00:00Z",
          "local": "2016-03-06T13:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-03-06T21:00:00Z",
          "local": "2016-03-06T14:00:00-07:00"
        }
      }
    }
  ]
}
```

### 5. 获取传感器的日平均值

```bash
curl --request GET \
    --url "https://api.openaq.org/v3/sensors/3917/days?limit=1000" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```python
from openaq import OpenAQ
client = OpenAQ(api_key="YOUR-OPENAQ-API-KEY")
client.measurements.list(sensors_id=3917, data="days", limit=1000)
client.close()
```

```shell
curl --request GET \
    --url "https://api.openaq.org/v3/sensors/3917/days?limit=2" \   
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 2,
    "found": ">2"
  },
  "results": [
    {
      "value": 0.0435,
      "flagInfo": {
        "hasFlags": false
      },
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": null
      },
      "period": {
        "label": "1day",
        "interval": "24:00:00",
        "datetimeFrom": {
          "utc": "2016-03-06T07:00:00Z",
          "local": "2016-03-06T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-03-07T07:00:00Z",
          "local": "2016-03-07T00:00:00-07:00"
        }
      },
      "coordinates": null,
      "summary": {
        "min": 0.0430000014603138,
        "q02": 0.04301999881863594,
        "q25": 0.04324999824166298,
        "median": 0.04349999874830246,
        "q75": 0.04374999925494194,
        "q98": 0.04397999867796898,
        "max": 0.04399999976158142,
        "avg": 0.04349999874830246,
        "sd": 0.0007071067811921239
      },
      "coverage": {
        "expectedCount": 24,
        "expectedInterval": "24:00:00",
        "observedCount": 2,
        "observedInterval": "02:00:00",
        "percentComplete": 8,
        "percentCoverage": 8,
        "datetimeFrom": {
          "utc": "2016-03-06T20:00:00Z",
          "local": "2016-03-06T13:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-03-06T21:00:00Z",
          "local": "2016-03-06T14:00:00-07:00"
        }
      }
    },
    {
      "value": 0.039,
      "flagInfo": {
        "hasFlags": false
      },
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": null
      },
      "period": {
        "label": "1day",
        "interval": "24:00:00",
        "datetimeFrom": {
          "utc": "2016-03-07T07:00:00Z",
          "local": "2016-03-07T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-03-08T07:00:00Z",
          "local": "2016-03-08T00:00:00-07:00"
        }
      },
      "coordinates": null,
      "summary": {
        "min": 0.03700000047683716,
        "q02": 0.03708000108599663,
        "q25": 0.03799999877810478,
        "median": 0.039000000804662704,
        "q75": 0.03999999910593033,
        "q98": 0.04092000052332878,
        "max": 0.04100000113248825,
        "avg": 0.039000000804662704,
        "sd": 0.0028284271247461927
      },
      "coverage": {
        "expectedCount": 24,
        "expectedInterval": "24:00:00",
        "observedCount": 2,
        "observedInterval": "02:00:00",
        "percentComplete": 8,
        "percentCoverage": 8,
        "datetimeFrom": {
          "utc": "2016-03-07T15:00:00Z",
          "local": "2016-03-07T08:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-03-07T16:00:00Z",
          "local": "2016-03-07T09:00:00-07:00"
        }
      }
    }
  ]
}
```

### 6. 获取传感器的年平均值

```bash
curl --request GET \
    --url "https://api.openaq.org/v3/sensors/3917/days/yearly?limit=1000" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```python
from openaq import OpenAQ
client = OpenAQ(api_key="YOUR-OPENAQ-API-KEY")
client.measurements.list(sensors_id=3917, data="days", rollup="yearly", limit=1000)
client.close()
```

```shell
curl --request GET \
    --url "https://api.openaq.org/v3/sensors/3917/days/yearly?limit=2" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 2,
    "found": 11
  },
  "results": [
    {
      "value": 0.0352,
      "flagInfo": {
        "hasFlags": false
      },
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": null
      },
      "period": {
        "label": "1 year",
        "interval": "1year",
        "datetimeFrom": {
          "utc": "2016-01-01T07:00:00Z",
          "local": "2016-01-01T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2017-01-01T07:00:00Z",
          "local": "2017-01-01T00:00:00-07:00"
        }
      },
      "coordinates": null,
      "summary": {
        "min": 0.0020000000949949026,
        "q02": 0.011843333207070827,
        "q25": 0.027611244469881058,
        "median": 0.03681818023324013,
        "q75": 0.04402083344757557,
        "q98": 0.05304347723722458,
        "max": 0.05480952560901642,
        "avg": 0.035233967136249045,
        "sd": 0.011171429379843176
      },
      "coverage": {
        "expectedCount": 366,
        "expectedInterval": "8784:00:00",
        "observedCount": 299,
        "observedInterval": "7176:00:00",
        "percentComplete": 82,
        "percentCoverage": 82,
        "datetimeFrom": {
          "utc": "2016-03-06T07:00:00Z",
          "local": "2016-03-06T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2017-01-01T07:00:00Z",
          "local": "2017-01-01T00:00:00-07:00"
        }
      }
    },
    {
      "value": 0.0336,
      "flagInfo": {
        "hasFlags": false
      },
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": null
      },
      "period": {
        "label": "1 year",
        "interval": "1year",
        "datetimeFrom": {
          "utc": "2017-01-01T07:00:00Z",
          "local": "2017-01-01T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2018-01-01T07:00:00Z",
          "local": "2018-01-01T00:00:00-07:00"
        }
      },
      "coordinates": null,
      "summary": {
        "min": 0.001500000013038516,
        "q02": 0.008359999731183052,
        "q25": 0.025325757451355457,
        "median": 0.035999998450279236,
        "q75": 0.042547618970274925,
        "q98": 0.05318019062280655,
        "max": 0.05939130485057831,
        "avg": 0.03363834716624149,
        "sd": 0.012054109878931697
      },
      "coverage": {
        "expectedCount": 365,
        "expectedInterval": "8760:00:00",
        "observedCount": 339,
        "observedInterval": "8136:00:00",
        "percentComplete": 93,
        "percentCoverage": 93,
        "datetimeFrom": {
          "utc": "2017-01-01T07:00:00Z",
          "local": "2017-01-01T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2018-01-01T07:00:00Z",
          "local": "2018-01-01T00:00:00-07:00"
        }
      }
    }
  ]
}
```

### 7. 获取最新的 PM2.5 值

```bash
curl --request GET \
    --url "https://api.openaq.org/v3/parameters/2/latest?limit=1000" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```python
from openaq import OpenAQ
client = OpenAQ(api_key="YOUR-OPENAQ-API-KEY")
client.parameters.latest(parameters_id=2, limit=1000)
client.close()
```

```shell
curl --request GET \
    --url "https://api.openaq.org/v3/parameters/2/latest?limit=2" \
    --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 2,
    "found": 24256
  },
  "results": [
    {
      "datetime": {
        "utc": "2026-02-03T13:00:00Z",
        "local": "2026-02-03T22:00:00+09:00"
      },
      "value": 19,
      "coordinates": {
        "latitude": 35.21815,
        "longitude": 128.57425
      },
      "sensorsId": 8539597,
      "locationsId": 2622686
    },
    {
      "datetime": {
        "utc": "2026-02-03T12:00:00Z",
        "local": "2026-02-03T14:00:00+02:00"
      },
      "value": -1,
      "coordinates": {
        "latitude": 54.88361359025449,
        "longitude": 23.83583450024486
      },
      "sensorsId": 23735,
      "locationsId": 8152
    }
  ]
}
```

### 8. 常用参数

| 参数名 | 描述 |
|--------|------|
| `limit` | 限制每页返回结果数量，默认 100，最大 10000 |
| `radius` | 搜索半径（米），用于附近位置查询 |
| `coordinates` | 中心坐标，格式为 `经度,纬度` |
| `bbox` | 边界框，格式为 `xmin,ymin,xmax,ymax` |
| `parameters_id` | 参数 ID（如 PM2.5 的 ID 为 2） |
| `data` | 数据类型：`measurements`（原始）、`days`（日均） |
| `rollup` | 汇总类型：`daily`（日均）、`yearly`（年均） |
| `page` | 页码 |

### 9. 污染物

| ID   | 污染物 | 单位  | EPA阈值 | 描述                         |
| ---- | ------ | ----- | ------- | ---------------------------- |
| 1    | pm10   | µg/m³ | 150.0   | 颗粒物 < 10微米              |
| 2    | pm25   | µg/m³ | 12.0    | 颗粒物 < 2.5微米（主要测试） |
| 7    | no2    | ppm   | 100.0   | 二氧化氮                     |
| 8    | co     | ppm   | 9.0     | 一氧化碳                     |
| 9    | so2    | ppm   | 75.0    | 二氧化硫                     |
| 10   | o3     | ppm   | 0.070   | 地面臭氧（主要测试）         |

## 获取 API Key

1. 访问 [OpenAQ API 注册页面](https://api.openaq.org/)
2. 注册账号并登录
3. 在账户设置中获取 API Key

## 使用 API Key

- 环境变量`OPENAQ_API_KEY`

## 相关链接

- [OpenAQ 官方文档](https://docs.openaq.org/)
- [Python 客户端库 (py-openaq)](http://dhhagan.github.io/py-openaq/)

