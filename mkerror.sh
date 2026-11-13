#!/bin/bash
NOW=$(date +"%Y-%m-%d %H:%M:%S")
# 先判断文件是否存在，不存在就新建
if [ -f ERROR.md ]; then
    { echo "# $NOW"; cat ERROR.md; } > ERROR.md.tmp
    mv ERROR.md.tmp ERROR.md
else
    echo "# $NOW" > ERROR.md
fi
echo "✅ 已在 ERROR.md 头部追加时间行：# $NOW"
