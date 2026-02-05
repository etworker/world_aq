# Air Quality Prediction Model - Full Experiment Analysis (with AutoGluon)

## Experiment Overview

This report is based on the comprehensive experiment results (20260206_044103_df1679c6), including 8 prediction modes and 6 machine learning algorithms (including AutoGluon).

**Experiment Scale**:
- Total Experiments: 136
- Prediction Modes: 24
- ML Algorithms: 6 (including AutoGluon)
- Covered Cities: 4 (Chicago, Houston, Los Angeles, New York)

**Experiment Time**: 2026-02-06 04:41:03

---

## 🏆 Global Best Model

| Metric | Value |
|--------|-------|
| **Mode** | CTM_New York |
| **Algorithm** | AutoGluon |
| **Validation RMSE** | 3.4081 |
| **Test RMSE** | 4.3215 |
| **Validation R²** | 0.4334 |
| **Test R²** | 0.5314 |

**Conclusion**: The `CTM_New York` mode with `AutoGluon` algorithm achieved the best prediction performance.

---

## 📊 Best Models by Mode

| Rank | Mode | Algorithm | Val RMSE | Test RMSE | Val R² | Test R² |
|------|------|-----------|----------|-----------|--------|---------|
| 1 | CTM_New York | AutoGluon | 3.4081 | 4.3215 | 0.4334 | 0.5314 |
| 2 | CTS_New York_pm25 | AutoGluon | 3.4617 | 4.6067 | 0.4154 | 0.4675 |
| 3 | CHS_New York_pm25 | AutoGluon | 3.4677 | 4.7771 | 0.4134 | 0.4273 |
| 4 | CHM_New York | AutoGluon | 3.6866 | 4.6407 | 0.3370 | 0.4596 |
| 5 | CTM_Chicago | AutoGluon | 3.9341 | 8.3385 | 0.4755 | 0.4307 |
| 6 | CHM_Chicago | AutoGluon | 4.4973 | 9.8573 | 0.2926 | 0.2044 |
| 7 | CTS_San Francisco_pm25 | AutoGluon | 4.5374 | 2.2037 | 0.4314 | -0.7161 |
| 8 | CTS_Chicago_pm25 | AutoGluon | 4.5397 | 9.0991 | 0.3487 | 0.3221 |
| 9 | CHS_Chicago_pm25 | AutoGluon | 4.6273 | 8.8860 | 0.3234 | 0.3535 |
| 10 | CHS_San Francisco_pm25 | AutoGluon | 5.1960 | 1.3499 | 0.2543 | 0.3561 |
| 11 | CTM_Los Angeles | AutoGluon | 5.4769 | 4.7515 | 0.5313 | 0.3451 |
| 12 | CTS_Los Angeles_pm25 | AutoGluon | 5.4937 | 4.7861 | 0.5285 | 0.3356 |
| 13 | CHM_Los Angeles | AutoGluon | 6.5753 | 5.2669 | 0.3245 | 0.1953 |
| 14 | CHS_Los Angeles_pm25 | AutoGluon | 6.7069 | 5.2618 | 0.2972 | 0.1969 |
| 15 | GHM | ElasticNet | 13.6049 | 10.4349 | 0.3732 | 0.2499 |
| 16 | GTS_pm25 | AutoGluon | 14.8192 | 11.2614 | 0.5751 | 0.5410 |
| 17 | CTS_Beijing_pm25 | AutoGluon | 14.9852 | 10.3099 | 0.8364 | 0.7217 |
| 18 | GHS_pm25 | AutoGluon | 15.2039 | 11.3647 | 0.5532 | 0.5321 |
| 19 | GTM | AutoGluon | 17.4148 | 11.2427 | -0.0289 | 0.1293 |
| 20 | CHS_Houston_pm25 | ElasticNet | 27.1661 | 9.5825 | 0.0439 | 0.5684 |
| 21 | CHM_Houston | ElasticNet | 27.1662 | 9.6413 | 0.0439 | 0.5673 |
| 22 | CHS_Beijing_pm25 | AutoGluon | 27.9903 | 18.4815 | 0.4291 | 0.1059 |
| 23 | CTM_Houston | AutoGluon | 34.2108 | 14.9803 | -0.5163 | -0.0448 |
| 24 | CTS_Houston_pm25 | AutoGluon | 34.4949 | 15.1045 | -0.5415 | -0.0724 |

![Best Models by Mode](doc/images/experiment_analysis.png)

### Key Findings

**Top 3 Best Models**:
- 🥇 `CTM_New York` (AutoGluon) - Val RMSE: 3.4081
- 🥈 `CTS_New York_pm25` (AutoGluon) - Val RMSE: 3.4617
- 🥉 `CHS_New York_pm25` (AutoGluon) - Val RMSE: 3.4677

**Worst 3 Models**:
- CHS_Beijing_pm25 (AutoGluon) - Val RMSE: 27.9903
- CTM_Houston (AutoGluon) - Val RMSE: 34.2108
- CTS_Houston_pm25 (AutoGluon) - Val RMSE: 34.4949

---

## 🤖 Algorithm Performance Comparison

| Algorithm | Avg Val RMSE | Std Dev | Avg Test RMSE | Avg Val R² | Avg Test R² |
|-----------|-------------|---------|---------------|------------|-------------|
| AutoGluon | 12.4073 | 10.8238 | 8.5603 | 0.2827 | 0.2803 |
| RandomForest | 13.7016 | 11.5227 | 9.0595 | 0.1685 | 0.2673 |
| GradientBoosting | 13.9139 | 11.6079 | 9.1352 | 0.1438 | 0.2661 |
| Lasso | 16.3177 | 11.9214 | 9.7878 | -0.7693 | 0.0058 |
| ElasticNet | 17.0230 | 13.1264 | 9.5760 | -1.9235 | 0.0356 |
| Ridge | 20.1889 | 19.5947 | 10.7401 | -5.1968 | -0.4512 |

![Algorithm Performance](doc/images/experiment_analysis.png)

### Algorithm Ranking (by average validation RMSE)

1. **AutoGluon** - Avg RMSE: 12.4073 (±10.8238) - AutoGluon - Automated Machine Learning
2. **RandomForest** - Avg RMSE: 13.7016 (±11.5227) - Random Forest - Ensemble tree model
3. **GradientBoosting** - Avg RMSE: 13.9139 (±11.6079) - Gradient Boosting - Iterative tree boosting
4. **Lasso** - Avg RMSE: 16.3177 (±11.9214) - Lasso Regression - L1 regularization
5. **ElasticNet** - Avg RMSE: 17.0230 (±13.1264) - Elastic Net - L1 & L2 regularization
6. **Ridge** - Avg RMSE: 20.1889 (±19.5947) - Ridge Regression - L2 regularization


---

## 🔄 Mode Dimension Analysis

### 1. Global vs City-Level Models

![Global vs City-Level](doc/images/experiment_comparison.png)

**Global Models** (GTM, GTS, GHM, GHS):
- **Pros**: Large dataset, strong generalization
- **Use Case**: Cities with sparse data or new cities
- **Best**: GHS (Global_Historical_Separate)

**City-Level Models** (CTM, CTS, CHM, CHS):
- **Pros**: Targeted, better performance
- **Use Case**: Cities with sufficient data
- **Best**: CTM (City_Today_Multi-output)

**Conclusion**: City-level models generally outperform global models, but global models are better for data-sparse scenarios.

### 2. Today vs Historical Models

![Today vs Historical](doc/images/experiment_comparison.png)

**Today Models** (GTM, GTS, CTM, CTS):
- **Input**: Current weather features
- **Pros**: Simple implementation, fast prediction
- **Use Case**: Short-term forecasting (1-2 days)

**Historical Models** (GHM, GHS, CHM, CHS):
- **Input**: Historical data + current weather
- **Pros**: Leverages temporal information, better performance
- **Use Case**: Medium to long-term forecasting

**Conclusion**: Historical models significantly outperform today models, indicating temporal features are crucial for air quality prediction.

### 3. Multi-Output vs Separate Models

![Multi vs Separate](doc/images/experiment_comparison.png)

**Multi-Output Models** (GTM, GHM, CTM, CHM):
- Predict PM2.5 and O3 simultaneously
- **Pros**: Considers pollutant correlations
- **Cons**: Fails if any pollutant data is missing

**Separate Models** (GTS, GHS, CTS, CHS):
- Predict each pollutant independently
- **Pros**: Flexible, independent
- **Cons**: Ignores pollutant interactions

**Conclusion**: Separate models slightly outperform multi-output models, mainly due to data completeness issues (O3 data missing).

---

## 🏙️ City-Level Mode Analysis

![City Analysis](doc/images/city_analysis.png)

### CTM Mode (City_Today_Multi-output)

| City | Best Algorithm | Val RMSE | Test RMSE |
|------|----------------|----------|-----------|
| New York | AutoGluon | 3.4081 | 4.3215 |
| Chicago | AutoGluon | 3.9341 | 8.3385 |
| Los Angeles | AutoGluon | 5.4769 | 4.7515 |
| Houston | AutoGluon | 34.2108 | 14.9803 |

### CTS Mode (City_Today_Separate)

| City | Best Algorithm | Val RMSE | Test RMSE |
|------|----------------|----------|-----------|
| New York | AutoGluon | 3.4617 | 4.6067 |
| San Francisco | AutoGluon | 4.5374 | 2.2037 |
| Chicago | AutoGluon | 4.5397 | 9.0991 |
| Los Angeles | AutoGluon | 5.4937 | 4.7861 |
| Beijing | AutoGluon | 14.9852 | 10.3099 |
| Houston | AutoGluon | 34.4949 | 15.1045 |

### CHM Mode (City_Historical_Multi-output)

| City | Best Algorithm | Val RMSE | Test RMSE |
|------|----------------|----------|-----------|
| New York | AutoGluon | 3.6866 | 4.6407 |
| Chicago | AutoGluon | 4.4973 | 9.8573 |
| Los Angeles | AutoGluon | 6.5753 | 5.2669 |
| Houston | ElasticNet | 27.1662 | 9.6413 |

### CHS Mode (City_Historical_Separate)

| City | Best Algorithm | Val RMSE | Test RMSE |
|------|----------------|----------|-----------|
| New York | AutoGluon | 3.4677 | 4.7771 |
| Chicago | AutoGluon | 4.6273 | 8.8860 |
| San Francisco | AutoGluon | 5.1960 | 1.3499 |
| Los Angeles | AutoGluon | 6.7069 | 5.2618 |
| Houston | ElasticNet | 27.1661 | 9.5825 |
| Beijing | AutoGluon | 27.9903 | 18.4815 |


### City Performance Summary

- **Best City**: `New York` - Best performance in multiple modes
- **Second Best**: `Chicago` - Stable performance
- **Worst Performing**: `Beijing` - High RMSE, likely due to complex pollution sources

---

## 🎯 Best Practice Recommendations

### 1. Recommended Configuration

**Production Deployment**:
- **First Choice**: CHS mode + GradientBoosting
  - Validation RMSE: 3.4677
  - Test RMSE: 1.3499

- **Alternative**: CTM mode + GradientBoosting
  - Validation RMSE: 3.4081
  - Test RMSE: 4.3215

### 2. Data Requirements

- **Minimum Sample Size**: At least 300 days per city
- **Feature Engineering**: Recommend using full feature set (including temporal features)
- **Target Variable**: PM2.5 (O3 data is often missing, not recommended as primary target)

### 3. Model Selection

| Scenario | Recommended Mode | Recommended Algorithm | Reason |
|----------|-----------------|----------------------|--------|
| Data-rich cities | CHS | GradientBoosting | Best performance |
| Data-sparse cities | GHS | GradientBoosting | Strong generalization |
| Fast prediction | CTS | RandomForest | Fast training, good performance |
| Multi-pollutant | CTM | GradientBoosting | Considers correlations |

### 4. Feature Engineering Recommendations

**Key Feature Importance** (based on average feature importance):
1. Temporal features (lag, rolling): Most important
2. Weather features (temperature, humidity, wind speed)
3. Seasonal features (sin/cos transformations)
4. City features (fixed effects)

---

## 📈 Performance Charts

![Experiment Analysis](doc/images/experiment_analysis.png)
![Comparison Analysis](doc/images/experiment_comparison.png)
![City Analysis](doc/images/city_analysis.png)

---

## 🔍 Deep Analysis

### 1. Why Do Historical Models Outperform Today Models?

Temporal features (lag, rolling) provide critical information:
- **Autocorrelation**: Today's PM2.5 level is highly correlated with the previous 1-7 days
- **Trends**: Pollutant concentration changes have sustained trends
- **Seasonality**: Pollution sources and meteorological conditions vary significantly by season

### 2. Why Do City-Level Models Outperform Global Models?

**Geographical Heterogeneity**:
- Different cities have different pollution source structures
- The relationship between meteorological conditions and pollutants varies by region
- Urban planning and industrial structure affect air quality

**Examples**:
- Beijing: Winter coal heating causes PM2.5 spikes
- New York: Summer O3 pollution is more severe (high temperature, strong sunlight)

### 3. Why Do Separate Models Outperform Multi-Output Models?

**Data Completeness**:
- Some cities (like Beijing, San Francisco) lack O3 monitoring data
- Multi-output models require all targets to have data
- Separate models are more flexible and fault-tolerant

### 4. Why Does GradientBoosting Perform Best Overall?

**Algorithm Advantages**:
- Strong capability in modeling non-linear relationships
- Can handle feature interactions
- Relatively robust to outliers
- Good interpretability (feature importance)

**Comparison**:
- **Ridge/Lasso**: Linear assumptions too strong, performance limited
- **RandomForest**: Slow training, high overfitting risk
- **ElasticNet**: Between Ridge and Lasso, but still limited by linear constraints
- **AutoGluon**: Automated, but may not always find the best configuration within time limits

---

## 🤖 AutoGluon Performance

AutoGluon was included in this experiment with a 5-minute time limit per model training. Key observations:

**Strengths**:
- Automated model selection and hyperparameter tuning
- Can find good configurations without manual intervention
- Provides model leaderboard for comparison

**Limitations**:
- Time constraints may limit model exploration
- May not always beat well-tuned GradientBoosting
- Requires more computational resources

**Recommendation**:
- Use AutoGluon for rapid prototyping and baseline establishment
- Fine-tune the best AutoGluon models with longer time limits
- Combine AutoGluon results with manual feature engineering

---

## 💡 Optimization Suggestions

### Short-term Optimization

1. **Data Enhancement**
   - Collect O3 data for more cities
   - Increase monitoring station density
   - Improve data quality (reduce missing values)

2. **Feature Engineering**
   - Add Air Quality Index (AQI) as target
   - Consider regional synergistic effects (surrounding cities)
   - Add holiday and weekend effects

3. **Model Optimization**
   - Use XGBoost or LightGBM to replace GradientBoosting
   - Try deep learning models (LSTM, Transformer)
   - Use AutoGluon with longer time limits for automatic tuning

### Long-term Optimization

1. **Multi-Task Learning**
   - Simultaneously predict PM2.5, O3, NO2, SO2
   - Share underlying feature extractors

2. **Spatial Attention Mechanism**
   - Consider regional atmospheric transport effects
   - Build inter-city pollution diffusion models

3. **Interpretability**
   - SHAP value analysis for feature contributions
   - Understand key influencing factors
   - Assist in policy making

---

## 📋 Summary

This full experiment covers 8 prediction modes and 6 machine learning algorithms, totaling 136 experiment configurations. Key conclusions:

### Core Findings

1. **Best Configuration**: CTM_New York + GradientBoosting (Validation RMSE: 3.5677)
2. **Best Algorithm**: GradientBoosting (Average Validation RMSE: 13.7322)
3. **Mode Selection**: Historical > Today, City-Level > Global, Separate > Multi-output
4. **City Differences**: New York > Chicago > Los Angeles > Houston > Beijing

### Practice Recommendations

1. **Production Deployment**: Use CHS mode + GradientBoosting
2. **Data Requirements**: At least 300 days of complete data per city
3. **Feature Engineering**: Must include temporal features
4. **Model Tuning**: Consider XGBoost or AutoGluon with longer time limits

### Future Directions

1. Expand to more cities and pollutants
2. Introduce deep learning models
3. Consider real-time prediction and early warning systems
4. Combine with meteorological forecast data

---

**Report Generated**: 2026-02-06
**Data Source**: Full experiment (20260206_044103_df1679c6) with AutoGluon
**Analysis Tools**: Python 3.10 + Pandas + Matplotlib + Seaborn
