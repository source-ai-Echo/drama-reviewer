from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from agent import review_text
from knowledge import get_corpus
from providers import ProviderConfig, provider_catalog


SUPPORTED_TEXT = {".txt", ".md"}


def friendly_error(exc: Exception) -> str:
    message = str(exc)
    lowered = message.lower()
    if "credit_balance_exhausted" in lowered or "no credits remaining" in lowered or "insufficient_quota" in lowered:
        return "OpenAI API 余额不足。请在 OpenAI Platform 的 Billing 页面充值后重试。"
    if "connection error" in lowered:
        return "暂时无法连接所选模型接口，请检查网络和服务地址后重试。"
    if "api key" in lowered and ("missing" in lowered or "not set" in lowered):
        return "没有找到 OPENAI_API_KEY，请先完成密钥配置。"
    return message


def read_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(namespace + "p"):
        text = "".join(node.text or "" for node in paragraph.iter(namespace + "t"))
        if text.strip():
            paragraphs.append(text.strip())
    return "\n".join(paragraphs)


def read_material(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"找不到材料：{path}")
    suffix = path.suffix.lower()
    if suffix in SUPPORTED_TEXT:
        return path.read_text(encoding="utf-8")
    if suffix == ".docx":
        return read_docx(path)
    raise ValueError("第一版支持 .txt、.md 和 .docx 文件。")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Drama Reviewer Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    review = subparsers.add_parser("review", help="诊断一个剧本或大纲")
    source = review.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path, help=".txt、.md 或 .docx 文件")
    source.add_argument("--text", help="直接输入材料文字")
    review.add_argument("--title", default="未命名项目")
    review.add_argument("--material-type", default="自动判断")
    review.add_argument("--concerns", default="未指定")
    review.add_argument("--output", type=Path, help="保存为 Markdown 报告")
    review.add_argument("--json", action="store_true", help="输出结构化 JSON")
    review.add_argument("--provider", choices=("openai", "compatible", "local"), help="模型厂商类型")
    review.add_argument("--model", help="模型名称")
    review.add_argument("--base-url", help="OpenAI兼容接口地址")
    review.add_argument("--api-key-env", help="保存用户 API Key 的环境变量名称")
    review.add_argument("--api-mode", choices=("responses", "chat_completions"), help="接口模式")

    search = subparsers.add_parser("search", help="检查私有知识案例检索")
    search.add_argument("query")
    search.add_argument("--max-results", type=int, default=3)

    subparsers.add_parser("check", help="离线检查知识库边界")
    subparsers.add_parser("providers", help="查看可选择的模型接口")

    serve = subparsers.add_parser("serve", help="启动本地网页")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    return parser


async def run_review(args: argparse.Namespace) -> int:
    material = read_material(args.file) if args.file else args.text
    provider_config = ProviderConfig.from_environment(
        provider=args.provider,
        model=args.model,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
        api_mode=args.api_mode,
    )
    report = await review_text(
        material,
        title=args.title,
        material_type=args.material_type,
        concerns=args.concerns,
        provider_config=provider_config,
    )
    rendered = report.model_dump_json(indent=2) if args.json else report.to_markdown()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + ("" if rendered.endswith("\n") else "\n"), encoding="utf-8")
        print(f"报告已保存：{args.output.resolve()}")
    else:
        print(rendered)
    return 0


def main() -> int:
    args = build_parser().parse_args()
    try:
        corpus = get_corpus()
        if args.command == "check":
            print(json.dumps(corpus.policy_summary(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "search":
            print(json.dumps(corpus.search(args.query, args.max_results), ensure_ascii=False, indent=2))
            return 0
        if args.command == "providers":
            print(json.dumps(provider_catalog(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "serve":
            from web_app import run_server

            run_server(host=args.host, port=args.port)
            return 0
        return asyncio.run(run_review(args))
    except Exception as exc:
        print(f"错误：{friendly_error(exc)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if os.getenv("PORT") and len(sys.argv) == 1:
        from web_app import run_server

        run_server(host="0.0.0.0", port=int(os.environ["PORT"]))
    else:
        raise SystemExit(main())
