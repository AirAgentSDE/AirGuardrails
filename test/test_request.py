import os
from openai import OpenAI


safer_client = OpenAI(
    api_key="not-used",
    base_url="http://localhost:8080/v1"
)


def instant_request_safe():
    completion = safer_client.chat.completions.create(
        model="hf.co/unsloth/Qwen3.6-27B-GGUF:Q4_K_M",
        messages=[
            {"role": "user", "content": "Write a hello world program in Rust."}
        ],
        extra_body={
            "guardrails": {
                "config_ids": ["content_safety_reasoning", "main"],
                "options": {
                    "rails": {
                        "input": True,
                        "output": True,
                        "dialog": True
                    },
                    "llm_params": {
                        "stop": None
                    },
                    "log": {
                        "activated_rails": True,
                        "llm_calls": True,
                    },
                }
            }
        }
    )
    print(completion.choices[0].message.content)
    print("-"*20)
    print(completion)


if __name__ == "__main__":
    print("-"*10, "start", "-"*10)
    instant_request_safe()
    print("-"*10, "end", "-"*10)