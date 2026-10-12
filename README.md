# 长文转短视频分镜 · article-to-video-shots

![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.2.0-orange)
![Agents](https://img.shields.io/badge/agents-workbuddy%20%7C%20claude%20%7C%20cursor-lightgrey)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)

把你写好的长文，拆成一份能直接投喂文生视频模型的分镜脚本。

公众号推文、博客、测评稿、教程、报告、技术文档丢进来，产出一份带时间轴的镜头清单。每个镜头包含画面描述、中文提示词、英文提示词、口播配音、屏幕字幕五样东西，可以直接复制进可灵、即梦、Sora、Veo、Runway 去生成。

既是一个 **Agent Skill**（给 AI 助手用），也是一个 **命令行工具**（给人直接用）。

---

## 它解决什么

把长文改成视频脚本，通常踩三个坑，而且都是在片子做完后才发现。

| 坑 | 表现 | 本项目怎么拦 |
|---|---|---|
| 结构照搬 | 一脸同一个机位的口播画面，三秒被划走 | 强制重排成钩子／推进／收束的镜头结构，一个镜头只放一个信息点 |
| 提示词写不来 | 「性价比高」这种话模型听不懂，出来的画面完全不对 | 要求翻译成看得见的动作，并提供九种镜头公式和镜头语言词表 |
| 时长对不上 | 配音念不完，或者画面空转 | 按 4.5 字每秒自动核算，超出直接报错，还会提示哪些镜头太空 |

还有一个容易忽略的：**画面里不能出现任何需要模型渲染的文字**。中文必废，出来全是乱码。这条现在是硬检查。

---

## 三十秒上手

装好之后就三条命令。

```bash
# 1 从长文生成带时间轴的骨架
avs init 你的文章.md --duration 60

# 2 把每个镜头的五项填实（画面、中英提示词、配音、字幕）

# 3 体检到全绿再去渲染
avs check 分镜.md --strict
```

产出的分镜长这样：

```markdown
## 镜头 3｜演示（12-20 秒）

画面：深色终端窗口，一行命令逐字出现，其中一个片段高亮为古铜金色
中文提示词：竖屏 9:16，电影级打光……镜头正对屏幕，轻微手持感
英文提示词：vertical 9:16, cinematic lighting……
配音：OpenAI 兼容，原来的代码一行不改，只换地址和 Key
字幕：只换地址和 Key
```

---

## 安装

### 用 pip（推荐，装完就有 `avs` 命令）

```bash
pip install -e .
# 或者从 GitHub 直接装
pip install git+https://github.com/lijinhongucl-pixel/article-to-video-shots.git
```

### 不想装 Python 包

直接把仓库里的 `avs_cli/skill/` 整个目录复制到你的 Agent 的 skills 目录下，重命名为 `article-to-video-shots` 即可。

### 让 AI 助手也能用这套方法

运行一键安装，CLI 会自动探测本机装了哪些 Agent，把技能分别装进去。

```bash
avs install                # 装到本机所有已发现的 Agent
avs install --project      # 只装到当前项目的 skills 目录
avs install --agent claude # 只装到 Claude Code
avs install --dir ~/.your-agent/skills   # 手动指定，万能兜底
```

看看装到哪了、有没有装全：

```bash
avs list      # 只看本机已发现的
avs doctor    # 体检安装结果
```

支持的 Agent：

| Agent | 用户级目录 | 项目级目录 | 支持程度 |
|---|---|---|---|
| WorkBuddy | `~/.workbuddy/skills` | `.workbuddy/skills` | 已验证 |
| Claude Code | `~/.claude/skills` | `.claude/skills` | 已验证 |
| Cursor | `~/.cursor/skills` | `.cursor/skills` | 已验证 |
| CodeBuddy | `~/.codebuddy/skills` | `.codebuddy/skills` | 社区验证 |
| OpenCode | `~/.config/opencode/skills` | `.opencode/skills` | 社区验证 |
| Gemini CLI | `~/.gemini/skills` | `.gemini/skills` | 实验支持 |
| Codex CLI | `~/.codex/skills` | `.codex/skills` | 实验支持 |
| Trae | — | `.trae/skills` | 实验支持 |

标「实验支持」的目录在不同版本里位置可能不一样。**不确定就用 `--dir` 手动指定**，这是永远管用的兜底方式。

各家的路径配置集中在 `avs_cli/adapters.json`，新增一个平台只需要往里加一条。

---

## 命令参考

| 命令 | 作用 |
|---|---|
| `avs install` | 安装技能到一个或多个 Agent |
| `avs list [--all]` | 查看支持哪些 Agent、本机装了哪些 |
| `avs doctor` | 体检安装结果 |
| `avs uninstall [--agent x]` | 卸载 |
| `avs init 文章.md --duration 60` | 从长文生成分镜骨架 |
| `avs check 分镜.md [--strict] [--json]` | 体检，`--strict` 时提醒也算失败 |
| `avs learn add / show / digest / promote` | 经验沉淀 |

`avs init`、`avs check`、`avs learn` 会转发到已安装目录下的对应脚本，不需要记路径。

没装 Python 包时，也可以直接跑脚本：

```bash
python3 avs_cli/skill/scripts/init_storyboard.py 文章.md --duration 60
python3 avs_cli/skill/scripts/check_storyboard.py 分镜.md --strict
```

---

## 完整工作流

假设你有一篇写好的公众号推文 `article.md`，要做一条六十秒的竖屏短视频。

**第一步，生成骨架**

```bash
avs init article.md --duration 60
```

它会读文章的小标题作为候选镜头主题，按钩子短、中段平均、收尾略长的规则切好时间轴，生成一个全是 TODO 的骨架。

**第二步，逐项填实**

打开生成的 `分镜_article.md`，每个镜头填五项。中文口播按每秒 4.5 个字算，8 秒的镜头最多 36 个字。

写提示词记住一条：**把抽象意思翻译成看得见的动作**。不要写「效率提升」，写「五个窗口逐个关闭收拢成一把钥匙」。

两个参考词库可以直接取用：

- `avs_cli/skill/references/shot-patterns.md` 九种镜头类型的画面公式和翻车点
- `avs_cli/skill/references/prompt-patterns.md` 镜头语言中英对照词表

**第三步，体检到全绿**

```bash
avs check 分镜.md
```

有 E 级报错就改，改到零为止。接 CI 就加 `--strict`。

---

## 九项体检

| 代号 | 拦什么 |
|---|---|
| E1 | 缺必备字段 |
| E2 | 配音字数超出该镜头时长能念完的范围 |
| E3 | 画面描述里出现需要模型渲染的文字 |
| E4 | 镜头数不在 6 到 9 之间 |
| E5 | 时间轴断档、重叠或起点不为零 |
| E6 | 提示词没带全局风格前缀 |
| E7 | 英文提示词里混入了中文 |
| E8 | 命中历史沉淀的画面禁用词 |
| E9 | 字段还留着 TODO 占位符 |

另有五类提醒：画面出现金额百分比、提示词过短或过长、字幕超过 15 字、单镜头超过 8 秒、配音量相对画面过空。提醒默认不影响退出码，`--strict` 后算失败。

支持多文件批量检查，`--json` 输出机器可读结果。

---

## 会进化的部分

每做完一条片子，把学到的写回去。

```bash
# 记一条被否决的表达
avs learn add --category 画面 --text "别给手部特写" --why "模型画手必崩"

# 记一个渲染必崩的元素，之后体检会自动拦它
avs learn add --avoid "沙漏" --why "该模型渲染沙漏必崩"
```

第二条最有用。记过的禁用词会自动变成新的检查项，不用改一行代码，这就是 E8。

`avs learn show` 会统计每条经验的命中次数。**同一条出现三次以上，就把它升级成规则写进 SKILL.md**，这才是真的进化，不然只是记账。

经验文件不放在技能包内。全局在 `~/.workbuddy/avs/learnings.jsonl`，项目级在当前目录 `.avs/learnings.jsonl`，升级不会丢。

---

## 目录结构

```
article-to-video-shots/
├── avs_cli/
│   ├── cli.py              命令行入口
│   ├── adapters.json       各 Agent 技能目录配置
│   └── skill/              技能本体，随 pip 包分发
│       ├── SKILL.md        给 AI 助手读的方法论
│       ├── scripts/        四个 Python 脚本
│       └── references/     镜头类型库与镜头语言词表
├── pyproject.toml
├── LICENSE
├── CHANGELOG.md
└── .github/workflows/ci.yml
```

---

## 常见问题

**找不到我的 Agent 的目录怎么办**

用 `--dir` 直接指定。`avs install --dir ~/.my-agent/skills`，CLI 会在该目录下建 `article-to-video-shots/` 并复制技能进去。这是兜底方案，任何平台都适用。

**为什么口播按 4.5 字每秒算**

中文自然口播在这个速度上最清楚也不赶。你可以用 `check_storyboard.py --speech-rate 5.0` 调整。

**为什么画面里不能有文字**

文生视频模型渲染中文几乎必崩，出来是乱码。所有文字信息都应该放到「字幕」字段，交给后期叠加，而不是让模型画出来。

**能接流水线吗**

能。`check_storyboard.py` 的退出码符合 CI 约定，出错为 1。`--json` 输出结构化结果。GitHub Actions 的 `.github/workflows/ci.yml` 里有一份现成配置。

**必须联网吗**

不需要。四个脚本只用 Python 标准库，检测、生成、体检全部离线可跑。

---

## 参与贡献

欢迎提 Issue 和 PR。两件事特别欢迎：

一是补充 `adapters.json` 里新平台的路径，尤其是标「实验支持」的那几个。最好附上你本机的真实路径和版本号。

二是分享你在实际出片时总结的规则。如果某条规则你反复用到，建议直接写进 `SKILL.md`，让所有人受益。

改动脚本后记得跑一遍 CI 里的回归步骤。

## 许可证

MIT
