# Debug 日志

## 1. NemoGuardrails v0.21.0 硬编码参数导致回复截断

**现象：** 护栏调用 LLM 时，模型回复被意外提前终止，输出不完整。

**根因：** NemoGuardrails 0.21.0 在内部硬编码了以下参数：
- `temperature` — 固定值，无法通过配置覆盖
- `stop_sequence` — 包含默认的停止序列，会提前触发终止
- `max_tokens` — 设置了较低的上限（如 256），限制输出长度

其中 `stop_sequence` 和 `max_tokens` 是导致回复截断的直接原因。

**修复方式：** 在对应护栏的 `action.py` 中覆盖这些参数，将 `stop` 设为 `None`，并放宽 `max_tokens` 限制。

**教训：** 使用第三方 guardrails 框架时，需确认其内部 LLM 调用参数是否可配置，避免隐式参数干扰业务逻辑。

---

## 2. vllm_openai 与 openai_chat 返回行为不一致

**现象：** 同一模型在使用 vllm_openai 类型调用时产生异常行为（输出异常、不符合预期），而 openai_chat 类型调用正常。

**调用参数对比：**

```
# openai-chat 调用参数（正常）
{
  'model': 'huggingface.co/mradermacher/qwen3guard-gen-4b-gguf:Q8_0',
  'model_name': 'huggingface.co/mradermacher/qwen3guard-gen-4b-gguf:Q8_0',
  'stream': False,
  'n': 1,
  'temperature': 0.7,
  '_type': 'openai-chat',
  'stop': None
}

# vllm-openai 调用参数（异常）
{
  'model_name': 'huggingface.co/mradermacher/qwen3guard-gen-4b-gguf:Q8_0',
  'temperature': 0.0,
  'top_p': 1.0,
  'frequency_penalty': 0.0,
  'presence_penalty': 0.0,
  'n': 1,
  'logit_bias': {},
  'max_tokens': 256,
  '_type': 'vllm-openai',
  'stop': None
}
```

**关键差异：**
- `temperature`：openai_chat 为 0.7，vllm_openai 被覆盖为 0.0（贪婪解码）
- `max_tokens`：openai_chat 未限制，vllm_openai 强制 256
- `model` 字段：vllm_openai 缺少 `model` 传递
- 额外参数：vllm_openai 注入了 `frequency_penalty`、`presence_penalty`、`logit_bias` 等

**根因：** NemoGuardrails 对 `vllm-openai` 类型使用了独立的参数模板，默认值与 `openai-chat` 差异较大，且配置优先级不同，导致用户配置被内部默认值覆盖。

**修复方式：** 统一将模型调用类型从 `vllm-openai` 修改为 `openai-chat`，通过 OpenAI 兼容接口调用 vLLM 服务。

**教训：** 当 vLLM 提供 OpenAI 兼容 API 时，优先使用 `openai-chat` 类型调用，避免框架对不同 provider 类型的参数处理差异。
