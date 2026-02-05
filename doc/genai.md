# GenAI 图片生成文档

## 1. 模块目标

本项目面向个人终端用户提供不仅是数字化的 AQI 预测，更是一种直观、富有情感的视觉体验。GenAI 模块的目标是根据当天的空气质量预测结果、天气状况、城市特色以及健康建议，生成一张独一无二的每日主题图片。这张图片将作为用户端的主要展示内容，直观传达“今日空气如何”以及“我该注意什么”。

## 2. 生成策略

### 2.1 核心要素融合

生成的图片需要融合以下四个维度的信息：

1.  **城市地标与特色 (City Identity)**：画面背景需体现用户所在城市的标志性建筑或地理特征（如纽约的帝国大厦、旧金山的金门大桥），增强用户的代入感。
2.  **天气与环境氛围 (Weather & Atmosphere)**：根据预测的天气（晴、雨、多云）和空气质量（清晰、朦胧、灰黄），渲染画面的光影、色彩和能见度。AQI 优良时天空通透蓝天白云，AQI 较差时增加大气雾感或暖黄色调。
3.  **每日主题 (Daily Theme)**：为每一天设定一个微主题（如“晨跑”、“通勤”、“周末野餐”、“居家阅读”），通过画面中人物的行为来隐喻。
4.  **健康建议可视化 (Health Advice)**：通过画面人物的着装和行为传达健康建议。例如，空气差时人物佩戴口罩或在室内活动；空气好时人物在户外运动。

### 2.2 提示词工程 (Prompt Engineering)

提示词构建是将结构化数据转化为图像的关键。我们将采用分层构建法生成 Prompt：

**结构模板：**
`[艺术风格] of [城市地标] under [天气状况] sky, [空气质量视觉效果], featuring [人物行为/主题], [健康防护细节]. High quality, photorealistic, cinematic lighting.`

**示例构建逻辑：**

*   **Input Data**:
    *   City: San Francisco
    *   AQI: 155 (Unhealthy)
    *   Weather: Cloudy
    *   Theme: Commute
*   **Generated Prompt**:
    "A photorealistic digital art of the Golden Gate Bridge in San Francisco under a cloudy sky. The atmosphere is hazy with a slight yellowish tint indicating air pollution. In the foreground, a person is commuting on a bicycle wearing a protective N95 mask. Cinematic lighting, detailed texture, 8k resolution."

## 3. 技术选型

### 3.1 模型选择

考虑到项目基于 AWS 架构，我们将优先使用 **Amazon Bedrock** 服务来调用基础模型，以确保合规性、稳定性和易集成性。

*   **首选模型：Stability AI - Stable Diffusion XL (SDXL) 1.0 (on Bedrock)**
    *   **理由**：SDXL 在生成逼真风景、处理复杂光影和理解简短自然语言提示方面表现优异，且推理速度快，成本可控。
*   **备选模型：Amazon Titan Image Generator G1**
    *   **理由**：AWS 原生模型，对真实感场景有很好的支持，且支持水印等负责任 AI 功能。

### 3.2 生成参数配置

*   **Style Preset**: `Photographic` 或 `Cinematic`，确保生成的图片具有照片级的真实感和质感。
*   **Negative Prompts**: `cartoon, illustration, text, watermark, blurry, deformed, low quality, ugly`，用于排除不希望出现的卡通风格或低质量元素。
*   **Aspect Ratio**: 推荐 `9:16` (适合移动端竖屏展示) 或 `1:1`。

## 4. 业务流程

1.  **触发生成**：当 AQI 预测模型完成对某城市次日的预测后，触发 GenAI 模块。
2.  **Prompt 组装**：系统根据城市元数据、预测结果（AQI等级）、天气预报自动填槽生成 Prompt。
3.  **API 调用**：后端 Lambda 函数调用 Amazon Bedrock API (InvokeModel)。
4.  **图像存储**：生成的图片（Base64或二进制流）解码后存储至 Amazon S3 `public-read` 存储桶中。
5.  **元数据关联**：将图片 URL 更新至当天的预测结果数据库中，供前端查询展示。

## 5. TBD (待定事项)

*   **多语言支持**：目前 Prompt 仅支持英文，未来考虑支持根据用户语言偏好生成特定文化元素的图片。
*   **风格个性化**：未来可允许用户选择偏好的艺术风格（如油画风、赛博朋克风）。
