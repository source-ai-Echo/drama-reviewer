from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class StoryUnderstanding(BaseModel):
    format_and_genre: str = "未能从材料确定"
    protagonist_and_goal: str = "未能从材料确定"
    central_conflict: str = "未能从材料确定"
    dramatic_question: str = "未能从材料确定"
    thematic_tension: str = "未能从材料确定"


class PriorityIssue(BaseModel):
    priority: Literal["关键", "重要", "润色"]
    title: str
    evidence: list[str] = Field(min_length=1, max_length=5)
    audience_effect: str
    likely_root_cause: str
    revision_direction: str
    implementation_options: list[str] = Field(default_factory=list, max_length=3)


class DimensionNotes(BaseModel):
    structure_and_escalation: str
    character_and_relationships: str
    scenes_and_pacing: str
    dialogue_and_subtext: str
    genre_tone_and_format: str
    ending_and_payoff: str


class DramaReview(BaseModel):
    title: str = "剧本诊断报告"
    overall_assessment: str
    evidence_boundary: str
    story_understanding: StoryUnderstanding
    strengths: list[str] = Field(default_factory=list, max_length=5)
    priority_issues: list[PriorityIssue] = Field(min_length=1, max_length=6)
    dimensions: DimensionNotes
    revision_order: list[str] = Field(min_length=1, max_length=5)
    preserve: list[str] = Field(default_factory=list, max_length=5)
    comparable_cases_used: list[str] = Field(default_factory=list, max_length=3)

    def to_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            "## 总体判断",
            self.overall_assessment,
            "",
            "## 信息边界",
            self.evidence_boundary,
            "",
            "## 作品理解",
            f"- 类型与形式：{self.story_understanding.format_and_genre}",
            f"- 主角及目标：{self.story_understanding.protagonist_and_goal}",
            f"- 核心冲突：{self.story_understanding.central_conflict}",
            f"- 核心戏剧问题：{self.story_understanding.dramatic_question}",
            f"- 主题张力：{self.story_understanding.thematic_tension}",
            "",
            "## 已经成立的部分",
        ]
        lines.extend(f"- {item}" for item in self.strengths)
        lines.extend(["", "## 关键问题"])
        for index, issue in enumerate(self.priority_issues, 1):
            lines.extend(
                [
                    f"### {index}. {issue.title}",
                    f"- 级别：{issue.priority}",
                    f"- 文本依据：{'；'.join(issue.evidence)}",
                    f"- 观众影响：{issue.audience_effect}",
                    f"- 可能成因：{issue.likely_root_cause}",
                    f"- 修改方向：{issue.revision_direction}",
                ]
            )
            if issue.implementation_options:
                lines.append(f"- 可选方案：{'；'.join(issue.implementation_options)}")
        lines.extend(
            [
                "",
                "## 分维度观察",
                f"- 结构与升级：{self.dimensions.structure_and_escalation}",
                f"- 人物与关系：{self.dimensions.character_and_relationships}",
                f"- 场景与节奏：{self.dimensions.scenes_and_pacing}",
                f"- 对白与潜台词：{self.dimensions.dialogue_and_subtext}",
                f"- 类型与基调：{self.dimensions.genre_tone_and_format}",
                f"- 结尾与回报：{self.dimensions.ending_and_payoff}",
                "",
                "## 修订顺序",
            ]
        )
        lines.extend(f"{index}. {item}" for index, item in enumerate(self.revision_order, 1))
        if self.preserve:
            lines.extend(["", "## 建议保留"])
            lines.extend(f"- {item}" for item in self.preserve)
        if self.comparable_cases_used:
            lines.extend(["", "## 内部参考记录"])
            lines.append("- 本次使用的本地知识案例：" + "、".join(self.comparable_cases_used))
        return "\n".join(lines).strip() + "\n"
