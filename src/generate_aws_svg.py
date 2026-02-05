#!/usr/bin/env python3
"""
生成包含 AWS 官方图标的 SVG 架构图
将 AWS 产品的 PNG 图标嵌入到 SVG 中
"""

import base64
from pathlib import Path


def encode_png_to_base64(png_path):
    """将 PNG 文件编码为 Base64"""
    with open(png_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


# AWS 产品图标映射
aws_icons = {
    'apigateway': {
        'name': 'API Gateway',
        'file': 'apigateway.png'
    },
    'apprunner': {
        'name': 'App Runner',
        'file': 'apprunner.png'
    },
    'bedrock': {
        'name': 'Bedrock',
        'file': 'bedrock.png'
    },
    'cloudfront': {
        'name': 'CloudFront',
        'file': 'cloudfront.png'
    },
    'eventbridge': {
        'name': 'EventBridge',
        'file': 'eventbridge.png'
    },
    'glue': {
        'name': 'Glue',
        'file': 'glue.png'
    },
    'lambda': {
        'name': 'Lambda',
        'file': 'lambda.png'
    },
    's3': {
        'name': 'S3',
        'file': 's3.png'
    },
    'sagemaker': {
        'name': 'SageMaker',
        'file': 'sagemaker.png'
    }
}


def generate_svg_with_icons():
    """生成包含 AWS 官方图标的 SVG"""

    # 图标目录
    icons_dir = Path('/Users/etworker/Documents/code/others/world_aq/doc/images')

    # 编码所有图标
    encoded_icons = {}
    for key, icon_info in aws_icons.items():
        png_path = icons_dir / icon_info['file']
        if png_path.exists():
            encoded_icons[key] = encode_png_to_base64(png_path)
            print(f"✓ 已编码: {icon_info['name']}")
        else:
            print(f"✗ 未找到: {icon_info['file']}")

    # 生成 SVG
    svg_content = f'''<svg width="1200" height="800" viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Arrow Marker -->
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333" />
    </marker>
  </defs>

  <!-- Background -->
  <rect width="100%" height="100%" fill="#FFFFFF"/>

  <!-- ================= ARCHITECTURE BOUNDARIES ================= -->

  <!-- 1. AWS Cloud Boundary -->
  <rect x="50" y="50" width="1100" height="700" rx="10" fill="none" stroke="#545B64" stroke-width="2"/>
  <text x="80" y="80" font-family="Arial" font-weight="bold" fill="#545B64">AWS Cloud</text>

  <!-- 2. Region Boundary -->
  <rect x="100" y="100" width="1000" height="600" rx="10" fill="none" stroke="#E7157B" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="120" y="130" font-family="Arial" font-size="14" fill="#E7157B">Region: us-east-1 (N. Virginia)</text>

  <!-- 3. VPC Boundary -->
  <rect x="150" y="200" width="900" height="450" rx="10" fill="#F7F7F7" stroke="#248814" stroke-width="3"/>
  <text x="170" y="230" font-family="Arial" font-weight="bold" fill="#248814">VPC (10.0.0.0/16)</text>

  <!-- 4. Availability Zone (AZ) Boundary -->
  <rect x="180" y="250" width="840" height="380" rx="10" fill="none" stroke="#3B48CC" stroke-width="1" stroke-dasharray="8,4"/>
  <text x="200" y="275" font-family="Arial" font-size="12" fill="#3B48CC">Availability Zone A</text>


  <!-- ================= SUBNETS ================= -->

  <!-- Public Subnet -->
  <rect x="210" y="300" width="200" height="300" rx="5" fill="#E1F3F8" stroke="#0073BB" stroke-width="1"/>
  <text x="220" y="325" font-family="Arial" font-size="12" fill="#0073BB">Public Subnet</text>
  <text x="220" y="340" font-family="Arial" font-size="10" fill="#555">IGW / NAT Access</text>

  <!-- Private Subnet (Compute & ML) -->
  <rect x="450" y="300" width="540" height="300" rx="5" fill="#F0FAFF" stroke="#0073BB" stroke-width="1"/>
  <text x="470" y="325" font-family="Arial" font-size="12" fill="#0073BB">Private Subnet</text>
  <text x="470" y="340" font-family="Arial" font-size="10" fill="#555">No Direct Internet Access</text>


  <!-- ================= COMPONENTS & ICONS ================= -->

  <!-- Edge Services (Outside VPC) -->
  <g>
    <image href="data:image/png;base64,{encoded_icons.get('cloudfront', '')}" x="290" y="110" width="80" height="80"/>
    <text x="330" y="210" text-anchor="middle" font-family="Arial" font-size="12">CloudFront</text>
  </g>

  <g>
    <image href="data:image/png;base64,{encoded_icons.get('s3', '')}" x="490" y="110" width="80" height="80"/>
    <text x="530" y="210" text-anchor="middle" font-family="Arial" font-size="12">S3 Static Web</text>
  </g>

  <!-- Public Subnet Components -->
  <rect x="260" y="400" width="100" height="100" rx="5" fill="white" stroke="#ccc"/>
  <image href="data:image/png;base64,{encoded_icons.get('apigateway', '')}" x="275" y="415" width="70" height="70"/>
  <text x="310" y="500" text-anchor="middle" font-family="Arial" font-size="11">API Gateway</text>
  <text x="310" y="515" text-anchor="middle" font-family="Arial" font-size="9" fill="#777">(VPC Endpoint)</text>

  <!-- Private Subnet Components - Group 1: Data Ingestion -->
  <g transform="translate(480, 350)">
    <rect x="0" y="0" width="140" height="100" rx="5" fill="white" stroke="#ddd"/>
    <image href="data:image/png;base64,{encoded_icons.get('eventbridge', '')}" x="15" y="20" width="30" height="30"/>
    <image href="data:image/png;base64,{encoded_icons.get('lambda', '')}" x="75" y="20" width="30" height="30"/>
    <text x="70" y="80" text-anchor="middle" font-family="Arial" font-size="10">Scheduler</text>
    <text x="70" y="95" text-anchor="middle" font-family="Arial" font-size="10" fill="#555">+ Ingestion Lambda</text>
  </g>

  <!-- Private Subnet Components - Group 2: ML Training -->
  <g transform="translate(640, 350)">
    <rect x="0" y="0" width="120" height="100" rx="5" fill="white" stroke="#ddd"/>
    <image href="data:image/png;base64,{encoded_icons.get('sagemaker', '')}" x="30" y="10" width="60" height="60"/>
    <text x="60" y="85" text-anchor="middle" font-family="Arial" font-size="10">SageMaker</text>
    <text x="60" y="98" text-anchor="middle" font-family="Arial" font-size="9" fill="#555">(AutoGluon)</text>
  </g>

  <!-- Private Subnet Components - Group 3: Inference & GenAI -->
  <g transform="translate(800, 350)">
    <rect x="0" y="0" width="160" height="200" rx="5" fill="white" stroke="#ddd"/>
    <image href="data:image/png;base64,{encoded_icons.get('lambda', '')}" x="60" y="20" width="40" height="40"/>
    <text x="80" y="75" text-anchor="middle" font-family="Arial" font-size="11">Inference Lambda</text>

    <image href="data:image/png;base64,{encoded_icons.get('bedrock', '')}" x="60" y="100" width="40" height="40"/>
    <text x="80" y="155" text-anchor="middle" font-family="Arial" font-size="11">Bedrock</text>
    <text x="80" y="170" text-anchor="middle" font-family="Arial" font-size="9" fill="#555">(Image Gen)</text>
  </g>

  <!-- Data Layer (S3 Data Lake) - Inside VPC via Gateway Endpoint -->
  <rect x="550" y="650" width="200" height="100" rx="5" fill="white" stroke="#2E7D32" stroke-width="2"/>
  <image href="data:image/png;base64,{encoded_icons.get('s3', '')}" x="620" y="660" width="60" height="60"/>
  <text x="650" y="740" text-anchor="middle" font-family="Arial" font-size="12">S3 Data Lake</text>
  <text x="650" y="755" text-anchor="middle" font-family="Arial" font-size="10" fill="#555">(Gateway Endpoint)</text>


  <!-- ================= CONNECTORS / FLOW ================= -->

  <!-- User -> CloudFront -->
  <path d="M60 150 L290 150" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="150" y="140" font-family="Arial" font-size="12">HTTPS</text>

  <!-- CloudFront -> S3 Web -->
  <path d="M370 150 L490 150" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- CloudFront -> API Gateway -->
  <path d="M330 190 L330 400" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="340" y="250" font-family="Arial" font-size="12">API Calls</text>

  <!-- API GW -> Inference Lambda -->
  <path d="M360 450 L860 450 L860 420" fill="none" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Ingestion -> S3 Lake -->
  <path d="M590 450 L590 650" stroke="#333" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow)"/>
  <text x="600" y="550" font-family="Arial" font-size="10">Write Data</text>

  <!-- SageMaker -> S3 Lake -->
  <path d="M700 450 L700 650" stroke="#333" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow)"/>
  <text x="710" y="550" font-family="Arial" font-size="10">Read/Write Model</text>

  <!-- Inference -> S3 Lake -->
  <path d="M820 420 L820 580 L740 650" fill="none" stroke="#333" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow)"/>

  <!-- Inference -> Bedrock -->
  <path d="M880 420 L880 450" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- External Data -->
  <rect x="20" y="550" width="100" height="80" fill="#eee" stroke="#999"/>
  <text x="70" y="580" text-anchor="middle" font-family="Arial" font-size="11">NOAA / OpenAQ</text>
  <text x="70" y="600" text-anchor="middle" font-family="Arial" font-size="9">(Internet)</text>

  <!-- Ingestion accesses Internet via NAT (Implicit) -->
  <path d="M70 550 L70 400 L500 400" fill="none" stroke="#999" stroke-width="1" stroke-dasharray="2,2"/>

</svg>'''

    return svg_content


if __name__ == '__main__':
    print("正在生成包含 AWS 官方图标的 SVG 架构图...")
    svg_content = generate_svg_with_icons()

    output_path = Path('/Users/etworker/Documents/code/others/world_aq/doc/images/arch_v3.svg')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

    print(f"\n✓ 已生成: {output_path}")
    print(f"  文件大小: {output_path.stat().st_size} 字节")
