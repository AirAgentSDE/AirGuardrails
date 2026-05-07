# Decision Trace

## D001: 内容安全审核使用中文原生 Prompt

**日期**: 2026-04-29
**状态**: 已采纳
**影响范围**: 所有`configs/`下的`prompts.yml`

### 背景

内容安全审核本质上是文本分类任务（判断 safe/unsafe + 类别），属于 NLP 分类任务范畴。guardrails 系统需要审核中文用户输入和 AI 输出。

### 决策

内容安全审核 prompt 使用中文（目标语言）编写，而非英文。

### 依据

- [Multilingual Prompt Engineering in LLMs: A Survey Across NLP Tasks](https://arxiv.org/abs/2505.11665) 研究表明，对于分类任务（如情感分类、内容审核），native-language prompt 的性能优于英文 prompt。这与推理任务（数学推理、代码生成）不同，后者英文 prompt 通常表现更好。
- 当前 guardrails 面向中文场景，审核对象为中文内容，使用中文 prompt 减少语言转换带来的语义损失。

### 影响

- `configs/` 下的 `/prompts.yml` 中的 prompt 必须使用中文编写
- 后续新增内容安全策略时，prompt 也应遵循中文优先原则
- 对于面向其他语言的 guardrails 场景，应使用对应语言编写 prompt
