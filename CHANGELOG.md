# 更新日志

本项目所有值得记录的改动都写在这里，格式参考 Keep a Changelog。

## 1.2.0

**新增跨平台一键安装 CLI**

- 新增 `avs` 命令行工具，零依赖，Python 3.9 起可用
- `avs install` 自动探测本机已装的 Agent，把技能装进各自的 skills 目录
- 支持 WorkBuddy、Claude Code、Cursor、CodeBuddy、OpenCode、Gemini CLI、Codex CLI、Trae
- 支持安装到用户全局或当前项目两种模式，支持 `--dir` 手动指定路径兜底
- `avs list` 查看Agent 与安装状态，`avs doctor` 体检安装结果，`avs uninstall` 卸载
- `avs init` / `avs check` / `avs learn` 直接转发到对应脚本，装完即可用，不必记脚本路径
- 支持 `--source` 从本地目录安装、`--url` 从远程压缩包安装

**项目结构改为标准开源布局**

- 技能本体移到 `avs_cli/skill/`，便于随 pip 包分发
- 新增 LICENSE、CHANGELOG、.gitignore、pyproject.toml
- 新增 GitHub Actions CI，自动做语法检查、安装自检、分镜体检回归
- 可以通过 `pip install -e .` 安装并获得 `avs` 命令

## 1.1.0

**体检扩到九项硬伤**

- 新增 E6 提示词缺全局风格前缀、E7 英文提示词混入中文、E8 命中历史禁用词、E9 字段仍为占位符
- 新增五类提醒，包括单镜头超过 8 秒、配音量相对画面过空
- `check_storyboard.py` 支持多文件、`--strict`、`--json`，退出码符合 CI 约定

**新增自我进化机制**

- 新增 `learn.py`，沉淀经验到 `~/.workbuddy/avs/learnings.jsonl` 与项目级 `.avs/learnings.jsonl`
- 经验文件记过的画面禁用词会自动变成新的检查项，无需改代码
- 同一条经验出现三次以上建议升级为 SKILL.md 的硬规则

**新增脚手架**

- 新增 `init_storyboard.py`，从长文读取小标题作为候选镜头主题并按规则切分时间轴
- 单镜头不超过 8 秒，目标时长装不下时提示删内容而不是拉长镜头

## 1.0.0

首个版本，提供五要素分镜写作法与基础体检。
