# Drama Reviewer

一个面向电影、电视剧、短剧和舞台剧的剧本诊断工具。它从故事引擎、结构、人物、场景、节奏及对白等维度，给出有文本依据、按优先级排列的修改建议。

这个仓库同时包含两种用法：**Codex Skill** 和 **本地 Agent 网页**。它们使用同一套审剧方法，你只需选择适合自己的入口。

## 先选择你的使用方式

| 我想要…… | 应该选择 | 入口 |
| --- | --- | --- |
| 直接在 Codex 对话中审剧 | **安装 Skill** | 阅读下方“安装 Skill” |
| 打开独立网页、上传剧本并生成报告 | **运行本地 Agent** | [查看本地 Agent 使用指南](app/README.md) |

### 路线 A：在 Codex 中使用 Skill

适合已经使用 Codex 的用户。安装后，在对话中输入 `$drama-reviewer` 并附上剧本或故事梗概即可。

### 路线 B：使用本地 Agent 网页

适合想要图形界面、文件上传和报告下载的用户：

1. 点击 GitHub 页面右上方的 **Code → Download ZIP**。
2. 解压下载的文件。
3. macOS 双击 `app/start-mac.command`；Windows 双击 `app/start-windows.bat`。
4. 浏览器打开后，选择模型并提供剧本。

首次启动需要联网安装运行组件，但不需要购买域名或租用服务器。

> **隐私与费用：** 仓库不包含作者的私人剧本或 API Key。使用 OpenAI 或第三方云端模型时，剧本会发送给对应服务商，费用由使用者自己的 API Key 账户承担；使用真正运行在本机的模型时，可以不产生云端模型费用。

## 能做什么

- 快速诊断故事梗概、提案或分场大纲
- 为完整剧本提供结构化评审意见
- 分析单场戏的目标、阻力、策略和转折
- 诊断人物能动性、人物弧光及关系变化
- 分析节奏、信息释放、对白和潜台词
- 在保留作者意图的前提下提供局部改写方向

Drama Reviewer 不会把某一种编剧公式当作普遍标准，也不会在未经要求时重写整部作品。

## 仓库结构

```text
drama-reviewer/
├── SKILL.md
├── app/                    # 本地 Agent 网页（可独立运行）
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

## 关于本地 Agent

网页默认只在本机 `127.0.0.1` 开放。用户可填写自己的 OpenAI/兼容服务 API Key，或连接已经运行的本地模型。网页不会把 API Key 保存到磁盘或浏览器存储。

完整说明见 [本地 Agent 使用指南](app/README.md)。

## 安装 Skill

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
