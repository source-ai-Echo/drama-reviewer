# Drama Reviewer 本地 Agent

这是可在个人电脑运行的剧本诊断网页。它不会内置作者的 API Key，也不包含任何私人剧本。

## 最简单的启动方式

1. 在 GitHub 页面点击 **Code → Download ZIP** 并解压。
2. macOS 双击 `app/start-mac.command`；Windows 双击 `app/start-windows.bat`。
3. 首次启动会安装运行依赖，完成后浏览器自动打开 `http://127.0.0.1:8765`。
4. 选择模型，上传或粘贴剧本，然后开始诊断。

macOS 第一次若阻止打开，可右键 `start-mac.command` 后选择“打开”。如果文件失去执行权限，可在终端运行 `chmod +x app/start-mac.command`。

## 模型与费用

- **OpenAI**：填写使用者自己的 API Key，费用归该 Key 所属账户。
- **兼容接口**：填写第三方服务的模型名、地址和 API Key。
- **本地模型**：默认连接 `http://127.0.0.1:11434/v1`，无需云端 Key，但需自行先启动兼容服务。

网页收到的 API Key 只保留在单次请求内存中，不写入磁盘或浏览器存储。若不想在网页输入 Key，也可复制 `.env.example` 为 `.env.local` 后使用命令行；不要提交该文件。

隐私说明：选择 OpenAI 或第三方兼容接口时，剧本会发送给对应模型服务商；选择并运行真正的本地模型时，剧本才可以不离开电脑。使用任何非本人剧本前，请先确认你有权上传和分析。

## 案例库

仓库仅附带 3 个虚构摘要，用来验证检索流程。你可以创建自己的本地案例库，并通过 `DRAMA_CORPUS_ROOT` 指向它。案例库至少需要：

```text
your-corpus/
├── manifests/corpus.json
├── calibration/guidance.md
└── cases/knowledge/*.md
```

只有 `corpus.json` 的 `retrieval_files` 中列出的 `cases/knowledge/` 文件会进入检索。请只使用你拥有权利的材料。

## 手动启动

需要 Python 3.10 或更高版本：

```bash
cd app
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python main.py serve
```

离线检查（不会调用任何付费 API）：

```bash
.venv/bin/python evals/run_offline.py
```

## 支持的材料

- `.docx`
- `.txt`
- `.md`
- 直接粘贴文字

单次材料上限 20MB；Agent 内部文本上限为 50 万字符。长篇材料建议按集或章节分批诊断。
