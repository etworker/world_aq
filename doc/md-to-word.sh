#!/bin/bash
set -e

INPUT_MD="aws_arch.md"
OUTPUT_DOCX="aws_arch.docx"
TEMP_DIR="/tmp/md2docx_$$"
WORK_DIR="$TEMP_DIR/work"
mkdir -p "$WORK_DIR/images"

echo "📁 临时工作区: $WORK_DIR"

# ========================
# 步骤1: 复制源文件到工作区
# ========================
cp "$INPUT_MD" "$WORK_DIR/"
cd "$WORK_DIR"

# ========================
# 步骤2: 提取并渲染 Mermaid
# ========================
awk '
BEGIN { in_mermaid=0; count=0 }
/^```mermaid$/ {
  in_mermaid=1
  next
}
in_mermaid && /^```$/ {
  in_mermaid=0
  close("mermaid_" count ".mmd")
  print "![](images/mermaid_" count ".png)"
  count++
  next
}
in_mermaid {
  print $0 > ("mermaid_" count ".mmd")
  next
}
{ print }
' "$(basename "$INPUT_MD")" > "step1.md"

# 启用 nullglob 避免无匹配错误
shopt -s nullglob 2>/dev/null || true

# 渲染所有 Mermaid 文件
for mmd_file in mermaid_*.mmd; do
  [ -e "$mmd_file" ] || continue  # 再次保险
  idx=$(basename "$mmd_file" .mmd | sed 's/mermaid_//')
  png_file="images/mermaid_${idx}.png"
  
  echo "🖼️  渲染 Mermaid #$idx → $png_file"
  if mmdc -i "$mmd_file" -o "$png_file" -w 1600 -H 900 -b transparent 2>/dev/null; then
    echo "✅ 渲染成功"
  else
    echo "⚠️  降级渲染..."
    if mmdc -i "$mmd_file" -o "$png_file" -w 1200 -H 800 2>/dev/null; then
      echo "✅ 降级渲染成功"
    else
      echo "❌ 渲染失败，创建占位图"
      convert -size 400x300 xc:#f0f0f0 -pointsize 24 -fill "#666" \
        -gravity center "Mermaid #$idx\n(渲染失败)" "$png_file" 2>/dev/null || true
    fi
  fi
done

# ========================
# 步骤3: 处理 SVG（保持不变）
# ========================
if command -v rsvg-convert &> /dev/null; then
  echo "🔄 处理 SVG 资源..."
  grep -oE '!\[[^]]*\]\([^)]+\.svg\)|<img[^>]+src="[^"]+\.svg"' "step1.md" | \
  sed -E 's/.*\(([^)]+)\).*/\1/; s/.*src="([^"]+)".*/\1/' | sort -u | while read -r svg_relpath; do
    svg_abspath="$OLDPWD/${svg_relpath#./}"
    if [ ! -f "$svg_abspath" ]; then
      echo "⚠️  SVG 未找到: $svg_relpath，跳过"
      continue
    fi
    
    svg_dir=$(dirname "$svg_relpath")
    mkdir -p "$svg_dir" 2>/dev/null || true
    cp "$svg_abspath" "$svg_relpath"
    
    png_relpath="${svg_relpath%.svg}.png"
    if rsvg-convert -h 1200 "$svg_relpath" -o "$png_relpath" 2>/dev/null; then
      echo "✅ 转换: $svg_relpath → $png_relpath"
      sed -i '' "s|${svg_relpath}|${png_relpath}|g" "step1.md"
    fi
  done
else
  echo "⚠️  未安装 rsvg-convert（brew install librsvg），跳过 SVG 转换"
fi

# ========================
# 步骤4: 生成 Word
# ========================
echo "📄 生成 Word 文档..."
pandoc "step1.md" \
  -o "$OLDPWD/$OUTPUT_DOCX" \
  --dpi=300 \
  --wrap=auto \
  -V geometry:margin=1in \
  --metadata title="AWS Architecture" \
  --embed-resources \
  --standalone \
  --resource-path=".:$OLDPWD"

# ========================
# 步骤5: 验证输出
# ========================
if [ -f "$OLDPWD/$OUTPUT_DOCX" ]; then
  echo "✅ 转换完成: $OLDPWD/$OUTPUT_DOCX"
  echo "💡 提示: 打开 Word 后按 Ctrl+A 全选 → F9 刷新域代码"
else
  echo "❌ Word 生成失败"
  exit 1
fi