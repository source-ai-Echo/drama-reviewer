# Behavioral Test Cases

These cases test decisions and observable behavior rather than exact wording. Run them after changes to `SKILL.md` or its references.

## Case 1: Sparse premise and protected ending

**Expected trigger:** yes, explicit.

**Expected mode:** quick scan.

**Prompt:**

> 请快速诊断这个电影梗概：一名害怕与人冲突的殡仪馆化妆师发现，刚送来的死者是三年前失踪的姐姐。她偷偷调查，却在即将报警时得知父亲参与掩盖真相。结尾必须保留她在姐姐葬礼上公开父亲罪行的设定。重点检查故事引擎和人物选择。

**Pass conditions:**

- Identifies the protagonist, conflict, and connection between fear of conflict and the ending.
- Preserves the required funeral ending.
- Treats any deadline, evidence, motive, or new event as a revision possibility rather than a supplied fact.
- Marks missing urgency or stakes as not yet established instead of filling the report field with an invention.
- Gives no more than two strengths and two priority notes by default.
- Does not invent page numbers, quotations, or existing scenes.

## Case 2: Single scene with subtext

**Expected trigger:** yes, explicit.

**Expected mode:** scene diagnosis.

**Prompt:**

> 分析这场戏的潜台词和转折，不要扩写后续剧情：母亲正在给离家十年的儿子盛汤。儿子说：“味道没变。”母亲说：“锅早就换了。”儿子把一封没有拆开的信放到桌上。母亲继续盛汤，说：“凉了就不好喝了。”儿子收回信，起身离开。

**Pass conditions:**

- Focuses on the supplied scene rather than diagnosing an imagined full story.
- Identifies plausible objectives, resistance, and the change by the end.
- Labels interpretation as interpretation because motives are not explicitly stated.
- Does not invent the letter's contents or the reason for the son's absence.
- Does not continue the story or supply an unsolicited rewrite.

## Case 3: Writer constraint over formula

**Expected trigger:** yes, explicit.

**Expected mode:** quick scan.

**Prompt:**

> 这是一个反高潮短片：一个老人花整夜准备向旧友道歉，天亮后却把信烧了。请分析为什么这个结尾可能成立。不要建议他最终寄出信，也不要强行安排人物成长。

**Pass conditions:**

- Respects the anti-climax and the instruction not to send the letter.
- Evaluates meaning, setup, choice, and consequence without requiring transformation.
- Does not impose a beat sheet or conventional triumphant payoff.
- Does not turn "prepares all night" into specific existing actions such as revising drafts or recalling particular memories.

## Case 4: Negative trigger — generic book review

**Expected trigger:** no implicit invocation.

**Prompt:**

> 请评价这本历史学著作的论证和史料使用。

**Pass conditions:**

- The skill is not selected implicitly.

## Case 5: Negative trigger — blank-slate ghostwriting

**Expected trigger:** no implicit invocation.

**Prompt:**

> 从零替我写一部十集科幻剧，不需要先讨论概念。

**Pass conditions:**

- The skill is not selected implicitly because there is no existing dramatic concept or text to diagnose.

## Regression checklist

- Output language follows the user.
- Major notes contain evidence, audience effect, and revision direction.
- Suggestions are not reported as existing story facts.
- Root causes precede polish.
- User-protected facts and endings remain unchanged.
- Numerical scoring is absent unless requested or useful for a comparison.
