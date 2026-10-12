#!/usr/bin/env python3
"""avs - 长文转短视频分镜的一键接入工具

零依赖，Python 3.9 起可跑。

    avs install                   自动检测并装进本机所有已发现的 Agent
    avs install --agent claude    只装某一个
    avs install --project         装到当前项目的目录
    avs install --dir <路径>      手动指定，万能兜底
    avs list                      看看支持哪些、本机装了哪些
    avs doctor                    检查装好了没有
    avs uninstall                 卸载
    avs check 分镜.md              转发到体检脚本
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SLUG = "article-to-video-shots"
VERSION = "1.2.1"
SKILL_MARKER = "SKILL.md"

HERE = Path(__file__).resolve().parent
BUNDLED = HERE / "skill"
FORWARD = {
    "init": "init_storyboard.py",
    "check": "check_storyboard.py",
    "learn": "learn.py",
}
SYM_OK = "[已装]"
SYM_READY = "[可装]"
SYM_NONE = "[未见]"


def expand(p):
    return Path(os.path.expandvars(os.path.expanduser(p)))


def home():
    return Path.home()


def dwidth(s):
    """终端显示宽度，中文按两格算"""
    return sum(2 if ord(c) > 127 else 1 for c in s)


def pad(s, n):
    return s + " " * max(0, n - dwidth(s))


def load_adapters():
    raw = json.loads((HERE / "adapters.json").read_text(encoding="utf-8"))
    return raw["adapters"]


def agent_installed(a):
    return any(expand(d).exists() for d in a.get("detect", []))


def selectable(path):
    """这个位置能不能用：自己存在，或者某个祖先目录存在（HOME 不算）"""
    p = expand(path)
    if p.exists():
        return True
    h = home()
    cur = p.parent
    while True:
        if cur == h or cur == cur.parent:
            return False
        if cur.exists():
            return True
        cur = cur.parent


def pick_user_target(a):
    for c in a.get("user", []):
        if selectable(c):
            return expand(c) / SLUG
    return None


def pick_project_target(a):
    for c in a.get("project", []):
        return expand(c) / SLUG
    return None


def target_display(a):
    """list 里展示的路径。不做可达性过滤，只是告诉用户「装了会装到哪」"""
    for c in a.get("user", []):
        return expand(c) / SLUG, "用户级"
    for c in a.get("project", []):
        return expand(c) / SLUG, "项目级"
    return None, ""


def safe_prepare(dst, force):
    """复制前检查目标，避免误删无关目录"""
    if not dst.exists():
        return
    if not dst.is_dir():
        raise SystemExit("目标已存在且不是目录：%s" % dst)
    if not any(dst.iterdir()):
        return
    if (dst / SKILL_MARKER).exists() or force:
        return
    raise SystemExit(
        "目录已存在且内容不相关：%s\n"
        "看起来不是本技能的安装目录。确认要覆盖就加 --force。" % dst
    )


def copy_skill(src, dst, force=False):
    safe_prepare(dst, force)
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    sd = dst / "scripts"
    if sd.exists():
        for py in sd.glob("*.py"):
            try:
                py.chmod(0o755)
            except OSError:
                pass


def resolve_source(args):
    if getattr(args, "source", None):
        return Path(args.source).resolve()
    if (BUNDLED / SKILL_MARKER).exists():
        return BUNDLED
    raise SystemExit(
        "没找到技能副本。用 --source 指定 skill 目录，或先 git clone 本仓库。"
    )


def cmd_list(args):
    rows = load_adapters()
    if args.agent:
        rows = [a for a in rows if a["id"] == args.agent]
        if not rows:
            raise SystemExit("未知 agent：%s，用 avs list 看支持的列表" % args.agent)

    print()
    print("支持的 Agent 与安装状态")
    print()
    print("  " + pad("AGENT", 13) + pad("状态", 9) + "路径")
    print("  " + "-" * 74)

    found = 0
    installed = 0
    for a in rows:
        has = agent_installed(a)
        t, kind = target_display(a)
        if has:
            found += 1
            if t and t.exists():
                sym, note = SYM_OK, ""
                installed += 1
            else:
                sym, note = SYM_READY, ""
        else:
            sym, note = SYM_NONE, ""
            if not args.all:
                continue
        loc = str(t) if t else "（需 --project 或 --dir）"
        if kind == "项目级":
            loc = loc + "  (项目级)"
        if a["status"] != "verified":
            loc = loc + "  [" + a["status"] + "]"
        print("  " + pad(a["id"], 13) + pad(sym, 9) + loc)

    print()
    print("  已发现 %d 个 Agent，其中 %d 个装了本技能。" % (found, installed))
    print("  未发现 = 没检测到这个 Agent。可装 = Agent 在，但还没装本技能。")
    print("  标 community / experimental 的路径是推测值，用 --dir 手动指定更稳妥。")
    print()


def cmd_install(args):
    src = resolve_source(args)
    if not (src / SKILL_MARKER).exists():
        raise SystemExit("来源目录里没有 %s：%s" % (SKILL_MARKER, src))

    print()
    print("  来源  %s" % src)

    dsts = []
    skipped = []

    if args.dir:
        dsts.append(("<指定目录>", expand(args.dir) / SLUG))
    else:
        rows = load_adapters()
        if args.agent:
            rows = [a for a in rows if a["id"] == args.agent]
            if not rows:
                raise SystemExit("未知 agent：%s，用 avs list 看支持的列表" % args.agent)
        else:
            rows = [a for a in rows if agent_installed(a)]

        for a in rows:
            t = pick_project_target(a) if args.project else pick_user_target(a)
            if t is None:
                hint = "没有用户级路径，试试 --project" if not args.project else "没有可用路径"
                skipped.append((a["id"], hint))
                continue
            dsts.append((a["id"], t))

    print()

    if not dsts:
        print("  没有可用的安装目标。")
        for label, why in skipped:
            print("    " + pad(label, 13) + why)
        print()
        print("  手动指定：avs install --dir ~/.your-agent/skills")
        print("  或先看看支持哪些：avs list --all")
        print()
        return

    ok = 0
    for label, dst in dsts:
        try:
            copy_skill(src, dst, getattr(args, "force", False))
            print("  " + SYM_OK + "  " + pad(label, 13) + str(dst))
            ok += 1
        except (OSError, SystemExit) as e:
            print("  [失败] " + pad(label, 13) + str(e))

    for label, why in skipped:
        print("  [跳过] " + pad(label, 13) + why)

    print()
    if ok:
        print("  已安装 %d 处。" % ok)
        print()
        print("  接下来")
        print("    avs doctor             确认安装结果")
        print("    avs init 文章.md        生成分镜骨架")
        print("    avs check 分镜.md       体检")
    else:
        print("  一处都没装上。用 --dir 手动指定目录试试。")
    print()

    # 全部失败时返回非 0，方便脚本判断
    return 0 if ok else 1


def cmd_uninstall(args):
    rows = load_adapters()
    if args.agent:
        rows = [a for a in rows if a["id"] == args.agent]
    n = 0
    print()
    for a in rows:
        cands = []
        t = pick_user_target(a)
        if t:
            cands.append(t)
        for c in a.get("project", []):
            cands.append(expand(c) / SLUG)
        for c in cands:
            if c.exists() and (c / SKILL_MARKER).exists():
                shutil.rmtree(c)
                print("  已移除  " + str(c))
                n += 1
    print()
    print("  共移除 %d 处" % n if n else "  没有找到已安装的副本")
    print()


def cmd_doctor(args):
    print()
    print("  avs %s    Python %s" % (VERSION, sys.version.split()[0]))
    print("  内置技能副本：%s" % ("存在" if (BUNDLED / SKILL_MARKER).exists() else "缺失"))
    print()
    any_ok = False
    for a in load_adapters():
        if not agent_installed(a):
            continue
        t = pick_user_target(a)
        if t and t.exists():
            complete = (t / "scripts" / "check_storyboard.py").exists()
            print("  " + pad(a["id"], 13) + ("正常" if complete else "不完整") + "    " + str(t))
            any_ok = any_ok or complete
        else:
            print("  " + pad(a["id"], 13) + "未安装本技能")
    print()
    if not any_ok:
        print("  还没装到任何 Agent。运行 avs install")
    print()


def locate_installed():
    for a in load_adapters():
        t = pick_user_target(a)
        if t and (t / SKILL_MARKER).exists():
            return t
        for c in a.get("project", []):
            c = expand(c) / SLUG
            if (c / SKILL_MARKER).exists():
                return c
    if (BUNDLED / SKILL_MARKER).exists():
        return BUNDLED
    return None


def cmd_forward(name, argv):
    d = locate_installed()
    if d is None:
        raise SystemExit("没找到已安装的技能，先运行 avs install")
    script = d / "scripts" / FORWARD[name]
    if not script.exists():
        raise SystemExit("缺少脚本：%s" % script)
    return subprocess.run([sys.executable, str(script)] + list(argv)).returncode


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] in FORWARD:
        return cmd_forward(argv[0], argv[1:])

    ap = argparse.ArgumentParser(
        prog="avs",
        description="长文转短视频分镜 · 跨平台一键接入",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "例子：\n"
            "  avs install                     装进本机所有已发现的 Agent\n"
            "  avs install --project           装到当前项目\n"
            "  avs install --dir ~/.x/skills   手动指定目录\n"
            "  avs doctor                      检查安装结果\n"
            "  avs init 文章.md --duration 60   生成分镜骨架\n"
            "  avs check 分镜.md --strict      体检\n"
        ),
    )
    ap.add_argument("--version", action="version", version="avs %s" % VERSION)
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("install", help="安装技能到一个或多个 Agent")
    p.add_argument("--agent", help="只装指定 agent，如 claude / workbuddy")
    p.add_argument("--dir", help="直接指定目标父目录，绕过自动探测")
    p.add_argument("--project", action="store_true", help="装到当前项目")
    p.add_argument("--source", help="本地技能目录，默认用包内置的 skill/")
    p.add_argument("--force", action="store_true", help="目标存在无关内容时也覆盖")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("list", help="查看支持的 agent 与安装状态")
    p.add_argument("--agent")
    p.add_argument("--all", action="store_true", help="本机没装的也列出来")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("uninstall", help="卸载")
    p.add_argument("--agent")
    p.set_defaults(func=cmd_uninstall)

    p = sub.add_parser("doctor", help="体检安装结果")
    p.set_defaults(func=cmd_doctor)

    args = ap.parse_args(argv)
    if not getattr(args, "cmd", None):
        ap.print_help()
        return 0
    rc = args.func(args)
    return rc if isinstance(rc, int) else 0


if __name__ == "__main__":
    sys.exit(main())
