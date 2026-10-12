# 长文转短视频分镜

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.2.1-orange)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)
![Agents](https://img.shields.io/badge/agents-6-lightgrey)

把你写好的长文，拆成一份能直接投喂文生视频模型的分镜脚本。

微信公众号推文、博客、测评稿、教程、报告、技术文档丢进来，产出一份带时间轴的镜头清单。每个镜头包含**画面描述、中文提示词、英文提示词、口播配音、屏幕字幕**五样东西，可以直接复制进可灵、即梦、Sora、Veo、Runway 去生成。

它同时是两样东西：一个给 AI 助手用的 **Agent Skill**，和一个给人用的**命令行工具**。

---

## 它解决什么

把长文改成视频脚本，通常踩三个坑。坑的特点都是：做完了才发现，而且返工成本极高。

| 坑 | 具体表现 | 这里怎么解决 |
|---|---|---|
| **结构照搬** | 按段落顺序念一遍，出来是一堆同一个机位的口播画面，三秒被划走 | 强制重排成「钩子 / 推进 / 收束」的镜头结构，一个镜头只放一个信息点 |
| **提示词写不来** | 写「性价比高」，模型不知道该画什么，出来的画面跟你说的毫无关系 | 要求翻译成看得见的动作，并提供九种镜头公式和中英对照的镜头语言词表 |
| **时长对不上** | 配音念不完，或者画面已经空转两秒话还没说完 | 按 4.5 字／秒自动核算，超出直接报错，还会提示哪些镜头太空 |

还有一条容易忽略的硬伤：**画面里不能出现任何需要模型渲染的文字**。中文几乎必崩，出来全是乱码。这条现在是自动检查项（E3）。

### 用前用后

```
用前（照着段落写提示词）
  "介绍这个工具的效率提升"   →  模型不知道画什么，出来一堆抽象几何图形

用后（翻译成看得见的动作）
  "五个窗口逐个关闭，向中心收拢，最后合成一把金色钥匙"
                              →  画面清楚了，节奏也有了
```

---

## 快速开始

装好之后就三条命令：

```bash
# 1. 从长文生成带时间轴的骨架
avs init 你的文章.md --duration 60

# 2. 打开生成的分镜文件，把每个镜头的五项填实

# 3. 体检到全绿，再拿去渲染
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

有四种方式，按推荐程度排序。

### 方式一：pipx（推荐）

```bash
pipx install git+https://github.com/lijinhongucl-pixel/article-to-video-shots.git
avs install          # 装进本机已发现的 Agent
```

没有 pipx 的话：`brew install pipx`（macOS）或 `pip install --user pipx`。

### 方式二：一键脚本

```bash
curl -fsSL https://raw.githubusercontent.com/lijinhongucl-pixel/article-to-video-shots/main/install.sh | bash
```

脚本会下载仓库到临时目录、执行安装、然后清理临时文件。它只往各 Agent 的 skills 目录里写东西，不碰你的任何配置文件。

### 方式三：从源码

```bash
git clone https://github.com/lijinhongucl-pixel/article-to-video-shots.git
cd article-to-video-shots
python3 -m avs_cli.cli install
```

### 方式四：手动复制

不用 CLI 也行。把 `avs_cli/skill/` 整个目录复制到你 Agent 的 skills 目录下，重命名为 `article-to-video-shots`：

```bash
cp -r avs_cli/skill ~/.workbuddy/skills/article-to-video-shots    # WorkBuddy
cp -r avs_cli/skill ~/.claude/skills/article-to-video-shots       # Claude Code
```

---

## 支持的 Agent

| Agent | 用户级路径 | 项目级路径 | 确认程度 |
|---|---|---|---|
| **WorkBuddy** | `~/.workbuddy/skills` | `.workbuddy/skills` | verified |
| **Claude Code** | `~/.claude/skills` | `.claude/skills` | verified |
| **Codex CLI** | `~/.codex/skills` | `.codex/skills` | community |
| **Cursor** | `~/.cursor/skills` | `.cursor/skills` | community |
| **Gemini CLI** | `~/.gemini/skills` | `.gemini/skills` | experimental |
| **Trae** | — | `.trae/skills` | experimental |

确认程度的含义：

- **verified** — 官方文档明确写了这个路径
- **community** — 社区实践在用，但没在官方文档找到明确说明
- **experimental** — 推测值，不同版本可能不一样

所有路径都写在 `avs_cli/adapters.json`，新增一个平台只改这个配置文件，不用动代码。路径不对时用 `--dir` 手动指定，这是永远管用的兜底。

---

## CLI 命令

```bash
avs install                      装进本机所有已发现的 Agent
avs install --agent claude       只装 Claude Code
avs install --project            装到当前项目而不是用户全局
avs install --dir <路径>          手动指定目录，绕过自动探测
avs install --force              目标存在无关内容时也覆盖

avs list                         查看支持哪些、本机装了哪些
avs list --all                   本机没装的也列出来
avs doctor                       检查安装结果
avs uninstall                    卸载
avs uninstall --agent claude     只卸载某个

avs init 文章.md --duration 60    生成分镜骨架
avs check 分镜.md [--strict]      体检
avs learn add / show / digest    经验沉淀
```

后三个命令会转发到已安装目录下的脚本，所以装完之后不用记 Python 脚本的路径。

### 典型输出

```bash
$ avs list

支持的 Agent 与安装状态

  AGENT        状态     路径
  --------------------------------------------------------------------------
  workbuddy    [已装]   /Users/x/.workbuddy/skills/article-to-video-shots
  claude       [可装]   /Users/x/.claude/skills/article-to-video-shots
  codex        [可装]   /Users/x/.codex/skills/article-to-video-shots  [community]

  已发现 3 个 Agent，其中 1 个装了本技能。
```

---

## 怎么用

假设你有一篇写好的公众号推文 `article.md`，要做一条六十秒的竖屏短视频。

### 第一步：生成骨架

```bash
avs init article.md --duration 60
```

它会读文章的小标题作为候选镜头主题，按钩子短、中段平均、收尾略长的规则切好时间轴，生成一个全是 TODO 的骨架。

镜头数不用你操心——会按时长反推，单镜不超过 8 秒。要 50 秒就自动排 7 个镜头，不会出现「给了 50 秒只排出 41 秒」的情况。

### 第二步：逐项填实

打开生成的 `分镜_article.md`，每个镜头填五项。**核心技巧只有一条：把抽象意思翻译成看得见的动作。**

| 别这么写 | 这么写 |
|---|---|
| 效率提升 | 五个窗口逐个关闭，向中心收拢成一把钥匙 |
| 数据增长 | 柱状体从底部升起，旁边数字快速跳动 |
| 流程优化 | 三个节点依次点亮，中间的箭头变成直线 |

两个词库可以直接取用：

- `avs_cli/skill/references/shot-patterns.md` — 九种镜头类型的画面公式和翻车点
- `avs_cli/skill/references/prompt-patterns.md` — 镜头语言中英对照词表（景别、运镜、光线、质感）

中文口播按每秒 4.5 个字算，8 秒的镜头最多 36 个字。

### 第三步：体检到全绿

```bash
avs check 分镜.md
```

有 E 级报错就改，改到零为止。接 CI 就加 `--strict`，提醒也算失败。

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

另有五类提醒（不算失败，加 `--strict` 才算）：画面出现金额百分比、提示词过短或过长、字幕超过 15 字、单镜头超过 8 秒、配音量相对画面过空。

支持多文件批量检查，`--json` 输出机器可读结果。

---

## 会进化的部分

每做完一条片子，把学到的东西写回去：

```bash
# 记一条被否决的表达
avs learn add --category 画面 --text "别给手部特写" --why "模型画手必崩"

# 记一个渲染必崩的元素 —— 之后 E8 会自动拦它
avs learn add --avoid "沙漏" --why "该模型渲染沙漏必崩"
```

第二条最有用。记过的禁用词会自动变成新的检查项，**不用改一行代码**。

经验存在 `~/.workbuddy/avs/learnings.jsonl`（全局）和 `.avs/learnings.jsonl`（项目级），升级不会丢。

---

## 项目结构

```
article-to-video-shots/
├── avs_cli/
│   ├── cli.py              命令行入口
│   ├── adapters.json       各 Agent 路径配置（新增平台改这里）
│   └── skill/              技能本体
│       ├── SKILL.md        AI 助手读的方法论
│       ├── scripts/        四个 Python 脚本
│       └── references/     镜头类型库与镜头语言词表
├── install.sh              一键安装脚本
├── pyproject.toml
├── LICENSE                 MIT
├── CHANGELOG.md
├── CONTRIBUTING.md
└── .github/workflows/ci.yml
```

---

## 常见问题

**我的 Agent 不在支持列表里**

用 `--dir` 直接指定：

```bash
avs install --dir ~/.my-agent/skills
```

如果它工作正常，欢迎把路径加到 `avs_cli/adapters.json` 提个 PR（见 CONTRIBUTING.md）。

**提示「目录已存在且内容不相关」**

目标目录里有别的文件，工具不敢覆盖。确认可以覆盖就加 `--force`。这是防止误删你的东西。

**为什么口播按 4.5 字每秒算**

中文自然口播在这个速度上最清楚也不赶。可以调：`check_storyboard.py --speech-rate 5.0`。

**为什么画面里不能有文字**

文生视频模型渲染中文几乎必崩，出来是乱码。文字信息放「字幕」字段，交给后期叠加。

**能接流水线吗**

能。`check_storyboard.py` 退出码符合 CI 约定，出错为 1，`--json` 输出结构化结果。

**必须联网吗**

不需要。四个脚本只用标准库，检测、生成、体检全部离线可跑。

---

## 贡献

欢迎提 Issue 和 PR，尤其是这两类：

1. **补充 `adapters.json` 里的新平台路径**，特别是标 experimental 的几个，最好附上你的真实路径和版本号
2. **分享你在真实出片中总结的规则**

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT
