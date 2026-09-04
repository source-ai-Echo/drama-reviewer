from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

from knowledge import KnowledgeCorpus  # noqa: E402
from providers import ProviderConfig, build_model_runtime, provider_catalog  # noqa: E402
from schemas import DimensionNotes, DramaReview, PriorityIssue, StoryUnderstanding  # noqa: E402


def main() -> int:
    corpus = KnowledgeCorpus()
    policy = corpus.policy_summary()
    failures: list[str] = []
    if policy["retrieval_case_count"] < 1:
        failures.append("知识案例为空。")
    for path in corpus.allowed_paths:
        relative = str(path.relative_to(corpus.root))
        if not relative.startswith("cases/knowledge/"):
            failures.append(f"检索越界：{relative}")
    results = corpus.search("复仇 契约婚姻 商战 证据", 3)
    if not results:
        failures.append("知识检索没有返回结果。")
    if any("development" in str(item) or "blind-test" in str(item) for item in results):
        failures.append("非知识集材料发生泄漏。")
    sample_review = DramaReview(
        overall_assessment="样例判断",
        evidence_boundary="仅测试报告结构。",
        story_understanding=StoryUnderstanding(),
        strengths=["样例优点"],
        priority_issues=[
            PriorityIssue(
                priority="关键",
                title="样例问题",
                evidence=["第一段"],
                audience_effect="样例影响",
                likely_root_cause="样例原因",
                revision_direction="样例方向",
            )
        ],
        dimensions=DimensionNotes(
            structure_and_escalation="待判断",
            character_and_relationships="待判断",
            scenes_and_pacing="待判断",
            dialogue_and_subtext="待判断",
            genre_tone_and_format="待判断",
            ending_and_payoff="待判断",
        ),
        revision_order=["完成第一轮修改"],
    )
    if "# 剧本诊断报告" not in sample_review.to_markdown():
        failures.append("Markdown 报告渲染失败。")
    local_config = ProviderConfig.from_environment(provider="local", model="offline-test-model")
    runtime = build_model_runtime(local_config)
    if runtime.model.__class__.__name__ != "OpenAIChatCompletionsModel":
        failures.append("本地模型没有路由到兼容接口。")
    if runtime.tools_enabled:
        failures.append("本地模型不应默认依赖工具调用。")
    asyncio.run(runtime.close())
    if len(provider_catalog()) != 3:
        failures.append("模型接口目录不完整。")
    report = {
        "passed": not failures,
        "failures": failures,
        "policy": policy,
        "sample_result_count": len(results),
        "report_rendering": "passed" if not failures else "failed",
        "provider_routing": "passed" if not failures else "failed",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
