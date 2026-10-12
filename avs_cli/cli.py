#!/usr/bin/env python3
"""avs - 长文转短视频分镜的一键接入与日常使用入口

零依赖，Python 3.9+ 可跑。

    avs list                  看看本机装了哪些 agent，技能装到哪了
    avs install               安装到所有已发现的 agent
    avs install --agent claude --project
    avs doctor                体检安装结果
    avs uninstall --all
    avs check 分镜.md         日常使用，等价于跑 skill/scripts/check_storyboard.py
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

SLUG = "article-to-video-shots"
VERSION = "1.2.0"
SKILL_MARKER = "SKILL.md"
HERE = Path(__file__).resolve().parent
BUNDLED_SKILL = HERE / "skill"
DEFAULT_URL = (
    "https://github.com/lijinhongucl-pixel/article-to-video-shots/archive/refs/heads/main.tar.gz"
)
FORWARD_SCRIPTS = {
    "init": "init_storyboard.py",
    "check": "check_storyboard.py",
    "learn": "learn.py",
}


def expand(p):
    return Path(os.path.expandvars(os.path.expanduser(p)))


def load_adapters():
    data = json.loads((HERE / "adapters.json").read_text(encoding="utf-8"))
    return data


def agent_installed(adapter):
    """判断这台机器上是否装过这个 agent，依据是它的配置根目录在不在"""
    return any(expand(d).exists() for d in adapter.get("detect", []))


def targets_for(adapter, mode):
    roots = adapter.get("user", []) if mode == "user" else adapter.get("project", [])
    out = []
    for r in roots:
        base = expand(r) if mode == "project" else expand(r)
        out.append(base / SLUG)
    return out


def pick_target(adapter, mode):
    cands = targets_for(adapter, mode)
    if not cands:
        return None
    if mode == "user":
        for c in cands:
            parent = c.parent
            if parent.exists() or str(parent).startswith(str(Path.home())):
                return c if parent.exists() else None
        return None
    return cands[0]


def resolve_source(args):
    """决定技能从哪里复制过来"""
    if args.source:
        src = Path(args.source).resolve()
        return src, "本地目录"
    if (BUNDLED_SKILL / SKILL_MARKER).exists():
        return BUNDLED_SKILL, "安装包内置"
    if args.url:
        return download_skill(args.url), "远程下载"
    if not args.no_download:
        try:
            return download_skill(DEFAULT_URL or args.url), "远程下载"
        except Exception as e:
            raise SystemExit(
                f"没有可用的技能副本，联网下载也失败了（{e}）。\n"
                f"可以显式指定：avs install --source <本仓库的 avs_cli/skill 目录>"
            )
    raise SystemExit("没有可用的技能副本，请用 --source 指定 avs_cli/skill 目录")


def download_skill(url):
    if not url:
        raise ValueError("未提供下载地址")
    tmp = Path(tempfile.mkdtemp(prefix="avs-"))
    archive = tmp / "src.tar.gz"
    print(f"下载 {url}")
    with urllib.request.urlopen(url, timeout=60) as resp, open(archive, "wb") as f:
        f.write(resp.read())
    with tarfile.open(archive, "r:gz") as tf:
        tf.extractall(tmp / "unpacked", filter="data")
    root = find_skill_root(tmp / "unpacked")
    return root


def find_skill_root(base):
    """在解压目录里找到带 SKILL.md 且同层有 scripts 的那个目录"""
    candidates = list(base.rglob(SKILL_MARKER))
    if not candidates:
        raise SystemExit("下载的压缩包里没有找到 SKILL.md")
    for c in candidates:
        d = c.parent
        if (d / "scripts").is_dir() or (d / "references").is_dir():
            return d
    return candidates[0].parent


def copy_skill(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    for py in (dst / "scripts").glob("*.py") if (dst / "scripts").exists() else []:
        try:
            py.chmod(py.stat().st_mode | 0o111)
        except OSError:
            pass
    return dst


def cmd_list(args):
    adapters = load_adapters()
    if args.agent:
        adapters = [a for a in adapters if a["id"] == args.agent]
    print(f"{'agent':<14}{'安装状态':<10}{'技能位置'}")
    print("-" * 72)
    for a in adapters:
        found = agent_installed(a)
        if not found and not args.all:
            continue
        installed_at = []
        for mode in ("user", "project"):
            for t in targets_for(a, mode):
                if t.exists():
                    installed_at.append(str(t))
        mark = "已发现" if found else "未发现"
        loc = installed_at[0] if installed_at else "（未安装本技能）"
        print(f"{a['id']:<14}{mark:<10}{loc}")
    print()


def cmd_install(args):
    adapters = load_adapters()
    if args.dir:
        roots = [expand(args.dir) / SLUG]
        plan = [("<自定义>", "custom", roots)]
    else:
        if args.agent:
            adapters = [a for a in adapters if a["id"] == args.agent]
            if not adapters:
                raise SystemExit(f"未知的 agent：{args.agent}，可用 avs list --all 查看")
        elif not args.all:
            if os.environ.get("AVS_NONINTERACTIVE") != "1":
                detected = [a for a in adapters if agent_installed(a)]
                if not detected:
                    print("没有发现任何已知的 agent。指定目标再装：")
                    print("  avs install --dir ~/.your-agent/skills")
                    print("  avs install --agent claude")
                    return
                adapters = detected
        mode = "project" if args.project else "user"
        plan = []
        for a in adapters:
            if not agent_installed(a) and not args.force:
                continue
            t = pick_target(a, mode)
            if t is None:
                continue
            plan.append((a["id"], mode, [t]))
        if not plan:
            print("没有可安装的目标。用 avs list --all 看看支持哪些，或用 --dir 手动指定。")
            return

    src, origin = resolve_source(args)
    if not (src / SKILL_MARKER).exists():
        raise SystemExit(f"来源目录里没有 SKILL.md：{src}")
    print(f"技能来源 {origin}  {src}\n")

    for name, mode, roots in plan:
        for dst in roots:
            try:
                copy_skill(src, dst)
                print(f"已安装  {name:<12}{dst}")
            except OSError as e:
                print(f"失败    {name:<12}{dst}\n        {e}")
    print("\n下一步")
    print("  avs init 文章.md --duration 60    生成分镜骨架")
    print("  avs check 分镜.md                 体检")


def cmd_uninstall(args):
    adapters = load_adapters()
    if args.agent:
        adapters = [a for a in adapters if a["id"] == args.agent]
    removed = 0
    for a in adapters:
        for mode in ("user", "project"):
            for t in targets_for(a, mode):
                if t.exists():
                    shutil.rmtree(t)
                    print(f"已移除  {t}")
                    removed += 1
    if not removed:
        print("没有找到已安装的副本")
    else:
        print(f"共移除 {removed} 处")


def cmd_doctor(args):
    adapters = load_adapters()
    print(f"avs {VERSION}   Python {sys.version.split()[0]}")
    print(f"内置技能副本 {'存在' if (BUNDLED_SKILL / SKILL_MARKER).exists() else '缺失'}")
    print()
    installed_any = False
    for a in adapters:
        if not agent_installed(a):
            continue
        hits = [str(t) for mode in ("user", "project") for t in targets_for(a, mode) if t.exists()]
        state = "正常" if hits else "该 agent 已装但没装本技能"
        if hits:
            installed_any = True
        print(f"{a['id']:<12}{a['name']:<12}{state}")
        for h in hits:
            scripts_ok = (Path(h) / "scripts" / "check_storyboard.py").exists()
            print(f"{'':<24}└ {h}   scripts {'完整' if scripts_ok else '缺失'}")
    if not installed_any:
        print("还没有装到任何 agent。运行 avs install")


def locate_installed_skill():
    for a in load_adapters():
        for mode in ("user", "project"):
            for t in targets_for(a, mode):
                if (t / "scripts").exists() or (t / SKILL_MARKER).exists():
                    return t
    if (BUNDLED_SKILL / SKILL_MARKER).exists():
        return BUNDLED_SKILL
    return None


def cmd_forward(name, args):
    script = FORWARD_SCRIPTS[name]
    skill_dir = locate_installed_skill()
    if skill_dir is None:
        raise SystemExit("没有找到已安装的技能，先运行 avs install")
    target = skill_dir / "scripts" / script
    if not target.exists():
        raise SystemExit(f"缺少脚本：{target}")
    cmd = [sys.executable, str(target)] + args
    return subprocess.run(cmd).returncode


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    known = {"install", "list", "doctor", "uninstall", "init", "check", "learn"}
    passthrough = None
    if argv and argv[0] in FORWARD_SCRIPTS:
        passthrough = argv[0]
        return cmd_forward(passthrough, argv[1:])

    ap = argparse.ArgumentParser(
        prog="avs",
        description="长文转短视频分镜 · 一键接入与各平台安装",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "常用组合：\n"
            "  avs install                      装到本机所有已发现的 agent\n"
            "  avs install --project            装到当前项目的 skills 目录\n"
            "  avs doctor                       检查装好没有\n"
            "  avs init 文章.md --duration 60    从长文生成分镜骨架\n"
            "  avs check 分镜.md --strict        体检，提醒也算失败\n"
        ),
    )
    ap.add_argument("--version", action="version", version=f"avs {VERSION}")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("install", help="把技能装进一个或多个 agent")
    p.add_argument("--agent", help="只装到指定 agent，如 claude / workbuddy / cursor")
    p.add_argument("--dir", help="直接指定目标父目录，绕过自动探测")
    p.add_argument("--project", action="store_true", help="装到当前项目而不装到用户全局")
    p.add_argument("--all", action="store_true", help="不管有没有发现该 agent 都尝试安装")
    p.add_argument("--force", action="store_true", help="与 --all 配合，未发现的 agent 也创建目录")
    p.add_argument("--source", help="本地技能目录，默认用安装包内置的 avs_cli/skill")
    p.add_argument("--url", help="从远程压缩包安装")
    p.add_argument("--no-download", action="store_true", help="禁止联网下载")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("list", help="查看支持哪些 agent、本机装了哪些")
    p.add_argument("--agent")
    p.add_argument("--all", action="store_true", help="把本机未安装的 agent 也列出来")
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
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
