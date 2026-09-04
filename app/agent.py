from __future__ import annotations

import json
from pathlib import Path

from agents import Agent, Runner, function_tool

from config import CORPUS_ROOT, PUBLIC_SKILL_ROOT
from knowledge import get_corpus
from providers import ProviderConfig, build_model_runtime
from schemas import DramaReview


def _read_required(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"缺少运行规则文件：{path}")
    return path.read_text(encoding="utf-8")


def _runtime_instructions() -> str:
    skill = _read_required(PUBLIC_SKILL_ROOT / "SKILL.md")
    framework = _read_required(PUBLIC_SKILL_ROOT / "references" / "diagnostic-framework.md")
    calibration = _read_required(CORPUS_ROOT / "calibration" / "guidance.md")
    prompt = _read_required(Path(__file__).resolve().parent / "docs" / "prompt.md")
    return "\n\n".join((prompt, "公开审剧规则：\n" + skill, "诊断框架：\n" + framework, "案例库校准：\n" + calibration))


@function_tool
def search_knowledge_cases(query: str, max_results: int = 3) -> str:
    """检索已获准进入知识库的相似剧本案例；不可访问开发集或盲测集。

    Args:
        query: 用题材、人物关系、结构问题或关键情节组成的检索描述。
        max_results: 返回1至5个不同案例。
    """
    payload = {
        "policy": get_corpus().policy_summary(),
        "results": get_corpus().search(query, max_results=max_results),
    }
    return json.dumps(payload, ensure_ascii=False)


def build_agent(model: object, *, tools_enabled: bool = True) -> Agent:
    options = {
        "name": "Drama Reviewer",
        "instructions": _runtime_instructions(),
        "tools": [search_knowledge_cases] if tools_enabled else [],
        "output_type": DramaReview,
        "model": model,
    }
    return Agent(**options)


async def review_text(
    text: str,
    *,
    title: str = "未命名项目",
    material_type: str = "自动判断",
    concerns: str = "未指定",
    provider_config: ProviderConfig | None = None,
) -> DramaReview:
    if not text.strip():
        raise ValueError("剧本内容不能为空。")
    if len(text) > 500_000:
        raise ValueError("第一版单次最多读取50万字符，请先拆分材料。")

    initial_matches = get_corpus().search(f"{title}\n{material_type}\n{concerns}\n{text[:8000]}", 3)
    retrieval_context = json.dumps(initial_matches, ensure_ascii=False)
    user_input = f"""请对以下材料完成证据导向的中文剧本诊断。

项目名：{title}
材料类型：{material_type}
作者关注点：{concerns}

系统预检得到的相似知识案例（只作比较，不得把案例情节当成本稿事实）：
{retrieval_context}

待诊断材料：
<material>
{text}
</material>
"""
    config = provider_config or ProviderConfig.from_environment()
    runtime = build_model_runtime(config)
    try:
        result = await Runner.run(
            build_agent(runtime.model, tools_enabled=runtime.tools_enabled),
            user_input,
            run_config=runtime.run_config,
        )
        output = result.final_output
        if isinstance(output, DramaReview):
            return output
        return DramaReview.model_validate(output)
    finally:
        await runtime.close()
