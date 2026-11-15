#!/usr/bin/env bash
# tree.sh —— 纯 find + awk 实现的目录树（不依赖 tree 命令）
#
# 用法:
#   ./tree.sh                # 扫描脚本所在目录
#   ./tree.sh -L 2           # 最多看 2 层
#   ./tree.sh -F             # 目录名后加 "/"
#   ./tree.sh /some/dir      # 指定扫描目录
#
# 过滤: 隐藏项(.开头，含 .git/.DS_Store)、venv、__pycache__、dist、build
# 说明: 同级排序按字节序（LC_ALL=C，结果稳定可复现），因此含 '.'/'_' 混排时
#       顺序可能与系统的 tree 略有差异；想跟随系统 locale 可删掉 export LC_ALL=C。
#       文件名中含制表符/换行的极端情况不支持（用 tab 做字段分隔）。

set -uo pipefail
export LC_ALL=C   # 保证排序稳定（字节序），避免不同 locale 下顺序漂移

# ---------- 0. 定位脚本所在目录 ----------
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd -P) || {
  printf 'tree.sh: 无法定位脚本所在目录\n' >&2
  exit 1
}

ROOT=$SCRIPT_DIR
MAXDEPTH=""
SHOW_SLASH=0

usage() {
  cat <<EOF
用法: ${0##*/} [-L 深度] [-F] [目录]

  -L N    限制递归深度（1 = 只看直接子项）
  -F      目录名后追加 "/"
  目录    要扫描的目录，缺省为脚本所在目录
EOF
}

# ---------- 1. 解析参数 ----------
while [ $# -gt 0 ]; do
  case $1 in
    -L)
      [ $# -ge 2 ] || { printf 'tree.sh: -L 需要一个数字参数\n' >&2; exit 2; }
      MAXDEPTH=$2; shift 2 ;;
    -L*) MAXDEPTH=${1#-L}; shift ;;
    -F) SHOW_SLASH=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) printf 'tree.sh: 未知选项 %s\n' "$1" >&2; exit 2 ;;
    *) ROOT=$1; shift ;;
  esac
done

[ -d "$ROOT" ] || { printf 'tree.sh: 目录不存在: %s\n' "$ROOT" >&2; exit 1; }
ROOT=$(cd -- "$ROOT" && pwd -P) || exit 1

if [ -n "$MAXDEPTH" ]; then
  case $MAXDEPTH in
    ''|*[!0-9]*) printf 'tree.sh: -L 必须是非负整数\n' >&2; exit 2 ;;
  esac
  [ "$MAXDEPTH" -ge 1 ] || { printf 'tree.sh: -L 必须 >= 1\n' >&2; exit 2; }
fi

# 根目录显示名（tree 的惯例：首行打印根的名字）
ROOTNAME=${ROOT##*/}
[ -n "$ROOTNAME" ] || ROOTNAME='/'   # ROOT 为 "/" 时

# ---------- 2. 组装 find 表达式 ----------
# -mindepth 1: 根目录自身不进列表（单独打印首行）
FIND_BASE=( "$ROOT" -mindepth 1 )
[ -n "$MAXDEPTH" ] && FIND_BASE+=( -maxdepth "$MAXDEPTH" )

# 屏蔽规则：命中即 -prune（不再深入，且自身不打印）
PRUNE=( \( -name '.?*' \
        -o -name 'venv' \
        -o -name '__pycache__' \
        -o -name 'dist' \
        -o -name 'build' \) -prune )

# ---------- 3. find 采集 + awk 建树 / 排版 ----------
# 分两趟只为拿到「目录/文件」类型（-printf 是 GNU 专有，Mac 上没有，故用 -type 分离，保持可移植）
{
  find "${FIND_BASE[@]}" "${PRUNE[@]}" -o -type d -print | awk '{ printf "d\t%s\n", $0 }'
  find "${FIND_BASE[@]}" "${PRUNE[@]}" -o ! -type d -print | awk '{ printf "f\t%s\n", $0 }'
} | awk -v root="$ROOT" -v showname="$ROOTNAME" -v dslash="$SHOW_SLASH" '
BEGIN {
  FS = "\t"
  prefix = (root == "/") ? "/" : root "/"
  n_dir = 0; n_file = 0
}

# ---- 收集阶段：把每个路径拆成 (父目录 key, 自己) 存进 kids[父, 序号] ----
{
  type = $1
  path = $2
  if (type == "" || path == "") next
  if (substr(path, 1, length(prefix)) != prefix) next   # 防御：不属于本次根
  rel = substr(path, length(prefix) + 1)
  if (rel == "" || rel == ".") next

  n = split(rel, seg, "/")
  name = seg[n]

  # 父目录 key（根的直接子项父 key 为 ""）—— 这里必须用完整相对路径做 key，
  # 不能只用目录名，否则同名目录会串组，正是"跨父目录混淆最后节点"的根源
  parent = ""
  for (i = 1; i < n; i++) parent = (i == 1) ? seg[1] : parent "/" seg[i]

  if (type == "d") n_dir++; else n_file++
  label[rel] = name
  isdir[rel] = (type == "d")
  kids[parent, ++cnt[parent]] = rel
}

# ---- 每个父目录内部按名字排序（手写插入排序，不依赖 asort） ----
function sort_children(p,    n, i, j, cur) {
  n = cnt[p] + 0
  for (i = 2; i <= n; i++) {
    cur = kids[p, i]
    for (j = i - 1; j >= 1; j--) {
      if (label[kids[p, j]] <= label[cur]) break
      kids[p, j + 1] = kids[p, j]
    }
    kids[p, j + 1] = cur
  }
}

# ---- 递归打印：last 由「本组内序号 == 本组总数」判定，天然按父分组 ----
function walk(p, indent,    n, i, key, is_last, child_indent) {
  sort_children(p)
  n = cnt[p] + 0
  for (i = 1; i <= n; i++) {
    key = kids[p, i]
    is_last = (i == n)
    printf "%s%s%s%s\n", indent, (is_last ? "└── " : "├── "), label[key], \
           ((dslash && isdir[key]) ? "/" : "")
    # 子层缩进：本项是最后一项 -> 4 空格；否则 -> "│   "（保证竖线只在有后续兄弟的层级出现）
    child_indent = indent (is_last ? "    " : "│   ")
    walk(key, child_indent)
  }
}

END {
  print showname
  walk("", "")
  printf "\n%d director%s, %d file%s\n", \
         n_dir, (n_dir == 1 ? "y" : "ies"), n_file, (n_file == 1 ? "" : "s")
}
'
