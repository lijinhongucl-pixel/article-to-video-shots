# 贡献指南

感谢你想让这个项目变得更好。这里说明几类常见改动的路径。

## 提 Issue

- 报 bug 时请附上：操作系统、`python3 --version`、`avs doctor` 的完整输出。
- 建议新功能时请说清楚「你想做什么片子」和「现在卡在哪」，这比直接要一个功能更容易讨论。

## 改代码

```bash
git clone https://github.com/lijinhongucl-pixel/article-to-video-shots.git
cd article-to-video-shots
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
avs --version
```

改完跑一遍端到端，确认没破坏已有行为：

```bash
cd /tmp && mkdir -p t && cd t
printf '# 标题\n\n## 一节\n\n内容。\n' > art.md
avs init art.md --duration 45 --out sb.md
avs check sb.md | grep -q "E9" && echo "OK"
```

代码风格：零依赖是硬约束，除标准库外不要引入任何第三方包。

## 新增一个 Agent 适配器

这是最容易上手也最有价值的贡献。所有平台路径都集中在 `avs_cli/adapters.json`，**不用改 Python 代码**。

```json
{
  "id": "myagent",
  "name": "My Agent",
  "detect": ["~/.myagent"],
  "user": ["~/.myagent/skills"],
  "project": [".myagent/skills"],
  "status": "community"
}
```

字段说明：

| 字段 | 含义 |
|---|---|
| `id` | 命令行里用的标识，`avs install --agent myagent` |
| `name` | 展示名 |
| `detect` | 判断本机有没有装这个 Agent 的路径，通常是一级配置目录 |
| `user` | 用户级技能目录候选，按顺序取第一个可用的 |
| `project` | 项目级技能目录候选 |
| `status` | `verified` 官方文档确认 / `community` 社区验证 / `experimental` 推测值 |

`status` 请如实填写。标 `experimental` 不丢人，标错才会害别人删错目录。

## 贡献经验规则

如果你在真实出片中总结出一条反复用到的规则，欢迎提 PR 写进 `avs_cli/skill/SKILL.md`。质量要求：

- 说清楚「怎么做」，而不是「要注意」
- 最好带上反例，说明不这么做会出什么问题
