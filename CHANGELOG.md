# 更新日志

本文件记录每个版本值得关注的改动，格式参考 Keep a Changelog。

## [1.2.1]

### 新增

- `install.sh` 一键安装脚本，支持 `curl | bash`
- `CONTRIBUTING.md`，重点说明怎么新增一个 Agent 适配器
- GitHub Actions CI，覆盖 2 个操作系统 × 3 个 Python 版本，含安全保护回归测试
- README 补完整使用教程，明确四种安装方式的差异
- SKILL.md 增加「关于 avs 命令」章节，说明命令转发与安装路径无关性

### 修复

- 镜头数改为按时长反推。之前要 50 秒只会生成 6 个镜头共 41 秒，现在是 7 个镜头 49 秒
- `init_storyboard.py` 里有一行重复的 `return spans`
- 安装全部失败时退出码仍是 0，脚本无法判断成败，现在返回 1
- `avs list --all` 里未检测到 Agent 的平台会错误显示项目级路径，现在显示用户级

## [1.2.0]

### 新增

- **跨平台一键安装 CLI**（`avs` 命令），零依赖，Python 3.9 起可跑
  - `avs install` 自动检测本机已装的 Agent 并安装
  - `avs list` 查看支持哪些 Agent、本机装了哪些
  - `avs doctor` 检查安装结果
  - `avs uninstall` 卸载
  - `avs init / check / learn` 转发到对应脚本，不用记路径
- **六个 Agent 适配器**，路径配置集中在 `avs_cli/adapters.json`，新增平台只改配置不改代码
  - verified：WorkBuddy、Claude Code
  - community：Codex CLI、Cursor
  - experimental：Gemini CLI、Trae
- **三种安装方式**：pipx、一键脚本（`curl | bash`）、手动复制
- **标准开源项目结构**：LICENSE、CHANGELOG、.gitignore、pyproject.toml、CI

### 改进

- 镜头数改为按时长反推（单镜不超过 8 秒），不再出现「给了 50 秒只生成 41 秒」的情况
- 安装前检查目标目录，内容不相关时拒绝覆盖，避免误删用户文件
- 安装全部失败时返回非 0 退出码，方便脚本判断
- `avs list` 区分「未发现 Agent」和「Agent 在但没装技能」两种状态
- 各 Agent 路径标注确认程度（verified / community / experimental），不确定的明确标注

### 修复

- 多级目录路径判断错误：像 `~/.config/codex/skills` 这种，之前会误判为不可用
- `init_storyboard.py` 里有一行重复的 `return spans`

## [1.1.0]

### 新增

- 体检项从 5 项扩到 9 项：E6 提示词缺风格前缀、E7 英文提示词混入中文、E8 命中历史禁用词、E9 TODO 未填
- 五类提醒：金额百分比、提示词长度、字幕长度、单镜超时、配音过空
- `check_storyboard.py` 支持多文件、`--strict`、`--json`，退出码符合 CI 约定
- `learn.py` 经验沉淀机制，历史禁用词自动变成新检查项
- `init_storyboard.py` 从长文生成带时间轴的骨架

## [1.0.0]

首个版本。提供五要素分镜写作法与基础体检。
