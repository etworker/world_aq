#!/usr/bin/env python3
"""
生成包含 AWS 官方图标的 prototype.svg
将 prototype.svg 中的简单图标替换为 AWS 产品实际图标
"""

import base64
from pathlib import Path


def encode_png_to_base64(png_path):
    """将 PNG 文件编码为 Base64"""
    with open(png_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


# AWS 产品图标映射
aws_icons = {
    'apigateway': 'apigateway.png',
    'bedrock': 'bedrock.png',
    'cloudfront': 'cloudfront.png',
    'eventbridge': 'eventbridge.png',
    'lambda': 'lambda.png',
    's3': 's3.png',
    'sagemaker': 'sagemaker.png'
}


def generate_prototype_svg_with_icons():
    """生成包含 AWS 官方图标的 prototype.svg"""

    # 图标目录
    icons_dir = Path('/Users/etworker/Documents/code/others/world_aq/doc/images')

    # 编码所有图标
    encoded_icons = {}
    for key, file_name in aws_icons.items():
        png_path = icons_dir / file_name
        if png_path.exists():
            encoded_icons[key] = encode_png_to_base64(png_path)
            print(f"✓ 已编码: {file_name}")
        else:
            print(f"✗ 未找到: {file_name}")

    # 生成 SVG
    svg_content = f'''<svg width="1000" height="700" xmlns="http://www.w3.org/2000/svg">
  <!-- Styles -->
  <style>
    .text-title {{ font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; fill: #232F3E; }}
    .text-subtitle {{ font-family: Arial, sans-serif; font-size: 14px; fill: #555; }}
    .text-icon {{ font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #232F3E; text-anchor: middle; }}
    .box-region {{ fill: #FFFFFF; stroke: #879596; stroke-width: 2; stroke-dasharray: 5,5; }}
    .box-vpc {{ fill: #F2F6FA; stroke: #8C4F9F; stroke-width: 2; }}
    .box-subnet {{ fill: #FFFFFF; stroke: #248814; stroke-width: 1; }}
    .arrow {{ stroke: #232F3E; stroke-width: 2; marker-end: url(#arrowhead); fill: none; }}
  </style>

  <!-- Definitions for Arrows -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#232F3E" />
    </marker>
  </defs>

  <!-- Background -->
  <rect x="0" y="0" width="1000" height="700" fill="#FFFFFF"/>

  <!-- Title -->
  <text x="50" y="40" class="text-title">Rapid Prototype: AQI Prediction &amp; GenAI System</text>
  <text x="50" y="65" class="text-subtitle">AWS Serverless Architecture for ABC Company</text>

  <!-- External Sources (Left) -->
  <rect x="20" y="350" width="120" height="150" rx="10" fill="#F0F0F0" stroke="#999"/>
  <text x="80" y="375" class="text-icon">Public Data</text>

  <circle cx="80" cy="410" r="20" fill="#CCCCCC"/>
  <text x="80" y="415" class="text-icon" fill="white" font-size="10">NOAA</text>

  <circle cx="80" cy="460" r="20" fill="#CCCCCC"/>
  <text x="80" y="465" class="text-icon" fill="white" font-size="10">OpenAQ</text>

  <!-- AWS Cloud Region -->
  <rect x="180" y="100" width="750" height="550" rx="10" class="box-region"/>
  <text x="200" y="130" class="text-subtitle" font-weight="bold">AWS Cloud (US Region)</text>

  <!-- VPC -->
  <rect x="210" y="150" width="690" height="480" rx="10" class="box-vpc"/>
  <text x="230" y="175" class="text-subtitle" fill="#8C4F9F">VPC</text>

  <!-- S3 Data Lake (Shared) -->
  <g transform="translate(450, 520)">
    <image href="data:image/png;base64,{encoded_icons.get('s3', '')}" x="-10" y="-10" width="70" height="70"/>
    <text x="25" y="70" class="text-icon">Amazon S3</text>
    <text x="25" y="85" font-size="10" text-anchor="middle" fill="#555">(Raw / Clean / Models)</text>
  </g>

  <!-- 1. Data Ingestion Layer -->
  <g transform="translate(250, 500)">
    <!-- EventBridge -->
    <image href="data:image/png;base64,{encoded_icons.get('eventbridge', '')}" x="-5" y="15" width="50" height="50"/>
    <text x="20" y="80" class="text-icon">EventBridge</text>
    <text x="20" y="95" font-size="10" text-anchor="middle" fill="#555">(Scheduler)</text>

    <!-- Lambda Ingestion -->
    <image href="data:image/png;base64,{encoded_icons.get('lambda', '')}" x="75" y="15" width="50" height="50"/>
    <text x="100" y="80" class="text-icon">Lambda</text>
    <text x="100" y="95" font-size="10" text-anchor="middle" fill="#555">(Ingestion)</text>
  </g>

  <!-- Arrow: Sources -> Lambda -->
  <path d="M140,430 C180,430 180,530 330,530" class="arrow"/>
  <!-- Arrow: EventBridge -> Lambda -->
  <line x1="290" y1="530" x2="330" y2="530" class="arrow"/>
  <!-- Arrow: Lambda -> S3 -->
  <line x1="370" y1="530" x2="450" y2="540" class="arrow"/>

  <!-- 2. Machine Learning Layer -->
  <g transform="translate(600, 480)">
    <!-- SageMaker Studio -->
    <image href="data:image/png;base64,{encoded_icons.get('sagemaker', '')}" x="-5" y="-5" width="50" height="50"/>
    <text x="20" y="55" class="text-icon">SageMaker</text>
    <text x="20" y="70" font-size="10" text-anchor="middle" fill="#555">Studio (IDE)</text>

    <!-- SageMaker Training -->
    <image href="data:image/png;base64,{encoded_icons.get('sagemaker', '')}" x="95" y="-5" width="50" height="50"/>
    <text x="120" y="55" class="text-icon">SageMaker</text>
    <text x="120" y="70" font-size="10" text-anchor="middle" fill="#555">Training (AutoGluon)</text>
  </g>

  <!-- Arrow: S3 -> SageMaker -->
  <path d="M500,540 C550,540 550,500 600,500" class="arrow"/>
  <path d="M500,540 C550,540 650,540 700,520" class="arrow"/>

  <!-- 3. Application Backend Layer -->
  <g transform="translate(400, 250)">
     <!-- API Gateway -->
     <image href="data:image/png;base64,{encoded_icons.get('apigateway', '')}" x="-5" y="15" width="50" height="50"/>
     <text x="20" y="80" class="text-icon">API Gateway</text>

     <!-- Lambda Backend -->
     <image href="data:image/png;base64,{encoded_icons.get('lambda', '')}" x="115" y="15" width="50" height="50"/>
     <text x="140" y="80" class="text-icon">Lambda</text>
     <text x="140" y="95" font-size="10" text-anchor="middle" fill="#555">(Inference &amp; Logic)</text>
  </g>

  <!-- 4. GenAI Layer (Right Side) -->
  <g transform="translate(700, 250)">
    <image href="data:image/png;base64,{encoded_icons.get('bedrock', '')}" x="-5" y="15" width="50" height="50"/>
    <text x="20" y="80" class="text-icon">Amazon</text>
    <text x="20" y="95" class="text-icon">Bedrock</text>
    <text x="20" y="110" font-size="10" text-anchor="middle" fill="#555">(Stable Diffusion)</text>
  </g>

  <!-- 5. Frontend Layer (Top) -->
  <g transform="translate(250, 150)">
    <!-- Users -->
    <circle cx="-150" cy="50" r="20" fill="#FF9900"/>
    <text x="-150" y="85" class="text-icon">End Users</text>

    <!-- CloudFront -->
    <image href="data:image/png;base64,{encoded_icons.get('cloudfront', '')}" x="-5" y="25" width="50" height="50"/>
    <text x="20" y="85" class="text-icon">CloudFront</text>

    <!-- S3 Web -->
    <image href="data:image/png;base64,{encoded_icons.get('s3', '')}" x="75" y="25" width="50" height="50"/>
    <text x="100" y="85" class="text-icon">S3 (Web)</text>
  </g>

  <!-- Flow Arrows (App) -->
  <!-- User -> CloudFront -->
  <line x1="120" y1="200" x2="250" y2="200" class="arrow"/>
  <!-- CloudFront -> S3 Web -->
  <line x1="290" y1="200" x2="330" y2="200" class="arrow"/>
  <!-- User -> API GW -->
  <path d="M120,200 C150,200 150,300 400,300" class="arrow"/>
  <!-- API GW -> Lambda -->
  <line x1="440" y1="290" x2="520" y2="290" class="arrow"/>
  <!-- Lambda -> Bedrock -->
  <line x1="560" y1="290" x2="700" y2="290" class="arrow"/>
  <!-- Lambda -> Get Model from S3 -->
  <path d="M540,310 C540,400 480,520 480,520" class="arrow" stroke-dasharray="4"/>

  <!-- Legend -->
  <rect x="800" y="600" width="180" height="90" fill="white" stroke="#ccc"/>
  <text x="810" y="620" font-size="12" font-weight="bold" font-family="Arial">Legend</text>
  <circle cx="820" cy="635" r="5" fill="#D65A18"/> <text x="835" y="640" font-size="10" font-family="Arial">Compute</text>
  <circle cx="820" cy="655" r="5" fill="#2E7D32"/> <text x="835" y="660" font-size="10" font-family="Arial">Storage</text>
  <circle cx="820" cy="675" r="5" fill="#188D8D"/> <text x="835" y="680" font-size="10" font-family="Arial">GenAI (Bedrock)</text>

</svg>'''

    return svg_content


if __name__ == '__main__':
    print("正在生成包含 AWS 官方图标的 prototype.svg...")
    svg_content = generate_prototype_svg_with_icons()

    output_path = Path('/Users/etworker/Documents/code/others/world_aq/doc/images/prototype_v2.svg')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

    print(f"\n✓ 已生成: {output_path}")
    print(f"  文件大小: {output_path.stat().st_size} 字节")
