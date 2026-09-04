# Drama Reviewer

一个面向电影、电视剧、短剧和舞台剧的剧本诊断 Skill。它帮助 ChatGPT 和 Codex 从故事引擎、结构、人物、场景、节奏及对白等维度给出有文本依据、按优先级排列的修改建议。

## 能做什么

- 快速诊断故事梗概、提案或分场大纲
- 为完整剧本提供结构化评审意见
- 分析单场戏的目标、阻力、策略和转折
- 诊断人物能动性、人物弧光及关系变化
- 分析节奏、信息释放、对白和潜台词
- 在保留作者意图的前提下提供局部改写方向

这个 Skill 不会把某一种编剧公式当作普遍标准，也不会在未经要求时重写整部作品。

## 仓库结构

```text
drama-reviewer/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── diagnostic-framework.md
│   └── report-template.md
├── evals/
│   └── cases.md
├── README.md
└── LICENSE
```

## 安装

### 使用 Skill Installer

在 Codex 中调用 `$skill-installer`，然后要求它从本 GitHub 仓库安装：

```text
请从下面这个 GitHub 仓库安装 drama-reviewer：
[在这里粘贴仓库页面的 HTTPS 地址]
```

在 GitHub 仓库页面点击 **Code**，复制 HTTPS 地址并粘贴到上面的提示中。

### 手动安装

把整个仓库复制到个人 Skill 目录：

```text
~/.agents/skills/drama-reviewer/
```

也可以把它放入某个项目的：

```text
.agents/skills/drama-reviewer/
```

如果新安装的 Skill 没有立即出现，请重启 Codex。

## 使用示例

显式调用：

```text
$drama-reviewer

请快速诊断下面的故事梗概，重点检查主角目标、阻力和结尾回报。
```

```text
$drama-reviewer

请完整分析这份短剧剧本。先指出最关键的三个根本问题，再给出修改顺序。
```

```text
$drama-reviewer

分析这一场争吵戏。不要改变人物关系设定，重点检查潜台词和场景转折。
```

Skill 默认允许隐式调用：当请求明确涉及剧本诊断时，ChatGPT 或 Codex 也可以根据 `description` 自动选择它。

## 测试建议

发布前至少测试以下情况：

1. 只有一句话故事概念。
2. 一份完整故事梗概。
3. 一场缺少冲突的对话戏。
4. 一份非线性叙事大纲。
5. 用户明确要求保留结局或人物设定。
6. 与剧本无关的普通书评请求，确认 Skill 不会误触发。

检查输出是否引用了真实文本依据、区分了根本问题与表面症状，并提供了可执行的修改方向。

仓库已经提供可重复使用的[行为测试案例](evals/cases.md)。这些测试关注模式选择、事实边界、作者约束和误触发，而不是要求模型输出固定措辞。

第一轮隔离测试的结果和修订记录见[测试报告](evals/results-2026-09-04.md)。

## 路线图

- `v0.1`: 剧本、梗概和单场戏诊断
- `v0.2`: 人物小传与人物弧光专项模式
- `v0.3`: 分场大纲和节奏图谱
- `v0.4`: 对白与潜台词专项模式
- `v1.0`: 稳定报告格式、公开测试集和版本化发布

## 贡献

欢迎通过 Issue 提交失败案例、误触发案例和新的测试提示。改动评审规则时，请说明它解决的实际问题，并提供至少一个能观察到改进的测试案例。

## 许可证

MIT License。详见 [LICENSE](LICENSE)。

## 相关文档

- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills)
