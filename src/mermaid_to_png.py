#!/usr/bin/env python3
"""
Mermaid 图表转 PNG 脚本
从 Markdown 文件中提取 Mermaid 代码块，转换为 PNG 图片
"""

import re
import base64
import subprocess
import os
from pathlib import Path
from typing import List, Tuple


def extract_mermaid_blocks(markdown_file: str) -> List[Tuple[int, str, str]]:
    """
    从 Markdown 文件中提取 Mermaid 代码块
    返回: [(行号, 块ID, mermaid代码)]
    """
    with open(markdown_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    blocks = []
    in_mermaid = False
    mermaid_lines = []
    start_line = 0
    block_index = 0

    for i, line in enumerate(lines):
        if line.strip() == "```mermaid":
            in_mermaid = True
            start_line = i + 1
            mermaid_lines = []
        elif in_mermaid and line.strip() == "```":
            in_mermaid = False
            block_index += 1
            block_id = f"mermaid_{block_index}"
            blocks.append((start_line, block_id, "\n".join(mermaid_lines)))
        elif in_mermaid:
            mermaid_lines.append(line)

    return blocks


def mermaid_to_png_mmdc(mermaid_code: str, output_file: str) -> bool:
    """
    使用 mermaid-cli (mmdc) 将 Mermaid 转换为 PNG
    """
    try:
        # 创建临时文件
        temp_mmd = output_file.replace(".png", ".mmd")
        with open(temp_mmd, "w", encoding="utf-8") as f:
            f.write(mermaid_code)

        # 调用 mmdc
        result = subprocess.run(
            ["mmdc", "-i", temp_mmd, "-o", output_file, "-t", "default"], capture_output=True, timeout=30
        )

        # 清理临时文件
        if os.path.exists(temp_mmd):
            os.remove(temp_mmd)

        return result.returncode == 0
    except Exception as e:
        print(f"  转换失败: {e}")
        return False


def mermaid_to_png_pyppeteer(mermaid_code: str, output_file: str) -> bool:
    """
    使用 pyppeteer 将 Mermaid 转换为 PNG（需要安装 pyppeteer）
    """
    try:
        from pyppeteer import launch
        import asyncio

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        </head>
        <body>
            <div class="mermaid">
{mermaid_code}
            </div>
            <script>
                mermaid.initialize({{ startOnLoad: true }});
            </script>
        </body>
        </html>
        """

        async def render():
            browser = await launch(headless=True)
            page = await browser.newPage()
            await page.setContent(html_template, waitUntil="networkidle0")

            # 等待 mermaid 渲染完成
            await page.waitForSelector(".mermaid svg", timeout=10000)

            # 获取 SVG 元素并截图
            svg_element = await page.querySelector(".mermaid svg")
            await svg_element.screenshot({"path": output_file})

            await browser.close()

        asyncio.run(render())
        return True
    except ImportError:
        print("  未安装 pyppeteer，请运行: pip install pyppeteer")
        return False
    except Exception as e:
        print(f"  转换失败: {e}")
        return False


def mermaid_to_png_online(mermaid_code: str, output_file: str) -> bool:
    """
    使用 mermaid.ink 在线 API 将 Mermaid 转换为 PNG
    注意：依赖在线服务，可能不稳定
    """
    try:
        import requests

        # 使用 mermaid.ink API
        url = "https://mermaid.ink/img/"
        encoded = base64.b64encode(mermaid_code.encode("utf-8")).decode("utf-8")
        response = requests.get(f"{url}{encoded}", timeout=30)

        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
            return True
        return False
    except ImportError:
        print("  未安装 requests，请运行: pip install requests")
        return False
    except Exception as e:
        print(f"  转换失败: {e}")
        return False


def update_markdown_with_images(markdown_file: str, blocks: List[Tuple[int, str, str]], output_dir: str):
    """
    更新 Markdown 文件，将 Mermaid 代码块替换为图片引用
    """
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 从后往前替换，避免行号变化
    for line_num, block_id, _ in reversed(blocks):
        lines = content.split("\n")
        # 找到 mermaid 代码块的开始和结束
        start_idx = None
        end_idx = None
        for i in range(line_num - 1, len(lines)):
            if lines[i].strip() == "```mermaid":
                start_idx = i
                break

        if start_idx is not None:
            for i in range(start_idx + 1, len(lines)):
                if lines[i].strip() == "```":
                    end_idx = i
                    break

        if start_idx is not None and end_idx is not None:
            # 替换为图片引用
            image_path = f"{output_dir}/{block_id}.png"
            lines[start_idx : end_idx + 1] = [f"![{block_id}]({image_path})", "", ""]
            content = "\n".join(lines)

    # 写入新文件
    output_file = markdown_file.replace(".md", "_with_images.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n✓ 已生成带图片的 Markdown 文件: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Mermaid 图表转 PNG")
    parser.add_argument("markdown_file", help="Markdown 文件路径")
    parser.add_argument("-o", "--output-dir", default="doc/images", help="输出目录（默认: doc/images）")
    parser.add_argument(
        "-m", "--method", choices=["mmdc", "pyppeteer", "online"], default="online", help="转换方法（默认: online）"
    )

    args = parser.parse_args()

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 提取 Mermaid 代码块
    print(f"正在扫描: {args.markdown_file}")
    blocks = extract_mermaid_blocks(args.markdown_file)

    if not blocks:
        print("未找到 Mermaid 代码块")
        return

    print(f"找到 {len(blocks)} 个 Mermaid 代码块\n")

    # 转换每个代码块
    success_count = 0
    for line_num, block_id, mermaid_code in blocks:
        output_file = os.path.join(args.output_dir, f"{block_id}.png")
        print(f"转换 {block_id} (第 {line_num} 行) -> {output_file}")

        # 根据方法选择转换函数
        if args.method == "mmdc":
            success = mermaid_to_png_mmdc(mermaid_code, output_file)
        elif args.method == "pyppeteer":
            success = mermaid_to_png_pyppeteer(mermaid_code, output_file)
        else:  # online
            success = mermaid_to_png_online(mermaid_code, output_file)

        if success:
            success_count += 1
            print(f"  ✓ 转换成功")
        else:
            print(f"  ✗ 转换失败")

    print(f"\n转换完成: {success_count}/{len(blocks)} 成功")

    # 询问是否更新 Markdown 文件
    if success_count > 0:
        response = input("\n是否更新 Markdown 文件，将 Mermaid 代码块替换为图片引用？(y/n): ")
        if response.lower() == "y":
            update_markdown_with_images(args.markdown_file, blocks, args.output_dir)


if __name__ == "__main__":
    main()
