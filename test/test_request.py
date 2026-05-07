import os
from openai import OpenAI

client = OpenAI(
    api_key="not-used",
    base_url="http://localhost:8000/v1"
)

safer_client = OpenAI(
    api_key="not-used",
    base_url="http://localhost:8080/v1"
)


def stream_request_safe():
    completion = safer_client.chat.completions.create(
        model="glm-4.5-air",
        messages=[
            {"role": "user", "content": "Introduce yourself."}
        ],
        temperature=0.7,
        stream=True,
        extra_body={
            "guardrails": {
                "config_ids": ["dialog_api"]
            }
        }
    )

    for chunk in completion:
        print(chunk.choices[0].delta)


def instant_request_safe():
    completion = safer_client.chat.completions.create(
        model="glm-4.5-air",
        messages=[
            {"role": "user", "content": "Introduce yourself."}
        ],
        temperature=0.7,
        extra_body={
            "guardrails": {
                "config_ids": ["dialog_api"]
            }
        }
    )

    print(completion.choices[0].message.content)


if __name__ == "__main__":
    print("-"*5, "start", "-"*5)
    instant_request_safe()
    print("-"*5, "end", "-"*5)