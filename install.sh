#!/usr/bin/env bash
#
# article-to-video-shots 一键安装脚本
#
#   curl -fsSL https://raw.githubusercontent.com/lijinhongucl-pixel/article-to-video-shots/main/install.sh | bash
#
# 它会做三件事：下载本仓库到临时目录，把技能装进本机已发现的 Agent，然后清理临时文件。
# 不会修改你现有的任何配置文件，也不会在临时目录以外的地方写东西。
#

set -e

REPO_URL="https://github.com/lijinhongucl-pixel/article-to-video-shots"
TARBALL_URL="$REPO_URL/archive/refs/heads/main.tar.gz"
SLUG="article-to-video-shots"

say() { printf '%s\n' "$*"; }
die() { printf '\n[失败] %s\n' "$*" >&2; exit 1; }

# 1. 找 Python，要求 3.9 以上
PY=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
      PY="$candidate"
      break
    fi
  fi
done
[ -n "$PY" ] || die "没找到 Python 3.9 或更高版本。先装一个再运行本脚本。"

say "使用 $($PY -c 'import sys; print("Python %d.%d" % sys.version_info[:2])')"

# 2. 已经装过 avs 的话，提示一下但不阻止
if command -v avs >/dev/null 2>&1; then
  say ""
  say "检测到 avs 命令已存在，本脚本会继续用仓库最新代码安装一遍（等价于升级）。"
  say "想卸载的话：avs uninstall"
fi

# 3. 下载到临时目录
TMP="$(mktemp -d "${TMPDIR:-/tmp}/avs-install.XXXXXX")"
# 清理前先离开临时目录，避免删到自己脚下
cleanup() { cd / 2>/dev/null || true; rm -rf "$TMP"; }
trap cleanup EXIT

say ""
say "下载中..."

if command -v git >/dev/null 2>&1; then
  git clone --depth 1 --quiet "$REPO_URL" "$TMP/$SLUG" 2>/dev/null || {
    rm -rf "$TMP/$SLUG"
    curl -fsSL "$TARBALL_URL" | tar -xz -C "$TMP"
    # tarball 解出来的目录名带分支后缀
    if [ ! -d "$TMP/$SLUG" ] && [ -d "$TMP/${SLUG}-main" ]; then
      mv "$TMP/${SLUG}-main" "$TMP/$SLUG"
    fi
  }
else
  curl -fsSL "$TARBALL_URL" | tar -xz -C "$TMP"
  if [ ! -d "$TMP/$SLUG" ] && [ -d "$TMP/${SLUG}-main" ]; then
    mv "$TMP/${SLUG}-main" "$TMP/$SLUG"
  fi
fi

[ -f "$TMP/$SLUG/avs_cli/cli.py" ] || die "下载结果不完整，没找到 avs_cli/cli.py。请检查网络后重试。"

# 4. 安装
say ""
cd "$TMP/$SLUG"
"$PY" -m avs_cli.cli install

say ""
say "临时目录已清理。想直接用 avs 命令，装一下 pipx 版本："
say "  pipx install git+$REPO_URL"
say ""
say "或者不走 pipx，任何时候 git clone 本仓库后运行："
say "  python3 avs_cli/cli.py install"
say "  python3 avs_cli/cli.py check 分镜.md"
say ""
say "文档：$REPO_URL#readme"
